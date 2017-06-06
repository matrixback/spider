# coding: utf-8
"""
知道创宇爬虫作业。爬虫要求：

使用python编写一个网站爬虫程序，支持参数如下：
spider.py -u url -d deep -f logfile -l loglevel(1-5)  --testself -thread number --dbfile  filepath  --key=”HTML5”

参数说明：

-u 指定爬虫开始地址
-d 指定爬虫深度
--thread 指定线程池大小，多线程爬取页面，可选参数，默认10
--dbfile 存放结果数据到指定的数据库（sqlite）文件中
--key 页面内的关键词，获取满足该关键词的网页，可选参数，默认为所有页面
-l 日志记录文件记录详细程度，数字越大记录越详细，可选参数，默认spider.log
--testself 程序自测，可选参数

功能描述：

1、指定网站爬取指定深度的页面，将包含指定关键词的页面内容存放到sqlite3数据库文件中
2、程序每隔10秒在屏幕上打印进度信息
3、支持线程池机制，并发爬取网页
4、代码需要详尽的注释，自己需要深刻理解该程序所涉及到的各类知识点
5、需要自己实现线程池

提示1：使用re  urllib/urllib2  beautifulsoup/lxml2  threading optparse Queue  sqlite3 logger  doctest等模块
提示2：注意是“线程池”而不仅仅是多线程
提示3：爬取sina.com.cn两级深度要能正常结束

建议程序可分阶段，逐步完成编写，例如：

版本1:Spider1.py -u url -d deep
版本2：Spider3.py -u url -d deep -f logfile -l loglevel(1-5)  --testself
版本3：Spider3.py -u url -d deep -f logfile -l loglevel(1-5)  --testself -thread number
版本4：剩下所有功能
"""
import Queue
import threading
from collections import namedtuple
import requests
from urlparse import urlsplit, urljoin
import logging
from BeautifulSoup import BeautifulSoup
import re
import os
import sqlite3
import chardet
from optparse import OptionParser
import time

Task = namedtuple('Task', ['url', 'deep'])

def get_logger(logfile, loglevel):
    if loglevel > 5 or loglevel < 1:
        raise ValueError('log level set error')
    # logging 中指定了各个级别的数值,其中 logging.DEBUG = 10，logging.CRITICAL = 50
    loglevel = 60 - loglevel * 10
    logging.basicConfig(
        level=loglevel,
        filename=logfile,
        filemode='a',
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    )
    return logging.getLogger()


def get_optparser():
    usage = "usage: %prog [options] arg"
    parser = OptionParser()
    parser.add_option("-u", type="string", dest="url", help='must specify the base url')
    parser.add_option("-d", type="int", dest="deep", default=2, help='specify the depth you will crawl, default: 2')
    parser.add_option("-f", type="string", dest="logfile", default="spider.log", help="logfile name, default: spider.log")
    parser.add_option("-l", type="int", dest="loglevel", default=5, help="loglevel must be 1-5, default: 5")
    parser.add_option("--thread", type="int", dest="num_thread", default=10, help="thread number, default: 10")
    parser.add_option("--dbfile", type="string", dest="dbfile", default='spider.db', help="db file name, default: spider.db")
    parser.add_option("--key", type="string", dest="key", default=None, help="download files which contain the key, default: None")
    parser.add_option("--testself", action="store_true", dest="testself")

    return parser


class DB(object):
    def __init__(self, dbfile):
        dirname = os.path.dirname(__file__)
        self.dbfile = dbfile
        self.db = sqlite3.connect(dirname + '/' + dbfile, check_same_thread=False)   # 如果没有，则会创建一个。
        self.tablename = 'files'
        self.create_table()

    def create_table(self):
        cursor = self.db.cursor()
        try:
            cmd = 'CREATE TABLE IF NOT EXISTS `files` (`id` INTEGER PRIMARY KEY , `url` varchar(256) NOT NULL,' \
                  '`title` varchar(256), `page` TEXT NOT NULL);'
            cursor.execute(cmd)
            self.db.commit()
        except sqlite3.OperationalError:
            logger.critical(u'创建数据表失败，爬虫将退出。')
            exit(1)

    def insert(self, url, title, page):
        cursor = self.db.cursor()
        try:
            cursor.execute("insert into files (url, title, page) values (?, ?, ?)", (url, title, page))
            self.db.commit()
        except sqlite3.OperationalError:
            logger.critical(''.join([url, u'保存失败']))

    def query_all(self):
        cursor = self.db.cursor()
        try:
            cmd = 'select *  from {tablename}'.format(tablename='files')
            cursor.execute(cmd)
        except sqlite3.OperationalError:
            logger.critical(u'获取文件失败')
            return None
        else:
            return cursor.fetchall()

    def truncate_table(self):
        cursor = self.db.cursor()
        cmd = 'DELETE FROM files'
        print(cmd)
        cursor.execute(cmd)
        self.db.commit()


