from datetime import datetime
import logging
import logging.handlers
import os


def init_logger():
    formatter = logging.Formatter("%(asctime)s : %(message)s")
    date = datetime.now().strftime("%Y.%m.%d")
    names = ["order", "info", "account", "trading"]
    for name in names:
        logger = logging.getLogger(name)
        handler = logging.FileHandler("./Log/"+date+" - "+name+".log")
        handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

def setup_logger(name):
    logger = logging.getLogger(name)
    return logger

def log_order(msg):
    # btn눌렀을 떄
    # 거래 완료 되었을 때
    logger = setup_logger("order")
    logger.info(msg)

def log_acc(msg):
    logger = setup_logger("account")
    logger.info(msg)

def log_info(msg):
    # 로그인, set_code,
    logger = setup_logger("info")
    logger.info(msg)

def log_trading(msg, sign=0):
    # sign == "start"
    # sign == "stop"
    # TF_signal
    logger = setup_logger("trading")
    logger.info(msg+str(sign))



if not os.path.exists("./Log"):  # Log directory가 없으면 생성한다.
    os.makedirs("./Log")

init_logger()

if __name__ == "__main__":
    log_order("asd")
    log_acc("awe")
    log_info("azz")
    log_trading("n")
    log_order("asd22")
    log_acc("awe22")
    log_info("azz22")
    log_trading("n22")
    log_order("asd2233")
    log_acc("awe2233")
    log_info("azz2233")
    log_trading("n2233")

