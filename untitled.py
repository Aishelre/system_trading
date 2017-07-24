#-*-coding: utf-8 -*-
import sys
import time
import collections
from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QAxContainer import *

# TODO :


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('window.ui', self)
        self.setWindowTitle("Stock")
        self.setGeometry(300, 300, 600, 400)

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        #self.kiwoom.connect(self.kiwoom, SIGNAL("OnReceiveTrData(QString, QString, QString, QString, QString, int, QString, QString, QString)"), self.OnReceiveTrData)
        self.kiwoom.connect(self.kiwoom, SIGNAL("OnReceiveRealData(QString, QString, QString)"), self.OnReceiveRealData)
        #self.connect(self.ui.btn_log_in, SIGNAL("clicked()"), self.btn_clicked1) # 이전 코드
        self.ui.btn_log_in.clicked.connect(lambda : self.btn_clicked1())
        self.ui.btn_is_connected.clicked.connect(lambda : self.btn_clicked2())
        self.ui.btn_search.clicked.connect(lambda : self.btn_clicked3())
        self.ui.btn_real_time.clicked.connect(lambda : self.btn_clicked4())
        self.ui._btn_stop.clicked.connect(lambda : self.btn_stop())

    def OnEventConnect(self):
        pass

    def my_OnReceiveRealData(self, *param):
        # param[0] : 종목코드
        # param[1] : 주식호가잔량
        # param[2] : datas
        print("주문 발생")
        print("{}".format(param[1]))
        print("종목코드 : {}".format(param[0]))
        print(param[2])


    def OnReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        # sJongmokCode 종목코드
        # sRealType 리얼타입 ex.주식호가요청
        # sRealData 리얼데이터

        if sRealType == "주식호가잔량":
            self.my_OnReceiveRealData(sJongmokCode, sRealType, sRealData)


    def OnReceiveTrData(self, sScrNo, sRQName, sTRCode, sRecordName, sPreNext):
        # sScrNo - 화면 번호 ex.0101
        # sRQName - 사용자 구분 명 ex.주식기본정보
        # sTRCode - Tran 명 ex.OPT10001
        # sRecordName - Record 명 ex.
        # sPreNext - 연속 조회 유무 ex.0

        print("※Tr Data Event※")

        if sRQName == "주식기본정보":
            cnt = self.kiwoom.dynamicCall('GetRepeatCnt(QString, QString)', sTRCode, sRQName)
            name = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', sTRCode, "", sRQName, 0, "종목명")
            cord = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', sTRCode, "", sRQName, 0, "종목코드")
            cur_price = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', sTRCode, "", sRQName, 0, "현재가")
            stock_value = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', sTRCode, "", sRQName, 0, "시가총액")

            주식_기본_정보 = collections.OrderedDict()
            주식_기본_정보["종목명"] = name
            주식_기본_정보["종목코드"] = cord
            주식_기본_정보["현재가"] = cur_price
            주식_기본_정보["시가총액"] = stock_value

            for key, v in 주식_기본_정보.items():
                print("{} : {}".format(key, v.strip()))
            print("{} : {}\n{} : {}\n{} : {}\n{} : {}\n{} : {}\n{} : {}"
                  .format("cnt", cnt, "sScroNo", sScrNo, "sRQName", sRQName, "sTRCode", sTRCode, "sRecordName", sRecordName, "sPreNext", sPreNext))

        if sRQName == "주식호가요청":
            print("※주식 호가 요청")
            sell = ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1"]
            buy = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


            """
            for i in range(5):
                주식_호가_요청_매도 = dict({})
                주식_호가_요청_매수 = dict({})
                for num in sell:
                    #s1 = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', "매도"+num+"차선잔량대비")
                    #s2 = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', "매도"+num+"차선잔량")
                    #s3 = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', "매도"+num+"차선호가")

                    주식_호가_요청_매도[num] = [s1. s2. s3]


                #z1 = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', "매도최우선잔량")
                #z2 = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', "매도최우선호가")
                s2 = self.kiwoom.dynamicCall('GetCommRealData("s1", 61)')
                s2 = self.kiwoom.dynamicCall('GetCommRealData("s1", 61)')

                for num in buy:
                    # b1 = self.kiwoom.dynamicCall(commGetData() ~~~, "매도"+num+"차선잔량대비")
                    # b2 = self.kiwoom.dynamicCall(commGetData() ~~~, "매도"+num+"차선잔량")
                    # b3 = self.kiwoom.dynamicCall(commGetData() ~~~, "매도"+num+"차선호가")
                    # 주식_호가_요청_매수[num] = [a1. a2. a3]
                    pass
                    # z3 = self.kiwoom.dynamicCall(commGetData() ~~~, "매수최우선잔량")
                    # z4 = self.kiwoom.dynamicCall(commGetData() ~~~, "매수최우선호가")

                print(주식_호가_요청_매도)
                print(주식_호가_요청_매수)
                time.sleep(1)
"""

    def btn_clicked1(self):
        # 로그인 윈도우를 실행
        ret = self.kiwoom.dynamicCall("CommConnect()")

    def btn_clicked2(self):
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            print("Not connected")
        else:
            print("Connnected")

    def btn_clicked3(self):
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            print("Not connected")
            return
        # Tran 입력 값을 서버통신 전에 입력한다. SetInputValue 를 사용하면 OnReceiveTrData 함수가 실행된다.
        ret = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", "000660")
        # Tran을 서버로 송신한다.
        #ret = self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식기본정보", "OPT10001", 0, "0101")

    def btn_clicked4(self):
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            print("Not connected")
            return
        print("※ 실시간 데이터 수신 시작")
        ret1 = self.kiwoom.dynamicCall('SetRealReg(QString, QString, QString, QString)', "0102", "000660", "", "0")
        ret1 = self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식호가요청", "OPT10004", 0, "0102")

    def btn_stop(self):
        print("※ 실시간 데이터 수신 종료")
        ret = self.kiwoom.dynamicCall('SetRealRemove("All", "All")')



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
