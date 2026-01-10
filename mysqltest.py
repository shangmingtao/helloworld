import pymysql

# 打开数据库连接
db = pymysql.connect(
    host="t4ptuv8y87azk.oceanbase.aliyuncs.com",  # 数据库主机地址
    user="test_seal_stock",  # 数据库用户名
    passwd="test_seal_stock@2023", # 数据库密码
    database="test_seal_stock2"
)

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

# 使用 execute()  方法执行 SQL 查询
# print(cursor.execute("SELECT VERSION()"))
# print(cursor.execute("show tables;"))
# ta = cursor.execute("show tables;")
# for x in cursor:
#   print(x)

cursor.execute("SELECT name FROM gyl_t_base_organization  LIMIT 3")
myresult = cursor.fetchall()  # fetchall() 获取所有记录

for x in myresult:
    print(x)