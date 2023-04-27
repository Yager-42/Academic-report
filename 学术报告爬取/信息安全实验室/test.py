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

if __name__=='__main__':
    fp=open('page.txt','r',encoding='utf-8')
    content=fp.read()
    soup=BeautifulSoup(content,'lxml')
    main=soup.findAll('div',class_='TRS_Editor')[0]
    main_text=main.get_text().replace(u'\xa0','')
    print(findAddr(main_text))
    
