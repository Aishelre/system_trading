from math import *

file = "output.csv"
result = "result.csv"

strength = []

def processing(data, order):
    pre_remain = data - order
    if pre_remain == 0 and order == 0:
        st = 0
    elif pre_remain == 0 and order != 0:
        st = 1
    elif pre_remain != 0 and order == 0:
        st = 1
    else:
        #st = 1 + order / pre_remain * 1000
        st = e ** (1)
    return str(st)

with open(file, 'rt') as ori:
    with open(result, 'at') as re:
        ori_line = ori.readlines()
        length = len(ori_line)
        print(length)  # 19872

        for i in range(int(length/300)):
            print(i)
            quotes = ori_line[3*i].split(',')
            datas = ori_line[3 * i + 1].split(',')
            mores = ori_line[3*i + 2].split(',')

            for k in range(len(quotes)):
                if quotes[k] == 'time' or quotes[k] == 'now':
                    continue
                if quotes[k] == '\n' or datas[k] == '\n':
                    continue
                strength.append(processing(int(datas[k]), int(mores[k])))

            for q in quotes:
                re.write(str(q) + ",")
            re.write("\n,")
            for st in strength:
                re.write(str(st) + ",")
            re.write("\n,")



            pass




        pass