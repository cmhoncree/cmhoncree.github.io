# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 11:24:02 2019

@author: liang
"""

#coding=UTF-8
#欲顯示中文註解必須加上上述設定
import math
import matplotlib.pyplot as plot
import matplotlib.patches as mpatches
import itertools
import numpy as np
import pyodbc 
import getpass 
import pyodbc 
import sys
from pandas import DataFrame
import pandas as pd
from pandas.io.sql import read_sql
from decimal import *
import xlwings as xw
import xlwt

#Model B4TW total

#全域變數
###############################################################################
#產出圖片資料夾路徑
imageSaveDir = 'D:\Tmpx';
###############################################################################

#根據傳入的參數，計算結果並回傳
#Kh----------------------------------------------------------------------------
def Kh_cal(RH):
    if RH<=0.98:
        return (1-RH**3)
    elif 0.98<RH<=1:
        return 1-0.98**3
    else:
        print ("Humidity error( must be 0~1 )")

#根據傳入的參數，計算結果並回傳
#Ks----------------------------------------------------------------------------
def Ks_cal(geo):
    if geo==1:
        return 1
    elif geo==2:
        return 1.15
    elif geo==3:
        return 1.25
    elif geo==4:
        return 1.3
    elif geo==5:
        return 1.55
    else:
        print ("Geometry error( must be 1~5 )")

#根據傳入的參數，計算結果並回傳
#Table1------------------------------------------------------------------------
def Table1_cal(cement):
    if cement==1:
        return [0.016, -0.33, -0.06, -0.1, 360e-6, -0.8,   1.1,  0.11]
    elif cement==2:
        return [0.01,  -0.33,  3.55,  3.8, 410e-6, -0.8,     1,  0.11]
    elif cement==3:
        return [0.08,  -0.33,  -2.4, -2.7, 860e-6, -0.8, -0.27,  0.11]
    else:
        print ("Cement type error( must be 1~3 )")

#根據傳入的參數，計算結果並回傳
#Table2------------------------------------------------------------------------
def Table2_cal(cement):
    if cement==1:
        return [1,  3,  -4.5,  1,   210e-6,  -0.75,  -3.5]
    elif cement==2:
        return [1,  3,  -4.5,  1,   210e-6,  -0.75,  -3.5]
    elif cement==3:
        return [41, 3,  -4.5, 1.4,  -84e-6,  -0.75,  -3.5]
    else:
        print ("Cement type error( must be 1~3 )")

#根據傳入的參數，計算結果並回傳
#Table3------------------------------------------------------------------------
def Table3_cal(cement):
    if cement==1:
        return [0.7,  58.6e-3,  39.3e-3,  3.4e-3,  777e-6,  8,  3,  -1.1,  0.4,  -0.9,  2.45,  -0.85,  -1,  0.78]
    elif cement==2:
        return [0.8,  40.5e-3,  39.3e-3,  3.4e-3,  496e-6,  8,  3,  -1.1,  0.4,  -0.9,  2.45,  -0.85,  -1,  0.78]
    elif cement==3:
        return [0.6,  17.4e-3,  39.3e-3,  3.4e-3,  94.6e-6, 1,  3,  -1.1,  0.4,  -0.9,  2.45,  -0.85,  -1,  0.78]
    else:
        print ("Cement type error( must be 1~3 )")

#t-----------------------------------------------------------------------------

#根據傳入的參數，計算結果並回傳
def BTh_cal(Tcur):
    return math.exp(4000*(1/293.-1./(Tcur+273)))

#根據傳入的參數，計算結果並回傳
def BTs_cal(T):
    return math.exp(4000*(1/293.-1./(T+273)))

#根據傳入的參數，計算結果並回傳
def t0wave_cal(t0,BTh):
    return t0*BTh

#根據傳入的參數，計算結果並回傳
#E28---------------------------------------------------------------------------
def E28_cal(fc):
    return (fc**0.5)*3831./1000

#E(t)--------------------------------------------------------------------------
def E_cal(t):
    #存取全域變數
    return _E28*(t/(4+(6./7)*t))**0.5

#根據傳入的參數，計算結果並回傳
#tau0--------------------------------------------------------------------------
def tau0_cal(ac,wc,c,taucem,ptaua,ptauw,ptauc):
    return taucem*((ac/6.)**ptaua)*((wc/0.38)**ptauw)*((6.5*c/2350)**ptauc)

#根據傳入的參數，計算結果並回傳
#taush-------------------------------------------------------------------------
def taush_cal(vs,Ks,ktaua,tau0):
    return tau0*ktaua*((Ks*vs)**2)

#根據傳入的參數，計算結果並回傳
#e0----------------------------------------------------------------------------
def e0_cal(ac,wc,c,ecem,pea,pew,pec):
    return ecem*((ac/6.)**pea)*((wc/0.38)**pew)*((6.5*c/2350)**pec)

#根據傳入的參數，計算結果並回傳
#esh8--------------------------------------------------------------------------
def esh8_cal(e0,kea,E607_m,Et0_taush_m):
    return -1*e0*kea*E607_m/Et0_taush_m

#根據傳入的參數，計算結果並回傳
#S(t)--------------------------------------------------------------------------
def S_cal(twave_array,taush,fshtau):
    return [math.tanh((n/(taush*fshtau))**0.5) for n in twave_array]

#根據傳入的參數，計算結果並回傳
#esh---------------------------------------------------------------------------
def esh_cal(esh8,S,Kh,fshcem):
    return S*Kh*esh8*fshcem

#根據傳入的參數，計算結果並回傳
def eau8_cal(ac,wc,eaucem,faucem,gamaea,gamaew,fauwc):
    return -1*faucem*eaucem*((ac/6.)**gamaea)*((wc/0.38)**(gamaew*fauwc))

#根據傳入的參數，計算結果並回傳
#Bas---------------------------------------------------------------------------
def Bas_cal(twave_array,t0wave_array):
    return [1-np.exp(-0.2*n**0.5) for n in (twave_array+t0wave_array)]

#根據傳入的參數，計算結果並回傳
#alpha. eau
def eau_cal(eau8,Bas):
    return eau8*Bas


"""A=pd.DataFrame(data)
datatoexcel=pd.ExcelWriter("FromPython.xlsx",engine='xlsxwriter')
A.to_excel(datatoexcel, sheet_name='Sheet1') 
datatoexcel.save()
B=pd.DataFrame(info)
datatoexcel=pd.ExcelWriter("FromPython2.xlsx",engine='xlsxwriter')
B.to_excel(datatoexcel, sheet_name='Sheet1') 
datatoexcel.save()"""

#必要參數
#para1:w水量(不可為0)
#para2:c水泥量(不可為0)
#para3:Slag爐石量(可為0)
#para4:FlyAsh飛灰量(可為0)
#para5:SiO2矽灰量(可為0)
#para6:fc28設計強度(不可為0)
#para7:fine aggregate細粒料量(不可為0)
#para8:coarse aggregate粗粒料量(不可為0)
#para9:Super kg強塑劑量(可為0)-先跳過
#para10:t0養護天數(不可為0)
#para11:tp加載齡期(如空值和t0相同)
#非必要參數
#para12:RH相對溼度(如空白，放0.5)
#para13:T試驗溫度(如空白，放23)
#para14:Tcur養護溫度(如空白，放20)
#para15:VS體表比(如空白，放21)
#para16:Cem_type水泥種類(有三種)(如空白，放1)
#para17:Geo(如空值，放2)
def caculateData(imgHeadName, para1, para2, para3, para4, para5, para6, para7, para8, para9, para10, para11, para12, para13, para14, para15, para16, para17):
        w=float(para1)
        c=float(para2)
        slag=float(para3)
        fly=float(para4)
        SiO2=float(para5)
        fc=float(para6)
        a=float(para7)+float(para8);
        
        cm=c+fly+slag;
        wc=w/cm;
        ac=a/cm;
        FlyAsh=fly/cm*100
        Slag=slag/cm*100
        
        #para9:跳過
        t0=float(para10);
        
        RH=float(para12);
        T=float(para13);
        Tcur=float(para14);
        
        vs=float(para15);
        vs=float(vs)*2
        
        cement=float(para16);
        geo=float(para17);
        
        #目前未使用到
        curing=3
        
        t=np.linspace(0,10000,100000)
        t=np.array(t)
        
        ID=1
    
        Kh=Kh_cal(RH)
        Ks=Ks_cal(geo)
        BTh=BTh_cal(Tcur)
        BTs=BTs_cal(T)
        
        t0wave=t0wave_cal(t0,BTh)
    
        Table1=Table1_cal(cement)
        Table2=Table2_cal(cement)
        Table3=Table3_cal(cement)
    
        taucem=Table1[0]
        ptaua=Table1[1]
        ptauw=Table1[2]
        ptauc=Table1[3]
        ecem=Table1[4]
        pea=Table1[5]
        pew=Table1[6]
        pec=Table1[7]
    
        tauaucem=Table2[0]
        gamatauw=Table2[1]
        gamat=Table2[2]
        gamaalpha=Table2[3]
        eaucem=Table2[4]
        gamaea=Table2[5]
        gamaew=Table2[6]
    
        ktaua=2.8
        kea=1.7
    
        if Slag==0 and FlyAsh==0:
            faucem=1
            fauwc=1
            fshcem=1
            fshtau=1
        if Slag>0 and FlyAsh==0:
            faucem=0.75
            fauwc=0.2
            fshcem=1
            fshtau=0.9
        if Slag==0 and FlyAsh>40:
            faucem=0.5
            fauwc=0.1
            fshcem=0.8
            fshtau=2.0
        if Slag==0 and FlyAsh<=40:
            faucem=0.5
            fauwc=0.1
            fshcem=1
            fshtau=1.5
        if Slag>0 and FlyAsh>0 and t0<28:
            faucem=0.6
            fauwc=0.1
            fshcem=1.26
            fshtau=1.1
        if Slag>0 and FlyAsh>0 and t0>=28:
            faucem=0.6
            fauwc=0.1
            fshcem=0.81
            fshtau=1.1
    
    #calculation starts here-------------------------------------------------------
    
        tau0=tau0_cal(ac,wc,c,taucem,ptaua,ptauw,ptauc)
        taush=taush_cal(vs,Ks,ktaua,tau0)
        e0=e0_cal(ac,wc,c,ecem,pea,pew,pec)
    
        E28=E28_cal(fc)
        
        #存取全域變數
        global _E28;
        _E28 = E28;
        
        E607_m=E_cal(7*BTh+600*BTs)
        Et0_taush_m=E_cal(t0wave+taush*BTs)
        esh8=esh8_cal(e0,kea,E607_m,Et0_taush_m)
    
    #arraying
    
        t0_array=np.array([t0]*len(t))
        
        t0wave_array=np.array([t0wave]*len(t))
        twave_array=(t)*BTs
        S=np.array(S_cal(twave_array,taush,fshtau))
        esh=esh_cal(esh8,S,Kh,fshcem)*1e6
        eau8=eau8_cal(ac,wc,eaucem,faucem,gamaea,gamaew,fauwc)
        Bas=np.array(Bas_cal(twave_array,t0wave_array),dtype=float)
        eau=eau_cal(eau8,Bas)*1e6
        #print eau
        eshtotal=np.abs(esh+eau-eau[0])
        #print esh
            
        fig=plot.figure(1)
        plot.xscale('log')
        plot.plot(t,(eshtotal))
        plot.xlim(0.01,10000)
        plot.ylim(0,1200)
        
        #會出現警告訊息
        #plot.legend(loc='upper left',prop={'size':15})
        
        plot.title('Model B4TW Total Shrinkage',fontsize=20)
        plot.ylabel(r'Shrinkage strain $(10^{-6})$',fontsize=14)
        plot.xlabel(r'$t$  (days)',fontsize=14)   
    
        #plot.show()
        plot.savefig(imageSaveDir + '\\' + imgHeadName + '.jpg', dpi=100)

if __name__== "__main__":
    caculateData(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11], sys.argv[12], sys.argv[13], sys.argv[14], sys.argv[15], sys.argv[16], sys.argv[17], sys.argv[18]);