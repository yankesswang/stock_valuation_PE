
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

#"零售":{"LULU","GPS","COST","PG","KR","JWN","NKE","DG","FL"}
# "航空郵輪":{"AAL","LUV","DAL","UAL","BA","CCL","RCL"},"銀行":{"BAC","JPM","GS","C","WFC","BLK"},
# "傳統":{"DIS","CAT","GE","MMM","WM","ETN","ISRG","UNH","ABBV","CVS"},"支付":{"MA","V","PYPL","AXP"}
# ,"食品":{"MCD","SBUX","KO","PEP","CMG","YUM"},"半導體":{"TSM","AMD","QCOM","MU","INTC","ASML"}} 
company ={"大科技":{"GOOG","META","AMZN","NFLX","AAPL","MSFT"}}

ind = [17,0,1,2,3,5,4,6,7,8,9,10,11,12,14,13,16,15,18,19,20]
col = ["市值","本季", "下一季", "本年度","下一年","後五年","前五年","預估PE","23年EPS","23年合理價","24年EPS","24年合理價","五年PE MIN"
,"五年PE MEDIAN","五年PE MAX","五年PE最低價","五年PE中位價","五年PE最高價","股價","估值","相差百分比"]

f = pd.DataFrame()
ser = pd.Series(col,index = ind)
f["股票代號"] = ser

headers ={
            "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

for industry,company_group in company.items():
    
    for company_name in company_group:

        #從yahoo fiance抓取數據
        web = "https://hk.finance.yahoo.com/quote/" +company_name + "/analysis?p=" +company_name #從Yahooo Finance抓取23年和24年EPS
        res = requests.get(web, headers = headers)
        res.encoding = ("utf-8")
    
        soup = BeautifulSoup(res.text, 'html.parser')
        data = soup.select_one('#Col1-0-AnalystLeafPage-Proxy')

        dfs = pd.read_html(data.prettify())
        earning_23 = dfs[0]["本年度  (2023)"][2]
        earning_24 = dfs[0]["下一年  (2024)"][2] #從Yahooo Finance抓取分析師預期增長率
        
        stock = pd.DataFrame((dfs[5])[["預計增長", company_name]], index = ind)
        
        stock = stock.rename(columns={"預計增長":"股票代號"})

        stock.loc[4, "股票代號"]="後五年"     
        stock.loc[5, "股票代號"]="前五年"

        stock.loc[6, "股票代號"] = "預估PE"
        stock.loc[6, company_name] = round(float(stock.loc[4, company_name].replace("%","")) *2)

        stock.loc[7, "股票代號"] = "23年EPS" 
        stock.loc[7, company_name] = float(earning_23)  

        stock.loc[8, "股票代號"] = "23年合理價"     #價值=23年EPS*PE中位數
        stock.loc[8, company_name] = round(stock.loc[7, company_name] * stock.loc[6, company_name])

        stock.loc[9, "股票代號"] = "24年EPS"
        stock.loc[9, company_name] = float(earning_24) 

        stock.loc[10, "股票代號"] = "24年合理價"  
        stock.loc[10, company_name] = round(stock.loc[9, company_name] * stock.loc[6, company_name])
        

        web1 = "https://ycharts.com/companies/"+company_name+"/pe_ratio" #從ychart抓取公司過去五年度avg and median PE
        res1 = requests.get(web1, headers = headers)
        res1.encoding = ("utf-8")
        soup1 = BeautifulSoup(res1.text, 'html.parser')
        data1 = soup1.select(".key-stat")

        string = "".join([data1[i].getText() for i in range(len(data1))]).replace(" ", "")
        num = re.findall('-?\d+\.?\d*', string)
        PE_group = list(map(lambda x: round(float(x)), num))
        PE_group = [x for x in PE_group if len(str(x)) <= 4] #爬取過去五年公司PE數據


       
        stock.loc[11, "股票代號"] = "五年PE MIN"
        stock.loc[11, company_name] = PE_group[0]

        stock.loc[12, "股票代號"] = "五年PE MAX"
        stock.loc[12, company_name] = PE_group[1]

        stock.loc[13, "股票代號"] = "五年PE MEDIAN"
        stock.loc[13, company_name] = PE_group[3]

        stock.loc[14, "股票代號"] = "五年PE最低價"
        stock.loc[14, company_name] = round(stock.loc[11, company_name]*stock.loc[7, company_name])

        stock.loc[15, "股票代號"] = "五年PE最高價"
        stock.loc[15, company_name] = round(stock.loc[12, company_name]*stock.loc[7, company_name])
    
        stock.loc[16, "股票代號"] = "五年PE中位價"
        stock.loc[16, company_name] = round(stock.loc[13, company_name]*stock.loc[7, company_name])


        web2 = "https://hk.finance.yahoo.com/quote/"+company_name+"?p="+company_name+"&.tsrc=fin-srch"
        res2 = requests.get(web2, headers = headers)
        res2.encoding = ("utf-8")

        soup2 = BeautifulSoup(res2.text, 'html.parser') #抓取股票的市值和股價
        data2 = soup2.select_one('#quote-summary')
        dfs2 = pd.read_html(data2.prettify())

        stock.loc[17, "股票代號"]= "市值"
        stock.loc[17, company_name] = dfs2[1][1][0]
        stock.loc[18, "股票代號"] = "股價"
        stock.loc[18, company_name] = float(dfs2[0][1][0])

        stock.loc[19, "股票代號"] = "股價與估值比較"
        if stock.loc[18, company_name] > stock.loc[16, company_name]:  #與現有股價進行比對，檢視股票為高估或是低估
            stock.loc[19, company_name] = "高估"
        else:
            stock.loc[19, company_name] = "低估"

        stock.loc[20, "股票代號"] = "相差百分比"   #計算股價高估或低估的百分比
        stock.loc[20, company_name] = str(round(100*(stock[company_name][16]- stock[company_name][18])/stock[company_name][16]))+"%"
    
        f= pd.merge(f,stock) #把每家公司的資料合併

        
        
    file = industry+"23年 PE估值表.csv"  #將所有資料整合為csv檔輸出
    f.to_csv(file, encoding='big5')
    print(f)
    


