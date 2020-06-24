import os
from dotenv import load_dotenv,find_dotenv
from pymongo import MongoClient
from pathlib import Path
# 一、自动搜索 .env 文件
load_dotenv(verbose=True)


# 二、与上面方式等价
load_dotenv(find_dotenv(), verbose=True)

# 三、或者指定 .env 文件位置
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, verbose=True)
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
account_name = os.getenv('ACCOUNT_NAME')
client = MongoClient(db_host,27017)