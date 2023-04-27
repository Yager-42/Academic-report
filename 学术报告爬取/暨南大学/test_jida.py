import re
from tabnanny import check
from turtle import title
from bs4 import BeautifulSoup
from  fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
from dateutil.relativedelta import relativedelta

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
    find_title=re.findall(r'题目.：(.*?)时  间',content)
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

if __name__=="__main__":
    fp=open('page.txt','r',encoding='utf-8')
    content=fp.read()
    soup=BeautifulSoup(content,'lxml')
    b_content=soup.get_text()
    b_content=b_content.replace(u'\xa0','')
    print(findtitle(b_content))