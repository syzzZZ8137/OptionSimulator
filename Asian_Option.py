# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 08:26:35 2018

@author: shzb-200620
"""

import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.optimize import fsolve  
from matplotlib import pyplot as plt
import generate_path

def time_split(price_date,start_fixed_date,end_fixed_date,maturity_date):
    #输入：定价日，起均日，终均日，到期日
    #输出：三段时间及分属情况
    Ta = ((maturity_date - price_date).days+1)/365
    Tb = (maturity_date - start_fixed_date).days/365
    Tc = (maturity_date - end_fixed_date).days/365
    #分三种情况考虑
    #1.定价日位于起均日前
    #2.定价日位于起均日到终均日间
    #3.定价日位于终均日到到期日间
    if Ta>=Tb:
        sit = 1
    elif (Tc<Ta)&(Ta<Tb):
        sit = 2
    elif Ta<=Tc:
        sit = 3
    else:
        pass
    return Ta,Tb,Tc,sit

def Asian_Disc_MC(S_path,K,Ta,Tb,Tc,sit,r,SA,option_type,Nsamples,Tsteps):
    
    if sit == 1:
        t1 = Ta-Tb  #定价日到起均日
        t2 = Tb-Tc  #起均日到终均日
        num_start = int(t1/Ta*Tsteps)        #起均日步数
        num_end = int(t2/Ta*Tsteps) + num_start  #终均日步数
        Ari = S_path[:,num_start-1:num_end].mean(axis=1)  #均值计算
        
    elif sit == 2:
        t1 = Tb-Ta
        t2 = Ta-Tc
        num_start = 0       #起均日步数
        num_end = int(t2/Ta*Tsteps)  #终均日步数
        Ari = S_path[:,num_start:num_end].mean(axis=1)  #均值计算
        Ari = SA*(t1/(t1+t2))+Ari*(t2/(t1+t2))
        
    elif sit == 3:
        Ari = np.ones(Nsamples)*SA
    else:
        pass

    #四种亚式期权的收益结构
    if option_type == 'discrete-ari-call-fixed':
        for i in range(len(Ari)):
            Ari[i] = Ari[i]-K if (Ari[i]-K)>0 else 0
        payoff = Ari
        
    elif option_type == 'discrete-ari-put-fixed':
        for i in range(len(Ari)):
            Ari[i] = K-Ari[i] if (K-Ari[i])>0 else 0
        payoff = Ari
    
    elif option_type == 'discrete-ari-call-floating':
        payoff = S_path[:,-1]-Ari
        for i in range(len(payoff)):
            payoff[i] = payoff[i] if (payoff[i])>0 else 0
    
    elif option_type == 'discrete-ari-put-floating':
        payoff = Ari-S_path[:,-1]
        for i in range(len(payoff)):
            payoff[i] = payoff[i] if (payoff[i])>0 else 0
            
    else:
        pass
    
    V = np.mean(np.exp(-r*Ta)*payoff)
    se = np.sqrt((np.sum(payoff**2)-Nsamples*V**2)/Nsamples/(Nsamples-1))
    
    return V,se

def DG_MC_single(S_path,S_path_sup,S_path_sdn,ds,K,Ta,Tb,Tc,sit,r,SA,option_type,Nsamples=100000,Tsteps=1000):

    V,se = Asian_Disc_MC(S_path,K,Ta,Tb,Tc,sit,r,SA,option_type,Nsamples,Tsteps)
    V_sup,se = Asian_Disc_MC(S_path_sup,K,Ta,Tb,Tc,sit,r,SA,option_type,Nsamples,Tsteps)
    V_sdn,se = Asian_Disc_MC(S_path_sdn,K,Ta,Tb,Tc,sit,r,SA,option_type,Nsamples,Tsteps)

    delta = (V_sup - V_sdn)/(2*ds)
    gamma = (V_sup + V_sdn - 2*V)/(ds**2)
    
    return delta,gamma,V
    


if __name__ == '__main__':
    '''Input'''
    S = 1800
    K = 1800
    SA = 1800                                 #今日之前累计的平均,for not newly issued option

    price_date = pd.datetime(2018,7,1)        #期权报价日
    start_fixed_date = pd.datetime(2018,10,1)  #开始计算平均值的日期
    end_fixed_date = pd.datetime(2018,11,1)   #结束累计平均值的日期
    maturity_date = pd.datetime(2018,11,1)    #期权到期日
    sigma = 0.18
    r = 0.01
    q = 0
    T = (maturity_date - price_date).days/365
    
    option_type = 'discrete-ari-put-fixed'
    
    Nsamples = 50000
    Tsteps = 100
    
    ds = 0.0001*S
    
    '''Input'''
    
    Ta,Tb,Tc,sit = time_split(price_date,start_fixed_date,end_fixed_date,maturity_date)
    random = generate_path.random_gen(Nsamples,Tsteps)
    ret = generate_path.Ret_path_gen(r,sigma,q,T,random)
    S_path = generate_path.S_path_gen(S,ret)
    S_path_sup = generate_path.S_path_gen(S+ds,ret)
    S_path_sdn = generate_path.S_path_gen(S-ds,ret)
    delta,gamma,V = DG_MC_single(S_path,S_path_sup,S_path_sdn,ds,K,Ta,Tb,Tc,sit,r,SA,option_type,Nsamples,Tsteps)
    #greeks = [delta,gamma]
    #print(greeks)
    print(delta,gamma,V)

    
    
    