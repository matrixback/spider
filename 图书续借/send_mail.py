# coding: utf-8

import smtplib
from email.mime.text import MIMEText
from email.header import Header

server = smtplib.SMTP("smtp.163.com", 25)
server.set_debuglevel(1)

my_mail_addr = 'xxxxxxxxx@163.com'
password = 'xxxxxx'

def send_mail(message, to):
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = Header('图书续借')
    server.login(my_mail_addr, password)
    server.send_message(msg=msg, from_addr=my_mail_addr, to_addrs=[to] )
    server.quit()