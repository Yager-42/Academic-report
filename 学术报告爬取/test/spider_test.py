import asyncio
from concurrent.futures import ProcessPoolExecutor
from distutils.filelist import findall
from multiprocessing.connection import wait
from unittest import result
import aiohttp
import re
from requests import request
import requests
import time
import multiprocessing

page_num=0#得到的总页数
urls=[]#浏览的页面地址
tasks=[]#用于异步io申请浏览页面的列表
htmls=[]#得到的浏览页面的html
links=[]#从浏览页面得到的具体讲座页面的地址

find_page_num=re.compile(r'<em class="all_pages">(.*?)</em>')#查找该网页最多页数
find_detail_url=re.compile('<span class="news_title"><a href=\'(/sse/.*?)\' .*?</a></span>')


semaphore = asyncio.Semaphore(50)

#异步io实现爬虫
async def get_page(baseurl,headers):
    async with semaphore:
        global htmls
        async with aiohttp.ClientSession() as session:
            async with session.get(url=baseurl,headers=headers) as response:
                main_html= await response.text()
                htmls.append(main_html)
                await session.close()


#普通爬虫实现对第一个浏览页面的抓取并得到总页数
def get_main_page(baseurl,headers):
    global page_num,htmls
    response=requests.get(url=baseurl,headers=headers)
    html=response.text
    page_num=re.findall(find_page_num,html)[0]


#生成其他浏览页面的url
def make_main_url():
    global page_num
    num=int(page_num)
    for i in range(2,num+1):
        urls.append('http://www2.scut.edu.cn/sse/xshd/list{}.htm'.format(i))

#异步调用get_page得到浏览页面的html
def get_page_in_loop(headers,loop):
    global urls
    for url in urls:
        tasks.append(loop.create_task(get_page(url,headers)))
    loop.run_until_complete(asyncio.wait(tasks))

#异步调用get_page得到详细页面html
def get_detail_page_in_loop(headers,loop):
    global urls,tasks
    tasks=[]
    for link in urls:
        for url in link:
            tasks.append(loop.create_task(get_page(url,headers)))
    loop.run_until_complete(asyncio.wait(tasks))

#在浏览页面的html中寻找具体页面的地址
def findDetailUrl(html):
    link=re.findall(find_detail_url,html)
    return link


#用多线程实现对多个浏览页面的具体页面地址进行findDetailUrl
def parse_detail_url(pool):
    global htmls,links
    links=pool.map(findDetailUrl,htmls)

#生成真正的url
def multi_make_detail_url(pool):
    global links,urls
    urls=[]
    urls=pool.map(make_detail_url,links)
    
#连接生成url
def make_detail_url(link):
    urls=[]
    for part_of_url in link:
        urls.append('http://www2.scut.edu.cn'+part_of_url)
    return urls
    


    



def main():
    global htmls
    baseurl='http://www2.scut.edu.cn/sse/xshd/list.htm'
    headers={'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
    pool=ProcessPoolExecutor()
    loop=asyncio.get_event_loop()

    get_main_page(baseurl,headers)
    make_main_url()
    get_page_in_loop(headers,loop)
    parse_detail_url(pool)
    multi_make_detail_url(pool)
    htmls=[]
    get_detail_page_in_loop(headers,loop)
    loop.close()

    


if __name__=="__main__":
    start=time.time()
    main()
    end=time.time()
    print(end-start)



