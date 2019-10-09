from stilio.crawler.dht.crawling import CrawlingService
from stilio.persistence import utils as db_utils

if __name__ == "__main__":
    db_utils.init()
    crawler = CrawlingService()
    crawler.run()
