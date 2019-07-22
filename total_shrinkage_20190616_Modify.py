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

#SQL Server 伺服器主機名稱
server='(local)\SQLEXPRESS'
#資料庫名稱
database='NTU_Creep'

#測試用
#username='AlexHuang'
#password='12345'
#cnxn=pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

#SQL驗證使用者帳號
username='NTU_Creep_User'
#SQL驗證使用者密碼
password='tester1115'
###############################################################################

#根據傳入的參數，計算結果並回傳
#Kh----------------------------------------------------------------------------
def Kh_cal(RH):
    if RH<=0.98:
        return (1-RH**3)
    elif 0.98<RH<=1:
        return 12.94*(1-RH)-0.2
    else:
        print ("Humidity error( must be 0~1 )")

#根據傳入的參數，比對結果參數並回傳
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

#根據傳入的參數，比對結果參數並回傳
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
        
#根據傳入的參數，比對結果參數並回傳
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
        
#根據傳入的參數，比對結果參數並回傳
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

#根據傳入的參數，計算結果並回傳
def BTh_cal(Tcur):
    return math.exp(4000*(1/293.-1./(Tcur+273)))

#根據傳入的參數，計算結果並回傳
def BTs_cal(T):
    return math.exp(4000*(1/293.-1./(T+273)))
    
#根據傳入的參數，計算結果並回傳
def t0wave_cal(t0,BTh):
    return t0*BTh

#根據傳入的參數，計算結果並回傳
#E28---------------------------------------------------------------------------
def E28_cal(fc):
    return (fc**0.5)*4734./1000

#根據傳入的參數，計算結果並回傳
#E(t)--------------------------------------------------------------------------
def E_cal(t):
    #存取全域變數
    return _E28*(t/(4+(6./7)*t))**0.5

#根據傳入的參數，計算結果並回傳
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
#tauau-------------------------------------------------------------------------
def tauau_cal(wc,gamatauw,tauaucem):
    return tauaucem*((wc/0.38)**gamatauw)
    
#根據傳入的參數，計算結果並回傳
#Bas---------------------------------------------------------------------------
def Bas_cal(twave_array,t0wave_array):
    return [1-np.exp(-0.2*n**0.5) for n in (twave_array+t0wave_array)]       
    
#根據傳入的參數，計算結果並回傳
#alpha. eau
def eau_cal(eau8,Bas):
    return eau8*Bas

#根據傳入的參數，計算結果並回傳
def upper(x):
    #print(x);
    return 1/0.6*x

#根據傳入的參數，計算結果並回傳
def lower(x):
    return 0.6*x

def db_conn(user, pwd, imgHeadName, para1, para2, para3, para4, para5, para6, para7):
    caculateData(para1, para2, para3, para4, para5, para6, para7);
    #print("Para start 1:" + para1 + "/" + para2 + "/" + para3 + "/" + para4 + "/" + para5 + "/" + para6 + "/" + para7);
        
    #建立矩陣，語法:
    #numpy.arange(start,stop,step,dtype=None)
    #0->1199
    x=np.arange(0,1200,1)
    
    #未使用的參數
    #label_upper="Test"
    
    #繪製圖形
    #繪製最上方文字
    plot.plot(x,upper(x),"r--")
    #繪製中央文字
    plot.plot(x,x,color='k')
    #繪製最下方文字
    plot.plot(x,lower(x),"r--")
    
    #在圖片上顯示文字(x,y,文字內容,字型大小,文字顏色)
    plot.text(700, 1000, r'+40%', fontsize=12,color='r')
    plot.text(900, 650, r'-40%', fontsize=12,color='r')
    #顯示三個文字，分別是：
    plot.text(60, 900, 'NO. of Data Sets: %s\n\nNO. of Data Points: %s\n\nR Square: %s '%(len(_parameter), _count[len(_parameter)-1],round(_Rsquare,2)),style='italic',bbox={'facecolor':'white', 'alpha':0.5,'pad':8})

    #設定圖片主標題
    plot.title('Modified Model B4TW Total Shrinkage',fontsize=20)
    #設定 X 軸座標標題與字型大小
    plot.xlabel(r'$Test Data (10^{-6})$',fontsize=14)
    #設定 Y 軸座標標題與字型大小
    plot.ylabel(r'$Modified Model B4 Predicted Value (10^{-6})$',fontsize=14)  
    
    #顯示圖片在營幕上
    #plot.show()
    
    #dpi 如果設定為150，則圖片大小會變成960x720
    #dpi 如果設定為125，則圖片大小會變成800x600
    #dpi 如果設定為100，則圖片大小會變成640x480
    plot.savefig(imageSaveDir + '\\' + imgHeadName + '.jpg', dpi=100)

