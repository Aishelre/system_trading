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

def log_trading(msg):
    # sign == "start"
    # sign == "stop"
    # TF_signal
    logger = setup_logger("trading")
    logger.info(msg)



if not os.path.exists("./Log"):  # Log directory가 없으면 생성한다.
    os.makedirs("./Log")

init_logger()

if __name__ == "__main__":
    pass

