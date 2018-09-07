# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 12:48:56 2018

@author: Jax_GuoSen
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import fsolve  
from matplotlib import pyplot as plt

class OptionPricer:
    def __init__(self,S,r,sigma,K,price_date,maturity_date,status):
        self.info = {'und_price':S,
                     'rf':r,
                     'vol':sigma,
                     'strike':K,
                     'price_date':price_date,
                     'maturity_date':maturity_date,
                     'status':status}
        
        
class VanillaOption(OptionPricer):
    pass

def random_gen(N,T):
    z = np.random.randn(N,T)
    return z

class Rand_Path_Gen(OptionPricer):
    def Ret_path_gen(self,random):
        Ret_path = np.ones((random.shape[0],random.shape[1]))
        z = random
        dt = ((self.info['maturity_date']-self.info['price_date']).days)/365/random.shape[1]
        Ret_path = np.exp((self.info['rf']-0.5*self.info['vol']**2)*dt+self.info['vol']*np.sqrt(dt)*z)  #产生收益率序列
        return Ret_path
    
    def S_path_gen(self,ret):
        S_path = np.zeros((ret.shape[0],ret.shape[1]))
        S_path[:,0] = self.info['und_price']
        for i in range(ret.shape[1]-1):
            if type(ret) == np.ndarray:
                S_path[:,i+1] = S_path[:,i]*ret[:,i+1]    #产生股价序列
            else:
                S_path[:,i+1] = np.multiply(S_path[:,i],np.array(ret[:,i+1]).T[0])
        return S_path


class AsianOption(OptionPricer):
    
    def get_fixed_date(self,start_fixed_date,end_fixed_date,SA):
        self.start_fixed_date = start_fixed_date
        self.end_fixed_date = end_fixed_date
        self.SA = SA
    def time_split(self):
        #输入：定价日，起均日，终均日，到期日
        #输出：三段时间及分属情况
        self.Ta = ((self.info['maturity_date'] - self.info['price_date']).days)/365
        self.Tb = (self.info['maturity_date'] - self.start_fixed_date).days/365
        self.Tc = (self.info['maturity_date'] - self.end_fixed_date).days/365
        #分三种情况考虑
        #1.定价日位于起均日前
        #2.定价日位于起均日到终均日间
        #3.定价日位于终均日到到期日间
        if self.Ta>=self.Tb:
            self.sit = 1
        elif (self.Tc<self.Ta)&(self.Ta<self.Tb):
            self.sit = 2
        elif self.Ta<=self.Tc:
            self.sit = 3
        else:
            pass
        
    
    def Asian_Disc_MC(self,S_path):

        Nsamples = S_path.shape[0]
        Tsteps = S_path.shape[1]
        if self.sit == 1:
            t1 = self.Ta-self.Tb  #定价日到起均日
            t2 = self.Tb-self.Tc  #起均日到终均日
            num_start = int(t1/self.Ta*Tsteps)        #起均日步数
            num_end = int(t2/self.Ta*Tsteps) + num_start  #终均日步数
            Ari = S_path[:,num_start:num_end].mean(axis=1)  #均值计算
            #num_start 减 or 不减1
        elif self.sit == 2:
            t1 = self.Tb-self.Ta
            t2 = self.Ta-self.Tc
            num_start = 0       #起均日步数
            num_end = int(t2/self.Ta*Tsteps)  #终均日步数
            Ari = S_path[:,num_start:num_end].mean(axis=1)  #均值计算
            Ari = self.SA*(t1/(t1+t2))+Ari*(t2/(t1+t2))
        elif self.sit == 3:
            Ari = np.ones(Nsamples)*self.SA
        else:
            pass
        #亚式期权的收益结构
        if self.info['status'] == 'call':
            for i in range(len(Ari)):
                Ari[i] = Ari[i]-self.info['strike'] if (Ari[i]-self.info['strike'])>0 else 0
            payoff = Ari
        elif self.info['status'] == 'put':
            for i in range(len(Ari)):
                Ari[i] = self.info['strike']-Ari[i] if (self.info['strike']-Ari[i])>0 else 0
            payoff = Ari
        else:
            pass
        V = np.mean(np.exp(-self.info['rf']*self.Ta)*payoff)
        se = np.sqrt((np.sum(payoff**2)-Nsamples*V**2)/Nsamples/(Nsamples-1))
        
        return V,se
    
    def Run(self):
        pass
    
    

if __name__ == '__main__':
    a = pd.datetime(2018,7,5)
    b = pd.datetime(2018,10,3)
    c = a
    d = b
    
    rand = Rand_Path_Gen(15000,0.01,0.3,15000,a,b,'call')
    z = random_gen(N=50000,T=1000)
    ret = rand.Ret_path_gen(z)
    S = rand.S_path_gen(ret)
    
    
    V = AsianOption(15000,0.01,0.3,15000,a,b,'call')
    V.get_fixed_date(c,d,0)
    V.time_split()
    price,se = V.Asian_Disc_MC(S)
    print(price,se)
    
    
    
    
    
    
    
    


