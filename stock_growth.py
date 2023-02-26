# #抓取網頁原始碼
# import urllib.request as req
# url = "https://www.ptt.cc/bbs/movie/index.html"

# #建立一個requset物件，附加requset header資訊
# request = req.Request(url, headers ={
#     "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
# })

# with req.urlopen(request) as response:
#     data = response.read().decode("uft-8")
# print(data)

from bs4 import BeautifulSoup
import requests
import pandas as pd
import re






# headers ={
#         "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
#     }

# web = "https://hk.finance.yahoo.com/quote/" +"TSLA" + "/analysis?p=" +"TSLA"
# res = requests.get(web, headers = headers)
# res.encoding = ("utf-8")



# soup = BeautifulSoup(res.text, 'html.parser')
# data = soup.select_one('#Col1-0-AnalystLeafPage-Proxy')
# dfs = pd.read_html(data.prettify())
# second = dfs[0]["本年度  (2023)"][2]

# first = pd.DataFrame((dfs[5])[["stc", "TSLA"]], index = [0,1,2,3,5,4,6,7,8])
# first["stc"][4]="後五年"
# first["stc"][5]="前五年"
# first["stc"][6] = "23年EPS"
# first["TSLA"][6] = float(second)

# first["stc"][7] = "預估PE"
# first["stc"][8] = "23年合理價"

# first["TSLA"][7] = round(float(first["TSLA"][4].replace("%","")) *2)

# first["TSLA"][8] = round(first["TSLA"][7] * first["TSLA"][6])
# #print(first)

#  "NVDA",,"HD""WMT""UA"
# ,,,,"DPZ"
# ,,
# ,"高成長":{"U","PLTR","CRWD","SEA","SHOP","ZM","SNOW","ABNB"}

# 
# https://hk.finance.yahoo.com/quote/NVDA/analysis?p=NVDA
# 
# seq ={"大科技":{"GOOG","META","AMZN","NFLX","AAPL","MSFT"},"航空郵輪":{"AAL","LUV","DAL","UAL","BA","CCL","RCL"},"銀行":{"BAC","JPM","GS","C","WFC","BLK"},
# "傳統":{"DIS","CAT","GE","MMM","WM","ETN","ISRG","UNH","ABBV","CVS"},"支付":{"MA","V","PYPL","AXP"},"零售":{"LULU","GPS","COST","PG","KR","JWN","NKE","DG","FL"}
# ,"食品":{"MCD","SBUX","KO","PEP","CMG","YUM"},"半導體":{"TSM","AMD","QCOM","MU","INTC","ASML"}} 

ind = [17,0,1,2,3,5,4,6,7,8,9,10,11,12,14,13,16,15,18,19,20]
col = ["市值","本季", "下一季", "本年度","下一年","後五年","前五年","預估PE","23年EPS","23年合理價","24年EPS","24年合理價","五年PE MIN"
,"五年PE MEDIAN","五年PE MAX","五年PE最低價","五年PE中位價","五年PE最高價","股價","估值","相差百分比"]

seq ={"大科技":{"ABNB","ZM","SHOP","UBER","RBLX"}}

for key,value in seq.items():
    ser = pd.Series(col,index = ind)
    f = pd.DataFrame()
    f["股票代號"] = ser
   
    for ing in value:


        headers ={
            "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }

        web = "https://hk.finance.yahoo.com/quote/" +ing + "/analysis?p=" +ing
        res = requests.get(web, headers = headers)
        res.encoding = ("utf-8")
    

        soup = BeautifulSoup(res.text, 'html.parser')
        data = soup.select_one('#Col1-0-AnalystLeafPage-Proxy')
        dfs = pd.read_html(data.prettify())

        earning_23 = dfs[0]["本年度  (2023)"][2]
        earning_24 = dfs[0]["下一年  (2024)"][2]
        
        stock = pd.DataFrame((dfs[5])[["預計增長", ing]], index = ind)
        
        stock = stock.rename(columns={"預計增長":"股票代號"})

        stock["股票代號"][4]="後五年"
        stock["股票代號"][5]="前五年"

        stock["股票代號"][6] = "預估PE"
        stock[ing][6] = round(float(stock[ing][4].replace("%","")) *2)

        stock["股票代號"][7] = "23年EPS" 
        stock[ing][7] = float(earning_23)  

        stock["股票代號"][8] = "23年合理價"
        stock[ing][8] = round(stock[ing][7] * stock[ing][6])

        stock["股票代號"][9] = "24年EPS"
        stock[ing][9] = float(earning_24) 

        stock["股票代號"][10] = "24年合理價"  
        stock[ing][10] = round(stock[ing][9] * stock[ing][6])
        

        web1 = "https://ycharts.com/companies/"+ing+"/pe_ratio"
        res1 = requests.get(web1, headers = headers)
        res1.encoding = ("utf-8")

        soup1 = BeautifulSoup(res1.text, 'html.parser')
        data1 = soup1.select(".key-stat")

        string = " "
        for i in range(len(data1)):
            string += data1[i].getText()
        string= string.replace(" ","")

        num = re.findall('-?\d+\.?\d*',string)
        final =[]
        for i in range(len(num)):
            res = round(float(num[i]))
            if(len(str(res)) <= 4):
                final.append(res)
       

        stock["股票代號"][11] = "五年PE MIN"
        stock[ing][11] = final[0]

        stock["股票代號"][12] = "五年PE MAX"
        stock[ing][12] = final[1]

        

        stock["股票代號"][13] = "五年PE MEDIAN"
        stock[ing][13] = final[3]

        stock["股票代號"][14] = "五年PE最低價"
        stock[ing][14] = round(stock[ing][11]*stock[ing][7])

        stock["股票代號"][15] = "五年PE最高價"
        stock[ing][15] = round(stock[ing][12]*stock[ing][7])
    
        stock["股票代號"][16] = "五年PE中位價"
        stock[ing][16] = round(stock[ing][13]*stock[ing][7])


        web2 = "https://hk.finance.yahoo.com/quote/"+ing+"?p="+ing+"&.tsrc=fin-srch"
        res2 = requests.get(web2, headers = headers)
        res2.encoding = ("utf-8")



        soup2 = BeautifulSoup(res2.text, 'html.parser')
        data2 = soup2.select_one('#quote-summary')
        dfs2 = pd.read_html(data2.prettify())

        stock["股票代號"][17] = "市值"
        stock[ing][17] = dfs2[1][1][0]

        stock["股票代號"][18] = "股價"
        stock[ing][18] = float(dfs2[0][1][0])

        if stock[ing][18] > stock[ing][16]:
            tmp = "高估"
        else:
            tmp = "低估"

        stock["股票代號"][19] = "估值"
        stock[ing][19] = tmp

        stock["股票代號"][20] = "相差百分比"
        stock[ing][20] = str(round(100*(stock[ing][16]- stock[ing][18])/stock[ing][16]))+"%"
    
        
        f= pd.merge(f,stock)

        
        
    file = key+"23年 PE估值表.csv"
    f.to_csv(file, encoding='big5')
    print(f)
    


