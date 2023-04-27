import asyncio
from concurrent.futures import ProcessPoolExecutor
from distutils.filelist import findall
from gettext import find
import html
from multiprocessing.connection import wait
from signal import signal
from turtle import title
from unittest import result
import aiohttp
import re
from requests import head, request
import requests
import time
import multiprocessing
import datetime
from dateutil.relativedelta import relativedelta
from  fuzzywuzzy import fuzz
from fuzzywuzzy import process
from bs4 import BeautifulSoup
import xlwt
from time import time
semophore=asyncio.Semaphore(2)#同步信号量，用来控制并发度，因为清华爬的快会封，所以改成同步爬取


def get_page_num(headers):
    base_url='https://cs.fudan.edu.cn/24259/list1.htm'
    response=requests.get(base_url,headers).content.decode('utf-8')
    page_num=8
    return page_num


#根据页数生成其他网页的的连接
def make_url(page_num):
    urls=[]
    for num in range(1,page_num+1):
        urls.append('https://cs.fudan.edu.cn/24259/list{}.htm'.format(num))
    return urls

#上面三个函数拿到所有浏览页面的url

#异步io爬虫
async def craw(url,headers):
    async with semophore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url,headers=headers) as response:
                html= await response.text(encoding='utf-8')            
                await session.close()
                print('爬取成功')
                return html

#解析爬取得到的html得到链接（这里每个网站重新写）
def parse_html_for_urls(main_htmls):
    urls=[]
    for html in main_htmls:
        soup=BeautifulSoup(html,'lxml')
        part_urls=soup.findAll('div',class_='news_title')
        for part_url in part_urls:
            temp=('https://cs.fudan.edu.cn'+part_url.findAll('a')[0]['href'])
            if('redirect' not in temp):
                urls.append(temp)
    return urls


        
    


def get_url_wanted(loop,headers):
    tasks=[]

    page_nums=get_page_num(headers)#得到页数
    main_url=make_url(page_nums)#生成浏览页面的url
    
    for mainUrl in main_url:
        tasks.append(loop.create_task(craw(mainUrl,headers)))#创建协程任务
    loop.run_until_complete(asyncio.wait(tasks))#执行协程任务
    main_htmls=[]
    for task in tasks:
        main_htmls.append(task.result())#获得任务结果，所有浏览页面的url
    
    urls=parse_html_for_urls(main_htmls)#解析浏览页面的url

    return urls

#对所有讲座url发起请求得到html
def craw_html(urls,loop,headers):
    tasks=[]
    htmls=[]
    for url in urls:
        tasks.append(loop.create_task(craw(url,headers)))
    loop.run_until_complete(asyncio.wait(tasks))
    for task in tasks:
        htmls.append(task.result())
    return htmls



def findAddr(content):
    list=[]
    findlocate=re.findall(r'地点\n(.*?)\n',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
    findlocate=re.findall(r'地点：\n(.*?)\n',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
    return list
    


def findtime(content):
    list=[]
    findtime=re.findall(r'时间\n(.*?)\n',content)
    if(len(findtime)!=0):
        list.append(findtime)
    findtime=re.findall(r'时间：\n(.*?)\n',content)
    if(len(findtime)!=0):
        list.append(findtime)
    return list
    
def findname(content):
    list=[]
    findname=re.findall(r'演讲者\n(.*?)\n',content)
    if(len(findname)!=0):
        list.append(findname)
    findname=re.findall(r'演讲人\n：\n(.*?)\n',content)
    if(len(findname)!=0):
        list.append(findname)
    findname=re.findall(r'报告人\n：\n(.*?)\n',content)
    if(len(findname)!=0):
        list.append(findname)
    return list


#每个网站都要重新写，因为长得都不一样
def parse_html(htmls,check_list,urls):
    list=[]
    print('开始清洗数据')
    for index in range(len(htmls)):
        info_dic={'链接':'','题目':'','通知时间':'','报告人':'','报告时间':'','地点':'','学校':'复旦大学','mark':0}
        soup=BeautifulSoup(htmls[index],'lxml')
        main=soup.findAll('div',class_='entry')[0]
        main_text=main.get_text('\n','<strong>')
        for check in check_list:
            if(fuzz.partial_ratio(check,main_text)>=75):
                info_dic['mark']=1
                break
        info_dic['链接']=urls[index]
        info_dic['题目']=soup.findAll('h1',class_='arti_title')[0].get_text()
        info_dic['报告人']=findname(main_text)
        info_dic['报告时间']=findtime(main_text)
        info_dic['通知时间']=soup.findAll('span',class_='arti_update')[0].get_text()
        info_dic['地点']=findAddr(main_text)
        if(len(info_dic['报告人'])!=0):
            list.append(info_dic)
    return list
            
    
def get_info():
    headers={'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
    check_list=['信息安全','密码学','information safety','crypto','编码','加密','信号','signal','code']#用fuzzwuzzy模糊匹配
    loop=asyncio.get_event_loop()
    urls=get_url_wanted(loop,headers)
    if(len(urls)!=0):
        htmls=craw_html(urls,loop,headers)
        dic=parse_html(htmls,check_list,urls)
        if(len(dic)!=0):
            for i in dic:
                for key,value in i.items():
                    print(key+':'+str(value).replace('[','').replace(']','').replace('\'',''))
                print('------------------------')
            return dic
        else:
            print('没有符合条件的报告')
            return []
    else:
        print('没有符合条件的报告')
        return []


def save2excle(dics):
    book=xlwt.Workbook(encoding='utf-8',style_compression=0)
    sheet=book.add_sheet('复旦大学',cell_overwrite_ok=True)
    col=('链接','题目','通知时间','报告人','报告时间','地点','学校','mark')
    for i in range(0,8):
        sheet.write(0,i,col[i])
    for i in range(len(dics)):
        dic=list(dics[i].items())
        for j in range(0,8):
            string=str(dic[j][1]).replace('[','').replace(']','').replace('\'','')
            sheet.write(i+1,j,string)
    book.save('复旦大学.xls')

def main():
    start=time()
    dic=get_info()
    end=time()
    print('running time is :%s seconds'%(end - start))
    save2excle(dic)

def interface():
    dic=get_info()
    save2excle()
    return dic

if __name__=="__main__":
    main()