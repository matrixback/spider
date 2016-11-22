# coding: utf-8

import requests
import re
from bs4 import BeautifulSoup
import time
import logging
from send_mail import send_mail, my_mail_addr

logging.basicConfig(
    level=logging.INFO,
    filename="books_spider_log",
    filemode='a',
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
)

base_url = "http://my.scu.edu.cn/"

headers = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
    'Host': "my.scu.edu.cn",
    'Referer': "http://my.scu.edu.cn/index.portal"
}

session = requests.session()

def hold_books():
    '''
         从图书馆直接登陆有点困难，所以选择了从校园信息门户登录，登录后一直找各种链接地址，最后到续借页，续借很简单，直接
         GET 参数加参数即可。
    '''
    # step1 log_in
    # get login page cookies
    session.get(base_url, headers=headers)

    # get ready to login
    data = {
        "Login.Token1": "2014223070030",
        "Login.Token2": "reform2014",
        "goto": "http://my.scu.edu.cn/loginSuccess.portal",
        "gotoOnFail": "http://my.scu.edu.cn/loginFailure.portal"
    }
    url = "http://my.scu.edu.cn/userPasswordValidate.portal"
    time.sleep(2)
    r = session.post(url, data=data, headers=headers)
    if r.status_code != requests.codes.ok:
        logging.critical('login error')
        send_mail('login error', my_mail_addr)

    # get real loged page
    new_url = "http://my.scu.edu.cn/index.portal"
    time.sleep(2)
    session.get(new_url,  headers=headers)


    # 2 step2 get borrow page
    bor_info_url = "http://opac.scu.edu.cn:8118/ice/login_ice.jsp?type=borinfo"
    time.sleep(2)
    r = session.get(bor_info_url, headers=headers)


    # 3 step3 find borrowed page link and enter in
    bor_info_url = re.findall(r'http://opac.scu.edu.cn:8080.*SCU50', r.text)[0]
    headers['Referer'] = r.url
    time.sleep(2)
    r = session.get(bor_info_url, headers=headers)

    # 4 step4 find book which will overdue and hole_request
    hold_request_url = r.url
    hold_request(hold_request_url, r)



def hold_request(url, r):
    soup = BeautifulSoup(r.text, 'html.parser')
    borrowed_books = soup.find_all("td", class_="td1", valign="top", width="2%", align="center")
    books_info = [(l.find("input", type="checkbox")['name'], l.find_next_siblings()[3].string,\
                                                             l.find_next_siblings()[1].string) \
                                                                      for l in borrowed_books]

    headers['Referer'] = url
    hold_request_url = url.split('?')[0]     # only need prefix
    for book in books_info:
        if int(int(book[1]) - int(time.strftime("%Y%m%d"))) <= 2:    # find book will overdue
            book_id = book[0]
            params = {
                "adm_library": "SCU50",
                book_id: "Y",
                "func": "bor-renew-all",
                "renew_selected": "Y"
            }
            try:
                r = session.get(hold_request_url, params=params, headers=headers)
            except Exception:
                logging.critical('hold request fail, please verify reasons')
                send_mail(my_mail_addr, "hold request fail, please verify reasons")
                continue
            else:
                if r.status_code == requests.codes.ok:
                    logging.info('hold request success book %s' % book[2])
                    send_mail(my_mail_addr)
                else:
                    logging.critical('hold request fail, please verify reasons')
    else:
        logging.info('no book will overdue')

if __name__ == '__main__':
    hold_books()
