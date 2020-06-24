from flask import Flask,request,make_response,render_template,views
from flask_restful import  Api, Resource
import mongo_client_two
import json
import time
import os
from pathlib import Path
import hashlib
app = Flask(__name__)
app.config["SECRET_KEY"] = "123456"
from dotenv import load_dotenv,find_dotenv
# 一、自动搜索 .env 文件
load_dotenv(verbose=True)
# 二、与上面方式等价
load_dotenv(find_dotenv(), verbose=True)

# 三、或者指定 .env 文件位置
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, verbose=True)
db_name = os.getenv('DB_NAME')
account_name = os.getenv('ACCOUNT_NAME')
api = Api(app)#路由设置
class api_new(Resource):#接口
        def post(self):
               data = json.load(request.get_data())#获取body中的数据，降json格式转化为字典格式
               num = ['aaa','bbb','ccc']
               '''
                    
               {
           "aaa": "111111", // 必需参数
           "bbb": "222222", // 必需参数
           "ccc": "333333", // 必需参数
           "ddd": "444444" // 可选参数
               }
              
               '''
               for x in num:
                   if data.get(x) == None:#检验传入的参数是否存在以上的必须字段
                      return '该参数不存在必须在段{}'.format(x),404
               db = mongo_client_two.client[db_name]
               account = db[account_name]
               ac = account.find_one({'aaa': data.get('aaa')})
               if ac:
                   if data.get('aaa') == account.find_one({'aaa': data.get('aaa')})['aaa']:
                       print(1)
                       account.update_one(account.find_one({'aaa': data.get('aaa')}), {"$set": data})
                   else:
                       account.insert_one(data)
               else:
                   account.insert_one(data)
        def get(self):
            return make_response(render_template('hello.html'))
api.add_resource(api_new,'/api/database/foo/bar/')#注册路由
class jiekou(Resource):
      def get(self,sign,*args,**kwargs):
             '''

             本次演示过程 实现从get开始，先从url获取api数据（例如我给的sign签名）
             从网页cookie中获取用户人的信息(例如姓名：username)(request.cookies.get('name'))(获取登陆页面的用户人姓名)
             sign转化成MD5
             用户名测试过程，由于没有登陆界面，就自己创建一个用户名（zhangsan）
             添加时间，以便后面检验
             数据库存入{username:{sign:md5,
             time:time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}}数据
             '''
             username = 'zhangsan'#测试过程设置用户名
             md5 =hashlib.md5(str(sign).encode(encoding='UTF-8')).hexdigest()
             db_two = os.getenv('DB_NAME_TWO')
             db_two = mongo_client_two.client[db_two]
             account_two = db_two['md5']#存放在sign，MD5数据努中
             account_two.insert({'name':username,str(sign):md5,
             'time':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})
             return make_response(render_template('hello.html',sign=sign,md5=md5))
      def post(self,sign,*args,**kwargs):
             '''
            其次从post过来获取body里面的数据（request.json()）-------本次采用从表格的演示形式（request.form.get）
            将获取到的数据（例如：username）MD5
            获取时间（import time）
            time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            数据库查询（account.find_one({username:MD5})）
            如果找到了，返回相应的页面
            反之返回错误信息，以及状态码
            当找到了，对应删除相关的数据，防止被后者恶意使用
            网址链接：https://blog.saintic.com/blog/241.html
            验证方式：
            1  验证时间戳是否有效(小于等于服务器时间戳且在30s之内请求有效)（MD5的加密时间戳）
            从数据库里面的time里判断
            2  验证accesskey_id是否有效
            验证cookie数据获取的username是否存在数据库里面
            3  验证签名
            验证sign签名的MD5码是否符合
             '''
             username = str(request.form.get('username'))
             db_two = os.getenv('DB_NAME_TWO')
             db_two = mongo_client_two.client[db_two]
             account_two = db_two['md5']
             md5 = hashlib.md5(username.encode(encoding='UTF-8')).hexdigest()
             ac = account_two.find_one({'name':username})
             time_api = 0#记录相隔日期
             if ac:#如果存在该用户
                time_old = ac['time']#获取时间
                time_new = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))#获取当前时间
                time_old = time_old.split('-')
                time_new = time_new.split('-')#测试过程设定保存的日期为7天,并将他们相隔日期定义为time_api变量
                if time_new[0]==time_old[0]:
                   if time_new[1]!=time_old[1]:#如果不在同一月份
                      time_api = int(time_new[1])+30-int(time_old[1])
                      if time_api<=7:
                          if ac[sign]==md5:
                              account_two.remove(ac)#防止恶意使用
                              return make_response(render_template('hello.html', sign='yes', md5=123))
                          else:
                              return make_response(render_template('hello.html'),404)
                      else:
                          return make_response(render_template('login.html'), 404)
                   else:
                       time_api = int(time_new[1])-int(time_old[1])
                       if time_api<=7:
                          if ac[sign]==md5:
                              account_two.remove(ac)  # 防止恶意使用
                              return make_response(render_template('hello.html', sign='yes', md5=123))
                          else:
                              return make_response(render_template('hello.html'),404)
                       else:
                           return make_response(render_template('login.html'), 404)
                else:
                    return make_response(render_template('login.html'),404)
api.add_resource(jiekou,'/api/<int:sign>/')
if __name__ =='__main__':
    app.run(debug=True)