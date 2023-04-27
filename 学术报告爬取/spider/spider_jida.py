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

semophore=asyncio.Semaphore(100)

#通过最普通方法对第一个页面发起请求得到该网站的总页数
def get_page_num(url,headers):
    response=requests.get(url=url,headers=headers)
    html=response.text
    page_num=re.findall(r'<em class="all_pages">(.*?)</em>',html)[0]
    return page_num

#根据页数生成其他网页的的连接
def make_url(page_num):
    page_num_int=int(page_num)
    urls=[]
    for num in range(1,page_num_int+1):
        urls.append('http://xxxy.jnu.edu.cn/27469/list{}.htm'.format(num))
    return urls

#异步io爬虫
async def craw(url,headers):
    async with semophore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url,headers=headers) as response:
                html= await response.text()            
                await session.close()
                print('爬取成功')
                return html

#解析爬取得到的html得到链接（这里每个网站重新写）
def parse_html_for_urls(main_htmls):
    print('正在解析讲座信息网页url')
    urls=[]
    for html in main_htmls:
        soup=BeautifulSoup(html,'lxml')
        main=soup.findAll('div','list-rightbox')[0]
        first_meeting=main.findAll('div','list-title')[0]
        url=str(first_meeting.findAll('a')[0]['href'])
        if(len(re.findall(r'upload',url))==0):
            urls.append(url)
        lis_area=main.findAll('ul',class_='list-ul')[0]
        lis=lis_area.findAll('li')
        for li in lis:
            url=str(li.findAll('a')[0]['href'])
            if(len(re.findall(r'upload',url))==0):
                urls.append(url)
    return urls


        
    


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
    
    urls=parse_html_for_urls(main_htmls)#解析会议的url

    for index in range(len(urls)):
        urls[index]='http://xxxy.jnu.edu.cn'+urls[index]#生成会议的url
    return urls

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
    findlocate=re.findall(r'地.*?点.?：(.*?)主持人',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地.*?点.?：(.*?)热烈欢迎',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地.*?点.?：(.*?) ',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    return list
    


def findtime(content):
    list=[]
    findtime=re.findall(r'时.*?间.?：(\d+年\d+月\d+日)',content)
    if(len(findtime)!=0):
        list.append(findtime)
    return list
    
def findname(content):
    list=[]
    findname=re.findall(r'报告人：(.*?)报告人简介',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人：(.*?)内容简介',content)
    if(len(findname)!=0):
        for i in findname:
            if(len(re.findall(r'时 *间',i))!=0):
                findname=re.findall(r'报告人：(.*?)时 *间',content)
                list.append(findname)
                return list
        list.append(findname)
        return list
    findname=re.findall(r'报告人：(.*?)时 间',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    return list


def findtitle(content):
    list=[]
    find_title=re.findall(r'题目.：(.*?)内容简介',content)
    if(len(find_title)!=0):
        list.append(find_title)
        return list
    find_title=re.findall(r'题目.：(.*?)报告人',content)
    if(len(find_title)!=0):
        list.append(find_title)
        return list
    find_title=re.findall(r'题  目：(.*?)内容简介',content)
    if(len(find_title)!=0):
        list.append(find_title)
        return list
    find_title=re.findall(r'题 目：(.*?)内容简介',content)
    if(len(find_title)!=0):
        list.append(find_title)
        return list
    find_title=re.findall(r'题 目：(.*?)报告人',content)
    if(len(find_title)!=0):
        list.append(find_title)
        return list

def beautify_content(content):
    b_content=content.get_text()
    b_content=b_content.replace(u'\xa0','')
    return b_content

#每个网站都要重新写，因为长得都不一样
def parse_html(htmls,check_list,urls):
    print('正在解析网页信息')
    list=[]
    for index in range(len(htmls)):
        info_dic={'链接':'','题目':'','通知时间':'','报告人':'','报告时间':'','地点':'','学校':'暨南大学','mark':0}
        soup=BeautifulSoup(htmls[index],'lxml')
        title=soup.findAll('h4',class_='article-title')[0].get_text()
        if(fuzz.partial_ratio('学术讲座',title)<80):
            continue
        main=soup.findAll('div',class_='wp_articlecontent')[0]
        b_content=beautify_content(main)
        for check in check_list:
            if(fuzz.partial_ratio(check,b_content)>=70):
                info_dic['mark']=1
                break
        info_dic['题目']=title
        info_dic['通知时间']=soup.findAll('p',class_='article-small')[0].findAll('span')[0].get_text()
        info_dic['报告人']=findname(b_content)
        info_dic['报告时间']=findtime(b_content)
        info_dic['地点']=findAddr(b_content)
        info_dic['链接']=urls[index]
        list.append(info_dic)
    return list
            
    
def get_info():
    baseurl='http://xxxy.jnu.edu.cn/27469/list1.htm'
    headers={'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
    check_list=['信息安全','密码学','information safety','cryptography','编码','加密','信号','signal']#用fuzzwuzzy模糊匹配
    loop=asyncio.get_event_loop()
    urls=get_url_wanted(baseurl,loop,headers)
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
    sheet=book.add_sheet('清华大学',cell_overwrite_ok=True)
    col=('链接','题目','通知时间','报告人','报告时间','地点','学校','mark')
    for i in range(0,8):
        sheet.write(0,i,col[i])
    for i in range(len(dics)):
        dic=list(dics[i].items())
        for j in range(0,8):
            string=str(dic[j][1]).replace('[','').replace(']','').replace('\'','')
            sheet.write(i+1,j,string)
    book.save('暨南大学.xls')


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