def caculateData(para1, para2, para3, para4, para5, para6, para7):
    #組合連線字串並連結資料庫
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + \
           server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password);
    
    #參考文件:https://code.google.com/archive/p/pyodbc/wikis
    #產生讀取資料用指標
    cursor=cnxn.cursor()
    
    #參數1/2:fc28->混凝土28天抗壓強度，分大於等於和小於等於(*)
    #參數3:Shrinkage_type->潛變種類，字串，只有三種:auto/drying/total(*)
    #參數4:C->水泥量，固定不可為Null
    #參數5/6:Slag_percent->爐石取代百分比，分大於等於和小於等於(*)
    #參數7/8:FlyAsh_percent->飛灰取代百分比，分大於等於和小於等於(*)
    #參數9:File_data_reference->資料參考代碼，固定不可為特定資料
    Args = "fc28 >= " + para1;
    Args = Args + " AND fc28 <= " + para2;
    Args = Args + " AND Shrinkage_type = '" + para3 + "'";
    Args = Args + " AND c NOT LIKE 'NULL'"
    Args = Args + " AND (Slag_percent > " + para4;
    Args = Args + " AND  Slag_percent <= " + para5;
    Args = Args + " AND FlyAsh_percent >= " + para6;
    Args = Args + " AND FlyAsh_percent <= " + para7 + ")";
    Args = Args + "AND File_data_reference NOT LIKE 's_013_17%'\
    AND File_data_reference NOT LIKE 's_036%'\
    AND File_data_reference NOT LIKE 's_017%'"
    
    #參數1:ShrinkagFile->收縮數據名稱
    A="SELECT * FROM [NTU_Creep].[dbo].[Tw_OPC_Shrinkag_Data] WHERE ShrinkagFile \
    IN(SELECT File_data_reference FROM [NTU_Creep].[dbo].[Tw_OPC_Shrinkage_Info] WHERE " + Args + ")"
    
    B="Select * FROM [NTU_Creep].[dbo].[Tw_OPC_Shrinkage_Info] WHERE " + Args
                    
    #讀取 SQL 指令或資料庫資料表並寫入 DataFrame
    #Read SQL query or database table into a DataFrame
    data=pd.read_sql(A,cnxn)
    info=pd.read_sql(B,cnxn)
    
    #利用指標準備並執行 SQL 指令
    #Prepares and executes SQL
    cursor.execute(A)
    
    #取得所有資料
    exdata=cursor.fetchall()
    
    #利用指標準備並執行 SQL 指令
    #Prepares and executes SQL
    cursor.execute(B)
    
    #取得所有資料
    parameter=cursor.fetchall()
    global _parameter;
    _parameter = parameter;
    
    #(運算過程中用不到，純粹檢核用)
    #參考文件:https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
    #將 DataFrame 載入 pandas
    #A=pd.DataFrame(data)
    #將資料匯出成 Excel 檔案
    #datatoexcel=pd.ExcelWriter("FromPython.xlsx",engine='xlsxwriter')
    #A.to_excel(datatoexcel, sheet_name='Sheet1') 
    #datatoexcel.save()
    
    #(運算過程中用不到，純粹檢核用)
    #參考文件:https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
    #將 DataFrame 載入 pandas
    #B=pd.DataFrame(info)
    #將資料匯出成 Excel 檔案
    #datatoexcel=pd.ExcelWriter("FromPython2.xlsx",engine='xlsxwriter')
    #B.to_excel(datatoexcel, sheet_name='Sheet1') 
    #datatoexcel.save()
    
    #建立一個 Element 均為 None 且數量剛好是查詢結果資料數量的矩陣
    count=[None]*len(exdata)
    
    #print("資料列共:" + str(count));
    
    #range(start, stop[, step])
    for m in range(0,(len(exdata)-1)):
        if exdata[m+1][2]!=exdata[m][2]:
            count[m]=m
      
    #print("資料列共:" + str(count));
        
    count[(len(exdata)-1)]=len(exdata)-1
    count=list(filter(None,count))
    
    count2=[None]*len(parameter)*2
    
    #range(start, stop[, step])
    for n in range(0,(len(parameter))):
        count2[2*n+1]=count[n]
    
    #range(start, stop[, step])
    for n in range(1,len(parameter)):
        count2[2*n]=count[n-1]+1
    
    count2[0]=0
    
    #存取全域變數
    global _count;
    _count = count;
    
    count3=[None]*len(parameter)
    
    #range(start, stop[, step])
    ###############################################################################
    for n in range(0,len(parameter)):
        count3[n]=range(count2[2*n],count2[2*n+1]+1) 
    
    time=[None]*len(parameter)
    ###############################################################################
    
    #range(start, stop[, step])
    ###############################################################################
    for n in range (0,(len(parameter))):
        time[n]=[None]*(count2[2*n+1]-count2[2*n]+1)
    
    time=np.array(time)
    ###############################################################################
    
    #range(start, stop[, step])
    ###############################################################################
    for n in range(0,len(parameter)):
        for m in count3[n]:
            exdata[m][3]=float(exdata[m][3])
            time[n][count3[n].index(m)]=exdata[m][3]
    
    value=[None]*len(parameter)
    ###############################################################################
    
    #range(start, stop[, step])
    ###############################################################################
    for n in range (0,(len(parameter))):
        value[n]=[None]*(count2[2*n+1]-count2[2*n]+1)
    
    value=np.array(value)
    ###############################################################################
    
    for n in range(0,len(parameter)):
        for m in count3[n]:
            exdata[m][4]=float(exdata[m][4])
            value[n][count3[n].index(m)]=exdata[m][4]
    
    #設定變數值
    IDlist=[None]*len(parameter)
    eshtotallist=[None]*len(parameter)
    datalist=[None]*len(parameter)
    NOmixture=0
    NOdatapoint=0
    N=len(parameter)
    ndlist=[0]*len(parameter)
    nklist=[None]*len(parameter)
    wijlist=[None]*len(parameter)
    nwlist=[None]*len(parameter)
    wijOij=[None]*len(parameter)
    wijCijOij=[None]*len(parameter)
    Ojlist=[None]*len(parameter)
    wjlist=[None]*len(parameter)
    wj2list=[None]*len(parameter)
    fjlist=[0]*6
    nlist=[0]*6
    Fjlist=[0]*6
    Milist=[0]*6
    Mitemp=[0]*6
    Oilist=[0]*6
    Oitemp=[0]*6
    Vilist=[0]*6
    Vitemp=[0]*6
    Ojlist_G=[0]*7
    Ojtemp=[0]*7
    RMSjlist=[0]*7
    RMSjtemp=[0]*7
    nGlist=[0]*7
    FCEB=0
    MCEB=0
    VCEB=0
    NCEB=0
    Obar=0
    RMSbar=0
    wG=0
    NG=0
    
    data=[None]*len(parameter)
    
    #range(start, stop[, step])
    ###############################################################################
    for n in range(0,len(parameter)):
        data[n]=[None]*24
    ###############################################################################
    
    #range(start, stop[, step])
    ###############################################################################
    for n in range(0,len(parameter)):
        fc=parameter[n][35]
        fc=float(fc)
    
        wc=parameter[n][9]
        wc=float(wc)
    
        c=parameter[n][11]
        c=float(c)
        ac=parameter[n][10]
        ac=float(ac)
    
        vs=parameter[n][42]
        vs=float(vs)*2
    
        RH=parameter[n][48]
        RH=RH.replace("%", "")
        RH=float(RH)
    
        tp=parameter[n][44]
        t0=parameter[n][44]
        
        cement=parameter[n][53]
        curing=parameter[n][54]
    
        SiO2=parameter[n][18]
        SiO2=float(SiO2)
        FlyAsh=parameter[n][19]
        FlyAsh=float(FlyAsh)
        Slag=parameter[n][20]
        Slag=float(Slag)
        SG=(c*Slag/100/(1-FlyAsh/100))/(1-Slag/100/(1-FlyAsh/100))
        F=(c*FlyAsh/100/(1-Slag/100))/(1-FlyAsh/100/(1-Slag/100))
        c=c+SG+F
        geo=parameter[n][55]
        
        T=parameter[n][46]
        Tcur=parameter[n][45]
    
        t=time[n]
        t=np.array(t)
        exvalue=value[n]
        ID=parameter[n][2]
        IDlist[n]=ID
    
        Kh=Kh_cal(RH)
        Ks=Ks_cal(geo)
        BTh=BTh_cal(Tcur)
        BTs=BTs_cal(T)
        t0=t0*BTh
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
    
        ktaua=2.3
        kea=1.6
    
        if Slag==0 and FlyAsh==0:
            faucem=1
            fauwc=1
            fshcem=1
            fshtau=1
        elif Slag>0 and FlyAsh==0:
            faucem=0.75
            fauwc=0.2
            fshcem=1
            fshtau=0.9
        elif Slag==0 and FlyAsh>40:
            faucem=0.5
            fauwc=0.1
            fshcem=0.8
            fshtau=2.0
        elif Slag==0 and FlyAsh<=40:
            faucem=0.5
            fauwc=0.1
            fshcem=1
            fshtau=1.5
        elif Slag>0 and FlyAsh>0:
            faucem=0.6
            fauwc=0.1
            fshcem=1.26
            fshtau=1.1
    #calculation starts here-------------------------------------------------------
    
        tau0=tau0_cal(ac,wc,c,taucem,ptaua,ptauw,ptauc)
        taush=taush_cal(vs,Ks,ktaua,tau0)
        e0=e0_cal(ac,wc,c,ecem,pea,pew,pec)
    
        E28=E28_cal(fc)
        global _E28;
        _E28 = E28;
        E607_m=E_cal(7*BTh+600*BTs)
        Et0_taush_m=E_cal(t0wave+taush*BTs)
        esh8=esh8_cal(e0,kea,E607_m,Et0_taush_m)
    
    #arraying
    
        t0_array=np.array([t0]*len(t))
        tp_array=np.array([tp]*len(t))
        taush_array=np.array([taush]*len(t))
    
        t0wave_array=np.array([t0wave]*len(t))
        twave_array=(t)*BTs
        S=np.array(S_cal(twave_array,taush,fshtau))
        esh=esh_cal(esh8,S,Kh,fshcem)*1000000
        eau8=eau8_cal(ac,wc,eaucem,faucem,gamaea,gamaew,fauwc)
        #print eau8
        tauau=tauau_cal(wc,gamatauw,tauaucem)
        tauau_array=np.array([tauau]*len(t))
        Bas=np.array(Bas_cal(twave_array,t0wave_array),dtype=float)
        eau=eau_cal(eau8,Bas)*1e6
        #print eau
        eshtotal=np.abs(esh+eau-eau[0])
        #print esh
    
        exvalue=np.abs(exvalue)
       
        plot.scatter(exvalue,eshtotal,c='b')
           
        eshtotallist[n]=eshtotal
        datalist[n]=exvalue
        #預設環境會出現警告訊息
        plot.axes().set_aspect('equal', adjustable='box')
        plot.xlim(0,1200)
        plot.ylim(0,1200)
    ###############################################################################
    
    eshtotallist2=[]
    
    #range(start, stop[, step])
    ###############################################################################
    for n in range(0,len(parameter)):
        if sum(eshtotallist[n])>0:
            eshtotallist2.extend(eshtotallist[n])
    ###############################################################################
    
    datalist2=[]
    
    #range(start, stop[, step])
    ###############################################################################
    for n in range(0,len(parameter)):
        if sum(datalist[n])>0:
            datalist2.extend(datalist[n])
    ###############################################################################
    
    average=sum(datalist2)/len(datalist2)
    SST=sum((np.array(datalist2)-average)**2)
    SSR=sum((np.array(datalist2)-np.array(eshtotallist2))**2)
    Rsquare=1-SSR/SST
    global _Rsquare;
    _Rsquare = Rsquare;
   
## 參數1:圖片檔案名稱
## 參數2:查詢條件1
## 參數3:查詢條件2
if __name__== "__main__":
    db_conn(username, password, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8]);