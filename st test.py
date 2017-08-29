from math import *
from datetime import datetime

cord = "047810"

today = datetime.now().strftime("%m.%d ")
file = today + cord + " - output.csv"
result = today + cord + " - STR result.csv"
result2 = today + cord + " - STR processed.csv"

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
        print(length)  # 19872

        for i in range(int(length/3)):
            print(i)
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

            put_index = quotes.index(now) + 1

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

with open(result, 'rt') as re:  # 강도의 합을 다른 파일에 출력한다.
    with open(result2, 'wt') as pro:
        for line in re:
            l = line[:-2].split(',')
            pro.write(l[0] + ',')
            pro.write(l[1] + ',')
            l = list(map(float, l))
            val = sum(l[2:])
            print(val)
            pro.write(str(val) + '\n')

        pro.close()
    re.close()