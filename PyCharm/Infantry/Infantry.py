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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup



broswer = webdriver.Chrome()
wait = WebDriverWait(broswer, 10)

def get_page_index(url):
    try:
        print('index:',url,'正在链接')
        broswer.get(url)
    except TimeoutException:
        print('请求超时，正在重链',url)
        return get_page_index()

def parse_page_index():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#waterfall > div:nth-child(1) > a')))
    html = broswer.page_source
    soup = BeautifulSoup(html, 'lxml')
    urls = soup.select('div .movie-box')
    for url in urls:
        yield url['href']


def get_page_detail(url):
    try:
        print(url,'正在链接')
        broswer.get(str(url))
    except TimeoutException:
        print('请求超时，正在重链', url)
        return get_page_detail(url)


def parse_page_detail():
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.container > div.row.movie > div.col-md-9.screencap > a > img')))
        html = broswer.page_source
        soup = BeautifulSoup(html, 'lxml')
        title_images = soup.select('.bigImage img')
        magnets = [soup.find(attrs={'title':'滑鼠右鍵點擊並選擇【複製連結網址】'})]
        for title_image, magnet in zip(title_images, magnets):
            print("爬取成功")
            print('title:',title_image['title'])
            print('image:', title_image['src'])
            print('magnet:',magnet['href'])
            return {
                'title':title_image['title'],
                'image':title_image['src'],
                'magnet':magnet['href']
                }
    except:
        return None

def write_to_file(detail):
    with open('Infantry.txt', 'a', encoding='utf-8') as f:
        f.write(str(detail)+ '\n')
        f.close()

def main(offset):
    url = 'https://www.javbus.com/uncensored/genre/sub/' + str(offset)
    get_page_index(url)
    count = 0
    for url in parse_page_index():
        get_page_detail(url)
        print('链接成功',url)
        result = parse_page_detail()
        write_to_file(result)
        count += 1
        print('*'*20,offset,"****",count,'*'*20)

if __name__ == '__main__':
    for i in range(8,12):
        main(i)
    broswer.close()