#-*-coding: utf-8 -*-
import sys
import time
import collections
from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QAxContainer import *

# TODO : 특정 시간에 주문이 없을 경우에도 파일 출력 가능하게 만들기



class Singleton:
    __instance = None

    @classmethod
    def __get_instance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__get_instance
        return cls.__instance


class My_Kiwoom(Singleton):
    callback = None

    def __init__(self):
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.connect(self.kiwoom, SIGNAL("OnReceiveTrData(QString, QString, QString, QString, QString, int, QString, QString, QString)"), self.OnReceiveTrData)
        self.kiwoom.connect(self.kiwoom, SIGNAL("OnReceiveRealData(QString, QString, QString)"), self.OnReceiveRealData)
        self.kiwoom.connect(self.kiwoom, SIGNAL("OnEventConnect(int)"), self.OnEventConnect)
        self.cur_account = 0
        self.pre_data = ["0" for i in range(65)]


    def change_acc(self, cur_acc):
        self.cur_account = cur_acc
        print(self.cur_account)

    def btn_login(self):
        # 로그인 윈도우를 실행
        ret = self.kiwoom.dynamicCall("CommConnect()")

    def btn_is_connected(self):
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            print("Not connected")
        else:
            print("Connnected")
            acc_all = self.kiwoom.dynamicCall('GetLoginInfo(QString)', ["ACCNO"])
            account = acc_all[:-1].split(';')  # 계좌 리스트 마지막에 공백 문자 있음
            print(account)
            self.callback.show_account(account)

    def btn_clicked3(self):
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            print("Not connected")
            return
        # Tran 입력 값을 서버통신 전에 입력한다. SetInputValue 를 사용하면 OnReceiveTrData 함수가 실행된다.
        ret = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", "000660")
        # Tran을 서버로 송신한다.
        #ret = self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식기본정보", "OPT10001", 0, "0101")

    def btn_real_start(self):
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            print("Not connected")
            return
        print("※ 실시간 데이터 수신 시작")
        ret = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", "000660")
        ret1 = self.kiwoom.dynamicCall('SetRealReg(QString, QString, QString, QString)', "0102", "000660", "", "0")
        ret1 = self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식호가요청", "OPT10004", 0, "0102")

    def btn_real_stop(self):
        print("※ 실시간 데이터 수신 종료")
        ret = self.kiwoom.dynamicCall('SetRealRemove("All", "All")')

    def set_callback(self, the_callback):
        self.callback = the_callback

    def my_OnReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        # param[0] : 종목코드
        # param[1] : 주식호가잔량
        # param[2] : datas
        print("주문 발생")
        print("종목코드 : {}".format(sJongmokCode))

        data = sRealData.split('\t')[:65]
        self.output_result("o_output.csv", data)
        self.data_processing(data)

    def data_processing(self, cur_data):
        """
        매 초마다 (현재 물량 - 이전 물량) 으로 1초간 주문량을 구함
        매 초 처음 틱으로 구하는 것은 아님
        """
        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        if cur_data[0] == self.pre_data[0] and cur_data[1] == self.pre_data[1]:  # 같은 시간, 같은 호가창
            pass

        elif cur_data[0] != self.pre_data[0]:  # 다른 시간
            for i in data_seq:
                self.pre_data[i + 1] = int(self.pre_data[i+1])
                cur_data[i + 1] = int(cur_data[i+1])
                cur_data[i + 2] = int(cur_data[i+2])
                cur_data[i+2] = cur_data[i+1] - self.pre_data[i+1]
                self.pre_data[i + 1] = str(self.pre_data[i+1])
                cur_data[i + 1] = str(cur_data[i+1])
                cur_data[i + 2] = str(cur_data[i+2])
            self.output_result("p_output.csv", cur_data)
            self.pre_data = cur_data

        elif cur_data[0] == self.pre_data[0] and cur_data[1] != self.pre_data[1]:  # 같은 시간, 다른 호가창
            self.output_result("p_output.csv", cur_data)
            self.pre_data = cur_data

    def data_processing1(self, cur_data):
        """
        주문이 들어올 때마다
        같은 시간의 ...@#$% 좀 이상함
        """
        # cur_data, pre_data
        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        if cur_data[0] == self.pre_data[0] and cur_data[1] == self.pre_data[1]:  # 같은 시간, 같은 호가창
            for i in data_seq:
                self.pre_data[i + 1] = int(self.pre_data[i+2])
                cur_data[i + 2] = int(cur_data[i+2])
                cur_data[i+2] += self.pre_data[i+2]
                self.pre_data[i + 1] = str(self.pre_data[i+2])
                cur_data[i + 2] = str(cur_data[i+2])
            self.output_result("p_output.csv", cur_data)
        elif cur_data[0] != self.pre_data[0]:
            self.output_result("p_output.csv", cur_data)
        else:  # [0]!=[0] (다른 시간), [1]!=[1] (호가창 변경)
            pass
        pre_data = cur_data

    def output_result(self, output_file, data):
        print("※ 파일 출력 함수")
        data_seq = [58,52,46,40,34,28,22,16,10,4,1,7,13,19,25,31,37,43,49,55]  # 호가 오름차순 +1 : 잔량, +2 : 추가주문량
        try:
            with open(output_file, "at") as fp:
                fp.write(data[0] + ",")
                for i in data_seq:
                    fp.write(data[i]+",")
                fp.write("\n,")
                for i in data_seq:
                    fp.write(data[i+1]+",")
                fp.write("\n,")
                for i in data_seq:
                    fp.write(data[i+2]+",")
                fp.write("\n")
                fp.close()

        except PermissionError:
            print("************ PermissionError ************")
            with open(output_file, "at") as fp:  #+"_error.csv", "at") as fp:
                fp.write(data[0] + ",")
                for i in data_seq:
                    fp.write(data[i]+",")
                fp.write("\n,")
                for i in data_seq:
                    fp.write(data[i+1]+",")
                fp.write("\n,")
                for i in data_seq:
                    fp.write(data[i+2]+",")
                fp.write("\n")
                fp.close()
        print("* 데이터 출력 완료")

    def OnEventConnect(self, nErrCode):
        self.callback._changed(nErrCode)


    def OnReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        # sJongmokCode 종목코드
        # sRealType 리얼타입 ex.주식호가요청
        # sRealData 리얼데이터

        print("※Real Data Event※")

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


