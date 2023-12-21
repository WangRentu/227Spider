#-*- codeing = utf-8 -*-

from bs4 import BeautifulSoup     #网页解析，获取数据
import re       #正则表达式，进行文字匹配
import urllib.request,urllib.error      #制定URL，获取网页数据
import xlwt     #进行excel操作
import xlrd     #进行excel操作
import pymysql  #进行SQLite数据库操作
import pandas
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.faker import Faker


#影片片名
findTitle = re.compile(r'<div class="rvi__tit1" data-v-e4a51846="" title="(.*?)">')
#找到评价人数
findJudge = re.compile(r'<span class="rvi__tag rvi__tag1" data-v-e4a51846="" style="display:;">(\d+(.\d+)?)万人评分</span>')
#找到影片信息
findInfo = re.compile(r'<div class="rvi__type1" data-v-e4a51846="" style="display:;" title="(.*?)">(.*?)</div>', re.S)
#找到剧情概要
findStory = re.compile(r'<p class="rvi__des2" data-v-e4a51846="" title="(.*?)">(.*?)</p>', re.S)
#影片评分
findRating = re.compile(r'<span class="rvi__index__num" data-v-e4a51846="">(\d\.\d)?</span>')
#信息分割
findCut = re.compile(r'(\d{4}) / (.*?) / (.*)')



def main():
    url = "https://www.iqiyi.com/ranks1/1/-4"
    #1.爬取网页
    #datalist = getData(url)
    #savepath = "爱奇艺电影Top25.xls"
    dbpath = "爱奇艺电影Top25"
    #3.保存数据
    #saveDatatoExcel(datalist,savepath)
    #washData(savepath)
    datalist = []
    savepath = "爱奇艺电影Top25-处理后.xls"
    with xlrd.open_workbook(savepath) as book:
        sheet = book.sheet_by_name("爱奇艺电影Top25-处理后")
        for i in range(1, sheet.nrows):
            datalist.append(sheet.row_values(i))
    #saveDatatoDatabase(datalist,dbpath)
    

    #askURL("https://movie.douban.com/Top100?start=")





#爬取网页
def getData(url):
    datalist = []
    html = askURL(url)      #保存获取到的网页源码

     # 2.逐一解析数据
    soup = BeautifulSoup(html,"html.parser")
    for item in soup.find_all('div',class_ = "rvi__con"):     #查找符合要求的字符串，形成列表
        #print(item)   #测试：查看电影item全部信息
        data = []    #保存一部电影的所有信息
        item = str(item)

        title = re.findall(findTitle, item)[0]
        data.append(title)  # 提加电影名

        judgeNum = float(re.findall(findJudge, item)[0][0])
        data.append(judgeNum)  # 提加评价人数

        info = re.findall(findInfo, item)[0][0]
        data.append(info)  # 提加信息

        story = re.findall(findStory, item)[0][0]
        data.append(story)  # 提加剧情概要

        datalist.append(data)       #把处理好的一部电影信息放入datalist

    count = 0
    for item in soup.find_all('div',class_ = "rvi__right"):
        item = str(item)
        rate = float(re.findall(findRating, item)[0])
        datalist[count].append(rate)  # 提加评分
        count += 1

    return datalist



#得到指定一个URL的网页内容
def askURL(url):
    head = {                #模拟浏览器头部信息，向爱奇艺服务器发送消息
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }
                            #用户代理，表示告诉爱奇艺服务器，我们是什么类型的机器、浏览器（本质上是告诉浏览器，我们可以接收什么水平的文件内容）

    request = urllib.request.Request(url,headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html




#保存数据
def saveDatatoExcel(datalist,savepath):
    print("save....")
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)  #创建workbook对象
    sheet = book.add_sheet('爱奇艺电影Top25',cell_overwrite_ok=True)    #创建工作表
    col = ("影片名称","评价人数（万）","影片信息","剧情概要","评分")
    for i in range(5):
        sheet.write(0,i,col[i]) #列名
    for i in range(len(datalist)):
        data = datalist[i]
        for j in range(5):
            sheet.write(i+1,j,data[j])      #数据

    book.save(savepath)       #保存


def saveDatatoDatabase(datalist,dbpath):
    init_db(dbpath)
    conn = pymysql.connect(host='localhost', user='root', password='4227', database=dbpath, port=3306)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index == 1 or index == 2 or index == 3:
                continue
            data[index] = data[index].join(['"', '"'])
        sql = '''
                insert into aqyTop25 (
                name,judges,score,year,types,actors,story) 
                values(%s, %f, %f, %d, %s, %s, %s)''' % (data[0], data[1], data[2], data[3], data[4], data[5], data[6])
        print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()

def init_db(dbpath):
    sql = '''
        CREATE TABLE IF NOT EXISTS aqyTop25 
        (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        judges DOUBLE,
        score DOUBLE,
        year INT,
        types VARCHAR(255),
        actors VARCHAR(255),
        story TEXT
        )
    '''  #创建数据表
    conn = pymysql.connect(host='localhost', user='root', password='4227', database=dbpath, port=3306)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

def washData(savepath):
    with xlrd.open_workbook(savepath) as book:
        sheet = book.sheet_by_name('爱奇艺电影Top25')
        newBook = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建workbook对象
        newSheet = newBook.add_sheet('爱奇艺电影Top25-处理后', cell_overwrite_ok=True)  # 创建工作表
        for i in range(2):
            col = sheet.col(i)
            for j in range(len(col)):
                newSheet.write(j, i, col[j].value)
        col = sheet.col(4)
        for j in range(len(col)):
            newSheet.write(j, 2, col[j].value)
        col = sheet.col(3)
        for j in range(len(col)):
            newSheet.write(j, 6, col[j].value)
        newSheet.write(0, 3, '年份')
        newSheet.write(0, 4, '类型')
        newSheet.write(0, 5, '演员')
        col = sheet.col(2)
        for i in range(1, len(col)):
            info = col[i]
            infotpl = re.findall(findCut, info.value)[0]
            newSheet.write(i, 3, float(infotpl[0]))
            newSheet.write(i, 4, '、'.join(infotpl[1].split()))
            newSheet.write(i, 5, '、'.join(infotpl[2].split()))
        newBook.save("爱奇艺电影Top25-处理后.xls")





if __name__ == "__main__":          #当程序执行时
#调用函数
    main()
    #init_db("movietest")
    print("爬取完毕！")