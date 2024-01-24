import scrapy


class EtsyshopItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    url = scrapy.Field()
    logo_url = scrapy.Field()
    description = scrapy.Field()
    stars = scrapy.Field()
    location = scrapy.Field()
    announcement = scrapy.Field()
    announcement_last_updated = scrapy.Field()
    product = scrapy.Field()
    product_on_sale = scrapy.Field()
    sales = scrapy.Field()
    admirers = scrapy.Field()
    review = scrapy.Field()
    review_page = scrapy.Field()
    star_seller = scrapy.Field()
    on_etsy_since = scrapy.Field()
    first_review_date = scrapy.Field()
    free_shipping = scrapy.Field()
    instagram = scrapy.Field()
    facebook = scrapy.Field()
    pinterest = scrapy.Field()
    twitter = scrapy.Field()
    websites = scrapy.Field()
    not_selling = scrapy.Field()
    taking_break = scrapy.Field()
    # pass
    
    #设置item里面的每一项默认都为None，避免在pipelines.py里面读取的时候出现类似KeyError
    def __init__(self, *args, **kwargs):
        super(EtsyshopItem, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.setdefault(field, None)
    
    
class EtsyshopsalesItem(scrapy.Item):
    # name = scrapy.Field()
    shop_id = scrapy.Field()
    sales = scrapy.Field()
    reviews = scrapy.Field()
    star_seller = scrapy.Field()
    product = scrapy.Field()
    product_on_sale = scrapy.Field()
    stars = scrapy.Field()
    admirers = scrapy.Field()
    date = scrapy.Field()
    created_at = scrapy.Field()
    # pass
    
    #设置item里面的每一项默认都为None，避免在pipelines.py里面读取的时候出现类似KeyError
    def __init__(self, *args, **kwargs):
        super(EtsyshopsalesItem, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.setdefault(field, None)
    
class EtsyfirstreviewdateItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    first_review_date = scrapy.Field()
    # pass
    
    #设置item里面的每一项默认都为None，避免在pipelines.py里面读取的时候出现类似KeyError
    def __init__(self, *args, **kwargs):
        super(EtsyfirstreviewdateItem, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.setdefault(field, None)

