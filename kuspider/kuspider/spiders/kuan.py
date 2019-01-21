# -*- coding: utf-8 -*-
import re

import scrapy

from kuspider.items import KuspiderItem


class KuanSpider(scrapy.Spider):
    name = 'kuan'
    allowed_domains = ['www.coolapk.com']
    start_urls = ['http://www.coolapk.com/apk/']
    custom_settings = {
        'DOWNLOAD_DELAY':3,
        'CONCURRENT_REQUESTS_PER_DOMAIN':8
    }

    def start_requests(self):
        pages = []
        for page in range(1,570):
            url = 'https://www.coolapk.com/apk?p=%s' % page
            page = scrapy.Request(url,callback=self.parse)
            pages.append(page)
        return pages

    def parse(self, response):
        contents = response.css('.app_left_list>a')
        for content in contents:
            url = content.css('::attr("href")').extract_first()
            url = response.urljoin(url)
            yield scrapy.Request(url,callback=self.parse_url,dont_filter=True)

    def parse_url(self,response):
        item = KuspiderItem()
        item['name'] = response.css('.detail_app_title::text').extract_first()
        results = self.get_comment(response)
        item['volume'] = results[0]
        item['download'] = results[1]
        item['follow'] = results[2]
        item['comment'] = results[3]
        item['tags'] = self.get_tags(response)
        item['score'] = response.css('.rank_num::text').extract_first().encode('utf-8')
        num_socore = response.css('.apk_rank_p1::text').extract_first().encode('utf-8')
        item['num_score'] = re.search('共(.*?)个评分',num_socore).group(1)
        yield item

    def get_comment(self,response):
        message = response.css('.apk_topba_message::text').extract_first().encode('utf-8')
        result = re.findall(r'\s+(.*?)\s+/\s+(.*?)下载\s+/\s+(.*?)人关注\s+/\s+(.*?)个评论.*?',message)
        if result:
            results = list(result[0])
            return results

    def get_tags(self,response):
        data = response.css('.apk_left_span2')
        tags = [item.css('::text').extract_first() for item in data]
        return tags






















