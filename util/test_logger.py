# from loguru import logger
from logger import Logger
import time
# logger.add("/home/yejj/tmp/2232323.log",rotation="500MB", encoding="utf-8", enqueue=True, retention="10 days")

# logger.info('This is info information')


if __name__ =="__main__":
    test_l = Logger('alice')

    test_l.l.add("/home/yejj/tmp/2232323.log",rotation="500MB", encoding="utf-8", enqueue=True, retention="10 days")
    while True:
        test_l.l.info("this is info")
        time.sleep(20)
        
