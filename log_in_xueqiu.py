#coding: utf-8
'''
雪球网的登录，会将你的密码用 md5 加密，然后 post。
'''
import hashlib
import requests
from bs4 import BeautifulSoup
import winsound

header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/51.0.2704.103 Safari/537.36",
            'Host': "xueqiu.com",
            'referer': "https://xueqiu.com"
        }

session = requests.Session()

def get_passwd_md5(passwd):
    m = hashlib.md5()
    m.update(passwd.encode())
    return m.hexdigest().upper()

def sign_in(telephone, passwd):

    print('sign in...')
    url_sign_in = 'https://xueqiu.com/user/login'
    pay_load = {
                'areacode': '86',
                'password':	get_passwd_md5(passwd),
                'remember_me': 'on',
                'telephone': telephone
               }

    html = session.post(url_sign_in, data=pay_load, headers=header)

    print('sign ok')

    soup = BeautifulSoup(html.content, 'html.parser')
    title = soup.find('title')

    if title is not None and title.string == '我的首页 - 雪球':
        print('sign ok')
    else:
        print('sign failed')
        winsound.Beep(500, 1000)     # 如果登录失败，发出声音


if __name__ == '__main__':
    passwd = 'xxxxxxx'
    telephone = 'xxxxxxx'
    sign_in(telephone, passwd)


