#coding: utf-8
Pythonic 代码

1) a, b = b, a

2) age = config_dict.get(‘age’,  24)
可以省去好多事后判断工作。

3) 字符串合并
''.join(['age:', '45', 'job:', 'programer'])

4) with open(filename, ‘r’) as f:
	for line in f:
		do something

5) if name =="Tom" or name == "Dick" or name == "hary":
  用if name in ("Tom", "Dick", "Harry")代替

6）装饰器，简化一些代码前的判断
def Profile_view(request):
	if not check_is_logined(request):
		throw HTTP 401
		.....

def Setting_view(request):
	if not check_is_logined(request):
		throw HTTP 401
	.....

可以直接写个装饰器，处理登录的问题，让Profile_view，Setting_view只处理自己的事情，简化逻辑。

@check_is_logined_otherwise_throw
def Profile_view(request):
	....

7) 列表推导式简化 for 循环逻辑
nums = range(1, 100)
primes = []
for x in nums:
	if is_prime(x):
		primes.append(x)

用列表推导式：
nums = range(1, 100)
primes = [x for x im nums if is_prime(x)]

8) enumerate
index = 0
for x in li:
	print(index, x)
	index += 1

用enumerate：
for index, x in enumerate(li):
	print(index, x)

9) yield 语句
简化列表生成，惰性，省内存
def list_gen(arg):
	ls = []
	for i in ....
		ls.append(i)
	return ls

def list_gen(arg):
	for i in ...
		yiled i

10) map
li = [1, 2, 3]
for x in ls:
	x += 3   #不会改变 li 里面的值

li = [1, 2, 3]
for i in range(len(li)):
	li[i] += 3

li = list(map(lambda x: x+3, li])
map 返回一个惰性序列，用list显式化

