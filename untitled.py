#-*-coding: utf-8 -*-
#2017.07.27 16:00

import math
import collections
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
import Output_data

# TODO : 특정 시간에 주문이 없을 경우에도 파일 출력 가능하게 만들기
# TODO : std_price 를 기본 값으로 설정

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
        self.kiwoom.OnEventConnect.connect(self.OnEventConnect)
        self.kiwoom.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.kiwoom.OnReceiveRealData.connect(self.OnReceiveRealData)

        self.cur_account = str()
        self.passwd = str()
        self.cur_code = str()

        self.output_file_name = "output.csv"
        self.bat_size = 3  # bat_size 초 동안의 데이터가 한번에 저장됨
        self.data_bat = []  # t초 데이터가 들어갈 리스트
        self.pre_data = [0 for i in range(65)]  # 1초 단위의 데이터를 저장하기 위해 이전 데이터와의 시간 간격을 체크

        self.std_price = 0
        self.opening_price = 0
        self.quotes = []

        self.dict_data = collections.OrderedDict()
        self.pre_dict_data = collections.OrderedDict()
        self.order = collections.OrderedDict()
        self.order_bat = []

        self.prevent_overlap = 0

        self.st_data = collections.OrderedDict()
        self.st_bat = []  # 주문의 강도를 파일로 출력

    def event_connect(self):
        pass
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
        ret = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        # Tran을 서버로 송신한다.
        ret = self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식기본정보", "OPT10001", 0, "0101")

    def btn_real_start(self):
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            print("Not connected")
            return
        print("※ 실시간 데이터 수신 시작")
        ret = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        ret = self.kiwoom.dynamicCall('SetRealReg(QString, QString, QString, QString)', "0102", self.cur_code, "", "0")
        ret = self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식호가요청", "OPT10004", 0, "0102")

    def btn_real_stop(self):
        print("※ 실시간 데이터 수신 종료")
        ret = self.kiwoom.dynamicCall('SetRealRemove("All", "All")')

    def set_acc(self, cur_acc):  # self.cur_account 변수에, 선택한 계좌번호 입력
        self.cur_account = cur_acc
        print(self.cur_account)

    def set_passwd(self, passwd):
        self.passwd = passwd
        print(self.passwd)

    def set_cur_code(self, cur_code):
        self.btn_real_stop()
        self.pre_data = [0 for i in range(65)]
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            print("Not connected")
            return
        self.cur_code = cur_code
        ret = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        ret = self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "기준가_시가", "OPT10001", 0, "0103")

    def set_quote(self):
        self.quotes.clear()
        self.std_price = int(self.std_price)
        self.opening_price = abs(int(self.opening_price))

        lower_limit = math.ceil(self.std_price * 0.7)
        upper_limit = math.floor(self.std_price * 1.3)
        i = self.set_unit(lower_limit)
        j = self.set_unit(upper_limit)

        while lower_limit % i != 0:
            lower_limit += 1
        while upper_limit % j != 0:
            upper_limit -= 1
        print("하한가 : {}, 상한가 : {}".format(lower_limit, upper_limit))

        q = lower_limit
        self.dict_data.clear()
        self.dict_data['time'] = 0
        while upper_limit not in self.quotes:
            self.quotes.append(q)  # 매수, 매도 시 선택할 수 있는 호가
            q += i
            i = self.set_unit(q)
            self.dict_data[q] = 0  # 호가 '잔량' 기본 셋팅
            self.order[q] = 0  # '주문량' 기본 셋팅

        self.callback.show_quote(self.quotes, self.opening_price)

    def set_unit(self, num):
        if num < 5000:
            i = 5
        elif num < 10000:
            i = 10
        elif num < 50000:
            i = 50
        elif num < 100000:
            i = 100
        elif num < 500000:
            i = 500
        else:
            i = 1000
        return i

    def my_OnReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        # param[0] : 종목코드
        # param[1] : 주식호가잔량
        # param[2] : datas

        #print(self.prevent_overlap)
        #if self.prevent_overlap == 1:
        #    return
        #lse:
        #    self.prevent_overlap = 1

        print("주문 발생")
        print("종목코드 : {}".format(sJongmokCode))

        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        data = sRealData.split('\t')[:65]
        data = list(map(int, data))
        self.callback.show_price(abs(int(data[4])))

        self.dict_data['time'] = data[0]

        for k in data_seq:  # 해당 호가에 주문 잔량을 넣어준다.
            self.dict_data[data[k]] = data[k+1]

        if len(self.pre_dict_data) == 0:  # 초기 실행일 때
            print("초기 실행")
            self.pre_dict_data = self.dict_data.copy()  #collections.OrderedDict(self.dict_data)
            return


        #Output_data.output_result("o_output.csv", data)
        #Output_data.dict_output_result("d_o_output.csv", self.dict_data)
        self.data_processing4(data)

        #self.prevent_overlap = 0

    def data_processing4(self, data):
        """
        dict 형으로 사용
        """
        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        if self.dict_data['time'] == self.pre_dict_data['time']:  # 같은 시간
            print("같은 시간")
            pass

        elif self.dict_data['time'] != self.pre_dict_data['time']:  # 다른 시간
            print("다른 시간")

            cur = str(self.dict_data['time'])
            pre = str(self.pre_dict_data['time'])

            cur_time = list(map(int, [cur[2:4], cur[4:]]))  # [2:4] - 분, [4:] - 초
            pre_time = list(map(int, [pre[2:4], pre[4:]]))
            empty_time = (cur_time[0]*60 + cur_time[1]) - (pre_time[0]*60 + pre_time[1])

            for i in range(1, empty_time):  # 1초 이상 주문이 없었을 때
                self.pre_dict_data['time'] += 1
                if self.pre_dict_data['time'] % 100 == 60:
                    self.pre_dict_data['time'] += 40
                for k in data_seq:
                    self.order[data[k]] = 0

                    pass
                #Output_data.dict_output_batch(self.output_file_name, self.pre_dict_data, self.data_bat, self.bat_size)
                #Output_data.output_strength("strength.csv", self.dict_data, self.st_bat, self.bat_size)
                print("빈 시간 : {}".format(self.pre_dict_data['time']))

            for k in data_seq:  # 추가 주문량 계산
                self.order[data[k]] = self.dict_data[data[k]] - self.pre_dict_data[data[k]]
                print(self.dict_data[data[k]], self.pre_dict_data[data[k]])
                print(self.order[data[k]])
            self.pre_dict_data = self.dict_data.copy()  #collections.OrderedDict(self.dict_data)
            print("output 진입")
            Output_data.dict_output_batch(self.output_file_name, self.dict_data, self.order, self.data_bat, self.order_bat, self.bat_size)
            #Output_data.output_strength("strength.csv", self.dict_data, self.st_bat, self.bat_size)
        print("data_processing 완료")


    def data_processing3(self, cur_data):
        """
        for 문을 위한 시간 데이터 따로 생성
        """
        # TODO 호가 중간중간 비는거 처리?
        # TODO 더 편한 관리를 위해 제대로 된 list 나 dict 가 필요할 듯...

        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        if cur_data[0] == self.pre_data[0]:  # 같은 시간 주문
            for k in data_seq:
                if cur_data[k] != self.pre_data[k]:  # 호가 순서가 하나라도 다르면 출력
                    cur_data_t = list(cur_data)
                    self.pre_data = cur_data_t
                    Output_data.output_batch(self.output_file_name, cur_data_t, self.data_bat, self.bat_size)
                else:  # 호가 순서가 모두 같으면 패스
                    pass

        if cur_data[0] != self.pre_data[0]:  # 다른 시간 주문, 같은 호가 순서
            for k in data_seq:
                if cur_data[k] != self.pre_data[k]:  # 호가 순서가 하나라도 다르면 패스
                    break
            pre_data_t = list(self.pre_data)
            cur_data_t = list(cur_data)

            cur = str(cur_data_t[0])
            pre = str(pre_data_t[0])

            cur_time = list(map(int, [cur[2:4], cur[4:]]))
            pre_time = list(map(int, [pre[2:4], pre[4:]]))
            empty_time = (cur_time[0]*60 + cur_time[1]) - (pre_time[0]*60 + pre_time[1])

            for i in range(1, empty_time):  # 1초 이상 주문이 없었을 때
                pre_data_t[0] += 1
                if pre_data_t[0] % 100 == 60:
                    pre_data_t[0] += 40
                for k in data_seq:
                    pre_data_t[k + 2] = 0
                # Output_data.output_result("output.csv", pre_data_t)  # 시간 꼬임
                Output_data.output_result("test.csv", pre_data_t)
                print("빈 시간 : {}".format(pre_data_t[0]))

            for i in data_seq:  # cur_data 추가 주문량 계산
                cur_data_t[i + 2] = cur_data_t[i + 1] - self.pre_data[i + 1]
            self.pre_data = cur_data_t
            Output_data.output_batch(self.output_file_name, cur_data_t, self.data_bat, self.bat_size)

        if cur_data[0] != self.pre_data[0]:  # 다른 시간, 다른 호가 순서
            # TODO 2개 이상 호가 차이 나는 경우에 대해서 관리해야함
            for k in data_seq:
                if cur_data[k] != self.pre_data[k]:  # 호가 순서가 하나라도 다르면 출력
                    pre_data_t = list(self.pre_data)
                    cur_data_t = list(cur_data)
                    if cur_data[58] - self.pre_data[58] > 0:
                        for i in range(len(data_seq) - 1):
                            k = data_seq[i]
                            cur_data_t[k + 2] = cur_data_t[k + 1] - pre_data_t[data_seq[i + 1] + 1]
                    elif cur_data[58] - self.pre_data[58] < 0:
                        for i in range(1, len(data_seq)):
                            k = data_seq[i]
                            cur_data_t[k + 2] = cur_data_t[k + 1] - pre_data_t[data_seq[i - 1] + 1]
                    Output_data.output_batch(self.output_file_name, cur_data_t, self.data_bat, self.bat_size)
                else:
                    pass

    def data_processing2(self, cur_data):
        """
        for 문을 위한 시간 데이터 따로 생성
        """
        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        if cur_data[0] == self.pre_data[0] and cur_data[1] == self.pre_data[1]:  # 같은 시간, 같은 호가 순서
            pass

        elif cur_data[0] != self.pre_data[0]:  # 다른 시간
            pre_data_t = list(self.pre_data)
            cur_data_t = list(cur_data)

            cur = str(cur_data_t[0])
            pre = str(pre_data_t[0])

            cur_time = list(map(int, [cur[2:4], cur[4:]]))
            pre_time = list(map(int, [pre[2:4], pre[4:]]))
            empty_time = (cur_time[0]*60 + cur_time[1]) - (pre_time[0]*60 + pre_time[1])

            for i in range(1, empty_time):  # 1초 이상 주문이 없었을 때
                pre_data_t[0] += 1
                if pre_data_t[0] % 100 == 60:
                    pre_data_t[0] += 40
                for k in data_seq:
                    pre_data_t[k + 2] = 0
                # Output_data.output_result("output.csv", pre_data_t)  # 시간 꼬임
                Output_data.output_result("test.csv", pre_data_t)
                print("빈 시간 : {}".format(pre_data_t[0]))

            for i in data_seq:  # cur_data 추가 주문량 계산
                cur_data_t[i + 2] = cur_data_t[i + 1] - self.pre_data[i + 1]
            self.pre_data = cur_data_t
            Output_data.output_batch(self.output_file_name, cur_data_t, self.data_bat, self.bat_size)

        elif cur_data[0] == self.pre_data[0] and cur_data[1] != self.pre_data[1]:  # 같은 시간, 다른 호가 순서
            cur_data_t = list(cur_data)
            self.pre_data = cur_data_t
            Output_data.output_batch(self.output_file_name, cur_data_t, self.data_bat, self.bat_size)

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

    def OnEventConnect(self, nErrCode):
        if nErrCode == 0:
            self.callback.show_log("로그인 성공")
        else:
            self.callback.show_log("로그인 해제")
        acc_all = self.kiwoom.dynamicCall('GetLoginInfo(QString)', ["ACCNO"])  # str type
        account = acc_all[:-1].split(';')  # 계좌 리스트 마지막에 공백 문자 있음
        self.callback.status_changed(nErrCode)  # 상태바 메시지 변경
        self.callback.refresh_account(account, nErrCode)  # combo box 에 계좌 입력

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
        if sRQName == "기준가_시가":
            self.std_price = self.kiwoom.dynamicCall('GetCommData(Qstring, Qstring, int, Qstring)', sTRCode, sRQName, 0, "기준가").strip()
            self.opening_price = self.kiwoom.dynamicCall('GetCommData(Qstring, Qstring, int, Qstring)', sTRCode, sRQName, 0, "시가").strip()
            self.btn_real_stop()
            self.set_quote()

        if sRQName == "주식기본정보":
            name = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "종목명")
            cord = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "종목코드")
            self.opening_price = self.kiwoom.dynamicCall('GetCommData(Qstring, Qstring, int, Qstring)', sTRCode, sRQName, 0, "시가")
            self.std_price = self.kiwoom.dynamicCall('GetCommData(Qstring, Qstring, int, Qstring)', sTRCode, sRQName, 0, "기준가")
            cur_price = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "현재가")
            stock_value = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "시가총액")
            cnt = self.kiwoom.dynamicCall('GetRepeatCnt(QString, QString)', sTRCode, sRQName)

            info_name = ["종목명","종목코드","시가","기준가","현재가","시가총액"]
            info = [name, cord, self.opening_price, self.std_price, cur_price, stock_value]

            self.callback.show_log("", t=True)
            for i in range(len(info)):
                info[i] = info[i].strip()
                self.callback.show_log(info_name[i]+" : "+info[i], t=False, pre="  *")

            print("{} : {}\n{} : {}\n{} : {}\n{} : {}\n{} : {}\n{} : {}"
                  .format("cnt", cnt, "sScroNo", sScrNo, "sRQName", sRQName, "sTRCode", sTRCode, "sRecordName", sRecordName, "sPreNext", sPreNext))
