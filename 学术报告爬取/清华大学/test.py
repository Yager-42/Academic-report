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

def findname(content):
    list=[]
    findlocate=re.findall(r'地点：\n(.*)',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
    return list

if __name__=='__main__':
    fp=open('page.txt','r',encoding='utf-8')
    content=fp.read()
    soup=BeautifulSoup(content,'lxml')
    main=soup.findAll('div',class_='subAcademicDetail')[0]
    main_text=main.get_text('\n','<strong>')
    print(len(main_text))
    print(findname(main_text))