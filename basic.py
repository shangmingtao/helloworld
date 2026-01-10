# import sys
# age = 25                # 普通变量名，最常见
# user_name = "Alice"     # 用下划线连接单词，清晰易读
# _total = 100            # 下划线开头通常表示“内部使用”或“私有”
# MAX_SIZE = 1024         # 全大写通常表示“常量”（固定不变的值）
# # calculate_area()        # 函数名，动词+名词
# # StudentInfo             # 类名，首字母大写（驼峰命名法）
# # __private_var           # 双下划线开头，有特殊含义
#
#
# 姓名 = "张三"  # 合法
# π = 3.14159   # 合法
#
#
# def is_valid_identifier(name):
#     try:
#         exec(f"{name} = None")
#         return True
#     except:
#         return False

# print(True and False)  # False
# print(is_valid_identifier("var2"))  # True

# total = ['item_one', 'item_two', 'item_three',
#         'item_four', 'item_five']
#
# name = """ab
#         cd
#         ef"""

# str = '123456789'
#
# print(str)  # 输出字符串
# print(str[0:-1])  # 输出第一个到倒数第二个的所有字符
# print(str[0])  # 输出字符串第一个字符
# print(str[2:5])  # 输出从第三个开始到第六个的字符（不包含）
# print(str[2:])  # 输出从第三个开始后的所有字符
# print(str[1:5:2])  # 输出从第二个开始到第五个且每隔一个的字符（步长为2）
# print(str * 2)  # 输出字符串两次
# print(str + '你好')  # 连接字符串
#
# print('------------------------------')
#
# print('hello\nrunoob')  # 使用反斜杠(\)+n转义特殊字符
# print(r'hello\nrunoob')  # 在字符串前面添加一个 r，表示原始字符串，不会发生转义


# x = 'runoob'; sys.stdout.write(x + '\n')

# x = "a"
# y = "b"
# # 换行输出
# print(x)
# print(y)
#
# print('---------')
# # 不换行输出
# print(x, end=" ")
# print(y, end=" ")
# print()

# import sys
# print('================Python import mode==========================')
# print ('命令行参数为:')
# for i in sys.argv:
#     print (i)
# print ('\n python 路径为',sys.path)

# a, b, c, d = 20, 5.5, True, 4+3j
# print(type(a), type(b), type(c), type(d))
# print(isinstance(a, int))
# print(type(a))

'''
a = 7
b = a
print(a, end=" ")
print(b, end=" ")
# print(a); print(b)
# del b; print(b)
'''

# a = 7
# a = 8
# print(a, end=" ")
# number = 10
# text = "这是一个数字：" + str(number)
# print(text)

#
# def change(a):
#     print('第一次%s' + str(a))
#     a = 10
#     print('第二次%s' + str(a))
#     return a
#
# a = 5
# print(change(a))
# print('第三次%s' + str(a))

# numbers = [1, 2, 3, 4, 5]
# squared = list(map(lambda x: x**2, numbers))
# print(squared)  # 输出: [1, 4, 9, 16, 25]
# print(map(lambda x: x**2, numbers))


# numbers = [1, 2, 3, 4, 5]
# abc = lambda x, y: x * y
# print(abc(2,3))


def my_decorator(func):
    def wrapper():
        print("在原函数之前执行")
        func()
        print("在原函数之后执行")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()