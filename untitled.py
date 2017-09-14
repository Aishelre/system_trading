#-*-coding: utf-8 -*-

from datetime import datetime
import math
import collections
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
import Output_data
import time
import threading
import copy


#TODO 상한가에 대한 경우도 생각해야함.

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
        self.kiwoom.OnReceiveChejanData.connect(self.OnReceiveChejanData)

        self.cur_account = str()
        self.passwd = str()
        self.cur_code = str()

        self.output_file_name = str()
        self.st_file_name = str()
        self.market = str()  # 코스피 or 코스닥
        self.bat_size = 3  # bat_size 초 동안의 데이터가 한번에 저장됨

        self.now = 0
        self.std_price = 0
        self.opening_price = 0
        self.quotes = []

        self.quote_list = []
        self.pre_dict_data = collections.OrderedDict()
        self.data_bat = []
        self.order = collections.OrderedDict()
        self.order_bat = []

        self.prevent_overlap = 0

        self.st_data = collections.OrderedDict()
        self.st_bat = []  # 주문의 강도를 파일로 출력

        self.stop = False
        self.real_data = collections.OrderedDict()

    def get_cur_code(self):
        return self.cur_code

    def btn_test(self):
        self.kiwoom.dynamicCall("")

        print("btn_test")
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "계좌번호", self.cur_account)
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "비밀번호", "0000")
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "상장폐지조회구분", "0")
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "비밀번호입력매체구분", "00")

        self.kiwoom.dynamicCall("CommRqData(QString, QString, QString, QString)", "계좌조회", "OPW00004", "0", "0001")

    def reset_datas(self):
        del self.st_bat[:]
        del self.data_bat[:]
        del self.order_bat[:]
        self.pre_dict_data = collections.OrderedDict()
        self.quotes.clear()

        self.order.clear()

        self.real_data.clear()

    def set_callback(self, the_callback):
        self.callback = the_callback

    def status_check(self):
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            self.callback.show_log("Not Connected", t=True)
            return 0
        else:
            return 1

    def btn_call(self, quote, total):
        if self.status_check() == 0 or (quote == total ==0):
            return

        sRQName = "매수"  # 사용자 구분 요청 명
        sScreenNo = "1010"  # 화면 번호
        sAccNo = str(self.cur_account)  # 계좌 번호
        nOrderType = 1  # 주문 유형 (1:신규매수, 2:신규매도, 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정)
        sCode = str(self.cur_code)  # 주식 종목 코드
        nQty = math.floor(total / quote)  # 주문 수량
        nPrice = quote  # 주문 단가
        sHogaGb = "00"  # 00:지정가, 03:시장가,
        sOrgOrderNo = ""  # 원 주문 번호 (취소, 정정 시)

        print(quote, total)
        print(sAccNo, sCode, nQty, nPrice)

        nQty = 1  # TODO 테스트용으로 항상 '1주' 구매

        self.callback.show_log("매수 주문 전송")
        self.kiwoom.dynamicCall('SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)',
                                [sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo])

    def btn_put(self, quote, total):
        if self.status_check() == 0:
            return
        self.callback.show_log("매도 주문 전송")
        pass

    def show_order_log(self, signal_, code_, name_, price_, vol_, total_):
        signal = signal_
        code = code_
        name = name_
        price = price_
        vol = vol_
        total = price * vol

        self.callback.show_order_log("", t=True)
        self.callback.show_order_log("========< " + signal + " >========", t=False, pre="  * ")
        self.callback.show_order_log(code + " " + name, t=False, pre="  * ")
        self.callback.show_order_log(str(price) + "] 원 x [" + str(vol) + "] 개 = [" + str(total) + "] 원", t=False, pre="  * [")

    def btn_login(self):
        # 로그인 윈도우를 실행
        self.kiwoom.dynamicCall("CommConnect()")

    def btn_search_basic(self):
        if self.status_check() == 0:
            return
        self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식기본정보", "OPT10001", 0, "0101")

    def btn_real_start(self):
        self.real_thread = threading.Thread(target=self.data_processing_thread, args=())
        self.real_thread.start()
        self.stop = False

        print("btn real start")
        if self.status_check() == 0:
            return
        self.callback.ui.btn_real_data.setEnabled(False)
        self.callback.ui.btn_stop.setEnabled(True)

        self.callback.show_log("※ 실시간 데이터 수신 시작")
        self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        self.kiwoom.dynamicCall('SetRealReg(QString, QString, QString, QString)', "0102", self.cur_code, "", "0")
        self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식호가요청", "OPT10004", 0, "0102")

    def btn_real_stop(self):
        self.stop = True
        print("btn real stop")
        if self.status_check() == 0:
            self.kiwoom.dynamicCall('SetRealRemove("All", "All")')
            return
        self.callback.ui.btn_real_data.setEnabled(True)
        self.callback.ui.btn_stop.setEnabled(False)


        self.callback.show_log("※ 실시간 데이터 수신 종료", t=True)
        self.kiwoom.dynamicCall('SetRealRemove("All", "All")')

    def set_acc(self, cur_acc):  # self.cur_account 변수에, 선택한 계좌번호 입력
        self.cur_account = cur_acc
        self.callback.show_log(self.cur_account+" 선택", t=True)

    def set_passwd(self, passwd):
        self.passwd = passwd
        self.callback.show_log("패스워드 입력", t=True)

    def set_cur_code(self, cur_code):
        self.reset_datas()

        self.kiwoom.dynamicCall('SetRealRemove("All", "All")')
        if self.status_check() == 0:
            return
        self.cur_code = cur_code
        self.output_file_name = "{}{}{}".format(datetime.now().strftime("%m.%d "), self.cur_code, " - output.csv")
        self.st_file_name = "{}{}{}".format(datetime.now().strftime("%m.%d "), self.cur_code, " - strength.csv")
        self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "기준가_시가", "OPT10001", 0, "0103")

        foo = self.kiwoom.GetMarketType(self.cur_code)
        if foo == 0:
            self.market = "코스피"
        elif foo == 10:
            self.market = "코스닥"
        #else:
        #   #throw Error

    def set_quote(self):
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
        self.real_data.clear()
        self.order.clear()
        self.real_data['time'] = 0
        self.real_data['now'] = 0
        while upper_limit not in self.quotes:
            self.real_data[q] = [0,0]  # [0] : 잔량, [1] : 주문량
            self.order[q] = 0  # '주문량' 기본 셋팅
            self.quotes.append(q)  # 매수, 매도 시 선택할 수 있는 호가
            i = self.set_unit(q)
            q += i

        self.callback.show_quote(self.quotes, self.opening_price)

    def set_unit(self, num):
        if self.market == "코스피":
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
        elif self.market == "코스닥":
            if num < 1000:
                i = 1
            elif num < 5000:
                i = 5
            elif num < 10000:
                i = 10
            else:
                i = 100
            return i
        else :
            print("시장 구분 에러.")

    def my_OnReceiveRealData_new(self, sJongmokCode, sRealType, sRealData):
        #print(self.prevent_overlap)
        #if self.prevent_overlap == 1:
        #    return
        #else:
        #    self.prevent_overlap = 1
        #self.prevent_overlap = 0 # 이 함수 제일 마지막에 넣어야 함.

        #print("★ new event handler 신호 - 종목코드 : {}".format(sJongmokCode))
        print("pre : ", self.pre_dict_data)
        print("cur : ", self.real_data)

        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        data = sRealData.split('\t')[:65]
        data = list(map(int, data))
        data = list(map(abs, data))

        self.real_data['time'] = data[0]
        self.real_data['now'] = data[4]
        self.callback.show_price(abs(int(data[4])))  # GUI에 매수1 가격 보여줌

        self.quote_list = [data[k] for k in data_seq]  # 이벤트로 들어온 호가 리스트를 저장한다.
        for k in range(0,10):  # 해당 호가에 주문 잔량을 넣어준다.
            idx = data_seq[k]
            self.real_data[data[idx]][0] = data[idx+1]

        for k in range(10,20):  # 매도 호가의 주문 잔량은 기본적으로 (-)이다.
            idx = data_seq[k]
            self.real_data[data[idx]][0] = -1 * data[idx+1]

        if len(self.pre_dict_data) == 0 or self.pre_dict_data['time'] == 0:  # 초기 실행일 때
            print("초기 실행 : {}".format(self.pre_dict_data))
            self.pre_dict_data = copy.deepcopy(self.real_data)
            return

    def data_processing_thread(self):
        """
        btn_real_start를 누르면
        주문이 안들어와도 계속 실행된다.
        btn_real_stop을 누르면 종료.
        
        self.output_file_name
        self.quote_list         20개의 호가 정보 리스트. 이 리스트를 참조하여 위의 [호가]에 접근한다.
        """

        """
         print("Thread {}".format(datetime.now().strftime("%H:%M:%S")))
                    for q in self.quote_list:  # 추가 주문량 계산
                        self.order[q] = self.dict_data[q] - self.pre_dict_data[q]
                    self.pre_dict_data = self.dict_data.copy()

                    d = collections.OrderedDict(self.dict_data)
                    self.data_bat.append(d)
                    o = collections.OrderedDict(self.order)
                    self.order_bat.append(o)

                    for i in self.order:
                        self.order[i] = 0  # 주문 가능 호가가 변경되는 경우, 주문 불가능 호가에 주문량이 저장되는 것을 방지

                    if len(self.data_bat) >= self.bat_size:  # bat_size 개 정보가 들어 있으면
                        with open("testthrea", "at") as fp:
                            for i in range(0, len(self.data_bat)):
                                fp.write("time" + "," + "now" + ",")
                                for j in range(0, len(self.quote_list)):
                                    fp.write(str(self.quote_list[j]) + ",")
                                fp.write("\n")

                                fp.write(str(self.data_bat[i]['time']) + ',' + str(self.data_bat[i]["now"]) + ',')
                                for q in self.quote_list:
                                    fp.write(str(self.data_bat[i][q]) + ',')
                                fp.write("\n,,")

                                for q in self.quote_list:
                                    fp.write(str(self.order_bat[i][q]) + ',')
                                fp.write("\n")

                            fp.close()
                        print(" ** NEW DICT 출력 완료 ** ")
                        del self.data_bat[:]
                        del self.order_bat[:]

                    self.pre_dict_data = self.dict_data.copy()

                    if self.stop == True:
                        break
                    else:
                        # 데이터들을 비워준다. pre데이터에 cur데이터를 넣어준다. (order계산을 위해)
                        # ...
                        time.sleep(1)  # 1초 간격으로 재실행된다.
                    pass
                    """
        while True:
            print("Thread {}".format(datetime.now().strftime("%H:%M:%S")))
            for q in self.quote_list:  # 추가 주문량 계산
                print("{} - {} = {} ".format(self.real_data[q][0], self.pre_dict_data[q][0], self.real_data[q][0] - self.pre_dict_data[q][0]))
                self.real_data[q][1] = self.real_data[q][0] - self.pre_dict_data[q][0]
                #TODO 이전 잔량이 0이었다면 추가주문량을 0으로 만들어줘서
                #TODO 호가가 새로 바뀌어도 이상값이 생기지 않게 해준다.
            #print("DATA : ", end="")
            #for q in self.quote_list:
            #    print("( {} - {} )".format(q, self.real_data[q]), end=", ")
            #print()

            # output data
            Output_data.output_for_thr("Thread output test.csv", self.real_data, self.quote_list)

            if self.stop == True:
                break
            else:
                # 데이터들을 비워주는 코드 구현해야함.
                self.pre_dict_data = copy.deepcopy(self.real_data)
                time.sleep(1)  # 1초 간격으로 재실행된다.


    def data_processing_new(self, quote_list):
        """
        list를 사용하면 호가창 변경시 추가 주문량을 계산 할 수가 없기 때문에 dict를 무조건 써야함.
        data에 들어온 호가들을 리스트에 저장하고,
        이 호가들을 key로 하는 dict에 for문을 통해 접근한다.
        """
        return
        if self.dict_data['time'] == self.pre_dict_data['time']:  # 같은 시간
            pass

        elif self.dict_data['time'] != self.pre_dict_data['time']:  # 다른 시간
            cur = str(self.dict_data['time'])
            pre = str(self.pre_dict_data['time'])

            cur_time = list(map(int, [cur[:-4], cur[-4:-2], cur[-2:]]))  # [0:-4] - 시. [-4:-2] - 분, [-2:] - 초
            pre_time = list(map(int, [pre[:-4], pre[-4:-2], pre[-2:]]))
            empty_time = (cur_time[0] - pre_time[0]) * 3600 + (cur_time[1] - pre_time[1]) * 60 + (
            cur_time[2] - pre_time[2])  # 1시간 이상 비는 경우는 고려 안함.

            for i in range(1, empty_time):  # 1초 이상 주문이 없었을 때
                self.pre_dict_data['time'] += 1
                if self.pre_dict_data['time'] % 100 == 60:  # ex) 9:58:60 -> 9:59:00
                    self.pre_dict_data['time'] += 40
                if int(self.pre_dict_data['time'] / 100) % 100 == 60:  # ex) 9:60:00 -> 10:00:00
                    self.pre_dict_data['time'] += 4000

                for q in quote_list:
                    self.order[q] = 0
                Output_data.dict_output_batch_new(self.output_file_name, self.pre_dict_data, self.order, self.data_bat,
                                              self.order_bat, self.bat_size, quote_list)
                print("NEW 빈 시간 : {}".format(self.pre_dict_data['time']))

            for q in quote_list:  # 추가 주문량 계산
                self.order[q] = self.dict_data[q] - self.pre_dict_data[q]
            self.pre_dict_data = self.dict_data.copy()
            Output_data.dict_output_batch_new(self.output_file_name, self.dict_data, self.order, self.data_bat,
                                          self.order_bat, self.bat_size, quote_list)

            print("{} NEW data_processing 완료".format(datetime.now().strftime("%H:%M:%S ")))

    def my_OnReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        #print(self.prevent_overlap)
        #if self.prevent_overlap == 1:
        #    return
        #else:
        #    self.prevent_overlap = 1
        return
        print("신호 - 종목코드 : {}".format(sJongmokCode))
        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        data = sRealData.split('\t')[:65]
        data = list(map(int, data))
        data = list(map(abs, data))
        self.callback.show_price(abs(int(data[4])))  # gui에 매수1 가격 보여줌

        self.dict_data['time'] = data[0]
        self.dict_data['now'] = data[4]  # 매수 1

        for k in data_seq:  # 해당 호가에 주문 잔량을 넣어준다.
            self.dict_data[data[k]] = data[k+1]
            #print(data[k], data[k+1])

        if len(self.pre_dict_data) == 0:  # 초기 실행일 때
            self.pre_dict_data = self.dict_data.copy()  # shallow copy
            return

        self.data_processing(data)
        self.data_processing_new()
        #self.prevent_overlap = 0

    def data_processing(self, data):
        """
        dict 형으로 사용
        """
        return
        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        if self.dict_data['time'] == self.pre_dict_data['time']:  # 같은 시간
            pass

        elif self.dict_data['time'] != self.pre_dict_data['time']:  # 다른 시간
            cur = str(self.dict_data['time'])
            pre = str(self.pre_dict_data['time'])

            #cur_time = list(map(int, [cur[2:4], cur[4:]]))  # [2:4] - 분, [4:] - 초 #TODO 9시 데이터는 9mmss라서 문제 발생 -1 -2 -3 이용
            #pre_time = list(map(int, [pre[2:4], pre[4:]]))
            # empty_time = (cur_time[0]*60 + cur_time[1]) - (pre_time[0]*60 + pre_time[1])

            cur_time = list(map(int, [cur[:-4], cur[-4:-2], cur[-2:]])) # [0:-4] - 시. [-4:-2] - 분, [-2:] - 초
            pre_time = list(map(int, [pre[:-4], pre[-4:-2], pre[-2:]]))
            empty_time = (cur_time[0] - pre_time[0]) * 3600 + (cur_time[1] - pre_time[1]) * 60 + (cur_time[2] - pre_time[2]) # 1시간 이상 비는 경우는 고려 안함.

            for i in range(1, empty_time):  # 1초 이상 주문이 없었을 때
                self.pre_dict_data['time'] += 1
                if self.pre_dict_data['time'] % 100 == 60: # ex) 9:58:60 -> 9:59:00
                    self.pre_dict_data['time'] += 40
                if int(self.pre_dict_data['time']/100) % 100 == 60: # ex) 9:60:00 -> 10:00:00
                    self.pre_dict_data['time'] += 4000

                for k in data_seq:
                    self.order[data[k]] = 0
                Output_data.dict_output_batch(self.output_file_name, self.pre_dict_data, self.order, self.data_bat, self.order_bat, self.bat_size)
                #Output_data.output_strength(self.st_file_name, self.dict_data, self.st_bat, self.bat_size, self.order)
                print("빈 시간 : {}".format(self.pre_dict_data['time']))

            for k in data_seq:  # 추가 주문량 계산
                self.order[data[k]] = self.dict_data[data[k]] - self.pre_dict_data[data[k]]
                #print("{} - {} = {}".format(self.dict_data[data[k]], self.pre_dict_data[data[k]], self.order[data[k]]))
            self.pre_dict_data = self.dict_data.copy()
            Output_data.dict_output_batch(self.output_file_name, self.dict_data, self.order, self.data_bat, self.order_bat, self.bat_size)
            #Output_data.output_strength(self.st_file_name, self.dict_data, self.st_bat, self.bat_size, self.order)
            #self.order.clear()

        print("{} data_processing 완료".format(datetime.now().strftime("%H:%M:%S ")))

    def OnEventConnect(self, nErrCode):
        if nErrCode == 0:
            self.callback.show_log("로그인 성공")
        else:
            self.callback.show_log("로그인 해제")
        acc_all = self.kiwoom.dynamicCall('GetLoginInfo(QString)', ["ACCNO"])  # str type
        account = acc_all[:-1].split(';')  # 계좌 리스트 마지막에 공백 문자 있음
        self.callback.status_changed(nErrCode)  # 상태바 메시지 변경
        self.callback.refresh_account(account, nErrCode)  # combo box 에 계좌 입력

        for acc in account:
            if '5073' in acc:
                self.callback.show_log(" **** WARNING **** 실제 투자 접속", t=False)
            else:
                self.callback.show_log(" * 모의 투자 * ", t=False)

    def OnReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        # sJongmokCode 종목코드
        # sRealType 리얼타입 ex.'주식호가요청'
        # sRealData 리얼데이터
        # print("{} ※Real Data Event※".format(datetime.now().strftime("%H:%M:%S ")))

        if sRealType == "주식호가잔량":
            #self.my_OnReceiveRealData(sJongmokCode, sRealType, sRealData)
            self.my_OnReceiveRealData_new(sJongmokCode, sRealType, sRealData)

    def OnReceiveTrData(self, sScrNo, sRQName, sTRCode, sRecordName, sPreNext):
        # sScrNo - 화면 번호 ex.0101
        # sRQName - 사용자 구분 명 ex.주식기본정보
        # sTRCode - Tran 명 ex.OPT10001
        # sRecordName - Record 명 ex.
        # sPreNext - 연속 조회 유무 ex.0
        print("{} ※Tr Data Event※".format(datetime.now().strftime("%H:%M:%S ")))
        if sRQName == "현재가":
            self.now = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "현재가")

        if sRQName == "계좌조회":
            print("TR 계좌조회")
            num_code = self.kiwoom.dynamicCall('GetRepeatCnt(QString, QString)', sTRCode, sRQName)
            acc_info = dict()
            for cnt in range(num_code):
                list_ = []
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "종목코드")
                list_.append(t.strip())
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "종목명")
                list_.append(t.strip())
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "보유수량")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "총매입금액")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "예수금")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "평균단가")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "현재가")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "평가금액")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt,
                                           "손익금액")  # 수수료 포함 안된 금액
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "손익율")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "매입금액")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "결제잔고")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "전일매수수량")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "금일매수수량")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "전일매도수량")
                list_.append(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "금일매도수량")
                list_.append(t)
                acc_info[cnt] = list_

            for i in acc_info:
                print(i, " : ", acc_info[i])


        if sRQName == "매수":
            print("TR - 매수")
            print(sTRCode)
            pass

        if sRQName == "매도":
            print("TR - 매도")
            print(sTRCode)
            pass

        if sRQName == "기준가_시가":
            self.std_price = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "기준가").strip()
            self.opening_price = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "시가").strip()
            self.kiwoom.dynamicCall('SetRealRemove("All", "All")')
            self.set_quote()

        if sRQName == "주식기본정보":
            name = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "종목명")
            cord = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "종목코드")
            self.opening_price = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "시가")
            self.std_price = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "기준가")
            cur_price = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "현재가")
            stock_value = self.kiwoom.dynamicCall('GetCommData(QString, QString, int, QString)', sTRCode, sRQName, 0, "시가총액")
            cnt = self.kiwoom.dynamicCall('GetRepeatCnt(QString, QString)', sTRCode, sRQName)
            self.kiwoom.dynamicCall('SetRealRemove("All", "All")')

            info_name = ["종목명","종목코드", "시장", "시가","기준가","현재가","시가총액"]
            info = [name, cord, self.market, self.opening_price, self.std_price, cur_price, stock_value]

            self.callback.show_log("", t=True)
            for i in range(len(info)):
                info[i] = info[i].strip()
                self.callback.show_log(info_name[i]+" : "+info[i], t=False, pre="  * ")
            #print("{} : {}\n{} : {}\n{} : {}\n{} : {}\n{} : {}\n{} : {}"
            #      .format("cnt", cnt, "sScroNo", sScrNo, "sRQName", sRQName, "sTRCode", sTRCode, "sRecordName", sRecordName, "sPreNext", sPreNext))

    def OnReceiveChejanData(self, sGubun, nItemCnt, sFidList):
        # sGubun – 체결 구분 - '0': 주문체결통보, '1': 잔고통보, '3': 특이신호
        # nItemCnt - 아이템 갯수
        # sFidList – 데이터 리스트 - 데이터 구분은 ‘;’ 이다.
        print(sGubun, type(sGubun))
        print(nItemCnt)
        print(sFidList)

        fid_list = sFidList.split(';')
        for fid in fid_list:
            result = self.kiwoom.dynamicCall("GetChejanData(int)", int(fid))
            print("fid : {}, result : {}".format(fid, result))

        # 주문 -> 체결 -> 잔고 통보
        if sGubun == '0':
            """
            [9201] = 계좌번호
            [9203] = 주문번호
            [9205] = 관리자사번
            [9001] = 종목코드,업종코드
            [912] = 주문업무분류
            [913] = 주문상태
            [302] = 종목명
            [900] = 주문수량
            [901] = 주문가격
            [902] = 미체결수량
            [903] = 체결누계금액
            [904] = 원주문번호
            [905] = 주문구분
            [906] = 매매구분
            [907] = 매도수구분
            [908] = 주문/체결시간
            [909] = 체결번호
            [910] = 체결가
            [911] = 체결량
            [10] = 현재가
            [27] = (최우선)매도호가
            [28] = (최우선)매수호가
            [914] = 단위체결가
            [915] = 단위체결량
            [938] = 당일매매수수료
            [939] = 당일매매세금
            [919] = 거부사유
            [920] = 화면번호
            [921] = 터미널번호
            [922] = 신용구분(실시간 체결용)
            [923] = 대출일(실시간 체결용)
            """
            if self.kiwoom.dynamicCall("GetChejanData(int)", 913) == '접수':
                self.callback.show_order_log("주문 접수 완료", t=True)
            if self.kiwoom.dynamicCall("GetChejanData(int)", 913) == '체결':
                self.callback.show_order_log("주문 체결 완료", t=True)

            L = [9203,9205,9001,912,913,302,900,901,902,903,904,905,906,907,908,909,910,911,10,27,28,914,915,938,939,919,920,921,922,923]
            for i in L:
                print("{} : {}".format(i, self.kiwoom.dynamicCall("GetChejanData(int)", i)))

        elif sGubun == '1':
            """
            [9201] = 계좌번호
            [9001] = 종목코드,업종코드
            [917] = 신용구분
            [916] = 대출일
            [302] = 종목명
            [10] = 현재가
            [930] = 보유수량
            [931] = 매입단가
            [932] = 총매입가
            [933] = 주문가능수량
            [945] = 당일순매수량
            [946] = 매도/매수구분
            [950] = 당일총매도손일
            [951] = 예수금
            [27] = (최우선)매도호가
            [28] = (최우선)매수호가
            [307] = 기준가
            [8019] = 손익율
            [957] = 신용금액
            [958] = 신용이자
            [918] = 만기일
            [990] = 당일실현손익(유가)
            [991] = 당일실현손익률(유가)
            [992] = 당일실현손익(신용)
            [993] = 당일실현손익률(신용)
            [959] = 담보대출수량
            [924] = Extra Item
            """
            print("잔고 통보")
            L = [9001,917,916,302,10,930,931,932,933,945,946,950,951,27,28,307,8019,957,958,918,990,991,992,993,959,924]
            for i in L:
                print("{} : {}".format(i, self.kiwoom.dynamicCall("GetChejanData(int)", i)))
        else:
            print("기타 케이스")
