# -*- coding: utf-8 -*-

from crawl_thread import WeiboCrawlerThread
from queue import Queue
import configparser
import os
import util
import logging
import base64
import requests
import urllib
import rsa
import binascii


class LoginSina(object):

    def __init__(self, username, password, config):
        self.username = username
        self.password = password
        self.headers = {'User-Agent': config['Main']['User-Agent']}

    def get_su(self):
        username_base64 = base64.b64encode(urllib.parse.quote_plus(self.username).encode("utf-8"))
        return username_base64.decode("utf-8")

    def get_server_data(self, su):
        pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack" \
                  "&su={}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_= "
        pre_data_res = requests.get(pre_url.format(su), headers=self.headers)
        sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))
        return sever_data

    def get_password(self, password, server_time, nonce, pubkey):
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)
        message = str(server_time) + '\t' + str(nonce) + '\n' + str(password)
        message = message.encode("utf-8")
        passwd = rsa.encrypt(message, key)
        passwd = binascii.b2a_hex(passwd)
        return passwd

    def get_cookies(self):
        su = self.get_su()
        d = self.get_server_data(su)
        postdata = {
            'entry': 'sso',
            'gateway': '1',
            'from': 'null',
            'savestate': '0',
            'useticket': '0',
            'pagerefer': 'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout'
                         '.php%3Fbackurl',
            'vsnf': '1',
            'su': su,
            'service': 'sso',
            'servertime': d['servertime'],
            'nonce': d['nonce'],
            'pwencode': 'rsa2',
            'rsakv': '1330428213',
            'sp': self.get_password(self.password, d['servertime'], d['nonce'], d['pubkey']),
            'sr': '1366*768',
            'encoding': 'UTF-8',
            'cdult': '3',
            'domain': 'sina.com.cn',
            'prelt': '27',
            'returntype': 'TEXT'
        }
        login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        res = requests.post(login_url, data=postdata, headers=self.headers)
        ticket = eval(res.text)['crossDomainUrlList'][0][eval(res.text)['crossDomainUrlList'][0].find('ticket'):]
        new_url = 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack' \
                  '&{}&retcode=0'.format(
            ticket)
        return requests.get(new_url).cookies


def get_query_list(query_num, off_set, config):
    query_list = []
    return query_list


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Makedir for downloading data
    dir_name = os.path.join(os.getcwd(), config['Main']['download_dir_name'])
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # Init logging
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('log')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    cnt = 0

    # get cookie
    username = config['Weibo']['username']
    password = config['Weibo']['password']
    ls = LoginSina(username, password, config)
    cookie = ls.get_cookies()

    while True:
        if cnt >= int(config['Main']['max_num']):
            break

        # Queue of queries
        idQueue = Queue()
        if idQueue.empty():
            query_list = util.get_query_list(cnt, config)

            for q in query_list:
                idQueue.put(q)

        # consume all of the query & break
        if idQueue.empty():
            break

        # Launch threads
        crawlList = []
        for idx in range(0, int(config['Main']['crawler_num'])):
            name = 'crawler-{}'.format(idx)
            crawlList.append(name)

        threadList = []
        for crawlerName in crawlList:
            weiboCrawlerThreads = WeiboCrawlerThread(crawlerName, idQueue, config, logger, cookie)
            weiboCrawlerThreads.start()
            threadList.append(weiboCrawlerThreads)

        for weiboCrawlerThreads in threadList:
            weiboCrawlerThreads.join()

        cnt += len(query_list)
        logger.info("{} queries have been conducted. ".format(cnt))

    logger.info("Main thread quit. ")


if __name__ == '__main__':
    main()
