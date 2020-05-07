# -*- coding: utf-8 -*-
import urllib
import datetime
import re
import os


def get_datetime(data_str):
    try:
        today = datetime.datetime.today()
        if '今天' in data_str:
            H, M = re.findall(r'\d+', data_str)
            date = datetime.datetime(today.year, today.month, today.day, int(H), int(M)).strftime('%Y-%m-%d %H:%M')
        elif '年' in data_str:
            y, m, d, H, M = re.findall(r'\d+', data_str)
            date = datetime.datetime(int(y), int(m), int(d), int(H), int(M)).strftime('%Y-%m-%d %H:%M')
        else:
            m, d, H, M = re.findall(r'\d+', data_str)
            date = datetime.datetime(today.year, int(m), int(d), int(H), int(M)).strftime('%Y-%m-%d %H:%M')
    except:
        date = data_str
    return date


def save_weibo_page(path, content):
    if os.path.exists(path):
        return

    content_fout = open(path, 'w')
    for blog in content:
        blog_line = '\t'.join([str(tup[0]) + '\x01' + str(tup[1]) for tup in blog.items()])
        content_fout.write(blog_line + '\n')
    print('save_path is {}'.format(path))
    print(content)
    content_fout.flush()
    content_fout.close()

    return


def parse_weibo_url(url):
    keyword = url.strip().split('&')[0].replace('https://s.weibo.com/weibo/', '')
    start_time = url.strip().split(':')[-2]
    end_time = url.strip().split(':')[-1].replace('&page=', '')
    return keyword, start_time, end_time


def get_query_list(off_set, config):

    def get_keyword(keyword):
        return urllib.parse.quote(urllib.parse.quote(keyword))

    keyword = config['Main']['key_words']
    search_str = get_keyword(keyword) + '?q=' + urllib.parse.quote(keyword)

    start_date = datetime.datetime.strptime(config['Main']['start_time'], '%Y-%m-%d-%H')
    end_date = datetime.datetime.strptime(config['Main']['end_time'], '%Y-%m-%d-%H')
    start_date = start_date + datetime.timedelta(hours=off_set)

    if start_date > end_date:
        return []

    query_list = []
    while start_date < end_date:
        start_time_stamp = start_date
        end_time_stamp = start_time_stamp + datetime.timedelta(hours=1)
        url = 'https://s.weibo.com/weibo/' + search_str + '&t&typeall=1&suball=1&timescope=custom:'\
              + start_time_stamp.strftime('%Y-%m-%d-%H') + ':' + end_time_stamp.strftime('%Y-%m-%d-%H') + '&page='
        query_list.append(url)
        start_date = end_time_stamp
    return query_list
