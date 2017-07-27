
import sys
from PyQt4 import uic
from PyQt4.QtGui import *
import Kiwoom_stock


class My_window(QMainWindow):
    def __init__(self):

        super().__init__()
        self.ui = uic.loadUi('window.ui', self)
        self.setWindowTitle("Stock")
        self.setGeometry(300, 300, 600, 400)

        self.statusBar().showMessage('Not Connected')

        self.ui.btn_log_in.clicked.connect(lambda : kiwoom.btn_login())
        self.ui.btn_connected.clicked.connect(lambda : kiwoom.btn_is_connected())
        self.ui.btn_search.clicked.connect(lambda : kiwoom.btn_clicked3())
        self.ui.btn_start.clicked.connect(lambda : kiwoom.btn_real_start())
        self.ui.btn_stop.clicked.connect(lambda : kiwoom.btn_real_stop())

        self.ui.cb_acc.currentIndexChanged.connect(lambda : kiwoom.change_acc(self.cb_acc.currentText()))

    def updateStatusBar(self, string):
        self.statusBar().showMessage(string)

    def show_account(self, acc_list):
        for acc in acc_list:
            self.ui.cb_acc.addItem(acc)
    def status_changed(self, nErrCode):
        if nErrCode == 0:  # 로그인 성공
            self.statusBar().showMessage("Connected")
            #  계좌 박스를 채운다. show_account 함수 실행?
        else:
            self.statusBar().showMessage("Not Connected")
            #  계좌 박스를 비운다.


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = My_window()

    kiwoom = Kiwoom_stock.My_Kiwoom.instance()
    kiwoom.set_callback(myWindow)
    myWindow.show()
    app.exec_()
