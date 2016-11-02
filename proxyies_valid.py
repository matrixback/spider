#coding: utf-8
import requests
import datetime
import random

def get_ip():
    url = "http://api.xicidaili.com/free2016.txt"
    r = requests.get(url)
    ips = r.text.split(sep='\r\n')
    random.seed(datetime.datetime.now())
    cnt = 0
    while True:
        cnt += 1
        print(cnt)
        index = random.randint(0, len(ips)-1)
        proxies = {'http': ips[index]}
        try:
            r = requests.get('http://icanhazip.com', timeout=5.0, proxies=proxies)
            if r.status_code == requests.codes.ok:
                return ips[index]
        except Exception:
            pass
