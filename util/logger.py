from loguru import logger as loguru
import datetime
from threading import RLock
import os
import time


# one name bind one loguru handler
class LoggerFactory(object):
    LOG_FORMAT = "[{level}] {time:YYYY-MM-DD HH:mm:ss} [{extra[user_name]}]: {message}"
    lock = RLock()
    logger_dict = {}
    name_mapping = {}
    LOG_DIR = None

    # def __init__(self, name: str, file: str, **kwargs) -> None:    
    #     logger.add(file, format="{time:YYYY-MM-DD HH:mm:ss} | {extra[user_name]} | {level} |: {message}",
    #                level="INFO", encoding='utf-8', enqueue=True)
    #     self.logger = logger.bind(user_name=name)

    @staticmethod
    def set_directory(path: str):
        """set logger directory

        Args:
            path (str, optional): _description_. Defaults to '/tmp'.
            file_name (_type_, optional): _description_. Defaults to None.
        """
        with LoggerFactory.lock:
            if LoggerFactory.LOG_DIR:
                return
            LoggerFactory.LOG_DIR = path
            # make log dir
            os.makedirs(path, exist_ok=True)
            # remove history handler
            for name, log in LoggerFactory.logger_dict.items():
                loguru.remove(LoggerFactory.name_mapping[name])
            
            # refer to https://loguru.readthedocs.io/en/stable/overview.html
            loguru.remove()  # remove default stderr handler
            LoggerFactory.logger_dict = {}

    @staticmethod
    def new_logger(name: str, module_name: str):
        # name = datatime + module_name + party_name
        new_name = f"/{str(datetime.date.today()).replace('-', '_')}-{module_name}-{name}.log"
        handler_id = loguru.add(sink=LoggerFactory.LOG_DIR+new_name, 
                                format="{time:YYYY-MM-DD HH:mm:ss} | {extra[user_name]} | {level} |: {message}",
                                level="INFO", encoding='utf-8', enqueue=True,
                                filter= lambda x: name == x['extra']['user_name'])
        # logger.add 会返回一个handler_id  然后handler_id +1 
        logger = loguru.bind(user_name=name)
        # logger.setLevel(LoggerFactory.LEVEL)
        LoggerFactory.logger_dict[name] = logger
        LoggerFactory.name_mapping[name] = handler_id
        # return handler_id
    
    @staticmethod
    def get_logger(name: str, module_name: str):
        with LoggerFactory.lock:
            if name not in LoggerFactory.logger_dict:
                # print('new init logger')
                LoggerFactory.new_logger(name, module_name)
        return LoggerFactory.logger_dict[name]

    def test_cath(self, a, b):
        try:
            return a/b
        except Exception as e:
            self.logger.exception(e)
            return -1


def setDirectory(directory='/home/yejj/tmp'):
    LoggerFactory.set_directory(directory)


def getLogger(className=None, module_name='Undefined', log_dir=None):
    if className is None:
        className = 'default'
    if log_dir:
        setDirectory(log_dir)
    elif not log_dir and not LoggerFactory.LOG_DIR:
        setDirectory()
    # print(inspect.stack()[1])
    # print(inspect.getmodule(inspect.stack()[1][0]))
    return LoggerFactory.get_logger(className, module_name)


def trace(func):
    def wrapper(self, *args, **kwargs):
        # get logger handler
        try:
            # print(f"in subwrapper, name is {self.party_name}")
            log = LoggerFactory.logger_dict[self.party_name]
            start_time = time.time()
            res = func(self, *args, **kwargs)
            log.info(f"finish run {func.__name__}, cost time {time.time() - start_time}")
            return res
        except Exception as err:
            # log = LoggerFactory.logger_dict[self.party_name]
            log.exception(err)
            raise ValueError("The name of the logger is incorrect, please check the parameters.")
    return wrapper


if __name__ == "__main__":

    setDirectory('/home/yejj/tmp/')
    log = getLogger('alice', 'balabal')
    # log.info('hahahhahahahah')