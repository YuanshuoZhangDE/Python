# -*- coding: utf-8 -*-
# @Time    : 2020/1/30 21:26
# @Author  : ZhangDawei
# @Email   : zhangyuanshuode@163.com
# @File    : Spider.py
# @Software: PyCharm

## 1.抓取索引页内容,利用requests请求目标站点，得到索引网页HTML代码，返回结果。
## 2.抓取详细页内容,解析返回结果，得到详细页的链接，并进一步抓取详细页信息
## 3.下载图片与保存数据库，将图片下载到本地，并把页面信息及图片URL保存至MongoDB
## 4.开启循环及多线程，对多页内容遍历，开启多线程提高抓去速度
import os
import requests
from requests.exceptions import RequestException
import re
from bs4 import BeautifulSoup
from config import *
import pymongo
from hashlib import md5
from multiprocessing import Pool

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def get_page_index(url):
    try:
        proxies = {
            'http': 'http://127.0.0.1:1080',
            'https': 'https://127.0.0.1:1080'
        }
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        response = requests.get(url, proxies=proxies, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求索引失效")
        return None

def parse_page_index(html):
    #pattern = re.compile('<a.*?"movie-box"\shref="(.*?)">.*?photo-frame.*?<img.*?src="(.*?)"\stitle="(.*?)"></div>', re.S)
    soup = BeautifulSoup(html, 'lxml')
    items_movies = soup.select('div .movie-box')
    for url_movie in items_movies:
        yield url_movie['href']


def get_page_detail(url):
    try:
        proxies = {
            'http': 'http://127.0.0.1:1080',
            'https': 'https://127.0.0.1:1080'
        }
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        response = requests.get(url, proxies=proxies, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求详情页出错", url)
        return None

def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    titles = soup.select('.container h3')
    images = soup.select('.bigImage img')
    #magnets = soup.find(attrs={'style':'color:#333'})

    for title, image, in zip(titles, images):
        doenload_image(image['src'])
        return {
            'url':url,
            'title': title.get_text(),
            'image': image['src']
         }

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到MONGODB成功')
        return True
    return False

def doenload_image(url):
    print('正在下载',url)
    try:
        proxies = {
            'http': 'http://127.0.0.1:1080',
            'https': 'https://127.0.0.1:1080'
        }
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        response = requests.get(url, proxies=proxies, headers=headers)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except RequestException:
        print("请求图片出错", url)
        return None

def save_image(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()

def main(offset):
    url = 'https://www.javbus.com/star/2jv/' + str(offset)
    html = get_page_index(url)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        result = parse_page_detail(html, url)
        save_to_mongo(result)
        print(result)



if __name__ == '__main__':
    groups = [i for i in range(GROUP_START,GROUP_END+1)]
    pool = Pool()
    pool.map(main, groups)
    

    #for i in range(GROUP_START, GROUP_END + 1):
    #    main(i)
