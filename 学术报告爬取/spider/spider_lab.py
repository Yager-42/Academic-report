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

semophore=asyncio.Semaphore(100)

#通过最普通方法对第一个页面发起请求得到该网站的总页数
def get_page_num(url,headers):
    response=requests.get(url=url,headers=headers)
    html=response.content
    html_=html.decode('utf-8')
    page_num=re.findall(r'共(\d+)页',html_)[0]
    page_num=int(page_num)
    return page_num

#根据页数生成其他网页的的连接
def make_url(page_num):
    page_num_int=int(page_num)
    urls=[]
    urls.append('http://sklois.iie.cas.cn/tzgg/tzgg_16520/index.html')
    for num in range(1,page_num_int):
        urls.append('http://sklois.iie.cas.cn/tzgg/tzgg_16520/index_{}.html'.format(num))
    return urls

#异步io爬虫
async def craw(url,headers):
    async with semophore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url,headers=headers) as response:
                html= await response.text()            
                await session.close()
                return html

#解析爬取得到的html得到链接（这里每个网站重新写）
def parse_html_for_urls(main_htmls):
    urls_and_times=[]
    for html in main_htmls:
        soup=BeautifulSoup(html,'lxml')
        urls=soup.findAll('a',class_='hh14')
        times=soup.findAll('td',class_='time')
        for index in range(len(urls)):
            urls_and_times.append(times[index].text)
            urls_and_times.append(urls[index]['href'].replace('./',''))
    return urls_and_times


        
    


def get_url_wanted(baseurl,loop,headers):
    tasks=[]

    page_num=get_page_num(baseurl,headers)#获取页数
    main_url=make_url(page_num)#生成浏览页面的url
    
    for mainUrl in main_url:
        tasks.append(loop.create_task(craw(mainUrl,headers)))
    loop.run_until_complete(asyncio.wait(tasks))
    main_htmls=[]
    for task in tasks:
        main_htmls.append(task.result())#爬取浏览页面的url
    
    urls_and_times=parse_html_for_urls(main_htmls)#解析会议的url

    for index in range(len(urls_and_times)):
        if(index%2==1):
            urls_and_times[index]='http://sklois.iie.cas.cn/tzgg/tzgg_16520/'+urls_and_times[index]#生成会议的url
    return urls_and_times

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
    findlocate=re.findall(r'地 *点[:|：] *(.*?)\n',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'Address:(.*?)\n',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地点[:|：](.*)',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    return list
    


def findtime(content):
    list=[]
    findtime=re.findall(r'时 *间：(\d+[年|.]\d+[月|.]\d+日*)',content)
    if(len(findtime)!=0):
        list.append(findtime)
    findtime=re.findall(r'Time:(\d+[年|.]\d+[月|.]\d+日*)',content)
    if(len(findtime)!=0):
        list.append(findtime)
    return list
    
def findname(content):
    list=[]
    findname=re.findall(r'报告人：(.*?)\n',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'个人简介：\n(.*?)，',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'Speaker:(.*?)\n',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人简介：(.*?)is',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人中文简介：(.*?)2000',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人: (.*?)\n',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    return list


#每个网站都要重新写，因为长得都不一样
def parse_html(htmls,check_list,urls_and_times):
    list_=[]
    for index in range(len(htmls)):
        info_dic={'链接':'','题目':'','通知时间':'','报告人':'','报告时间':'','地点':'','学校':'信息安全实验室','mark':0}
        soup=BeautifulSoup(htmls[index],'lxml')
        title=soup.findAll('td',class_='lan_15')[0].get_text()
        if(fuzz.partial_ratio('报告讲座',title)<30):
            continue
        main=soup.findAll('div',class_='TRS_Editor')[0]
        main_text=main.get_text().replace(u'\xa0','')
        for check in check_list:
            if(fuzz.partial_ratio(check,main_text)>=67):
                info_dic['mark']=1
                break
        info_dic['链接']=urls_and_times[index*2+1]
        info_dic['通知时间']=urls_and_times[index*2]                
        info_dic['题目']=title
        info_dic['地点']=findAddr(main_text)
        info_dic['报告人']=findname(main_text)
        info_dic['报告时间']=findtime(main_text)
        list_.append(info_dic)
    return list_
            
    
def get_info():
    baseurl='http://sklois.iie.cas.cn/tzgg/tzgg_16520/index.html'
    headers={'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
    check_list=['信息安全','密码学','information safety','crypto','编码','加密','signal','网络安全','解码','security']#用fuzzwuzzy模糊匹配
    loop=asyncio.get_event_loop()
    urls_and_times=get_url_wanted(baseurl,loop,headers)
    urls=[]
    for index in range(len(urls_and_times)):
        if(index%2==1):
            urls.append(urls_and_times[index])
    if(len(urls)!=0):
        htmls=craw_html(urls,loop,headers)
        dic=parse_html(htmls,check_list,urls_and_times)
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
    sheet=book.add_sheet('信息安全实验室',cell_overwrite_ok=True)
    col=('链接','题目','通知时间','报告人','报告时间','地点','学校','mark')
    for i in range(0,8):
        sheet.write(0,i,col[i])
    for i in range(len(dics)):
        dic=list(dics[i].items())
        for j in range(0,8):
            string=str(dic[j][1]).replace('[','').replace(']','').replace('\'','')
            sheet.write(i+1,j,string)
    book.save('信息安全实验室.xls')


def interface():
    dic=get_info()
    save2excle()
    return dic

def main():
    start=time()
    dics=get_info()
    end=time()
    print('running time is :%s seconds'%(end - start))
    save2excle(dics)

if __name__=="__main__":
    main()