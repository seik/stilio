from stilio.persistence import database as db
from stilio.crawler.dht.crawling import CrawlingService

if __name__ == "__main__":
    db.init()
    crawler = CrawlingService()
    crawler.run()
