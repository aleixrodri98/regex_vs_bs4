# -*- coding: utf-8 -*-
import bs4
import re
import timeit
import utils
from lxml.html import fromstring
from scrapy.selector import Selector


class BaseCrawler(object):
    def __init__(self, page):
        self.page = page
        self.parser = None

    def get_extra_info_patterns(self):
        raise NotImplementedError()

    def extract(self):
        raise NotImplementedError()


class DummyRegexCrawler(BaseCrawler):
    def get_extra_info_patterns(self) -> dict:
        """Return regex based extra_info patterns."""
        return {
            'title': re.compile(r'<h1 class="title-link">(.*?)</h1>'),
            'postingDate': re.compile(r'date:</strong>\s*?(.+)</div>'),
            'postingUser': re.compile(r'posted by:\s*?</strong>\s*?<a href=".*?">(.*)</a>'),
            'postingUserUrl': re.compile(r'posted by:\s*?</strong>\s*?<a href="(.*?)">'),
        }

    def extract(self):
        results = []
        for key, pattern in self.get_extra_info_patterns().items():
            data = pattern.search(self.page)
            if data:
                results.append(data.group(0))
        return results


class DummyBs4Crawler(BaseCrawler):
    def get_extra_info_patterns(self) -> dict:
        return {
            'title': self.parser.find('h1', class_='title-link'),
            'postingDate': self.parser.find('div', class_='post-date'),
            'postingUser': self.parser.find('div', class_='author'),
            'postingUserUrl': self.parser.find('div', class_='author').find('a').get('href'),
        }

    def extract(self):
        self.parser = bs4.BeautifulSoup(str(self.page), 'lxml')
        results = []
        for key, pattern in self.get_extra_info_patterns().items():
            if pattern:
                results.append(pattern)
        return results

class DummyLxmlCrawler(BaseCrawler):
    def get_extra_info_patterns(self) -> dict:
        return {
            'title': self.parser.xpath('/html/body/div[3]/div/div[2]/div[8]/div/div/h1/text()'),
            'postingDate': self.parser.xpath('/html/body/div[3]/div/div[2]/div[8]/div/div/div[2]/text()'),
            'postingUser': self.parser.xpath('/html/body/div[3]/div/div[2]/div[8]/div/div/div[1]/a/text()'),
            'postingUserUrl': self.parser.xpath('/html/body/div[3]/div/div[2]/div[8]/div/div/div[1]/a/@href'),
        }

    def extract(self):
        self.parser = fromstring(str(self.page))
        results = []
        for key, pattern in self.get_extra_info_patterns().items():
            if pattern:
                results.append(pattern)
        return results

class DummyScrapyCrawler(BaseCrawler):
    def get_extra_info_patterns(self) -> dict:
        return {
            'title': self.parser.xpath('/html/body/div[3]/div/div[2]/div[8]/div/div/h1/text()').extract(),
            'postingDate': self.parser.xpath('/html/body/div[3]/div/div[2]/div[8]/div/div/div[2]/text()').extract(),
            'postingUser': self.parser.xpath('/html/body/div[3]/div/div[2]/div[8]/div/div/div[1]/a/text()').extract(),
            'postingUserUrl': self.parser.xpath('/html/body/div[3]/div/div[2]/div[8]/div/div/div[1]/a/@href').extract(),
        }

    def extract(self):
        self.parser = Selector(text=str(self.page))
        results = []
        for key, pattern in self.get_extra_info_patterns().items():
            if pattern:
                results.append(pattern)
        return results

def performance_test(crawler):
    results = crawler.extract()

    assert len(results) == 4

    return results


if __name__ == '__main__':
    # https://avxhm.se/music/Monty_Python_Soundtracks_Collection.html
    some_page = utils.load_html('page.html').lower()
    regex_crawler = DummyRegexCrawler(some_page)

    bs4_crawler = DummyBs4Crawler(some_page)

    lxml_crawler = DummyLxmlCrawler(some_page)

    scrapy_crawler = DummyScrapyCrawler(some_page)

    print(timeit.timeit('performance_test(regex_crawler)', number=100, globals=globals()))
    print(timeit.timeit('performance_test(bs4_crawler)', number=100, globals=globals()))
    print(timeit.timeit('performance_test(lxml_crawler)', number=100, globals=globals()))
    print(timeit.timeit('performance_test(scrapy_crawler)', number=100, globals=globals()))

    assert performance_test(regex_crawler) == performance_test(bs4_crawler)
