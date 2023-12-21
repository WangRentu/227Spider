import requests
# 模拟浏览器

import parsel
'''返回选择器对象'''

# 导入csv模块保存数据
import csv

# 数据库驱动
from sqlalchemy import create_engine
import pandas as pd

f = open('二手房.csv',mode='w',encoding='utf-8',newline='')
csv_writer = csv.DictWriter(f,fieldnames=[
        '标题',
        '小区',
        '区域',
        '总价',
        '单价',
        '户型',
        '面积',
        '朝向',
        '装修',
        '楼层',
        '年份',
        '建筑'
])

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}
for page in range(1,10):
    print(f"==================================正在搜索第{page}页内容==========================================")
    # 请求连接
    url = (f'https://cs.lianjia.com/ershoufang/pg{page}/')
    '''发送请求'''
    response = requests.get(url = url,headers = headers)
    # 相应对象
    '''<Response [200]>'''
    print(response)

    '''获取数据'''
    html_data = response.text
    print(html_data)


    # 把获取的html字符串数据，转换成可解析对象

    '''解析数据'''
    selector = parsel.Selector(html_data)
    # 第一次提取 提取30个房源对应的div标签
    divs = selector.css('.sellListContent li .info')

    for div in divs:
        # 第二次提取 提取具体标签内容
        title = div.css('.title a::text').get() # 获取标题
        area_list = div.css(".positionInfo a::text").getall()
        area = area_list[0] # 小区
        area_1 = area_list[1] # 区域
        total_price = div.css(".totalPrice span::text").get() # 总价
        unit_price = div.css(".unitPrice span::text").get() # 单价
        house_info = div.css(".houseInfo ::text").get().split(' | ') # 信息
        houseType = house_info[0]
        houseArea = house_info[1]
        face = house_info[2]
        house = house_info[3]
        fool = house_info[4]
        building = house_info[-1]  # 建筑
        if len(house_info):
            data = house_info[5]
        else:
            data = '未知'
        dict = {
            '标题': title,
            '小区': area,
            '区域': area_1,
            '总价': total_price,
            '单价': unit_price,
            '户型': houseType,
            '面积': houseArea,
            '朝向': face,
            '装修': house,
            '楼层': fool,
            '年份': data,
            '建筑': building
        }
        csv_writer.writerow(dict)
        print(dict)
# 创建数据库连接
engine = create_engine('mysql+pymysql://root:031716@localhost/db_test')
# csv -> 数据库
df = pd.read_csv('二手房.csv')
df.to_sql(name='ershoufang',con = engine,index = False,if_exists='replace')