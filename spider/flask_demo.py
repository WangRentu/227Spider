from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# 数据库配置（根据您的设置更改）
DATABASE_URI = 'mysql+pymysql://root:031716@localhost/db_test'

@app.route('/')
def index():
    # 创建数据库连接
    engine = create_engine(DATABASE_URI)
    # 读取数据
    df = pd.read_sql('SELECT * FROM second', con=engine)
    # 将数据转换为HTML表格
    return df.to_html()

if __name__ == '__main__':
    app.run(debug=True)
