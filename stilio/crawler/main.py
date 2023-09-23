from stilio.crawler.dht.crawling import CrawlingService
from stilio.persistence import database

if __name__ == "__main__":
    database.init()
    crawler = CrawlingService()
    crawler.run()
