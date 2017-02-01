from Queue import Queue, Empty
from urlparse import urljoin
from multiprocessing import Pool, Lock
import time

from bs4 import BeautifulSoup
import requests



def request(url, download_delay):
    time.sleep(download_delay)
    print(url)
    response = requests.get(url)
    return response


class ThreadScheduler(object):
    def __init__(self, crawler, max_concurrent_requests=10, download_delay=3):
        self.download_delay = download_delay
        self.crawler = crawler
        self.thread_pool = Pool(processes=max_concurrent_requests)

    def run(self):
        next_url = self.crawler.url_queue.get()
        while next_url:
            try:
                self.thread_pool.apply_async(request, args=(next_url, self.download_delay), callback=self.crawler.parse)
                self.crawler.url_queue.task_done()
                next_url = self.crawler.url_queue.get(timeout=10)
            except Empty:
                # maximum limit for page crawling reached. stop scheduling further threads.
                break

        self.wait_completion()

    def wait_completion(self):
        # wait to complete all existing threads.
        self.crawler.url_queue.join()
        self.thread_pool.close()
        self.thread_pool.join()


class Crawler(object):
    ANCHOR_TAG = "a"
    HREF = "href"

    def __init__(self, base_url,  max_pages_to_crawl=10, lock=None):
        self.max_pages_to_crawl = max_pages_to_crawl
        self.unique_pages = []
        self.bytes_downloaded = 0
        self.total_page_visited = 0

        self.base_url = base_url
        self.url_queue = Queue()
        self.url_queue.put(base_url)
        self.unique_pages.append(base_url)

        self.lock = lock

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
            if url not in self.unique_pages:
                self.url_queue.put(url)
                self.unique_pages.append(url)

    def update_stats(self, response):
        self.lock and self.lock.acquire()
        self.bytes_downloaded += len(response.content)
        self.total_page_visited += 1
        self.lock and self.lock.release()


    def max_limit_reached(self):
        return len(self.unique_pages) >= self.max_pages_to_crawl

    def normalize_url(self, raw_url):
        return urljoin(self.base_url, raw_url).strip('/')

    @staticmethod
    def get_response_encoding(response):
        encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
        return encoding