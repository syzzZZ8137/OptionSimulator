# -*- coding: utf-8 -*-
"""
Created on Wed May 23 17:04:59 2018

@author: Jax_GuoSen
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import generate_path
import Asian_Option as Asian
import hedge_PnL

def Main_Asian(price_date,maturity_date,\
                start_fixed_date,end_fixed_date,\
                S0,SA,K,T,Dayfreq,max_Dayfreq,\
                sigma,r,q,option_type,Nsamples,\
                Tsteps,multiplier,commis,\
                threshold,num):
    hedge_sig = []
    freq = int(max_Dayfreq/Dayfreq)
    for i in range(Tsteps):
        if np.mod(i,freq)==0:
            hedge_sig.append(True)
        else :
            hedge_sig.append(False)
        
    #分割Tsteps,要计算delta的点位，记为1，否则记为0。
    
    random = generate_path.random_gen(Nsamples,Tsteps)
    ret = generate_path.Ret_path_gen(r,sigma,q,T,random)
    S_path = generate_path.S_path_gen(S0,ret)
    
    Delta_path = np.zeros((random.shape[0],random.shape[1]))+100
    Gamma_path = np.zeros((random.shape[0],random.shape[1]))+100
    dt = T/(random.shape[1]-1)
    temp = 0
    
    for i in range(random.shape[0]):
        S = S0  #将S更新回初始
        price_date_new = price_date
        SA_lst = []  #存放均值序列
        Ta = T
        for j in range(random.shape[1]-1):
                
            if np.mod(j+1,max_Dayfreq) == 0:
                #判断是否经过1天
                price_date_new = price_date_new+pd.Timedelta('1 days')
                #print(price_date_new)
            Ta,Tb,Tc,sit = Asian.time_split(price_date_new,start_fixed_date,end_fixed_date,maturity_date)
            if sit == 2:
                #表示位于采价期间
                SA_lst.append(S_path[i,j])
                
            if hedge_sig[j]:
                #识别到对冲信号，则更新S矩阵
                #更新收益率序列
                #这里的S_path1 不同于 上面的 S_path,这里用于MC求Greeks
                random1 =generate_path.random_gen(2000,random.shape[1]-j)
                ret1 = generate_path.Ret_path_gen(r,sigma,q,Ta,np.matrix(random1))
                
                S_path1 = generate_path.S_path_gen(S,ret1)
                S_path1_sup = generate_path.S_path_gen(S+ds,ret1)
                S_path1_sdn = generate_path.S_path_gen(S-ds,ret1)
                
                if sit == 2:
                    SA = np.mean(SA_lst)
                    
                Delta_path[i,j],Gamma_path[i,j],V = Asian.DG_MC_single(S_path1,S_path1_sup,S_path1_sdn,ds,K,Ta,Tb,Tc,sit,r,SA,option_type,S_path1.shape[0],S_path1.shape[1])
                #print(Delta_path[i,j])
                temp = Delta_path[i,j]
                temp1 = Gamma_path[i,j]
            else:
                Delta_path[i,j] = temp
                Gamma_path[i,j] = temp1
                Ta = Ta - dt
            S = S_path[i,j+1] #更新下一个S
            
                    
            print(i,j)
    
    
    stat = []
    for i in range(random.shape[0]):
        data = pd.DataFrame(S_path[i,:],columns=['交易价'])
        data['结算价'] = data['交易价']
        data['期权头寸'] = pd.DataFrame(Delta_path[i,:])
        data['期权头寸'].fillna(0,inplace=True)
        data.loc[len(data)-1,'期权头寸'] = 0  #最后平仓
        data['期权头寸'] = data['期权头寸']*num
        data['期权头寸'] = data['期权头寸'].apply(lambda x:int(x))
        data,PnL = hedge_PnL.hedge_PNL_usage(data,multiplier,commis,threshold)
        stat.append([data.loc[len(data)-1,'成交量(手)'],PnL])
        print(i)
        
    stat = pd.DataFrame(stat,columns=['成交量(手)','PnL'])
    
    return stat,S_path,Delta_path,data



if __name__ == '__main__':
    '''Input'''
    S0 = 1800
    K = 1800
    sigma = 0.18
    r = 0.01
    q = 0
    SA = 1800
    ds = 0.0001*S0
    
    option_type = 'discrete-ari-put-fixed'
    price_date = pd.datetime(2018,6,15)        #期权报价日
    maturity_date = pd.datetime(2018,10,31)    #期权到期日
    start_fixed_date = pd.datetime(2018,10,1)  #开始计算平均值的日期
    end_fixed_date = pd.datetime(2018,10,31)   #结束累计平均值的日期
    
    multiplier = 10  #合约乘数
    commis = 20 #每手手续费
    threshold = 0  #期权头寸与期货头寸相差5手以内，不调仓
    num = 2000 #对应标的总手数
    Dayfreq = 1  #每天对冲几次，最好应被max_Dayfreq整除
    max_Dayfreq = 1 #每天产生的价格点，应大于Dayfreq ,i.e.与Tsteps有关。
    Nsamples = 500  #模拟样本数
    
    T =  (maturity_date-price_date).days/365
    Tsteps = (maturity_date-price_date).days*max_Dayfreq  #每天离散出max_Dayfreq个点
    
    '''Input'''
    
    
    '''调用'''
    
    if price_date <= start_fixed_date:
        stat,S_path,Delta_path,a = Main_Asian(price_date,maturity_date,\
                                            start_fixed_date,end_fixed_date,\
                                            S0,SA,K,T,Dayfreq,max_Dayfreq,\
                                            sigma,r,q,option_type,Nsamples,\
                                            Tsteps,multiplier,commis,\
                                            threshold,num)
        
        stat['成交量(手)'].plot(kind='hist',grid=True,color='blue')
        stat['成交量(手)'].plot(kind='density',grid=True,color='blue')
        stat['PnL'].plot(kind='hist',grid=True,color='red')
        stat['PnL'].plot(kind='density',grid=True,color='red')
        plt.plot(S_path.T)
        print(stat.describe())
    else:
        print('请确认定价日位于起均日之前')
    


