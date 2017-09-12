
import sys
import time
from multiprocessing import Process
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
from datetime import datetime
import Kiwoom_stock
import threading

class My_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('window.ui', self)
        self.setWindowTitle("Stock")

        self.statusBar().showMessage('Not Connected')

        self.ui.btn_log_in.clicked.connect(lambda : kiwoom.btn_login())
        self.ui.btn_basic_data.clicked.connect(lambda : kiwoom.btn_search_basic())
        self.ui.btn_real_data.clicked.connect(lambda: kiwoom.btn_real_start())
        self.ui.btn_stop.clicked.connect(lambda : kiwoom.btn_real_stop())
        self.ui.btn_stop.setEnabled(False)
        self.ui.btn_test_.clicked.connect(lambda : kiwoom.btn_test())

        self.ui.btn_call_.clicked.connect(lambda: kiwoom.btn_call(int(self.cb_call_price.currentText()), self.sb_call_total.value()))
        self.ui.btn_put_.clicked.connect(lambda: kiwoom.btn_put(int(self.cb_put_price.currentText()), self.sb_call_total.value()))

        self.ui.cb_acc.currentIndexChanged.connect(lambda : kiwoom.set_acc(self.cb_acc.currentText()))
        self.ui.list_int_code.itemClicked.connect(lambda : self.code_selected(self.list_int_code.currentItem().text()))

        self.ui.lb_cur_code.returnPressed.connect(lambda : self.code_selected(self.lb_cur_code.text()))
        self.ui.lb_passwd.returnPressed.connect(lambda : kiwoom.set_passwd(self.lb_passwd.text()))

        self.order_max = 500000  # 한 번에 주문 할 수 있는 최대 한도 설정
        self.ui.sb_call_total.setMaximum(self.order_max)
        self.ui.sb_put_total.setMaximum(self.order_max)

        self.resize_table()

        with open("int_code_list.txt", "rt") as fp:  # 저장된 종목을 불러온다.
        #with open("all_codes.txt", "rt") as fp:  # 저장된 종목을 불러온다.
            codes = fp.read().splitlines()
            for code in codes:
                self.ui.list_int_code.addItem(code)

        """
        multi threading으로 10분 sleep으로  9시, 15시가 지났는지 확인.
        지났으면 시작/종료. 10분동안 쓰레드가 정지이므로 while보다 나을 듯.
        """

        self.ui.btn_auto.clicked.connect(self.time_check_thread)

    def time_check_thread(self):
        thr = threading.Thread(target=self.time_check, args=())
        thr.daemon = True
        thr.start()

    def time_check(self):
        if kiwoom.get_cur_code() == "":
            self.ui.btn_auto.setEnabled(True)
            self.show_log("FAILED : Auto start failed. - select CODE", t=False)
            return

        self.show_log("Auto start executed", t=True)
        self.ui.btn_auto.setEnabled(False)

        now = int(datetime.now().strftime("%H"))
        while now <= 9:
            now = int(datetime.now().strftime("%H"))
            print(now)
            if now >= 9:
                print("9시 경과. 시작")
                self.ui.btn_real_data.click()  # 직접 kiwoom.btn () 을 호출하면 프로그램이 멈춘다.
                break
            else:
                print("9시 이전")
                time.sleep(600)  # 10분
        time.sleep(1)
        while True:
            now = int(datetime.now().strftime("%H"))
            print(now)
            if now >= 15:
                print("15시. 종료")
                self.ui.btn_stop.click()
                break
            else:
                print("15시 이전")
                time.sleep(600)  # 10분
        self.ui.btn_auto.setEnabled(True)


    def resize_table(self):
        width = 76
        self.ui.table.horizontalHeader().resizeSection(0, width)  # 종목코드
        self.ui.table.horizontalHeader().resizeSection(1, width+19)  # 종목명
        self.ui.table.horizontalHeader().resizeSection(2, width)  # 평가손익
        self.ui.table.horizontalHeader().resizeSection(3, width)  # 수익률
        self.ui.table.horizontalHeader().resizeSection(4, width)  # 매입가
        self.ui.table.horizontalHeader().resizeSection(5, width)  # 현재가
        self.ui.table.horizontalHeader().resizeSection(6, width)  # 손익분기
        self.ui.table.horizontalHeader().resizeSection(7, width)  # 매입금액
        self.ui.table.horizontalHeader().resizeSection(8, width)  # 평가금액
        self.ui.table.horizontalHeader().resizeSection(9, width)  # 보유수량
        self.ui.table.horizontalHeader().resizeSection(10, width)  # 가능수량

    def show_quote(self, quote, opening_price):
        self.ui.cb_call_price.clear()
        self.ui.cb_put_price.clear()

        quote = quote[::-1]
        for q in quote:
            self.ui.cb_call_price.addItem(str(q), q)
            self.ui.cb_put_price.addItem(str(q), q)
        self.ui.cb_call_price.setCurrentIndex(self.ui.cb_call_price.findData(opening_price))
        self.ui.cb_put_price.setCurrentIndex(self.ui.cb_call_price.findData(opening_price))

    def show_log(self, string, t=True, pre=""):
        nowTime = ""
        if t == True:
            nowTime = datetime.now().strftime("%H:%M:%S ")
        self.ui.list_log.addItem(pre+nowTime+string)
        self.ui.list_log.scrollToBottom()

    def show_order_log(self, string, t=True, pre=""):
        nowTime = ""
        if t == True:
            nowTime = datetime.now().strftime("%H:%M:%S ")
        self.ui.list_order_log.addItem(pre+nowTime+string)
        self.ui.list_order_log.scrollToBottom()

    def code_selected(self, cur_code):
        self.show_log("◈{}◈".format(cur_code))
        cur_code = cur_code.split(' ')[0]
        self.lb_cur_code.setText(cur_code)
        kiwoom.set_cur_code(cur_code)

    def show_price(self, price):
        self.ui.lb_price.setText(str(price))

    def refresh_account(self, acc_list, nErrCode):
        self.ui.cb_acc.clear()
        if nErrCode == 0:  # 로그인 성공
            for acc in acc_list:
                self.ui.cb_acc.addItem(acc)

    def status_changed(self, nErrCode):
        if nErrCode == 0:  # 로그인 성공
            self.statusBar().showMessage("Connected")
        else:
            self.statusBar().showMessage("Not Connected")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = My_window()

    kiwoom = Kiwoom_stock.My_Kiwoom.instance()
    kiwoom.set_callback(myWindow)
    myWindow.show()
    app.exec_()
