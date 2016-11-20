#coding: utf-8
from bs4 import BeautifulSoup
import requests

header_common = {
                     'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/51.0.2704.103 Safari/537.36",
                     'Host': "matrix.ac.cn",
                     'referer': "http://matrix.ac.cn"
                 }

# 用于保存全局会话
session = requests.Session()

def get_token():

    url_sign_in = 'http://matrix.ac.cn/admin'

    html = session.get(url_sign_in, headers=header_common)
    soup = BeautifulSoup(html.content, 'html.parser')

    form = soup.find('input', {'type': "hidden"})
    token = form['value']
    print(token)
    return token

def sign_in():

    print('sign in...')
    token = get_token()
    url_sign_in = 'http://matrix.ac.cn/admin/login/?next=/admin/'
    header_sign_in = {
                         'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/51.0.2704.103 Safari/537.36",
                         'Host': "matrix.ac.cn",
                         'referer':"http://matrix.ac.cn"
                     }
    pay_load = {
                'username':'matrix',
                'password': 'reform2014',
                'csrfmiddlewaretoken':token,
            }

    html = session.post(url_sign_in, data=pay_load, headers=header_sign_in)
    with open('matrix.html', 'wb') as f:
        f.write(html.content)
    print('sign ok')

sign_in()






