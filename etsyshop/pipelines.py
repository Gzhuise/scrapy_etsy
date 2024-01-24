from itemadapter import ItemAdapter
import pymysql
import re
import datetime
import time
from . import config


class EtsyshopPipeline:
    def open_spider(self, spider):
        self.db = pymysql.connect(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER, password=config.DB_PASSWORD, database=config.DB_NAME)
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        # 一、保存店铺信息
        # 对item字典中的所有值进行过滤
        filtered_item = {k: None if str(v).lower() == 'none' else self.db.escape_string(str(v)) for k, v in item.items()}
        # 对某些字段做特殊处理：去除html标签，截取部分内容
        if filtered_item['announcement']!=None:
            filtered_item['announcement'] = re.sub('<.*?>', '', filtered_item['announcement'])
            filtered_item['announcement'] = filtered_item['announcement'][:500]
        
        created_at = updated_at = int(time.time())
        
        sql = """
        INSERT INTO shop_info (url, logo_url, 
            description, stars, location, announcement, announcement_last_updated, product, product_on_sale, sales, 
            admirers, review, review_page, star_seller, on_etsy_since, first_review_date, free_shipping, instagram, facebook, pinterest, twitter, websites, not_selling, taking_break, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON DUPLICATE KEY UPDATE 
        url = VALUES(url),
        logo_url = VALUES(logo_url),
        description = VALUES(description),
        stars = VALUES(stars),
        location = VALUES(location),
        announcement = VALUES(announcement),
        announcement_last_updated = VALUES(announcement_last_updated),
        product = VALUES(product),
        product_on_sale = VALUES(product_on_sale),
        sales = VALUES(sales),
        admirers = VALUES(admirers),
        review = VALUES(review),
        review_page = VALUES(review_page),
        star_seller = VALUES(star_seller),
        on_etsy_since = VALUES(on_etsy_since),
        first_review_date = VALUES(first_review_date),
        free_shipping = VALUES(free_shipping),
        instagram = VALUES(instagram),
        facebook = VALUES(facebook),
        pinterest = VALUES(pinterest),
        twitter = VALUES(twitter),
        websites = VALUES(websites),
        not_selling = VALUES(not_selling),
        taking_break = VALUES(taking_break),
        updated_at = VALUES(updated_at)
        """
        self.cursor.execute(sql, (filtered_item['url'], filtered_item['logo_url'], filtered_item['description'], filtered_item['stars'], filtered_item['location'], filtered_item['announcement'], 
                                  filtered_item['announcement_last_updated'], filtered_item['product'], filtered_item['product_on_sale'], 
                                  filtered_item['sales'], filtered_item['admirers'], filtered_item['review'], filtered_item['review_page'], 
                                  filtered_item['star_seller'], filtered_item['on_etsy_since'], filtered_item['first_review_date'], filtered_item['free_shipping'], 
                                  filtered_item['instagram'], filtered_item['facebook'], filtered_item['pinterest'], filtered_item['twitter'], filtered_item['websites'], filtered_item['not_selling'], filtered_item['taking_break'], updated_at))
        self.db.commit()
        
        # 二、保存每周的店铺销量信息
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        sql = """
        INSERT INTO shop_sales (shop_id, sales, reviews, star_seller, product, product_on_sale, stars, admirers, date, not_selling, taking_break, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON DUPLICATE KEY UPDATE 
        shop_id = VALUES(shop_id),
        date = VALUES(date),
        sales = VALUES(sales),
        reviews = VALUES(reviews),
        star_seller = VALUES(star_seller),
        product = VALUES(product),
        product_on_sale = VALUES(product_on_sale),
        stars = VALUES(stars),
        admirers = VALUES(admirers),
        not_selling = VALUES(not_selling),
        taking_break = VALUES(taking_break),
        created_at = VALUES(created_at)
        """
        self.cursor.execute(sql, (filtered_item['id'], filtered_item['sales'], filtered_item['review'], filtered_item['star_seller'], filtered_item['product'], 
                                  filtered_item['product_on_sale'], filtered_item['stars'], filtered_item['admirers'], date, filtered_item['not_selling'], filtered_item['taking_break'], created_at))
        self.db.commit()
        
        return item

# 二、保存店铺销量信息
class EtsyshopsalesPipeline:
    def open_spider(self, spider):
        self.db = pymysql.connect(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER, password=config.DB_PASSWORD, database=config.DB_NAME)
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        # 对item字典中的所有值进行过滤
        filtered_item = {k: None if str(v).lower() == 'none' else self.db.escape_string(str(v)) for k, v in item.items()}
        
        sql = """
        UPDATE shop_info SET first_review_date = %s WHERE id = %s
        """
        self.cursor.execute(sql, (filtered_item['first_review_date'], filtered_item['id']))
        self.db.commit()
        
        return item
