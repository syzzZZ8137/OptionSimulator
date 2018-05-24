# -*- coding: utf-8 -*-
"""
Created on Wed May 23 14:42:04 2018

@author: Jax_GuoSen
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import generate_path
import Eu_Option as Eu
import hedge_PnL

def Main_Eu(S,K,T,Dayfreq,max_Dayfreq,sigma,r,q,option_type,Nsamples,Tsteps,multiplier,commis,threshold,num):
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
    S_path = generate_path.S_path_gen(S,ret)
    #plt.plot(S_path[:,:].T,lw = 1.5)
    
    Delta_path = np.zeros((S_path.shape[0],S_path.shape[1]))+100
    Gamma_path = np.zeros((S_path.shape[0],S_path.shape[1]))+100
    dt = T/(S_path.shape[1]-1)
    temp = 0
    for i in range(S_path.shape[0]):
        ttm = T
        for j in range(S_path.shape[1]):
            if hedge_sig[j]:
                S = S_path[i,j]
                Delta_path[i,j] = Eu.cpt_delta(S,K,ttm,r,sigma,q,option_type)
                Gamma_path[i,j] = Eu.cpt_gamma(S,K,ttm,r,sigma,q)
                temp = Delta_path[i,j]
                temp1 = Gamma_path[i,j]
            else:
                Delta_path[i,j] = temp
                Gamma_path[i,j] = temp1
    
            ttm = ttm - dt
            print(i,j)
    
    stat = []
    for i in range(S_path.shape[0]):
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
    
    return stat,Delta_path



if __name__ == '__main__':
    '''Input'''
    S = 1800
    K = 1800
    sigma = 0.18
    r = 0.01
    q = 0
    option_type = 'call'
    price_date = pd.datetime(2018,7,1)        #期权报价日
    maturity_date = pd.datetime(2018,10,1)    #期权到期日
    multiplier = 5  #合约乘数
    commis = 20 #每手手续费
    threshold = 50  #期权头寸与期货头寸相差5手以内，不调仓
    num = 1000 #对应标的总手数
    Dayfreq = 1  #每天对冲几次，最好应被max_Dayfreq整除
    max_Dayfreq = 3 #每天产生的价格点，应大于Dayfreq ,i.e.与Tsteps有关。
    Nsamples = 1000  #模拟样本数
    
    T =  (maturity_date-price_date).days/365
    Tsteps = (maturity_date-price_date).days*max_Dayfreq  #每天离散出max_Dayfreq个点
    
    '''Input'''
    
    '''调用'''
    V_price = Eu.BS_formula(S,K,T,r,sigma,q,option_type)*num*multiplier
    stat,Delta_path = Main_Eu(S,K,T,Dayfreq,max_Dayfreq,sigma,r,q,option_type,Nsamples,Tsteps,multiplier,commis,threshold,num)
    
    stat['成交量(手)'].plot(kind='hist',grid=True,color='blue')
    stat['成交量(手)'].plot(kind='density',grid=True,color='blue')
    stat['PnL'].plot(kind='hist',grid=True,color='red')
    stat['PnL'].plot(kind='density',grid=True,color='red')
    print(stat.describe())
    print('期权费',V_price)
    print('净赚(期权费+对冲盈亏)',V_price+stat['PnL'].mean())


