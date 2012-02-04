#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Joe Cotellese
# based on the work of Rolando Espinoza La fuente
#
# Changelog:
#   2012-02-04 - Initial version
from scrapy.contrib.loader import XPathItemLoader
from scrapy.item import Item, Field
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule, SitemapSpider
from optparse import OptionParser
import logging
logging.basicConfig()
import tldextract

class SeocrawlerItem(Item):
    # define the fields for your item here like:
    # name = Field()
    url = Field()
    title = Field()
    desc = Field()
    h1 = Field()


class SeoSpider(CrawlSpider):
    name = "seo"
    allowed_domains = []
    start_urls = []
    path_deny = [
        '/category/',
        '/tag/',
        '/page/',
    ]

    rules = (
        Rule(SgmlLinkExtractor(allow=(), deny=path_deny, allow_domains=('newcustomerworkshop.com',)), callback='parse_item', follow=True),
        )

    def __init__(self, url, allowed_domain):
        self.start_urls.append(url)
        self.allowed_domains.append(allowed_domain)
        CrawlSpider.__init__(self)
        
      
    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        item = SeocrawlerItem()
        item['url'] = response.url
        item['title'] = hxs.select('//head/title/text()').extract()
        item['desc'] = hxs.select('/html/head/meta[@content][@name="description"]/@content').extract()
        item['h1'] = hxs.select('//h1/text()').extract()
        return item

def parse_commandline():
    usage = "usage: %prog source"
    parser = OptionParser(usage=usage)
    opts,args = parser.parse_args()
    if args == []:
        parser.error("you must supply an URL to crawl")
    return parser

def main(parser):
    """Setups item signal and run the spider"""
    # set up signal to catch items scraped
    from scrapy import signals
    from scrapy.xlib.pydispatch import dispatcher

    #shut off logging to the console
    def catch_item(sender, item, **kwargs):
        pass
        
    dispatcher.connect(catch_item, signal=signals.item_passed)

    # shut off log
    from scrapy.conf import settings
    settings.overrides['LOG_ENABLED'] = False

    settings.overrides['FEED_URI'] = 'stdout.csv'
    settings.overrides['FEED_FORMAT'] = 'csv'
    # set up crawler
    from scrapy.crawler import CrawlerProcess

    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()
 
    args,opts = parser.parse_args()
    # schedule spider
    ext = tldextract.extract(opts[0])
    allowed_domain =  '.'.join(ext[1:])
    spider = SeoSpider(opts[0],allowed_domain)
    #spider.set_url('http://www.newcustomerworkshop.com')
    
    crawler.crawl(spider)

    # start engine scrapy/twisted
    print "STARTING ENGINE"
    crawler.start()
    print "ENGINE STOPPED"


if __name__ == '__main__':
    parser = parse_commandline()
    main(parser)