from datetime import datetime
import logging
import logging.handlers

#TODO 근데 trading.py에서 gui에 log출력할 때
#TODO 여러 줄에서 하지 말고 "~~\n ~~\n~~"이렇게 하면 안되나?

#TODO 각 로그에 따라 각각 디렉터리의 여러 파일에 기록한다.

date = datetime.now().strftime("%Y.%m.%d")
logger = logging.getLogger("crumbs")
logger.setLevel(logging.DEBUG)
filehandler = logging.FileHandler("./Log/" + date + " - order.log")
logger.addHandler(filehandler)

def log_order():
    # btn눌렀을 떄
    # 거래 완료 되었을 때
    #logging.basicConfig(filename="./Log/" + date + " - order.log", level=logging.DEBUG)

    logger.info("order")
    pass

def log_acc():
    #logging.basicConfig(filename="./Log/" + date + " - account.log")
    filehandler = logging.FileHandler("./Log/" + date + " - acc.log")
    logger.info("acc")
    pass

def log_info():
    # 로그인, set_code,
    #logging.basicConfig(filename="./Log/" + date + " - info.log")
    logger.info("general")
    pass

def log_trading(sign=0):
    # sign == "start"
    # sign == "stop"
    # TF_signal
    #logging.basicConfig(filename="./Log/" + date + " - trading.log")
    logger.info("trading")
    pass

log_order()
log_acc()
log_info()
log_trading()