class Reporter(threading.Thread):
    def __init__(self, queue, db, rlock, event, sleep_time=10):
        super(Reporter, self).__init__()
        self.queue = queue
        self.db = db
        self.rlock = rlock
        self.sleep_time = sleep_time
        self.event = event
        self.start()

    def run(self):
        while True:
            files = self.db.query_all()
            if files:
                files_size = len(files)
            else:
                print(u'获取文件失败')
                files_size = 0
            if self.event.is_set():
                print(u'共获取页面{0}'.format(files_size))
                return
            else:
                q_size = self.queue.qsize
                print(u'已获得 {0} 页面，待获取 {1} 页面'.format(files_size, q_size()))
                time.sleep(self.sleep_time)


class Spider(threading.Thread):
    def __init__(self, queue, rlock, db, key=None,):
        super(Spider, self).__init__()
        self.queue = queue
        self.daemon = True
        self.key = key
        self.task = None
        self.rlock = rlock
        self.db = db
        self.start()

    def run(self):
        session = requests.session()
        session.get(baseurl)
        while True:
            self.task = self.queue.get()
            print('url level:', self.task.deep, "url:", self.task.url)
            page = self.download_page(self.task.url, session)

            if page:
                title, links = self.get_title_and_links(page)
                # 如果没指定 key，或者指定了，并且页面存在 key，则保存，否则不保存。
                if not self.key or self.key in page:
                    self.save_page(self.task.url, title, page)

                if self.task.deep > 1:
                    deep = self.task.deep - 1
                    global added_urls
                    for link in links:
                        if link not in added_urls:
                            self.queue.put(Task(link, deep))
                            added_urls.add(link)

            self.queue.task_done()

    def download_page(self, url, session):
        ''' 下载文件，如果不成功，则返回 None '''
        splited_url = urlsplit(url)
        netloc = splited_url.netloc
        scheme = splited_url.scheme
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate',
            # 'Host': netloc,
            'Referer': ''.join([scheme, '//', netloc])
        }
        try:
            r = session.get(url, headers=headers, timeout=2)
            # r = requests.get(url, headers=headers, timeout=2)  # 把这个提交的时候禁止掉
            r.raise_for_status()
        except requests.RequestException as e:
            logger.error(e)
            return None
        else:
            return r.content


    def save_page(self, url, title, page):
        assert page, 'page is None'
        print('save page', title)
        charset = chardet.detect(page)
        encoding = charset.get('encoding')  # 出现没有encoding的错误。
        if encoding is None:
            encoding = 'utf-8'
        # db.insert 处理了异常，此处不再加异常。
        self.rlock.acquire()
        self.db.insert(url, title, page.decode(encoding, errors='ignore'))
        self.rlock.release()

    def get_title_and_links(self, page):
        #  由于BeautifulSoup 的 attrs 是列表，自己写个帮助函数取得链接。
        def get_link(tag):
            for attr in tag.attrs:
                if attr[0] == 'href':
                    return attr[1]

        if page is None:
            return None
        try:
            soup = BeautifulSoup(page)
        except TypeError as e:
            logger.error(e)
            return None

        title_tag = soup.find('title')
        title = title_tag.string if title_tag else None

        links = []

        full_link_tags = soup.findAll('a', href=re.compile(r'^https?://.*'))
        links.extend(list(map(get_link, full_link_tags)))

        short_links_tag = soup.findAll('a', href=re.compile(r'^/.*'))
        short_links = list(map(get_link, short_links_tag))
        splited_url = urlsplit(self.task.url)
        netloc = splited_url.netloc
        scheme = splited_url.scheme
        host = ''.join([scheme, '://', netloc])
        normaled_links = [urljoin(host, short_link) for short_link in short_links]
        links.extend(normaled_links)

        return title, links


class ThreadPool(object):
    def __init__(self, num_thread=10, dbfile='spider.db', key=None):
        self.queue = Queue.Queue()
        self.rlock = threading.RLock()
        self.db = DB(dbfile)
        self.event = threading.Event()
        Reporter(queue=self.queue, db=self.db, event=self.event, rlock=self.rlock, sleep_time=30)
        for _ in range(num_thread):
            Spider(queue=self.queue, db=self.db, rlock=self.rlock, key=key)

    def add_task(self, task):
        self.queue.put(task)

    def wait(self):
        self.queue.join()
        self.event.set()


def test_self():
    pass

if __name__ == '__main__':
    baseurl = 'http://mindhacks.cn'
    optparser = get_optparser()
    args = ['-u', 'http://www.baidu.com', '-d', '2', '--dbfile', 'baidu.db']
    # (options, args) = optparser.parse_args(sys.argv[1:])
    (options, args) = optparser.parse_args(args)
    if not options.url:
        optparser.error("must specify a baseurl, like python spider -u url")
    if options.loglevel > 5 or options.loglevel < 1:
        optparser.error("loglevel must be 1-5")

    logger = get_logger(loglevel=options.loglevel, logfile=options.logfile)
    added_urls = set()
    added_urls.add(options.url)

    pool = ThreadPool(num_thread=options.num_thread, dbfile=options.dbfile, key=options.key)
    pool.add_task(Task(options.url, options.deep))
    pool.wait()
    if options.testself:
        test_self()



