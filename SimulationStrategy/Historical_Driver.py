# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 09:58:19 2018

@author: Jax_GuoSen
"""

import pandas as pd
import Greeks
from datetime import datetime
import os
import OptionPricer


#part1
def greeks_driver():
    root = os.getcwd()
    data = pd.read_csv(root+'\\data_Hist\\Input\\OptionInfo.csv',sep=';')
    data['Maturity'] = data['Maturity'].apply(lambda x:datetime.strptime(x,'%Y-%m-%d %H:%M:%S'))
    res= []
    
    for i in data.index.tolist():
        Mt = data.loc[i,'Maturity']
        code = data.loc[i,'Code']
        tmp = pd.read_csv(root+'\\data_Hist\\Input\\%s.csv'%code,sep=';')
        tmp['time'] = tmp['time'].apply(lambda x:datetime.strptime(x,'%Y-%m-%d %H:%M:%S'))
        if data.loc[i,'OptionType'] in ['EC','EP']:
            for j in tmp.index.tolist():
                TTM = (Mt-tmp.loc[j,'time']).days/365
                status = 'call' if data.loc[i,'OptionType']=='EC' else 'put'
                V = Greeks.Greeks_Euro(tmp.loc[j,'undly'],tmp.loc[j,'HedgeRf'],tmp.loc[j,'HedgeVol'],data.loc[i,'Strike'],TTM,status)
                greeks = V.cpt_all_greeks()
                tmp.loc[j,'Delta'] = greeks['Delta']*data.loc[i,'Position']
                tmp.loc[j,'Gamma'] = greeks['Gamma']*data.loc[i,'Position']
                tmp.loc[j,'Rho(%)'] = greeks['Rho(%)']*data.loc[i,'Position']
                tmp.loc[j,'ThetaPerday'] = greeks['ThetaPerday']*data.loc[i,'Position']
                tmp.loc[j,'Vega(%)'] = greeks['Vega(%)']*data.loc[i,'Position']
            res.append(tmp)
        
        elif data.loc[i,'OptionType'] in ['AC','AP']:
            data['FixSt'] = data['FixSt'].apply(lambda x:datetime.strptime(x,'%Y-%m-%d %H:%M:%S'))
            data['FixEd'] = data['FixEd'].apply(lambda x:datetime.strptime(x,'%Y-%m-%d %H:%M:%S'))
            for j in tmp.index.tolist():
                print(j)
                z = OptionPricer.random_gen(N=10000,T=100)
                a = tmp.loc[j,'time']
                b = Mt
                c = data.loc[i,'FixSt']
                d = data.loc[i,'FixEd']
                FixPeriod = tmp[(tmp['time']>=c)&(tmp['time']<=a)]
                SA = FixPeriod['undly'].mean()
                status = 'call' if data.loc[i,'OptionType']=='AC' else 'put'
                V = Greeks.Aisan_Greeks(z,tmp.loc[j,'undly'],SA,tmp.loc[j,'HedgeRf'],tmp.loc[j,'HedgeVol'],data.loc[i,'Strike'],a,b,c,d,status)
                greeks = V.cpt_all_greeks()
                tmp.loc[j,'CumAvg'] = SA
                tmp.loc[j,'Delta'] = greeks['Delta']*data.loc[i,'Position']
                tmp.loc[j,'Gamma'] = greeks['Gamma']*data.loc[i,'Position']
                tmp.loc[j,'Rho(%)'] = greeks['Rho(%)']*data.loc[i,'Position']
                tmp.loc[j,'ThetaPerday'] = greeks['ThetaPerday']*data.loc[i,'Position']
                tmp.loc[j,'Vega(%)'] = greeks['Vega(%)']*data.loc[i,'Position']
            res.append(tmp)
    
    portfolio_greeks = pd.DataFrame(index=res[0].index,columns=['Delta','Gamma','Rho(%)','ThetaPerday','Vega(%)'])
    portfolio_greeks.loc[:,:] = 0
    for i in range(len(res)):
        portfolio_greeks = portfolio_greeks+res[i][['Delta','Gamma','Rho(%)','ThetaPerday','Vega(%)']]
    #portfolio_greeks.iloc[-1,:] = 0  #最后一行=0，即最后一天平仓
    portfolio_greeks.loc[:,'time'] = res[0]
    portfolio_greeks.loc[:,'undly'] = res[0]
    portfolio_greeks.loc[:,'CumAvg'] = res[0]
    portfolio_greeks.to_csv(root+'\\data_Hist\\Output\\portfolio_greeks.csv',sep=';')
    
    return portfolio_greeks
   

#part2
def position_driver(portfolio_greeks,threshold,is_overhedge):
    root = os.getcwd()
    data = pd.read_csv(root+'\\data_Hist\\Input\\OptionInfo.csv',sep=';')
    hedge_info = portfolio_greeks[['time','undly','Delta']]
    Multiplier = data.loc[:,'Multiplier'].min()
    threshold = threshold*Multiplier
    if is_overhedge:
        hedge_info['HedgingDelta'] = -hedge_info['Delta'].apply(lambda x:round(x/threshold)*threshold)
    else:
        hedge_info['HedgingDelta'] = -hedge_info['Delta'].apply(lambda x:int(x/threshold)*threshold)
    
    hedge_info['HedgingPos'] = hedge_info['HedgingDelta']/Multiplier
    hedge_info.loc[hedge_info.index.tolist()[-1],'HedgingPos'] = 0
    hedge_info['TradePos'] = hedge_info['HedgingPos'].diff()
    hedge_info['TradePos'][0] = hedge_info['HedgingPos'][0]
    hedge_info['volume'] = hedge_info['TradePos'].apply(lambda x:abs(x))
    hedge_info.to_csv(root+'\\data_Hist\\Output\\hedge_info.csv',sep=';')
    return hedge_info



#part3
def PNL_driver(Commission,hedge_info):
    root = os.getcwd()
    data = pd.read_csv(root+'\\data_Hist\\Input\\OptionInfo.csv',sep=';')
    Multiplier = data.loc[:,'Multiplier'].min()
    #print('最后一天未平仓'if hedge_info['HedgingPos'].tolist()[-1]!=0 else '最后一天已平仓')
    totalpnl = -sum(hedge_info['TradePos']*hedge_info['undly']*Multiplier)+hedge_info['HedgingPos'].tolist()[-1]*hedge_info['undly'].tolist()[-1]*Multiplier
    totalvolume = sum(hedge_info['volume'])
    TotalCommission = -totalvolume*Commission
    PNLwithCommission = TotalCommission+totalpnl
    maxholdposition = max(hedge_info['HedgingPos']) if max(hedge_info['HedgingPos'])>abs(min(hedge_info['HedgingPos'])) else min(hedge_info['HedgingPos'])
    maxholdpositiontime = hedge_info[hedge_info['HedgingPos']==maxholdposition]['time'].tolist()[0]
    res = pd.DataFrame([totalpnl,totalvolume,maxholdposition,maxholdpositiontime,Multiplier,Commission,TotalCommission,PNLwithCommission],index=['totalpnl','totalvolume','maxholdposition','maxholdpositiontime','multiplier','CommissionPerShare','TotalCommission','PNLwithCommission'])
    res.to_csv(root+'\\data_Hist\\Output\\PNL_result.csv',sep=';')    
    return res

    
    

'''
threshold 对冲最小变动单位/手数
is_overhedge 是否允许overhedge
Commission 每手手续费
'''
if __name__ == '__main__':
    portfolio_greeks = greeks_driver()
    hedge_info = position_driver(portfolio_greeks,threshold=1,is_overhedge = False)
    res = PNL_driver(Commission=10,hedge_info=hedge_info)
    print(res)
    


    
    
    
    
    
    
    