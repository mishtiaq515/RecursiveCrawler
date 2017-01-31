from Queue import Queue, Empty
from urlparse import urljoin
from multiprocessing import Pool
import time

from bs4 import BeautifulSoup
import requests


def request(url, download_delay):
    print("waiting %s" % url)
    time.sleep(download_delay)
    print("wait end %s" % url)
    response = requests.get(url)

    print("finished %s" % url)
    return response


class ThreadScheduler(object):
    def __init__(self, crawler, max_concurrent_requests=10, download_delay=0):
        self.download_delay = download_delay
        self.crawler = crawler
        self.thread_pool = Pool(processes=max_concurrent_requests)

    def run(self):
        next_url = self.crawler.url_queue.get()
        while next_url:
            try:
                self.thread_pool.apply_async(request, args=(next_url, self.download_delay), callback=self.crawler.parse)
                next_url = self.crawler.url_queue.get(timeout=10)
                self.crawler.url_queue.task_done()
            except Empty:
                # no more link to process
                print('no more link to process')
                break
        self.thread_pool.close()
        self.thread_pool.join()

        print("Page visited: %s, Bytes downloaded: %s"
              % (len(self.crawler.visited_pages), self.crawler.bytes_downloaded))


class Crawler(object):
    ANCHOR_TAG = "a"
    HREF = "href"

    def __init__(self, base_url, max_pages_to_crawl=10):
        self.max_pages_to_crawl = max_pages_to_crawl
        self.visited_pages = []
        self.bytes_downloaded = 0
        self.base_url = base_url

        self.url_queue = Queue()
        self.url_queue.put(base_url)
        self.visited_pages.append(base_url)

    def parse(self, response):
        """
        Extract all links from response and put
        in the queue for processing.
        """
        self.update_stats(response)
        encoding = self.get_response_encoding(response)
        soup = BeautifulSoup(response.content, from_encoding=encoding)
        for element in soup.find_all(self.ANCHOR_TAG, href=True):
            if self.max_limit_reached():
                break
            url = element[self.HREF]
            url = self.normalize_url(url)
            if url not in self.visited_pages:
                self.url_queue.put(url)
                self.visited_pages.append(url)

    def update_stats(self, response):
        self.bytes_downloaded += len(response.content)

    def max_limit_reached(self):
        return len(self.visited_pages) >= self.max_pages_to_crawl

    def normalize_url(self, raw_url):
        return urljoin(self.base_url, raw_url)

    @staticmethod
    def get_response_encoding(response):
        encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
        return encoding