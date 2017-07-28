#-*-coding: utf-8 -*-
#2017.07.27 16:00

import collections
from PyQt4.QtCore import *
from PyQt4.QAxContainer import *
import Output_data
from datetime import datetime

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
        self.cur_code = 0
        self.pre_data = ["0" for i in range(65)]  # 1초 단위의 데이터를 저장하기 위해 이전 데이터와의 시간 간격을 체크
        self.bat_size = 5  # bat_size 초 동안의 데이터가 한번에 저장됨
        self.data_bat = []  # t초 데이터가 들어갈 리스트
        self.output_file_name = "output.csv"

    def set_callback(self, the_callback):
        self.callback = the_callback

    def btn_login(self):
        # 로그인 윈도우를 실행
        ret = self.kiwoom.dynamicCall("CommConnect()")

    def btn_search_basic(self):
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            print("Not connected")
            return
        # Tran 입력 값을 서버통신 전에 입력한다. SetInputValue 를 사용하면 OnReceiveTrData 함수가 실행된다.
        ret = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", "000660")
        # Tran을 서버로 송신한다.
        ret = self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식기본정보", "OPT10001", 0, "0101")

    def btn_real_start(self):
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            print("Not connected")
            return
        print("※ 실시간 데이터 수신 시작")
        ret1 = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", "036630")
        ret1 = self.kiwoom.dynamicCall('SetRealReg(QString, QString, QString, QString)', "0102", "036630", "", "0")
        ret1 = self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식호가요청", "OPT10004", 0, "0102")

    def btn_real_stop(self):
        print("※ 실시간 데이터 수신 종료")
        ret = self.kiwoom.dynamicCall('SetRealRemove("All", "All")')

    def change_acc(self, cur_acc):  # self.cur_account 변수에, 선택한 계좌번호 입력
        self.cur_account = cur_acc
        print(self.cur_account)

    def change_cur_code(self, cur_code):
        self.cur_code = cur_code
        print(self.cur_code)

    def my_OnReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        # param[0] : 종목코드
        # param[1] : 주식호가잔량
        # param[2] : datas
        print("주문 발생")
        print("종목코드 : {}".format(sJongmokCode))

        data = sRealData.split('\t')[:65]

        if self.pre_data[0] == "0":
            self.pre_data = data
            return
        Output_data.output_result("o_output.csv", data)
        #self.data_processing(data)
        self.data_processing2(data)

    def data_processing(self, cur_data):
        """
        매 초마다 (현재 물량 - 이전 물량) 으로 1초간 주문량을 구함
        매 초 처음 틱으로 구하는 것은 아님
        """
        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        if cur_data[0] == self.pre_data[0] and cur_data[1] == self.pre_data[1]:  # 같은 시간, 같은 호가 순서
            pass

        elif cur_data[0] != self.pre_data[0]:  # 다른 시간
            for i in data_seq:
                self.pre_data[i + 1] = int(self.pre_data[i + 1])
                cur_data[i + 1] = int(cur_data[i + 1])
                cur_data[i + 2] = int(cur_data[i + 2])
                cur_data[i + 2] = cur_data[i + 1] - self.pre_data[i + 1]
                self.pre_data[i + 1] = str(self.pre_data[i + 1])
                cur_data[i + 1] = str(cur_data[i + 1])
                cur_data[i + 2] = str(cur_data[i + 2])
            self.pre_data = cur_data
            Output_data.output_batch(self.output_file_name, cur_data, self.data_bat, self.bat_size)
        elif cur_data[0] == self.pre_data[0] and cur_data[1] != self.pre_data[1]:  # 같은 시간, 다른 호가 순서
            self.pre_data = cur_data
            Output_data.output_batch(self.output_file_name, cur_data, self.data_bat, self.bat_size)

    def data_processing2(self, cur_data):
        """
        주문이 없던 시간의 데이터도 0으로 채워서 저장함
        """
        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]
        test = []
        if cur_data[0] == self.pre_data[0] and cur_data[1] == self.pre_data[1]:  # 같은 시간, 같은 호가 순서
            pass

        elif cur_data[0] != self.pre_data[0]:  # 다른 시간
            t = int(self.pre_data[0])
            for i in range(int(self.pre_data[0]) + 1, int(cur_data[0])):  # 1초 이상 주문이 없었을 때
                if int(self.pre_data[0]) % 100 == 59:
                    break
                t += 1
                self.pre_data[0] = str(t)
                for k in data_seq:
                    self.pre_data[k + 2] = "0"
                test = self.pre_data
                Output_data.output_result("test.csv", test) #self.pre_data)
                print(self.pre_data[0])


            for i in data_seq:
                self.pre_data[i + 1] = int(self.pre_data[i + 1])
                cur_data[i + 1] = int(cur_data[i + 1])
                cur_data[i + 2] = int(cur_data[i + 2])
                cur_data[i + 2] = cur_data[i + 1] - self.pre_data[i + 1]
                self.pre_data[i + 1] = str(self.pre_data[i + 1])
                cur_data[i + 1] = str(cur_data[i + 1])
                cur_data[i + 2] = str(cur_data[i + 2])
            self.pre_data = cur_data
            Output_data.output_batch(self.output_file_name, cur_data, self.data_bat, self.bat_size)

        elif cur_data[0] == self.pre_data[0] and cur_data[1] != self.pre_data[1]:  # 같은 시간, 다른 호가 순서
            self.pre_data = cur_data
            Output_data.output_batch(self.output_file_name, cur_data, self.data_bat, self.bat_size)

    def OnEventConnect(self, nErrCode):
        acc_all = self.kiwoom.dynamicCall('GetLoginInfo(QString)', ["ACCNO"])
        account = acc_all[:-1].split(';')  # 계좌 리스트 마지막에 공백 문자 있음
        self.callback.status_changed(nErrCode)  # 상태바 메시지 변경
        self.callback.show_account(account)  # combo box 에 계좌 입력

    def set_cur_code(self, cur_code):
        self.cur_code = cur_code


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

        if sRQName == "관심종목조회":
            print("관종조회")
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
