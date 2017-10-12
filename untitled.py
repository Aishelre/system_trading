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
import Data_Processing.Preprocessing_to_TF as Preprocessing_to_TF
#import Pyro4
#import numpy as np

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
        #self.uri = input("Pyro uri : ").strip()
        #self.transmitter = Pyro4.Proxy(self.uri)
        self.predict = 0

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.OnEventConnect.connect(self.OnEventConnect)
        self.kiwoom.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.kiwoom.OnReceiveRealData.connect(self.OnReceiveRealData)
        self.kiwoom.OnReceiveChejanData.connect(self.OnReceiveChejanData)
        self.kiwoom.OnReceiveMsg.connect(self.OnReceiveMsg)

        self.cur_account = str()
        self.cur_code = str()

        self.output_file_name = str()

        self.market = str()  # 코스피 or 코스닥

        self.now = 0
        self.std_price = 0
        self.opening_price = 0
        self.quotes = []

        self.quote_list = []
        self.pre_dict_data = collections.OrderedDict()
        self.real_data = collections.OrderedDict()

        self.stop = False

        self.today = datetime.now().strftime("%Y%m%d")

    def set_callback(self, the_callback):
        self.callback = the_callback

    def get_cur_code(self):
        return self.cur_code

    def reset_datas(self):
        self.pre_dict_data = collections.OrderedDict()
        self.quotes.clear()
        self.real_data.clear()

    def btn_login(self):
        self.kiwoom.dynamicCall("CommConnect()")

    def btn_search_basic(self):
        if self.status_check() == 0:
            return
        if self.cur_code == "":
            self.callback.show_log("Select Code")
            return
        self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식기본정보", "OPT10001", 0, "0101")

    def btn_real_start(self):
        if self.status_check() == 0:
            return
        if self.cur_code == "":
            self.callback.show_log("Select Code")
            return
        self.real_thread = threading.Thread(target=self.data_processing_thread, args=())
        self.real_thread.daemon = True
        self.real_thread.start()
        self.stop = False

        self.callback.ui.btn_real_data.setEnabled(False)
        self.callback.ui.btn_stop.setEnabled(True)

        self.callback.show_log("※ 실시간 데이터 수신 시작")
        self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        self.kiwoom.dynamicCall('SetRealReg(QString, QString, QString, QString)', "0102", self.cur_code, "", "0")
        self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식호가요청", "OPT10004", 0, "0102")

    def btn_real_stop(self):
        self.stop = True  # thread를 종료시키는 역할
        print("btn real stop")
        if self.status_check() == 0:
            self.kiwoom.dynamicCall('SetRealRemove("All", "All")')
            return

        self.callback.ui.btn_real_data.setEnabled(True)
        self.callback.ui.btn_stop.setEnabled(False)

        self.callback.show_log("※ 실시간 데이터 수신 종료", t=True)
        self.kiwoom.dynamicCall('SetRealRemove("All", "All")')

    def btn_call(self, quote, vol):
        if self.status_check() == 0 or quote == 0 or vol == 0:
            return

        sRQName = "매수"  # 사용자 구분 요청 명
        sScreenNo = "777"  # 화면 번호
        sAccNo = str(self.cur_account)  # 계좌 번호
        nOrderType = 1  # 주문 유형 (1:신규매수, 2:신규매도, 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정)
        sCode = str(self.cur_code)  # 주식 종목 코드
        nQty = vol  # 주문 수량
        nPrice = quote  # 주문 단가
        sHogaGb = "03"  # 00:지정가, 03:시장가,
        sOrgOrderNo = ""  # 원 주문 번호 (취소, 정정 시)

        print(quote, vol)
        print(sAccNo, sCode, nQty, nPrice)

        nQty = 1  # TODO 테스트용으로 항상 '1주' 구매

        self.callback.show_log("매수 주문 전송")
        self.kiwoom.dynamicCall('SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)',
                                [sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo])

    def btn_put(self, quote, vol):
        if self.status_check() == 0 or quote == 0 or vol == 0:
            return

        sRQName = "매도"  # 사용자 구분 요청 명
        sScreenNo = "778"  # 화면 번호
        sAccNo = str(self.cur_account)  # 계좌 번호
        nOrderType = 2  # 주문 유형 (1:신규매수, 2:신규매도, 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정)
        sCode = str(self.cur_code)  # 주식 종목 코드
        nQty = vol  # 주문 수량
        nPrice = quote  # 주문 단가
        sHogaGb = "03"  # 00:지정가, 03:시장가,
        sOrgOrderNo = ""  # 원 주문 번호 (취소, 정정 시)

        print(quote, vol)
        print(sAccNo, sCode, nQty, nPrice)

        nQty = 1  # TODO 테스트용으로 항상 '1주' 매도

        self.callback.show_log("매도 주문 전송")
        self.kiwoom.dynamicCall('SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)',
                                [sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo])

    def refresh_acc(self):
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "계좌번호", self.cur_account)
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "비밀번호", "0000")
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "상장폐지조회구분", "0")
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "비밀번호입력매체구분", "00")
        self.kiwoom.dynamicCall("CommRqData(QString, QString, QString, QString)", "계좌조회", "OPW00004", "0", "0001")

        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "계좌번호", self.cur_account)
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "비밀번호", "0000")
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "시작일자", self.today)
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "종료일자", self.today)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, QString, QString)", "실현손익조회", "OPT10074", "0", "0002")

    def status_check(self):
        if self.kiwoom.dynamicCall('GetConnectState()') == 0:
            self.callback.show_log("Not Connected", t=True)
            return 0
        else:
            return 1

    def show_order_log(self, signal_, code_, name_, price_, vol_):
        #  주문이 체결 된 후 호출됨.
        signal = signal_
        code = code_
        name = name_
        price = price_
        vol = vol_
        if signal == "+매수":
            self.callback.show_order_log("", t=True)
            self.callback.show_order_log("======== 매수 체결 ========", t=False, pre="  * ", color="red")
            self.callback.show_order_log(code + " " + name, t=False, pre="  * ")
            self.callback.show_order_log(str(price) + "] 원 x [" + str(vol) + "] 개 체결 완료", t=False,
                                         pre="  * [")
        elif signal == "-매도":
            self.callback.show_order_log("", t=True)
            self.callback.show_order_log("======== 매도 체결 ========", t=False, pre="  * ", color="blue")
            self.callback.show_order_log(code + " " + name, t=False, pre="  * ")
            self.callback.show_order_log(str(price) + "] 원 x [" + str(vol) + "] 개 체결 완료", t=False,
                                         pre="  * [")

    def set_acc(self, cur_acc):  # self.cur_account 변수에, 선택한 계좌번호 입력
        self.cur_account = cur_acc
        self.callback.show_log(self.cur_account+" 선택", t=True)

        if '5073' in self.cur_account or  '5134' in self.cur_account:
            self.callback.show_log(" **** WARNING **** 실제 투자 접속", t=False, color="red")
        else:
            self.callback.show_log(" * 모의 투자 * ", t=False, color="blue")
        self.refresh_acc()

    def set_cur_code(self, cur_code):
        self.reset_datas()

        self.kiwoom.dynamicCall('SetRealRemove("All", "All")')
        if self.status_check() == 0:
            return
        self.cur_code = cur_code
        self.output_file_name = "{}{}{}".format(datetime.now().strftime("%m.%d "), self.cur_code, " - output.csv")
        self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "기준가_시가", "OPT10001", 0, "0103")

        foo = self.kiwoom.GetMarketType(self.cur_code)
        if foo == 0:
            self.market = "코스피"
        elif foo == 10:
            self.market = "코스닥"

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

        q = lower_limit
        self.real_data[0] = [0,0]  # 상한가/하한가 초과 호가는 0으로 들어옴.
        self.real_data['time'] = 0
        self.real_data['now'] = 0
        while upper_limit not in self.quotes:
            self.real_data[q] = [0,0]  # [0] : 잔량, [1] : 주문량
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
            print("초기 실행 : {}")
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
        while True:
            if self.real_data['time'] == 0:
                print("신호 없음.")
                if self.stop == True:
                    break
                time.sleep(1)
                continue
            if self.stop == True:
                break
            print("Thread {}".format(datetime.now().strftime("%H:%M:%S")))
            for q in self.quote_list:  # 추가 주문량 계산
                #print(self.real_data[q][0] - self.pre_dict_data[q][0], end=" // ")
                self.real_data[q][1] = self.real_data[q][0] - self.pre_dict_data[q][0]
                #TODO 이전 잔량이 0이었다면 추가주문량을 0으로 만들어줘서
                #TODO 호가가 새로 바뀌어도 이상값이 생기지 않게 해준다.

            processed_data = Preprocessing_to_TF.process(copy.deepcopy(self.real_data), copy.deepcopy(self.quote_list))
            #self.predict = self.transmitter.wrapper(processed_data[2:])  # np.array 에 대해 argmax한 값. 0, 1, 2
            print("** predict value : ", self.predict)

            # Call trading function. Then should I reinitialize self.predict??
            if self.predict == 0:  # 주가 하락 예상
                # Call 매수/매도 함수
                # 보유량이 있는지 없는지에 따라서 매수/매도할 수 있도록 해야함.
                pass
            elif self.predict == 2:  # 주가 상승 예상
                pass

            # 데이터들을 비워주는 코드 구현해야함??
            self.pre_dict_data = copy.deepcopy(self.real_data)
            time.sleep(1)  # 1초 간격으로 재실행된다.
            # TODO 코드가 안정적인 상태로 고정되면 (1초 - thread실행 시간) 만큼 sleep한다.

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
        # sRealType 리얼타입 ex.'주식호가요청'
        # sRealData 리얼데이터
        if sRealType == "주식호가잔량":
            self.my_OnReceiveRealData_new(sJongmokCode, sRealType, sRealData)

    def OnReceiveTrData(self, sScrNo, sRQName, sTRCode, sRecordName, sPreNext):
        # sScrNo - 화면 번호 ex.0101
        # sRQName - 사용자 구분 명 ex.주식기본정보
        # sTRCode - Tran 명 ex.OPT10001
        # sRecordName - Record 명 ex.
        # sPreNext - 연속 조회 유무 ex.0
        print("{} ※Tr Data Event※".format(datetime.now().strftime("%H:%M:%S ")))

        if sRQName == "실현손익조회":
            self.total_call = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "총매수금액").strip()
            self.total_put = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0,  "총매도금액")  #
            self.commission = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "매매수수료").strip()
            self.commission = int(self.commission) + int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "매매세금").strip())
            self.profit = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "실현손익").strip()  # 이 자체가 실현손익
            self.callback.refresh_acc_table2(int(self.total_put), int(self.total_call), int(self.commission), int(self.profit))

        if sRQName == "현재가":
            self.now = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "현재가")

        if sRQName == "계좌조회":
            print("TR 계좌조회")
            #멀티데이터
            num_code = self.kiwoom.dynamicCall('GetRepeatCnt(QString, QString)', sTRCode, sRQName)
            acc_info_detail = list()
            손익금액 = 0
            for cnt in range(num_code):
                list_ = []
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "종목코드") #
                list_.append(t.strip())
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "종목명") #
                list_.append(t.strip())
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "손익금액")  #
                list_.append(int(t))
                손익금액 += int(t)
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "손익율") # %값으로 출력됨.
                list_.append(round(float(t), 4))
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "평균단가") # 매입 평균 단가
                list_.append(round(float(t), 4))
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "현재가") #
                list_.append(int(t))
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "매입금액") # (평균단가 * 보유 수량)
                list_.append(int(t))
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "평가금액") # (현재가 * 보유 수량)
                list_.append(int(t))
                t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, cnt, "보유수량") #
                list_.append(int(t))
                acc_info_detail.append(list_)

            if num_code != 0:
                self.callback.refresh_acc_table_detail(acc_info_detail)
            elif num_code == 0:
                self.callback.ui.tb_acc_detail.setRowCount(0)

            #싱글데이터
            acc_info = list()
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "총매입금액")  # 총 매입
            acc_info.append(int(t))
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "유가잔고평가액")  # 총 평가
            acc_info.append(int(t))
            acc_info.append(손익금액)  # 멀티 데이터에서 계산한 손익금액
            if float(acc_info[0] == 0.0):  # 매입이 0일 때
                현재수익률 = 0
            else:
                현재수익률 = str(round(float(손익금액) / float(acc_info[0]), 4) * 100)
            acc_info.append(현재수익률)
            acc_info = list(map(str, acc_info))

            self.callback.refresh_acc_table(acc_info)

        if sRQName == "매수":
            print("TR - 매수")
            print(sTRCode)  # KOA_NORMAL_BUY_KP_ORD
            pass

        if sRQName == "매도":
            print("TR - 매도")
            print(sTRCode)  # KOA_NORMAL_SELL_KP_ORD
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
            self.kiwoom.dynamicCall('SetRealRemove("All", "All")')

            info_name = ["종목명","종목코드", "시장", "시가","기준가","현재가"]
            info = [name, cord, self.market, self.opening_price, self.std_price, cur_price]

            self.callback.show_log("", t=True)
            for i in range(len(info)):
                info[i] = info[i].strip()
                self.callback.show_log(info_name[i]+" : "+info[i], t=False, pre="  * ")

    def OnReceiveChejanData(self, sGubun, nItemCnt, sFidList):
        # sGubun – 체결 구분 - '0': 주문체결통보, '1': 잔고통보, '3': 특이신호
        # nItemCnt - 아이템 갯수
        # sFidList – 데이터 리스트 - 데이터 구분은 ‘;’ 이다.
        #print(sGubun, type(sGubun))
        #print(nItemCnt)
        #print(sFidList)

        fid_list = sFidList.split(';')
        #for fid in fid_list:
        #    result = self.kiwoom.dynamicCall("GetChejanData(int)", int(fid))
        #    print("fid : {}, result : {}".format(fid, result))

        # 주문 -> 체결
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
            [901] = 주문가격  # 시장가 주문일 경우 0
            [902] = 미체결수량
            [903] = 체결누계금액  # "체결"시에만 체결누계(?)금액 출력.
            [904] = 원주문번호
            [905] = 주문구분
            [906] = 매매구분
            [907] = 매도수구분
            [908] = 주문/체결시간
            [909] = 체결번호
            [910] = 체결가 ####
            [911] = 체결량 ####
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
            signal = self.kiwoom.dynamicCall("GetChejanData(int)", 905)  # "+매수" or "-매도"
            c = self.kiwoom.dynamicCall("GetChejanData(int)", 9001)
            n = self.kiwoom.dynamicCall("GetChejanData(int)", 302).strip()
            p = self.kiwoom.dynamicCall("GetChejanData(int)", 901)
            v = self.kiwoom.dynamicCall("GetChejanData(int)", 900)

            if self.kiwoom.dynamicCall("GetChejanData(int)", 913) == '접수':
                if signal == "+매수":
                    color = "red"
                else:
                    color = "blue"
                self.callback.show_order_log("", t=True)
                self.callback.show_order_log(n + " [" + p + "]원 [" + v + "]주 " + signal, pre="[접수] ", t=False, color=color)
            elif self.kiwoom.dynamicCall("GetChejanData(int)", 913) == '체결':
                self.show_order_log(signal, c, n, p, v)
                self.refresh_acc()

            L = [9203,9205,9001,912,913,302,900,901,902,903,904,905,906,907,908,909,910,911,10,27,28,914,915,938,939,919,920,921,922,923]
            #for i in L:
            #    print("{} : {}".format(i, self.kiwoom.dynamicCall("GetChejanData(int)", i)))
        # 잔고 통보
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
            #for i in L:
            #    print("{} : {}".format(i, self.kiwoom.dynamicCall("GetChejanData(int)", i)))
        else:
            print("기타 케이스")

    def OnReceiveMsg(self, sScrNo, sRQName, sTrCode, sMsg):
        if sScrNo == "777":  # 매수
            self.callback.show_log(sMsg, pre="[M] ", color="purple")
        elif sScrNo == "778":  # 매도
            self.callback.show_log(sMsg, pre="[M] ", color="purple")
        else:
            self.callback.show_log(sMsg, pre="[M] ", color="purple")
