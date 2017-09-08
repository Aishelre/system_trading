"""
1초 단위의 주문 파일에서
st = order / pre_remain * 1000
으로 계산하여 저장한다.
"""
from math import *
from datetime import datetime

cord = "000660"

day = datetime.now().strftime("%m.%d ")
#day = "0909"
file = day + cord + " - output.csv"
result = day + cord + " - STR result.csv"

strength = []

def processing(data, order):
    pre_remain = data - order
    if pre_remain == 0 and order == 0:
        st = 0
    elif pre_remain == 0 and order != 0:
        st = 0.1
    elif pre_remain != 0 and order == 0:
        st = 0.1
    else:
        st = order / pre_remain * 1000
    return (st)

with open(file, 'rt') as ori:
    with open(result, 'wt') as re:
        ori_line = ori.readlines()
        length = len(ori_line)
        print("row : ", length)

        for i in range(int(length/3)):
            print(i+1, " / ", length/3)
            quotes = ori_line[3*i].split(',')
            datas = ori_line[3 * i + 1].split(',')
            mores = ori_line[3*i + 2].split(',')

            now = datas[1]

            strength.append(datas[0])
            strength.append(datas[1])
            for k in range(len(quotes)):
                if quotes[k] == 'time' or quotes[k] == 'now':
                    continue
                if quotes[k] == '\n' or datas[k] == '\n':
                    continue
                strength.append(processing(int(datas[k]), int(mores[k])))

            #put_index = quotes.index(now) + 1
            put_index = int(2 + (len(quotes)-2)/2)
            # 현재가 초과의 호가에 대해서는 (-1)을 곱한다.
            for i in range(put_index, len(strength)):
                strength[i] = float(strength[i]) * (-1)

            for i in range(2, len(strength)):
                if strength[i] > 0:
                    strength[i] += 1
                elif strength[i] < 0:
                    strength[i] -= 1

            for st in strength:  # 출력1
                re.write(str(st) + ",")
            re.write("\n")
            strength.clear()
        re.close()
    ori.close()
