# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import util
import requests
import time
import logging


class WeiboDownloader(object):

    def __init__(self, cookie):
        self.cookie = cookie
        self.logger = logging.getLogger('logger')

    def get_page_html(self, url, pageNum):
        page_url = url + str(pageNum)
        res = requests.get(page_url, cookies=self.cookie)
        return res.text.replace('\u200b', '')

    def get_page_num(self, url):
        soup = BeautifulSoup(self.get_page_html(url, 1), 'html.parser')

        if len(soup.select('.card-no-result')) > 0:
            page_num = 0
        else:
            page_num = len(soup.select('.s-scroll li'))
        return page_num

    def get_page_results(self, html):
        results = []
        soup = BeautifulSoup(html, 'html.parser')
        if len(soup.select('.card-no-result')) > 0:
            return None

        if len(soup.select('div[action-type="feed_list_item"]')) > 0:
            for item in soup.select('div[action-type="feed_list_item"]'):
                blog = {'博主昵称': item.select('.name')[0].get('nick-name'),
                        '博主主页': 'https:' + item.select('.name')[0].get('href')}

                if len(item.select('p.txt')) > 1:
                    blog['微博内容'] = item.select('p.txt')[1].get_text().strip()
                else:
                    blog['微博内容'] = item.select('p.txt')[0].get_text().strip()
                    blog['发布时间'] = util.get_datetime(
                        item.select('div[class="content"] p[class="from"] a')[0].get_text())
                    blog['微博地址'] = 'https:' + item.select('div[class="content"] p[class="from"] a')[0].get('href')

                try:
                    blog['微博来源'] = item.select('div[class="content"] p[class="from"] a')[1].get_text()
                except:
                    blog['微博来源'] = ''

                try:
                    sd = item.select('.card-act ul li')
                    if sd is None:
                        continue
                except:
                    continue

                try:
                    blog['转发'] = 0 if sd[1].text.replace('转发', '').strip() == '' \
                        else int(sd[1].text.replace('转发', '').strip())
                except:
                    blog['转发'] = 0

                try:
                    blog['评论'] = 0 if sd[2].text.replace('评论', '').strip() == '' \
                        else int(sd[2].text.replace('评论', '').strip())
                except:
                    blog['评论'] = 0

                try:
                    blog['赞'] = 0 if sd[3].select('em')[0].get_text() == '' \
                        else int(sd[3].select('em')[0].get_text())
                except:
                    blog['赞'] = 0

                results.append(blog)
        return results

    def get_contents(self, url):
        page_num = self.get_page_num(url)
        content = []
        for i in range(1, page_num + 1):
            time.sleep(5)
            try:
                page_html = self.get_page_html(url, i)
            except:
                time.sleep(120)
                page_html = self.get_page_html(url, i)
            page_results = self.get_page_results(page_html)
            content.extend(page_results)

        return content
