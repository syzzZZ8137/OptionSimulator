# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 12:27:16 2018

@author: Jax_GuoSen
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
import OptionPricer
import datetime

class Greeks_Euro:
    def __init__(self,S,r,sigma,K,T,status):
        self.info = {'und_price':S,
                     'rf':r,
                     'vol':sigma,
                     'strike':K,
                     'ttm':T,
                     'status':status}
        self.d1 = (np.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
        self.d2 = (np.log(S/K)+(r-0.5*sigma**2)*T)/(sigma*np.sqrt(T))
        self.c1 = -S*sigma/(2*np.sqrt(2*np.pi*T))*np.exp((-self.d1**2)/2)
        self.c2 = -r*K*np.exp(-r*T)*norm.cdf(self.d2)
        self.c3 = r*K*np.exp(-r*T)*norm.cdf(-self.d2)
        
    def cpt_delta(self):
        if self.info['status'] =='call':
            delta = norm.cdf(self.d1)
        elif self.info['status'] == 'put':
            delta = norm.cdf(self.d1)-1
        else:
            delta = np.nan
        return delta
    
    def cpt_theta(self):
        if self.info['status'] == 'call':
            theta = self.c1+self.c2
        elif self.info['status'] == 'put':
            theta = self.c1+self.c3
        else:
            theta = np.nan
        return theta/365
    
    def cpt_gamma(self):
        gamma = 1/(self.info['und_price']*np.sqrt(2*np.pi*(self.info['vol']**2)*self.info['ttm']))*np.exp((-self.d1**2)/2)
        return gamma
    
    
    def cpt_vega(self):
        vega = np.sqrt(self.info['ttm'])*self.info['und_price']*np.exp((-self.d1**2)/2)/np.sqrt(2*np.pi)
        return vega/100
    
    def cpt_rho(self):
        if self.info['status'] =='call':
            rho = self.info['strike']*self.info['ttm']*np.exp(-self.info['rf']*self.info['ttm'])*norm.cdf(self.d2)
        elif self.info['status'] == 'put':
            rho = -self.info['strike']*self.info['ttm']*np.exp(-self.info['rf']*self.info['ttm'])*norm.cdf(-self.d2)
        else:
            rho = np.nan
        return rho/100

    def cpt_all_greeks(self):
        res = {'Delta':round(self.cpt_delta(),8),
               'Gamma':round(self.cpt_gamma(),8),
               'Vega(%)':round(self.cpt_vega(),8),
               'ThetaPerday':round(self.cpt_theta(),8),
               'Rho(%)':round(self.cpt_rho(),8)     
               }
        return res



class Greeks_Diff:
    def diff(S):
        ds = S*0.0001 #price的万分之一 
        dvol = 0.001 #10bp
        dt = 1/3650  #0.1day
        dr = 0.0001  #1bp
        return ds,dvol,dt,dr

class Aisan_Greeks:
    def __init__(self,random,S,SA,r,sigma,K,price_date,maturity_date,start_fixed_date,end_fixed_date,status):
        self.S = S
        self.SA = SA
        self.r = r
        self.sigma = sigma
        self.K = K
        self.price_date = price_date
        self.maturity_date = maturity_date
        self.start_fixed_date = start_fixed_date
        self.end_fixed_date = end_fixed_date
        self.status = status
        self.random =random
        self.ds,self.dvol,self.dt,self.dr = Greeks_Diff.diff(self.S)
    
    def cal_AsianOption(self,S,SA,r,sigma,K,price_date,maturity_date,start_fixed_date,end_fixed_date,status):
        rand = OptionPricer.Rand_Path_Gen(S,r,sigma,K,price_date,maturity_date,status)
        ret = rand.Ret_path_gen(self.random)
        Spath = rand.S_path_gen(ret)
        #产生出S路径
        V = OptionPricer.AsianOption(S,r,sigma,K,price_date,maturity_date,status)
        V.get_fixed_date(start_fixed_date,end_fixed_date,SA)
        V.time_split()
        price,se = V.Asian_Disc_MC(Spath)
        return price,se
    
    def cpt_delta_gamma(self):
        V,se = self.cal_AsianOption(self.S,self.SA,self.r,self.sigma,self.K,\
                               self.price_date,self.maturity_date,\
                               self.start_fixed_date,self.end_fixed_date,\
                               self.status)
        V_S_up,se = self.cal_AsianOption(self.S+self.ds,self.SA,self.r,self.sigma,self.K,\
                               self.price_date,self.maturity_date,\
                               self.start_fixed_date,self.end_fixed_date,\
                               self.status)
        V_S_dn,se = self.cal_AsianOption(self.S-self.ds,self.SA,self.r,self.sigma,self.K,\
                               self.price_date,self.maturity_date,\
                               self.start_fixed_date,self.end_fixed_date,\
                               self.status)
        delta = (V_S_up - V_S_dn)/(2*self.ds)
        gamma = (V_S_up + V_S_dn - 2*V)/(self.ds**2)
        return delta,gamma
        
    def cpt_vega(self):
        V_vol_up,se = self.cal_AsianOption(self.S,self.SA,self.r,self.sigma+self.dvol,self.K,\
                               self.price_date,self.maturity_date,\
                               self.start_fixed_date,self.end_fixed_date,\
                               self.status)
        
        V_vol_dn,se = self.cal_AsianOption(self.S,self.SA,self.r,self.sigma-self.dvol,self.K,\
                               self.price_date,self.maturity_date,\
                               self.start_fixed_date,self.end_fixed_date,\
                               self.status)
        
        vega = (V_vol_up-V_vol_dn)/(2*self.dvol)
        return vega/100
    
    def cpt_theta(self):
        V,se = self.cal_AsianOption(self.S,self.SA,self.r,self.sigma,self.K,\
                               self.price_date,self.maturity_date,\
                               self.start_fixed_date,self.end_fixed_date,\
                               self.status)
        V_pass,se = self.cal_AsianOption(self.S,self.SA,self.r,self.sigma,self.K,\
                               self.price_date+datetime.timedelta(1),self.maturity_date,\
                               self.start_fixed_date,self.end_fixed_date,\
                               self.status)
        
        return V_pass-V
    
    def cpt_rho(self):
        V_r_up,se = self.cal_AsianOption(self.S,self.SA,self.r+self.dr,self.sigma,self.K,\
                               self.price_date,self.maturity_date,\
                               self.start_fixed_date,self.end_fixed_date,\
                               self.status)
        
        V_r_dn,se = self.cal_AsianOption(self.S,self.SA,self.r-self.dr,self.sigma,self.K,\
                               self.price_date,self.maturity_date,\
                               self.start_fixed_date,self.end_fixed_date,\
                               self.status)
        
        rho = (V_r_up-V_r_dn)/(2*self.dr)
        return rho/100

    def cpt_all_greeks(self):
        delta,gamma = self.cpt_delta_gamma()
        res = {'Delta':round(delta,8),
               'Gamma':round(gamma,8),
               'Vega(%)':round(self.cpt_vega(),8),
               'ThetaPerday':round(self.cpt_theta(),8),
               'Rho(%)':round(self.cpt_rho(),8)
               }
        return res
        
        
if __name__ == '__main__':    
    a = pd.datetime(2018,8,13)
    b = pd.datetime(2018,9,8)
    T = (b-a).days/365
    S = 507
    K1 = 512
    K2 = 482
    sigma1 = 0.31
    sigma2 = 0.225
    r = 0
    status = 'put'
    V1 = Greeks_Euro(S,r,sigma1,K1,T,status)
    V2 = Greeks_Euro(S,r,sigma2,K2,T,status)

    greeks1 = V1.cpt_all_greeks()
    greeks2 = V2.cpt_all_greeks()
    
    
    
    
    #z = OptionPricer.random_gen(N=50000,T=1000)
    
    
    #random,S,SA,r,sigma,K,price_date,maturity_date,start_fixed_date,end_fixed_date,status
    #V = Aisan_Greeks(z,15000,15000,0.01,0.3,15000,a,b,c,d,'call')
    #res = V.cpt_all_greeks()
    #print(res)
        
        
        
        
        
        
        