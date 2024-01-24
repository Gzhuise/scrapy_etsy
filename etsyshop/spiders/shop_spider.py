import scrapy
import pymysql
from etsyshop.items import EtsyshopItem
import re
from datetime import datetime
import json
from scrapy.selector import Selector
import pdb
from dateutil.parser import parse
from .. import config
import time

class ShopSpider(scrapy.Spider):
    name = "shop"
    custom_settings = {
        'ITEM_PIPELINES': {
            'etsyshop.pipelines.EtsyshopPipeline': 300,
        }
    }
    
    def start_requests(self):
        #获取所有的店铺URL
        shops = self.get_shop()
        for shop in shops:
            #输出店铺URL用于调试
            yield scrapy.Request(url=shop[2], callback=self._parse,
                                 meta={
                                    # "shop_id": shop[0],
                                    "zyte_api_automap": {
                                        "httpResponseBody": True 
                                        },
                                    },
                                )
            

    def parse(self, response):
        # pdb.set_trace() #调试模式，运行到这里会自动暂停，在命令行中对response进行多次的xpath测试，直到得到想要的结果
        item = EtsyshopItem()
        item['url'] = response.url
        # item['id'] = response.meta['shop_id']
        item['id'] = self.get_shop_id(response)
        

        # 0.1获取是否仍在营运
        not_selling = response.xpath('//div[@data-region="frozen-message"]//h4[contains(text(), "not selling on")]').get() 
        if not_selling is not None:
            item['not_selling'] = 1
            yield item
        else:
            item['not_selling'] = 0
        # 0.2获取是否仍在营运
        taking_break = response.xpath('//div[@data-region="vacation-notification-bar"]//h2[contains(text(), "taking a short break")]').get() 
        if taking_break is not None:
            item['taking_break'] = 1
            yield item
        else:
            item['taking_break'] = 0
        # 1.获取销量
        sales_str = response.xpath('//div[contains(@class, "shop-info")]//span[contains(@class, "wt-text-caption") and contains(@class, "wt-no-wrap")]/.//text()').extract_first()
        sales = None if sales_str==None else re.sub(r'[^0-9.]', '', sales_str)
        item['sales'] = sales
        # 2.获取评价数量
        reviews_str = response.xpath('//div[contains(@class, "reviews-total")]//div[contains(@class, "wt-display-inline-block")][last()]/text()').extract_first()
        review = None if reviews_str==None else re.sub(r'[^0-9.]', '', reviews_str)
        item['review'] = review
        # 3.获取Logo地址
        logo_url = response.xpath('//img[contains(@class, "shop-icon-external")]/@src').extract_first()
        item['logo_url'] = logo_url
        # 4.獲取店鋪描述
        description = response.xpath('//div[contains(@class, "shop-name-and-title-container")]/p[contains(@data-key,"headline")]/text()').extract_first()
        item['description'] = None if description==None else description.strip()
        # 5.獲取店鋪通告
        announcement = response.xpath('//div[contains(@class, "announcement-section")]/div[last()]').extract_first()
        item['announcement'] = announcement
        # 6.獲取店鋪通告发布时间
        announcement_update_str = response.xpath('//div[contains(@class, "announcement-section")]/div[2]/div[1]/span/text()').extract_first()
        if (announcement_update_str!=None) :
            # announcement_update_date = datetime.strptime(announcement_update_str, "%b %d, %Y") #用以下替换，比较智能
            announcement_update_date = parse(announcement_update_str)
            announcement_last_updated = announcement_update_date.strftime("%Y-%m-%d")
            item['announcement_last_updated'] = announcement_last_updated
        # 7.獲取評分數 
        stars = response.xpath('//input[contains(@name, "rating")]/@value').extract_first()
        item['stars'] = stars
        # 8.獲取地址
        location = response.xpath('//div[contains(@class, "shop-location")]//span/text()').extract_first()
        item['location'] = location
        # 9.獲取All产品数量
        product = response.xpath('//div[contains(@data-appears-component-name, "shop_home_listings_section")]//span[normalize-space(text())="All"]/following-sibling::span[1]/text()').extract_first()
        item['product'] = product
        # 10.獲取On sale产品数量
        product_on_sale = response.xpath('//div[contains(@data-appears-component-name, "shop_home_listings_section")]//span[normalize-space(text())="On sale"]/following-sibling::span[1]/text()').extract_first()
        item['product_on_sale'] = product_on_sale
        # 11.獲取点赞的人数
        admirers_str = response.xpath('//a[contains(text(), "Admirers")]/text()').extract_first()
        admirers = None if admirers_str==None else re.sub(r'[^0-9.]', '', admirers_str)
        item['admirers'] = admirers
        # 12.獲取加入ETSY的年份
        on_etsy_since_list = response.xpath('//div[contains(@data-appears-component-name, "shop_home_about_section")]//div[contains(@class, "shop-home-wider-sections")]//span/text()').extract()
        if len(on_etsy_since_list) > 1:
            item['on_etsy_since'] = on_etsy_since_list[1]
        # 13.获取社交媒体地址 
        item['instagram'] = response.xpath('//a[contains(@aria-label, "Instagram")]/@href').extract_first()
        item['pinterest'] = response.xpath('//a[contains(@aria-label, "Pinterest")]/@href').extract_first()
        item['twitter'] = response.xpath('//a[contains(@aria-label, "Twitter")]/@href').extract_first()
        item['facebook'] = response.xpath('//a[contains(@aria-label, "Facebook")]/@href').extract_first()
        shop_websites_href_list = response.xpath('//a[contains(@aria-label, "shop-website")]/@href').extract()
        if shop_websites_href_list!=None:
            websites = []
            for shop_website in shop_websites_href_list:
                websites.append(shop_website)
            item['websites'] = json.dumps(websites)
        # 14.获取评论的页数(每页10条)
        last_page_str = response.xpath('//div[@data-appears-component-name="shop_home_reviews_section"]//li[@class="wt-action-group__item-container"][last()-1]//span[last()]/text()').extract_first()
        review_page = None if last_page_str==None else re.sub(r'[^0-9.]', '', last_page_str)
        item['review_page'] = review_page
        # 15.获取是否是明星卖家
        star_seller = response.xpath('//div[contains(@class, "star-seller-badge")]').get()
        item['star_seller'] = 1 if star_seller is not None else 0
        # 15.是否含有free shipping
        free_shipping = response.xpath('//span[contains(@class, "wt-badge--statusValue")][contains(text(), "FREE shipping")]').get() 
        item['free_shipping'] = 1 if free_shipping is not None else 0
        
        # 其他字段设置为 None
        item['first_review_date'] = None
        
        yield item
     
        
    #连接mysql数据库
    def connect_mysql(self):
        db = pymysql.connect(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER, password=config.DB_PASSWORD, database=config.DB_NAME)
        return db
    
    # 根据店铺名称获取店铺的ID
    def get_shop_id(self, response):
        url_last_part = response.url.split('/')[-1]
        shop_name = url_last_part.split('?')[0]
        db = self.connect_mysql()
        cursor = db.cursor()
        sql = """
        SELECT `id` FROM `shop_info` WHERE `name` = %s
        """
        cursor.execute(sql, (shop_name))
        shop = cursor.fetchone()
        return shop[0]
    
    #在数据库中获取所有的店铺
    def get_shop(self):
        now_at = int(time.time()) - 86400
        db = self.connect_mysql()
        cursor = db.cursor()
        sql = "select id,category,url from shop_info where stat=1 and (not_selling=0 or not_selling is null) and updated_at< %s "
        cursor.execute(sql, now_at)
        shops = cursor.fetchall()
        return shops
    
            