import requests
import parsel
import csv

f = open('二手房.csv', mode='w', encoding='utf-8',newline='')
csv_writer = csv.DictWriter(f, fieldnames=[
      '标题',
      '售价',
      '单价',
      '小区',
      '商圈',
      '户型',
      '面积',
      '朝向',
      '装修',
      '楼层',
      '建筑结构',
      '日期',
])
csv_writer.writeheader()
#模拟地址
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
#请求连接
for page in range(1, 11):
    print(f'============正在采集第{page}页的数据内容============')
    url = f'https://jn.lianjia.com/ershoufang/pg{page}/'
    #发送请求
    response = requests.get(url=url, headers=headers)
    print(response)
    #获取相应文本数据
    html_data = response.text
    #转换html
    selector = parsel.Selector(html_data)
    #提取前30条
    divs = selector.css('.sellListContent li .info')
    #for循环遍历
    for div in divs:
        #提取具体数据
        title = div.css('.title a::text').get()  # 标题
        totalPrice = div.css('.priceInfo .totalPrice span::text').get()  # 售价
        unitPrice = div.css('.priceInfo .unitPrice::attr(data-price)').get()  # 单价
        area_info = div.css('.flood .positionInfo a::text').getall()  # 区域
        area = area_info[0]  # 小区
        area_1 = area_info[-1]  # 商圈
        houseInfo = div.css('.address .houseInfo::text').get().split(' | ')
        houseType = houseInfo[0]  # 户型
        houseArea = houseInfo[1].replace('平米','')  # 面积
        face = houseInfo[2]  # 朝向
        fitment = houseInfo[3]  # 装修
        fool = houseInfo[4]  # 楼层
        building = houseInfo[-1]  # 建筑
        if len(houseInfo) == 7:
            date = houseInfo[5]  # 日期
        else:
            date = '暂无数据'
        dit = {
           '标题': title,
           '售价': totalPrice,
           '单价': unitPrice,
           '小区': area,
           '商圈': area_1,
           '户型': houseType,
           '面积': houseArea,
           '朝向': face,
           '装修': fitment,
           '楼层': fool,
           '建筑结构': building,
           '日期': date,
        }
        csv_writer.writerow(dit)
        print(dit)
#创建文件对象
from sqlalchemy import create_engine
import pandas as pd
engine = create_engine('mysql+pymysql://root:zhang20040127@localhost/db_test')
df = pd.read_csv('二手房.csv')
df.to_sql(name='second',con=engine,index=False,if_exists='replace')



import jieba
from wordcloud import WordCloud

# 假设 df['标题'] 已经被正确加载
houseHot = df['标题'].values.tolist()
Hotstr = ' '.join(houseHot)
jieba_text = " ".join(jieba.lcut(Hotstr))
stopwords = ['品牌', '环境', '向', '住', '适合', '业主', '宽', '公司', '好', '小区']

wc = WordCloud(
    scale=5,
    margin=0,
    background_color="black",
    max_words=1200,
    width=800,
    height=450,
    font_path='C:\\Users\\lenovo\\Desktop\\优设标题黑.ttf',
    stopwords=stopwords,
    random_state=800
)

wc.generate_from_text(jieba_text)
wc.to_file('词云图.png')
# 显示生成的词云图
image = wc.to_image()
image.show()
