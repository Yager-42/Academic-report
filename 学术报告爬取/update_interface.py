from 北大数院 import spider_beida_shuyuan
from 北京大学 import spider_beida_xinxi 
from 复旦大学 import spider_fudan
from 暨南大学 import spider_jida 
from 清华大学 import spider_qinghua 
from 武汉大学 import spider_wuhan
from 信息安全实验室 import spider_lab
import datetime
import re
if __name__=='__main__':
    current_time=datetime.datetime.now()
    fp=open('time.txt','r+')
    string=fp.read()
    if(len(string)!=0):
        year=int(re.findall(r'(\d+)-',string)[0])
        month=int(re.findall(r'-(\d+)-',string)[0])
        day=int(re.findall(r'-(\d+) ',string)[0])
        last_time=datetime.datetime(year,month,day)
        if(current_time-last_time==datetime.timedelta(3)):
            spider_beida_shuyuan.interface()
            spider_beida_xinxi.interface()
            spider_fudan.interface()
            spider_jida.interface()
            spider_lab.interface()
            spider_qinghua.interface()
            spider_wuhan.interface()
            fp.write(str(current_time))
            fp.close()
    else:
        fp.write(str(current_time))
        fp.close()
    print('更新结束')