# -*- coding: utf-8 -*-
# @Time    : 2020/1/31 21:02
# @Author  : ZhangDawei
# @Email   : zhangyuanshuode@163.com
# @File    : JD.py
# @Software: PyCharm

# !/usr/bin/env python
# coding: utf-8

# ## 流程框架

# - 搜索关键字，利用selenium驱动浏览器搜索关键字
# - 分析页码并翻页，得到商品页码数，模拟翻页，得到后续页码的商品列表
# - 分析提取商品内容，利用PyQuery分析源码，解析得到商品列表
# - 存储至MongoDB，将商品列表信息存储到数据库




from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

broswer = webdriver.Chrome()
wait = WebDriverWait(broswer, 10)





def search():
    try:
        broswer.get('https://www.jd.com')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#key'))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#search > div > div.form > button'))
        )
        input.send_keys('口罩')
        submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > em:nth-child(1) > b'))
        )
        get_products()
        return total.text
    except TimeoutException:
        return search()




def next_page(pager_number):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > input'))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > a'))
        )
        input.clear()
        input.send_keys(pager_number)
        submit.click()
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.curr'), str(pager_number))
        )
        get_products()
    except TimeoutException:
        return next_page(pager_number)





def get_products():
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > em:nth-child(1) > b'))
    )
    html = broswer.page_source
    soup = BeautifulSoup(html, 'lxml')
    titles = soup.select('.gl-item .p-name.p-name-type-2 a em')
    urls = soup.select('.gl-item .p-img a')

    for title, url in zip(titles, urls):
        product = {
            'title': title.get_text(),
            'url': url['href']
        }
        print(product)





def main():
    total = int(search())
    for i in range(2, total + 1):
        next_page(i)





if __name__ == '__main__':
    main()

