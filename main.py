from crawler import Crawler, ThreadScheduler
from constants import SITE_URL, MAX_PAGES_TO_CRAWL, MAX_CONCURRENT_REQUESTS, DOWNLOAD_DELAY


if __name__ == "__main__":
    crawler = Crawler(base_url=SITE_URL, max_pages_to_crawl=MAX_PAGES_TO_CRAWL)
    thread_scheduler = ThreadScheduler(crawler=crawler, max_concurrent_requests=MAX_CONCURRENT_REQUESTS,
                                       download_delay=DOWNLOAD_DELAY)
    thread_scheduler.run()

    print("Page visited: %s, Bytes downloaded: %s"
          % (crawler.total_page_visited, crawler.bytes_downloaded))
