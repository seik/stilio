from stilio.persistence import database
from stilio.crawler.dht.crawling import CrawlingService

if __name__ == "__main__":
    database.init()
    crawler = CrawlingService()
    crawler.run()
