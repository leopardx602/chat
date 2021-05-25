import pymysql
import charts
from plot import plot, plotasync, line, area, spline, pie
import traceback
# 資料庫參數設定
db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "lisa1219",
    "db": "test01",
    "charset": "utf8"
}

try:
    conn = pymysql.connect(**db_settings)
except:
    traceback.print_exc()
