# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 10:49:27 2018

@author: Harrison
"""
import os 
import pandas as pd
def outputstat(csvdocument):
    pathroot=os.getcwd()
    Commission=10
    data1 = pd.read_csv(pathroot+'\\HedgeData\\'+csvdocument+'.csv')
    data1['tradeposition']=data1['holdposition'].diff()
    data1['tradeposition'][0]=data1['holdposition'][0]
    totalpnl=-sum(data1['tradeposition']*data1['CLOSE']*data1['multiplier'])
    data1['volume']=data1['tradeposition'].apply(lambda x:abs(x))
    totalvolume=sum(data1['volume'])
    TotalCommission=-totalvolume*Commission
    PNLwithCommission=TotalCommission+totalpnl
    maxholdposition=max(data1['holdposition']) if max(data1['holdposition'])>abs(min(data1['holdposition'])) else min(data1['holdposition'])
    maxholdpositiontime=data1[data1['holdposition']==maxholdposition]['time'][1]
    outcsv=pd.DataFrame([totalpnl,totalvolume,maxholdposition,maxholdpositiontime,data1['multiplier'][0],Commission,TotalCommission,PNLwithCommission],index=['totalpnl','totalvolume','maxholdposition','maxholdpositiontime','multiplier','CommissionPerShare','TotalCommission','PNLwithCommission']).T
    ExlPath=pathroot+"\\StatData"
    out = ExlPath+'\\'+csvdocument+'.csv'
    outcsv.to_csv(out,index=False,header=True)
if __name__ == '__main__':
    outputstat('position')