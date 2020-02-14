# -*- coding: utf-8 -*-
import scrapy

#from xicidailiSpider.xicidailiSpider.items import XicidailispiderItem


class XicidailiSpider(scrapy.Spider):
    name = 'xicidaili'
    allowed_domains = ['www.xicidaili.com']
    start_urls = [f'https://www.xicidaili.com/nn/{page}' for page in range(1, 4021)]

    def parse(self, response):
        # 提取数据
        xicis = response.xpath('//tr')
        for xici in xicis:
            ip = xici.xpath('./td[2]/text()').extract_first()
            port = xici.xpath('./td[3]/text()').extract_first()
            address = xici.xpath('./td/a/text()').extract_first()
            print(ip, port, address)


        # 翻页
        next_page = response.xpath('//a[@class="next_page"]/@href').extract_first()
        if next_page:
            # 拼接网址
            next_url = response.urljoin(next_page)
            # 发出请求Request,callback回调函数，将请求得到的响应交给自己处理
            yield scrapy.Request(url=next_url, callback=self.parse)
