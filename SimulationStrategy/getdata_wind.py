# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 12:29:15 2018

@author: Jax_GuoSen
"""

from WindPy import w
import pandas as pd
from datetime import datetime
import os
w.start()

#日数据
root = os.getcwd()
data = w.wsd("I1901.DCE", "close", "2018-08-09", "2018-09-06", "Period=D")  #日度以上数据
data = pd.DataFrame(data.Data,columns=data.Times,index=data.Fields).T

data.reset_index(inplace=True)
data.columns = ['time','undly']
data['time'] = data['time'].apply(lambda x:datetime(x.year,x.month,x.day,0,0,1))
data.to_csv(root+'\\data_Hist\\Input\\test.csv',sep=';',index=False)

'''
data = w.wsi("I1901.DCE", "close", "2018-09-07 09:00:00", "2018-09-07 12:27:29", "BarSize=60")  #分钟数据
data = pd.DataFrame(data.Data,columns=data.Times,index=data.Fields).T
data.to_csv(root+'\\data_Hist\\Input\\test.csv',sep=';')
'''
data = pd.read_csv(root+'\\data_Hist\\Input\\test.csv',sep=';')
