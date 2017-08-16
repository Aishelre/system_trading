#-*-coding: utf-8 -*-
#2017.08.15 12:00

from datetime import datetime
import math
import collections
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
import Output_data


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

        self.output_file_name = "output.csv"
        self.bat_size = 3  # bat_size 초 동안의 데이터가 한번에 저장됨

        self.std_price = 0
        self.opening_price = 0
        self.quotes = []

        self.dict_data = collections.OrderedDict()
        self.pre_dict_data = collections.OrderedDict()
        self.data_bat = []
        self.order = collections.OrderedDict()
        self.order_bat = []

        self.prevent_overlap = 0

        self.st_data = collections.OrderedDict()
        self.st_bat = []  # 주문의 강도를 파일로 출력

    def btn_test(self):
        print("btn_test")
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "계좌번호", self.cur_account)
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "비밀번호", "0000")
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "상장폐지조회구분", "0")
        self.kiwoom.dynamicCall("SetInputValue(QString, Qstring)", "비밀번호입력매체구분", "00")

        self.kiwoom.dynamicCall("CommRqData(QString, QString, QString, QString)", "계좌조회", "OPW00004", "0", "0001")

    def printa(self):
        print("predictdata : {}".format(self.pre_dict_data))
        print("data_bat : {}".format(self.data_bat))
        print("order_bat : {}".format(self.order_bat))

    def reset_datas(self):
        del self.st_bat[:]
        del self.data_bat[:]
        del self.order_bat[:]
        self.pre_dict_data = collections.OrderedDict()
        self.quotes.clear()

        self.printa()

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
        # Tran 입력 값을 서버통신 전에 입력한다. SetInputValue 를 사용하면 OnReceiveTrData 함수가 실행된다.
        self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        # Tran을 서버로 송신한다.
        self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식기본정보", "OPT10001", 0, "0101")

    def btn_real_start(self):
        if self.status_check() == 0:
            return
        self.callback.show_log("※ 실시간 데이터 수신 시작")
        self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        self.kiwoom.dynamicCall('SetRealReg(QString, QString, QString, QString)', "0102", self.cur_code, "", "0")
        self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "주식호가요청", "OPT10004", 0, "0102")

    def btn_real_stop(self):
        if self.status_check() == 0:
            self.kiwoom.dynamicCall('SetRealRemove("All", "All")')
            return
        self.callback.show_log("※ 실시간 데이터 수신 종료", t=True)
        self.kiwoom.dynamicCall('SetRealRemove("All", "All")')

    def set_acc(self, cur_acc):  # self.cur_account 변수에, 선택한 계좌번호 입력
        self.cur_account = cur_acc
        self.callback.show_log(self.cur_account+" 선택", t=True)

    def set_passwd(self, passwd):
        self.passwd = passwd
        self.callback.show_log("패스워드 입력", t=True)

    def set_cur_code(self, cur_code):
        self.printa()
        self.reset_datas()

        self.kiwoom.dynamicCall('SetRealRemove("All", "All")')
        if self.status_check() == 0:
            return
        self.cur_code = cur_code
        self.output_file_name = self.cur_code + " - output.csv"
        self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "종목코드", self.cur_code)
        self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "기준가_시가", "OPT10001", 0, "0103")

    def set_quote(self):
        self.std_price = int(self.std_price)
        self.opening_price = abs(int(self.opening_price))

        lower_limit = math.ceil(self.std_price * 0.7)
        upper_limit = math.floor(self.std_price * 1.3)
        i = self.set_kospi_unit(lower_limit)
        j = self.set_kospi_unit(upper_limit)

        while lower_limit % i != 0:
            lower_limit += 1
        while upper_limit % j != 0:
            upper_limit -= 1
        print("하한가 : {}, 상한가 : {}".format(lower_limit, upper_limit))

        q = lower_limit
        self.dict_data.clear()
        self.dict_data['time'] = 0
        while upper_limit not in self.quotes:
            self.dict_data[q] = 0  # 호가 '잔량' 기본 셋팅
            self.order[q] = 0  # '주문량' 기본 셋팅
            self.quotes.append(q)  # 매수, 매도 시 선택할 수 있는 호가
            i = self.set_kospi_unit(q)
            q += i

        self.callback.show_quote(self.quotes, self.opening_price)

    def set_kospi_unit(self, num):
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
        #print(self.prevent_overlap)
        #if self.prevent_overlap == 1:
        #    return
        #else:
        #    self.prevent_overlap = 1

        print("신호 - 종목코드 : {}".format(sJongmokCode))

        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        data = sRealData.split('\t')[:65]
        data = list(map(int, data))
        self.callback.show_price(abs(int(data[4])))

        self.dict_data['time'] = data[0]
        for k in data_seq:  # 해당 호가에 주문 잔량을 넣어준다.
            self.dict_data[data[k]] = data[k+1]

        if len(self.pre_dict_data) == 0:  # 초기 실행일 때
            self.pre_dict_data = self.dict_data.copy()  #collections.OrderedDict(self.dict_data)
            return

        #Output_data.output_result("o_output.csv", data)
        #Output_data.dict_output_result("d_o_output.csv", self.dict_data)
        self.data_processing(data)

        #self.prevent_overlap = 0

    def data_processing(self, data):
        """
        dict 형으로 사용
        """
        data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

        if self.dict_data['time'] == self.pre_dict_data['time']:  # 같은 시간
            pass

        elif self.dict_data['time'] != self.pre_dict_data['time']:  # 다른 시간
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
                Output_data.dict_output_batch(self.output_file_name, self.pre_dict_data, self.order, self.data_bat, self.order_bat, self.bat_size)
                #Output_data.output_strength("strength.csv", self.dict_data, self.st_bat, self.bat_size)
                print("빈 시간 : {}".format(self.pre_dict_data['time']))

            for k in data_seq:  # 추가 주문량 계산
                self.order[data[k]] = self.dict_data[data[k]] - self.pre_dict_data[data[k]]
                #print("{} - {} = {}".format(self.dict_data[data[k]], self.pre_dict_data[data[k]], self.order[data[k]]))
            self.pre_dict_data = self.dict_data.copy()
            print("output 진입")
            Output_data.dict_output_batch(self.output_file_name, self.dict_data, self.order, self.data_bat, self.order_bat, self.bat_size)
            #Output_data.output_strength("strength.csv", self.dict_data, self.st_bat, self.bat_size, self.order)
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
        print("{} ※Real Data Event※".format(datetime.now().strftime("%H:%M:%S ")))

        if sRealType == "주식호가잔량":
            self.my_OnReceiveRealData(sJongmokCode, sRealType, sRealData)

    def OnReceiveTrData(self, sScrNo, sRQName, sTRCode, sRecordName, sPreNext):
        # sScrNo - 화면 번호 ex.0101
        # sRQName - 사용자 구분 명 ex.주식기본정보
        # sTRCode - Tran 명 ex.OPT10001
        # sRecordName - Record 명 ex.
        # sPreNext - 연속 조회 유무 ex.0
        print("{} ※Tr Data Event※".format(datetime.now().strftime("%H:%M:%S ")))

        if sRQName == "계좌조회":
            print("TR 계좌조회")
            list_ = []
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "총매입금액")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "예수금")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "종목코드")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "종목명")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "보유수량")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "평균단가")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "현재가")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "평가금액")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "손익금액")  # 수수료 포함 안된 금액
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "손익율")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "매입금액")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "결제잔고")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "전일매수수량")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "금일매수수량")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "전일매도수량")
            t = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", sTRCode, sRQName, 0, "금일매도수량")

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

            info_name = ["종목명","종목코드","시가","기준가","현재가","시가총액"]
            info = [name, cord, self.opening_price, self.std_price, cur_price, stock_value]

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
