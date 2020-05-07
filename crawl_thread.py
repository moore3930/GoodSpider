# -*- coding: utf-8 -*-
import threading
import time
import os
import util
from webpage_parse import WeiboDownloader


class WeiboCrawlerThread(threading.Thread):
    def __init__(self, threadName, urlQueue, config, logger, cookie):
        super(WeiboCrawlerThread, self).__init__()
        self.threadName = threadName
        self.urlQueue = urlQueue
        self.config = config
        self.downloader = None
        self.logger = logger
        self.cookie = cookie

    def run(self):
        self.logger.info('Run ' + self.threadName)

        self.downloader = WeiboDownloader(self.cookie)

        while not self.urlQueue.empty():
            try:
                url = self.urlQueue.get(False)
                time.sleep(1)
                contents = self.request_webpage(url)
                _, start_time, end_time = util.parse_weibo_url(url)
                keywords = self.config['Main']['key_words']
                save_path = os.path.join(os.getcwd(), self.config['Main']['download_dir_name'],
                                         '-'.join([keywords, start_time, end_time]))
                util.save_weibo_page(save_path, contents)
                self.logger.info("{} extracts {} blogs from {}.".format(self.threadName, len(contents), url))

            except Exception as e:
                self.logger.info('empty', e)
                pass

    def request_webpage(self, url):
        contents = self.downloader.get_contents(url,)
        return contents

