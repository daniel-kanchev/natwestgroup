import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from natwestgroup.items import Article


class NatwestSpider(scrapy.Spider):
    name = 'natwest'
    start_urls = ['https://www.natwestgroup.com/news.html']

    def parse(self, response):
        links = response.xpath('//a[@class="automated-list__item-title"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get().strip()
        date = response.xpath('//p[@class="blog-publish-date"]/text()').get().strip()
        date = datetime.strptime(date, '%d %b %Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//div[@class="comp-rich-text"]//text()').getall()[:-5]
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()
        category = response.xpath('(//a[@class="tag-list-item"])[1]/text()').get()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('category', category)

        return item.load_item()
