
import sys
import time
from datetime import datetime
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import threading
import Kiwoom_stock

class My_window(QMainWindow, QApplication):
    def __init__(self):
        super().__init__()
        sys.excepthook = self.excepthook

        self.ui = uic.loadUi('Trading.ui', self)
        self.setWindowTitle("Stock")

        self.statusBar().showMessage('Not Connected')

        self.ui.btn_log_in.clicked.connect(lambda : kiwoom.btn_login())
        self.ui.btn_basic_data.clicked.connect(lambda : kiwoom.btn_search_basic())
        self.ui.btn_trading.clicked.connect(lambda: kiwoom.btn_trading_start())
        self.ui.btn_stop.clicked.connect(lambda : kiwoom.btn_real_stop())
        self.ui.btn_stop.setEnabled(False)
        self.ui.btn_ref_acc.clicked.connect(lambda : kiwoom.refresh_acc())

        self.ui.btn_call_.clicked.connect(lambda: kiwoom.btn_call(int(self.cb_call_price.currentText()), self.sb_call_vol.value()))
        self.ui.btn_put_.clicked.connect(lambda: kiwoom.btn_put(int(self.cb_put_price.currentText()), self.sb_put_vol.value()))

        self.ui.cb_acc.currentIndexChanged.connect(lambda : kiwoom.set_acc(self.cb_acc.currentText()))
        self.ui.list_int_code.itemClicked.connect(lambda : self.code_selected(self.list_int_code.currentItem().text()))

        self.ui.lb_cur_code.returnPressed.connect(lambda : self.code_selected(self.lb_cur_code.text()))

        self.resize_acc_table()

        with open("int_code_list.txt", "rt") as fp:  # 저장된 종목을 불러온다.
        #with open("all_codes.txt", "rt") as fp:  # 저장된 종목을 불러온다.
            codes = fp.read().splitlines()
            for code in codes:
                self.ui.list_int_code.addItem(code)

        self.ui.btn_auto.clicked.connect(self.time_check_thread)

    def time_check_thread(self):
        thr = threading.Thread(target=self.time_check, args=())
        thr.daemon = True
        thr.start()

    def time_check(self):
        if kiwoom.cur_code() == "":
            self.ui.btn_auto.setEnabled(True)
            self.show_log("[FAILED] Auto start failed. - select CODE", t=False)
            return

        self.show_log("Auto start executed", t=True)
        self.ui.btn_auto.setEnabled(False)

        now = int(datetime.now().strftime("%H"))
        while now <= 9:
            now = int(datetime.now().strftime("%H"))
            print(now)
            if now >= 9:
                print("9시 경과. 시작")
                self.ui.btn_trading.click()  # 직접 kiwoom.btn () 을 호출하면 프로그램이 멈춘다.
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

    def excepthook(self, type, value, traceback):
        print("Unhandled Error : ", type, value, traceback)

    def refresh_acc_table(self, acc_info):
        """
        tb_acc1 : 총 매입, 총 평가
        tb_acc2 : 평가 손익, 수익률
        """
        try:
            purchase = QTableWidgetItem(acc_info[0])
            eval = QTableWidgetItem(acc_info[1])
            profit = QTableWidgetItem(acc_info[2])  # Profit and Loss
            my_yield = QTableWidgetItem(acc_info[3]+"%")  # 현재 수익률

            items = [purchase, eval, profit, my_yield]
            for i in items:
                i.setTextAlignment(Qt.AlignCenter)  # cell의 중앙 정렬
            for i, v in enumerate(items[2:], 2):  # (+ , -)에 따라서 색 입히기.
                if float(acc_info[i]) > 0:
                    v.setForeground(QColor("red"))
                elif float(acc_info[i]) < 0:
                    v.setForeground(QColor("blue"))

            self.ui.tb_acc1.setItem(0, 0, purchase)
            self.ui.tb_acc1.setItem(0, 1, eval)
            self.ui.tb_acc2.setItem(0, 0, profit)
            self.ui.tb_acc2.setItem(0, 1, my_yield)
        except:
            pass

    def refresh_acc_table2(self, acc_info):
        """
        tb_acc3 : 총 매수, 총 매도
        tb_acc4 : 부가금, 실현 손익
        """
        try:
            total_call= QTableWidgetItem(str(acc_info[0]))
            total_put= QTableWidgetItem(str(acc_info[1]))
            commission = QTableWidgetItem("-"+str(acc_info[2]))
            d_profit = QTableWidgetItem(str(acc_info[3]))

            items = [total_call, total_put, commission, d_profit]
            for i in items:
                i.setTextAlignment(Qt.AlignCenter)
            if int(acc_info[3]) > 0:
                d_profit.setForeground(QColor("red"))
            elif int(acc_info[3]) < 0:
                d_profit.setForeground(QColor("blue"))

            self.ui.tb_acc3.setItem(0, 0, total_call)
            self.ui.tb_acc3.setItem(0, 1, total_put)
            self.ui.tb_acc4.setItem(0, 0, commission)
            self.ui.tb_acc4.setItem(0, 1, d_profit)
        except:
            pass

    def refresh_acc_table_detail(self, acc_info_detail):
        """ 
        This function sets stock table.
        Followings are example datas. 
        0  :  ['A000660', 'SK하이닉스', 17300, 11.78, 73450.0, 82100, 146900, 164200, 2]
        1  :  ['A023900', '풍국주정', -2700, -24.66, 10950.0, 8250, 10950, 8250, 1]
        """
        try:
            self.ui.tb_acc_detail.setRowCount(len(acc_info_detail))
            self.ui.tb_acc_detail.setColumnCount(len(acc_info_detail[0]))

            for i in range(0, len(acc_info_detail)):
                for j in range(0, len(acc_info_detail[i])):
                    item = QTableWidgetItem(str(acc_info_detail[i][j]))
                    if j == 2 or j == 3:  # 평가손익, 손익률에 대해
                        if acc_info_detail[i][j] > 0:
                            item.setForeground(QColor("red"))
                        else:
                            item.setForeground(QColor("blue"))
                    elif j == 5 or j == 7:  # 현재가, 평가금액에 대해
                        if acc_info_detail[i][j] > acc_info_detail[i][j-1]:
                            item.setForeground(QColor("red"))
                        else:
                            item.setForeground(QColor("blue"))

                    item.setTextAlignment(Qt.AlignCenter)  # cell의 중앙 정렬
                    self.ui.tb_acc_detail.setItem(i, j, item)
            self.resize_acc_table()
        except:
            pass

    def resize_acc_table(self):
        self.ui.tb_acc1.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 수정 못하도록 설정.
        self.ui.tb_acc2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tb_acc3.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tb_acc4.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tb_acc_detail.setEditTriggers(QAbstractItemView.NoEditTriggers)

        width = 87
        self.ui.tb_acc_detail.horizontalHeader().resizeSection(0, width+5)  # 종목코드
        self.ui.tb_acc_detail.horizontalHeader().resizeSection(1, width+10)  # 종목명
        self.ui.tb_acc_detail.horizontalHeader().resizeSection(2, width)  # 평가손익
        self.ui.tb_acc_detail.horizontalHeader().resizeSection(3, width)  # 수익률
        self.ui.tb_acc_detail.horizontalHeader().resizeSection(4, width)  # 매입가
        self.ui.tb_acc_detail.horizontalHeader().resizeSection(5, width)  # 현재가
        self.ui.tb_acc_detail.horizontalHeader().resizeSection(6, width+5)  # 매입금액
        self.ui.tb_acc_detail.horizontalHeader().resizeSection(7, width+5)  # 평가금액
        self.ui.tb_acc_detail.horizontalHeader().resizeSection(8, width-20)  # 보유수량
        self.ui.tb_acc_detail.horizontalHeader().resizeSection(9, width-20)  # 가능수량


    def show_quote(self, quote, opening_price):
        self.ui.cb_call_price.clear()
        self.ui.cb_put_price.clear()

        quote = quote[::-1]
        for q in quote:
            self.ui.cb_call_price.addItem(str(q), q)
            self.ui.cb_put_price.addItem(str(q), q)
        self.ui.cb_call_price.setCurrentIndex(self.ui.cb_call_price.findData(opening_price))
        self.ui.cb_put_price.setCurrentIndex(self.ui.cb_call_price.findData(opening_price))

    def show_log(self, string, t=True, pre="", color="black"):
        nowTime = ""
        if t == True:
            nowTime = datetime.now().strftime("%H:%M:%S ")
        item = QListWidgetItem(pre+nowTime+string)
        item.setForeground(QColor(color))
        self.ui.list_log.addItem(item)
        self.ui.list_log.scrollToBottom()

    def show_order_log(self, string, t=True, pre="", color="black"):
        nowTime = ""
        if t == True:
            nowTime = datetime.now().strftime("%H:%M:%S ")
        item = QListWidgetItem(pre+nowTime+string)
        item.setForeground(QColor(color))
        self.ui.list_order_log.addItem(item)
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

