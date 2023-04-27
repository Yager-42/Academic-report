from asyncore import write
import re
from tabnanny import check
from turtle import title
from bs4 import BeautifulSoup
from  fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
from dateutil.relativedelta import relativedelta
import easyocr
from requests import request
import requests

def findAddr(content):
    list=[]
    findlocate=re.findall(r'地点.*?:?(.*?)芏办单位',content)
    if(len(findlocate)!=0):
        for string in findlocate:
            if('时闻' not in string):
                list.append(findlocate)
                return list
    findlocate=re.findall(r'地点.*?:?(.*?)时闻',content)
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

if __name__=='__main__':
    fp=open('page.txt','r',encoding='utf-8')
    content=fp.read()
    reader=easyocr.Reader(['ch_sim', 'en'])
    find=reader.readtext('catch.jpg',detail=0)
    string=''
    for i in find:
        string+=i
    print(findAddr(string)[0][0].split('。'))
    
    '''
    soup=BeautifulSoup(content,'lxml')
    main=soup.findAll('div',class_='article-text')[0]
    main_text=main.get_text().replace('\n','')
    print(findAddr(main_text))'''
    
