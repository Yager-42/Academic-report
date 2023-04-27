import asyncio
from concurrent.futures import ProcessPoolExecutor
from distutils.filelist import findall
from gettext import find
import html
from multiprocessing.connection import wait
from signal import signal
from turtle import title
from unittest import result
from urllib import response
import aiohttp
import re
from requests import head, request
import requests
import multiprocessing
import datetime
from dateutil.relativedelta import relativedelta
from  fuzzywuzzy import fuzz
from fuzzywuzzy import process
from bs4 import BeautifulSoup
import xlwt
import time
import random
semophore=asyncio.Semaphore(1)#同步信号量，用来控制并发度，因为清华爬的快会封，所以改成同步爬取


def get_page_num(headers):
    base_url='http://cs.whu.edu.cn/news_list.aspx?category_id=53&page=1'
    response=requests.get(base_url,headers).text
    page_num=int(re.findall(r'<a href="/news_list.aspx\?category_id=53&page=(\d+)">',response)[-2])
    return page_num


#根据页数生成其他网页的的连接
def make_url(page_num):
    urls=[]
    for num in range(1,page_num+1):
        urls.append('http://cs.whu.edu.cn/news_list.aspx?category_id=53&page={}'.format(num))
    return urls

#上面三个函数拿到所有浏览页面的url

#异步io爬虫
def craw(url,headers):
    time.sleep(random.random())
    response=requests.get(url,headers).text
    print(time.strftime('%X'))
    return response

#解析爬取得到的html得到链接（这里每个网站重新写）
def parse_html_for_urls(main_htmls):
    urls=[]
    for html in main_htmls:
        soup=BeautifulSoup(html,'lxml')
        main=soup.findAll('div',class_='right_list')[0]
        lis=main.findAll('li')
        for li in lis:
            urls.append('http://cs.whu.edu.cn'+li.findAll('p',class_='p1')[0].findAll('a')[1]['href'])
    return urls


        
    


def get_url_wanted(headers):

    page_nums=get_page_num(headers)#得到页数
    main_url=make_url(page_nums)#生成浏览页面的url
    
    
    main_htmls=[]
    for url in main_url:
        main_htmls.append(craw(url,headers))
    
    urls=parse_html_for_urls(main_htmls)#解析浏览页面的url

    return urls

#对所有讲座url发起请求得到html
def craw_html(urls,headers):
    htmls=[]
    for url in urls:
        htmls.append(craw(url,headers))
    return htmls


def find_title(content):
    list=[]
    findtitle=re.findall(r'学术报告：(.*?)报告',content)
    if(len(findtitle)!=0):
        list.append(findtitle)
        return list
    findtitle=re.findall(r'报告题目.*?：(.*?)报告',content)
    if(len(findtitle)!=0):
        list.append(findtitle)
        return list
    findtitle=re.findall(r'题目.*?：(.*?)时间：',content)
    if(len(findtitle)!=0):
        list.append(findtitle)
        return list
    findtitle=re.findall(r'题目.*?：(.*?)报告人简介：',content)
    if(len(findtitle)!=0):
        list.append(findtitle)
        return list


def findAddr(content):
    list=[]
    findlocate=re.findall(r'地点：(.*?)报告',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
    return list
    


def findtime(content):
    list=[]
    findtime=re.findall(r'时间：(.*?)地点',content)
    if(len(findtime)!=0):
        list.append(findtime)
        return list
    findtime=re.findall(r'时间：(.*?)报告',content)
    if(len(findtime)!=0):
        list.append(findtime)
    return list
    
def findname(content):
    list=[]
    findname=re.findall(r'报告人：(.*?)报告人国籍',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人：(.*?)报告人单位',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人：(.*?)报告题目',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人：(.*?)报告人简介',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人：(.*?)时间',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    findname=re.findall(r'报告人简介：(.*?)，',content)
    if(len(findname)!=0):
        list.append(findname)
        return list
    return list


#每个网站都要重新写，因为长得都不一样
def parse_html(htmls,check_list,urls):
    list=[]
    print('开始清洗数据')
    for index in range(len(htmls)):
        info_dic={'链接':'','题目':'','通知时间':'','报告人':'','报告时间':'','地点':'','学校':'武汉大学','mark':0}
        soup=BeautifulSoup(htmls[index],'lxml')
        main=soup.findAll('div',class_='right_list_sp')[0]
        main_text=main.get_text().replace(u'\xa0','').replace('\n','')
        if(fuzz.partial_ratio('学术报告',main_text)!=100):
            continue
        for check in check_list:
            if(fuzz.partial_ratio(check,main_text)>=75):
                info_dic['mark']=1
                break
        info_dic['通知时间']=main.findAll('div',class_='info')[0].findAll('span')[0].get_text()
        info_dic['链接']=urls[index]
        info_dic['题目']=find_title(main_text)
        info_dic['报告人']=findname(main_text)
        info_dic['报告时间']=findtime(main_text)
        info_dic['地点']=findAddr(main_text)
        list.append(info_dic)
    return list
            
    
def get_info():
    headers={'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
    check_list=['信息安全','密码学','information safety','crypto','编码','加密','信号','signal','code']#用fuzzwuzzy模糊匹配
    urls=get_url_wanted(headers)
    if(len(urls)!=0):
        htmls=craw_html(urls,headers)
        dic=parse_html(htmls,check_list,urls)
        if(len(dic)!=0):
            for i in dic:
                for key,value in i.items():
                    print(key+':'+str(value).replace('[','').replace(']','').replace('\'','').replace('\r','').replace('\t',''))
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
    sheet=book.add_sheet('武汉大学',cell_overwrite_ok=True)
    col=('链接','题目','通知时间','报告人','报告时间','地点','学校','mark')
    for i in range(0,8):
        sheet.write(0,i,col[i])
    for i in range(len(dics)):
        dic=list(dics[i].items())
        for j in range(0,8):
            string=str(dic[j][1]).replace('[','').replace(']','').replace('\'','').replace('\r','').replace('\t','')
            sheet.write(i+1,j,string)
    book.save('武汉大学.xls')


def interface():
    dic=get_info()
    return dic


def main():
    dic=get_info()
    save2excle(dic)

if __name__=="__main__":
    main()