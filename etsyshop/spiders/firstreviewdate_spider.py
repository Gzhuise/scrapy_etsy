import scrapy
import pymysql
from etsyshop.items import EtsyfirstreviewdateItem
import re
from datetime import datetime
import json
from scrapy.selector import Selector
import pdb
from dateutil.parser import parse
from .. import config

class FirstreviewdateSpider(scrapy.Spider):
    name = "firstreviewdate"
    custom_settings = {
        'ITEM_PIPELINES': {
            'etsyshop.pipelines.EtsyshopsalesPipeline': 400,
        }
    }

    def start_requests(self):
        #获取所有的店铺
        shops = self.get_shop()
        for shop in shops:
            shopname = shop[2]
            page = str(shop[3])
            url = 'https://www.etsy.com/api/v3/ajax/bespoke/public/neu/specs/shop-reviews?log_performance_metrics=false&specs[shop-reviews][]=Shop2_ApiSpecs_Reviews&specs[shop-reviews][1][shopname]='+shopname+'&specs[shop-reviews][1][page]='+page+'&specs[shop-reviews][1][reviews_per_page]=10&specs[shop-reviews][1][should_hide_reviews]=true&specs[shop-reviews][1][is_in_shop_home]=true&specs[shop-reviews][1][sort_option]=Recency'
            yield scrapy.Request(url=url, callback=self.parse, meta={'id': shop[0],'url': shop[1]})
            

    def parse(self, response):
        # pdb.set_trace() #调试模式，运行到这里会自动暂停，在命令行中对response进行多次的xpath测试，直到得到想要的结果
        item = EtsyfirstreviewdateItem()
        item['id'] = response.meta['id']
        item['url'] = response.meta['url']
        
        # 解析JSON数据
        data = json.loads(response.text)
        # 检查'output'和'shop-reviews'是否存在
        if 'output' in data and 'shop-reviews' in data['output']:
            # 提取"shop-reviews"的HTML内容
            html_content = data['output']['shop-reviews']
            # 使用Scrapy的Selector来解析HTML
            selector = Selector(text=html_content)
            # 使用XPath来访问h1元素
            
            shop_first_reviews_text = selector.xpath('(//div[@class="review-item"]//p[@class="shop2-review-attribution"])/text()[last()]').extract_first()
            if shop_first_reviews_text is not None:
                shop_first_reviews_text = self.remove_before_on(shop_first_reviews_text)
                shop_first_reviews_text = shop_first_reviews_text.replace('Anonymous', '')
                shop_first_reviews_text = shop_first_reviews_text.replace('on', '')
                shop_first_reviews_text = shop_first_reviews_text.strip()
                ele_review_date_stamp = parse(shop_first_reviews_text)
                item['first_review_date'] = ele_review_date_stamp.strftime("%Y-%m-%d")
            
        yield item
     
    def remove_before_on(self, text):
        index = text.find('on')
        if index != -1:
            return text[index:]
        else:
            return text
        
    #连接mysql数据库
    def connect_mysql(self):
        db = pymysql.connect(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER, password=config.DB_PASSWORD, database=config.DB_NAME)
        return db
    
    #在数据库中获取所有的店铺
    def get_shop(self):
        db = self.connect_mysql()
        cursor = db.cursor()
        sql = "select id,url,name,review_page from shop_info where stat=1 and review_page is not null and first_review_date is null"
        cursor.execute(sql)
        shops = cursor.fetchall()
        return shops
    
            