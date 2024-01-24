#!/bin/bash
cd /www/wwwroot/admin.jadeous.com/crontab/scrapy_etsy

export PATH=/usr/local/bin:$PATH
nohup scrapy crawl shop  >./run.log 2>&1 &
nohup scrapy crawl firstreviewdate  >./run.log 2>&1 &