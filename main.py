from multiprocessing import freeze_support
from crawler import Crawler, ThreadScheduler
from constants import site_url

if __name__ == "__main__":
    freeze_support()
    crawler = Crawler(base_url=site_url)
    thread_scheduler = ThreadScheduler(crawler=crawler)
    thread_scheduler.run()
