import asyncio
from asyncore import read
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
from dateutil.relativedelta import relativedelta
from  fuzzywuzzy import fuzz
from fuzzywuzzy import process
from bs4 import BeautifulSoup
import easyocr
import xlwt
from time import time

semophore=asyncio.Semaphore(100)

#通过最普通方法对第一个页面发起请求得到该网站的总页数
def get_page_num(url,headers):
    response=requests.get(url=url,headers=headers)
    html=response.text
    soup=BeautifulSoup(html,'lxml')
    page_num_area=soup.findAll('span',class_='p_no')[0]
    a=str(page_num_area.findAll('a')[0]['href'])
    page_num=int(re.findall(r'jzxx/(\d+).htm',a)[0])
    page_num+=1
    return page_num

#根据页数生成其他网页的的连接
def make_url(page_num):
    page_num_int=int(page_num)
    urls=[]
    urls.append('https://eecs.pku.edu.cn/index/jzxx.htm')
    for num in range(2,3+1):
        urls.append('http://eecs.pku.edu.cn/index/jzxx/{}.htm'.format(page_num-num+1))
    return urls

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
        main=soup.findAll('ul',class_='list-text')[0]
        lis=main.findAll('li')
        for li in lis:
            url=str(li.findAll('a')[0]['href'])
            url=url.replace('../','',2)
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
        urls[index]='http://eecs.pku.edu.cn/'+urls[index]#生成会议的url
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
    findlocate=re.findall(r'地点.*?:?(.*?)芏办单位',content)
    if(len(findlocate)!=0):
        for string in findlocate:
            if('时间' not in string):
                list.append(findlocate)
                return list
    findlocate=re.findall(r'地点.*?:?(.*?)时间',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地点.*?:?(.*?)邀请人',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地点.*?:?(.*?)联系人',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地点.*?：?(.*?)主办',content)
    if(len(findlocate)!=0):
        for string in findlocate:
            if('时间' not in string):
                list.append(findlocate)
                return list
    findlocate=re.findall(r'地点.*?:?(.*?)时间',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地点.*?:?(.*?)主讲人',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地点.*?:?(.*?)Speaker',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地点.*?:?(.*?)Abstract',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地点.*?：?(.*?)主讲人简介',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'Location:(.*?)Topic',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'，(.*?)报告摘要',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地点：(.*?)摘要',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r' (.*?)题目',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地点：(.*?)主办单位',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    findlocate=re.findall(r'地点：(.*?)报告人',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
        return list
    return list
    


def findtime(content):
    list=[]
    findtime=re.findall(r'时间：? ?(\d+年??\d+月\d+日)',content)
    if(len(findtime)!=0):
        list.append(findtime)
        return list
    findtime=re.findall(r'时间：? ?(\d+年??\d+月\d+8)',content)
    if(len(findtime)!=0):
        list.append(findtime)
        return list
    findtime=re.findall(r'时闻：? ?(\d+年??\d+月\d+日)',content)
    if(len(findtime)!=0):
        list.append(findtime)
        return list
    findtime=re.findall(r'时闻：? ?(\d+年??\d+月\d+8)',content)
    if(len(findtime)!=0):
        list.append(findtime)
        return list
    findtime=re.findall(r'(\d+年??\d+月\d+日)',content)
    if(len(findtime)!=0):
        list.append(findtime)
        return list
    findtime=re.findall(r'Time:(.*?)Topic',content)
    if(len(findtime)!=0):
        list.append(findtime)
        return list
    return list
    
def findname(content):
    list=[]
    findname=re.findall(r'报告人:?(.*?)报告摘要',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人：?(.*?)时间',content)
    if(len(findname)!=0):
        for string in findname:
            if('地点' not in string):
                list.append(findname)
                return list
    findname=re.findall(r'报告人：?(.*?)地点',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人：?(.*?)题目',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'主讲人：?(.*?)时间',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'主讲人：?(.*?)Title',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'嘉宾：?(.*?)演讲题目',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'嘉宾：?(.*?)时间',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'演讲人：?(.*?)时间',content)
    if(len(findname)!=0):
        for string in findname:
            if('地点' not in string):
                list.append(findname)
                return list
    findname=re.findall(r'报告人简介：(.*?)博士',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人简介：(.*?)教授',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人简介：(.*?)研究员',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人简介:?(.*?)。',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人简介:?(.*?),',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人简介:?(.*?)is',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'Speaker:?(.*?)Abstract:',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'Biography:?(.*?)is',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'Bios?:? ?(.*?)is',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'主讲人介绍:?(.*?)，',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'教授简介：?(.*?),',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'嘉宾：?(.*?)时间',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    return list



def find(html,check_list,url):
    info_dic={'链接':'','题目':'','通知时间':'','报告人':'','报告时间':'','地点':'','学校':'北京大学','mark':0}
    soup=BeautifulSoup(html,'lxml')
    main=soup.findAll('div',class_='article-text')[0]
    main_text=main.get_text().replace('\n','')
    if(len(main_text)==0):
        #这是只有图片的网页
        print('图片解析信息')
        title=soup.findAll('div',class_='tit')[1].get_text()
        if('学术论坛' in title):
            return info_dic
        reader=easyocr.Reader(['ch_sim', 'en'])
        img_url='https://eecs.pku.edu.cn'+main.findAll('img')[0].get('src')
        IMG=requests.get(img_url).content
        result=reader.readtext(IMG,detail=0)
        text=''
        for p in result:
            text+=p
        for check in check_list:
            if(fuzz.partial_ratio(check,text)>=90):
                info_dic['mark']=1
                break
        info_dic['题目']=title
        info_dic['链接']=url
        info_dic['通知时间']=soup.findAll('div',class_='info')[0].findAll('span')[0].get_text()
        info_dic['报告时间']=findtime(text)
        info_dic['报告人']=findname(text)
        info_dic['地点']=findAddr(text)
        return info_dic
    else:
        print('文字解析信息')
        for check in check_list:
            if(fuzz.partial_ratio(check,main_text)>=70):
                info_dic['mark']=1
                break
        title=soup.findAll('div',class_='tit')[1].get_text()
        for i in ['通知','预告','活动']:
            if(fuzz.partial_ratio(i,title)==100):
                return info_dic
        info_dic['题目']=title
        info_dic['链接']=url
        info_dic['通知时间']=soup.findAll('div',class_='info')[0].findAll('span')[0].get_text()
        info_dic['报告时间']=findtime(main_text)
        info_dic['报告人']=findname(main_text)
        info_dic['地点']=findAddr(main_text)
        return info_dic


#每个网站都要重新写，因为长得都不一样
def parse_html(htmls,check_list,urls):
    print('开始解析信息')
    list=[]
    pool=multiprocessing.Pool(4)
    results=[]
    for index in range(len(htmls)):
        future=pool.apply_async(find,(htmls[index],check_list,urls[index],))
        results.append(future)
    pool.close()
    pool.join()
    for future in results:
        if(future.successful() and future.get()['链接']!=''):
            list.append(future.get())
    return list

            

def get_info():
    baseurl='https://eecs.pku.edu.cn/index/jzxx.htm'
    headers={'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
    check_list=['信息安全','密码学','information safety','crypto','编码','加密','信号','signal','data safety','security','encode','decode','safety']#用fuzzwuzzy模糊匹配
    loop=asyncio.get_event_loop()
    urls=get_url_wanted(baseurl,loop,headers)
    if(len(urls)!=0):
        htmls=craw_html(urls,loop,headers)
        dic=parse_html(htmls,check_list,urls)
        if(len(dic)!=0):
            for i in dic:
                for key,value in i.items():
                    print(key+':'+str(value).replace('[','').replace(']','').replace('\'','').replace('\n',''))
                print('------------------------')
            return dic
        else:
            print('没有符合条件的报告')
            return[]
    else:
        print('没有符合条件的报告')
        return []


def save2excle(dics):
    book=xlwt.Workbook(encoding='utf-8',style_compression=0)
    sheet=book.add_sheet('北京大学',cell_overwrite_ok=True)
    col=('链接','题目','通知时间','报告人','报告时间','地点','学校','mark')
    for i in range(0,8):
        sheet.write(0,i,col[i])
    for i in range(len(dics)):
        dic=list(dics[i].items())
        for j in range(0,8):
            string=str(dic[j][1]).replace('[','').replace(']','').replace('\'','').replace('\n','')
            sheet.write(i+1,j,string)
    book.save('北京大学信息学院.xls')


def interface():
    dic=get_info()
    save2excle(dic)
    return dic



def main():
    start=time()
    dic=get_info()
    end=time()
    print('running time is :%s seconds'%(end - start))
    save2excle(dic)

if __name__=="__main__":
    main()