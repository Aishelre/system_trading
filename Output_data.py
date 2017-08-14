# 17.07.27 16:00

import collections
from datetime import datetime

def output_strength(output_file, data, st_bat, bat_size):
    test = collections.OrderedDict(data)
    for k in test.keys():
        print("for")
        if k == 'time':
            continue
        pre_remain = test[k][0] - test[k][1]
        if pre_remain == 0:
            test[k] = 0
            continue
        else:
            test[k] = test[k][1] / pre_remain * 100
    st_bat.append(test)
    print(len(st_bat))

    if len(st_bat) >= bat_size:  # bat_size 개 정보가 들어 있으면
        with open(output_file, "at") as fp:
            for i in range(0, len(st_bat)):
                fp.write(str(st_bat[i]['time']) + ",")
                for key in st_bat[i].keys():
                    fp.write(str(key) + ",")
                fp.write("\n,")
                for st in st_bat.values():
                    fp.write(str(st) + ",")
                fp.write("\n")
            fp.close()
        print(" ** STRENGTH 출력 완료 ** ")
        del st_bat[:]

def dict_output_batch(output_file, data, order, data_bat, order_bat, bat_size):
    d = collections.OrderedDict(data)
    data_bat.append(d)
    o = collections.OrderedDict(order)
    order_bat.append(o)
    print(order) # TODO 값 확인. data_processing 에서 나온 제대로 된 값이 출력 되는지

    if len(data_bat) >= bat_size:  # bat_size 개 정보가 들어 있으면
        with open(output_file, "at") as fp:
            for i in range(0, len(data_bat)):
                for key in data_bat[i].keys():
                    fp.write(str(key) + ",")
                fp.write("\n")
                for key in data_bat[i].keys():
                    fp.write(str(data_bat[i][key]) + ",")  # 주문 잔량
                fp.write("\n,")
                print(order_bat)
                for key in order_bat[i].keys():
                    print("{} : {}".format(key, order_bat[i][key]))
                    fp.write(str(order_bat[i][key]) + ",")
                fp.write("\n")
            fp.close()
        print(" ** DICT 출력 완료 ** ")
        del data_bat[:]

def dict_output_result(output_file, dict_data):
    """
    모든 호가, 잔여량 출력 
    """
    with open(output_file, "at") as fp:
        fp.write(str(dict_data['time']) + ",")
        for key in dict_data.keys():
            fp.write(str(key) + ",")  # 주문 가격
        fp.write("\n")
        for value in dict_data.values():
            fp.write(str(value[0]) + ",")
        fp.write("\n")
        fp.close()

    print("* 실시간 데이터 출력 완료")


""" ======================================================================================== """
def output_batch(output_file, data, data_bat, bat_size):
    data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]
    # +0 : 호가 오름차순, +1 : 잔량, +2 : 추가주문량
    data_bat.append(data)

    try:
        if len(data_bat) >= bat_size:  # bat_size 개 정보가 들어 있으면
            with open(output_file, "at") as fp:
                for i in range(0, len(data_bat)):
                    fp.write((str(data_bat[i][0]) + ","))
                    for k in data_seq:
                        fp.write((str(data_bat[i][k]) + ","))
                    fp.write("\n,")
                    for k in data_seq:
                        fp.write((str(data_bat[i][k + 1]) + ","))  # 주문 잔량
                    fp.write("\n,")
                    for k in data_seq:
                        fp.write((str(data_bat[i][k + 2]) + ","))  # 추가 주문량
                    fp.write("\n")
                fp.close()
            del data_bat[:]
    except:
        # with open(output_file+"error.csv", "at") as fp:
        #    fp.write(str(datetime.now())+"\n")
        #    fp.close()
        print("Permissoin Error - {}".format(datetime.now()))
        with open(output_file + "err.csv", "at") as fp:
            for i in range(0, len(data_bat)):
                fp.write((str(data_bat[i][0]) + ","))
                for k in data_seq:
                    fp.write((str(data_bat[i][k]) + ","))
                fp.write("\n,")
                for k in data_seq:
                    fp.write((str(data_bat[i][k + 1]) + ","))  # 주문 잔량
                fp.write("\n,")
                for k in data_seq:
                    fp.write((str(data_bat[i][k + 2]) + ","))  # 추가 주문량
                fp.write("\n")
            fp.close()
        del data_bat[:]
    print("* 베치 데이터 출력 완료")

def output_result(output_file, data):
    """
    입력된 데이터를 바로 출력
    """
    data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49,
                55]  # 호가 오름차순 +1 : 잔량, +2 : 추가주문량
    try:
        with open(output_file, "at") as fp:
            fp.write(str(data[0]) + ",")
            for i in data_seq:
                fp.write(str(data[i]) + ",")  # 주문 가격
            fp.write("\n,")
            for i in data_seq:
                fp.write(str(data[i + 1]) + ",")  # 주문 잔량
            fp.write("\n,")
            for i in data_seq:
                fp.write(str(data[i + 2]) + ",")  # 추가 주문량
            fp.write("\n")
            fp.close()

    except PermissionError:
        print("************ PermissionError ************")
        with open(output_file + "_error.csv", "at") as fp:
            fp.write(str(data[0]) + ",")
            for i in data_seq:
                fp.write(str(data[i]) + ",")
            fp.write("\n,")
            for i in data_seq:
                fp.write(str(data[i + 1]) + ",")
            fp.write("\n,")
            for i in data_seq:
                fp.write(str(data[i + 2]) + ",")
            fp.write("\n")
            fp.close()
    print("* 실시간 데이터 출력 완료")
