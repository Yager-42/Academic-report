import re
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

def findAddr(content):
    list=[]
    findlocate=re.findall(r'地点：(.*?)报告',content)
    if(len(findlocate)!=0):
        list.append(findlocate)
    return list

if __name__=='__main__':
    fp=open('page.txt','r',encoding='utf-8')
    content=fp.read()
    soup=BeautifulSoup(content,'lxml')
    main=soup.findAll('div',class_='right_list_sp')[0]
    text=main.get_text().replace(u'\xa0',' ').replace('\n','')
    find=main.findAll('div',class_='sp1')[0].get_text()
    print(findAddr(text))