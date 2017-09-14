
import math
#import matplotlib.pyplot as plt

import preprocessing

date = "09.13"
code = "000660"

def continuity():
    infile = "output.csv"
    filename = date + " " + code + " - " + infile
    print(" ** 데이터 연속성 검정 **")
    with open(filename, "rt") as fp:
        time = 0
        t = 0
        for line in fp:
            time = (line.split(","))[0]
            if time == 'time' or time == 'now':
                continue
            if time == "" or time == '\n':
                continue

            if t == 0:  # 첫 cycle
                t = int(time) + 1
                continue

            if t % 100 == 60:
                t += 40
            if int(t % 10000 / 100) % 100 == 60:
                t += 4000
            if t > int(time):
                print(" ** ", time)
                continue

            elif t < int(time):
                print(" ** ", t)
                while t != int(time):
                    t += 1
                    if t < int(time):
                        print(" ** ", t)
            t += 1
    print("--- 데이터 연속성 검정 완료 ---")


def calculate_STR():
    infile = "output.csv"
    outfile = "STR result.csv"
    filename = date + " " + code + " - " + infile
    result = date  + " " + code + " - " + outfile
    strength = []

    print(" ** STR 계산 함수 **")

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

    with open(filename, 'rt') as ori:
        with open(result, 'wt') as re:
            ori_line = ori.readlines()
            length = len(ori_line)

            for i in range(int(length / 3)):
                print("cal_STR : {} / {}".format(i+1, length/3))
                quotes = ori_line[3 * i].split(',')
                datas = ori_line[3 * i + 1].split(',')
                mores = ori_line[3 * i + 2].split(',')

                now = datas[1]

                strength.append(datas[0])
                strength.append(datas[1])
                for k in range(len(quotes)):
                    if quotes[k] == 'time' or quotes[k] == 'now':
                        continue
                    if quotes[k] == '\n' or datas[k] == '\n':
                        continue
                    strength.append(processing(int(datas[k]), int(mores[k])))

                for j in range(2, len(strength)):
                    if strength[j] > 0:
                        strength[j] += 1
                    elif strength[j] < 0:
                        strength[j] -= 1

                for st in strength:  # 출력1
                    re.write(str(st) + ",")
                re.write("\n")
                strength.clear()
            re.close()
        ori.close()
    print("--- STR 계산 완료 ---")


def data_scaling():
    infile = "STR result.csv"
    outfile = "processed.csv"
    filename = date + " " + code + " - " + infile
    result = date + " " + code + " - " + outfile

    print(" ** Data Scaling 함수 **")
    with open(filename, 'rt') as ori:
        with open(result, 'wt') as re:
            ori_line = ori.readlines()
            length = len(ori_line)
            for i in range(length):
                print("scaling : {} / {}".format(i+1, length))
                line = ori_line[i].split(',')[:-1]  # line 마지막에 엔터가 있음
                line = list(map(float, line))
                re.write(str(line[0]) + ',' + str(line[1]))
                data = preprocessing.func_wrapper(line)
                for i in range(len(data)):
                    re.write(',' + str(data[i]))
                re.write('\n')


    print("--- Data Scaling 완료 ---")

if __name__ == "__main__":
    print("file : {} {}".format(date, code))
    continuity()
    calculate_STR()
    data_scaling()