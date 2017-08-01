
import sys
from PyQt4 import uic
from PyQt4.QtGui import *
from datetime import datetime
import Kiwoom_stock


class My_window(QMainWindow):
    def __init__(self):

        super().__init__()
        self.ui = uic.loadUi('window.ui', self)
        self.setWindowTitle("Stock")
        self.setGeometry(100, 100, 1000, 800)

        self.statusBar().showMessage('Not Connected')

        self.ui.btn_log_in.clicked.connect(lambda : kiwoom.btn_login())
        self.ui.btn_basic.clicked.connect(lambda : kiwoom.btn_search_basic())
        self.ui.btn_start.clicked.connect(lambda : kiwoom.btn_real_start())
        self.ui.btn_stop.clicked.connect(lambda : kiwoom.btn_real_stop())

        self.ui.cb_acc.currentIndexChanged.connect(lambda : kiwoom.set_acc(self.cb_acc.currentText()))
        self.ui.list_int_code.itemClicked.connect(lambda : self.code_selected(self.list_int_code.currentItem().text()))
        self.ui.lb_cur_code.returnPressed.connect(lambda : self.code_selected(self.lb_cur_code.text()))
        self.ui.lb_passwd.returnPressed.connect(lambda : kiwoom.set_passwd(self.lb_passwd.text()))

        self.order_max = 1000000  # 한 번에 주문 할 수 있는 최대 한도 설정
        self.ui.sb_call_vol.setMaximum(self.order_max)
        self.ui.sb_put_vol.setMaximum(self.order_max)

        self.resize_table()

        with open("int_code_list.txt", "rt") as fp:  # 저장된 종목을 불러온다.
            codes = fp.read().splitlines()
            for code in codes:
                self.ui.list_int_code.addItem(code)

    def resize_table(self):
        width = 84
        self.ui.table.horizontalHeader().resizeSection(0, width)  # 종목코드
        self.ui.table.horizontalHeader().resizeSection(1, width)  # 종목명
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

    def code_selected(self, cur_code):
        self.show_log("설정된 종목 코드 : {}".format(cur_code))
        self.lb_cur_code.setText(cur_code)
        # self.ui.list_int_code.setCurrentItem(cur_code) # not working
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
