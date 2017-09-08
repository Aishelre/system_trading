"""
strength에 대한 전처리가 된 파일을
MinMaxScaler와 유사하게 처리하여
'processed.csv'에 저장한다.
"""
import numpy as np
import math

def MinMaxScaler(data):
    """
    항상 0~1의 양수 값으로 출력되는 문제가 있음.
    """
    numerator = data - np.min(data, 0)
    denominator = np.max(data, 0) - np.min(data, 0)
    return numerator / (denominator + 1e-7)

def new_MinMaxScaler(data):
    """
    -1~1의 값으로 정규화 되어서
    문제 있는 이상치는 물론 의미 있는 이상치 마저 사라진다.
    """
    arr = np.empty((len(data)), float)
    for i in range(len(data)):
        if data[i] >= 0:
            numerator = data[i] - np.min(data)
            denominator = np.max(data) - np.min(data)
            arr[i] = numerator / (denominator + 1e-7)
        elif data[i] < 0:
            numerator = data[i] - np.max(data)
            denominator = np.max(data) - np.min(data)
            arr[i] = numerator / (denominator + 1e-7)
    return arr

def parabola(data):  # y^2 = 4 * p * x
    """
    +는 +로, -는 -로 정규화 해준다.
    p값을 조절하여 이상치 값을 조정해준다.????
    """
    p = 0.1
    # y = math.sqrt(4 * p * data[i])
    for i in range(len(data)):
        if data[i] >= 0:
            data[i] = math.sqrt(4 * p * data[i])
        elif data[i] < 0:
            data[i] = -1 * math.sqrt(4 * p * (-1) * data[i])
    return data

def func_wrapper(data):
    # value = MinMaxScaler(data)
    # value = new_MinMaxScaler(data)
    value = parabola(data)
    return value

if __name__ == "__main__":
    day = "09.08"
    code = "000660"
    filename = day + " " + code + " - STR result.csv"
    resultname = day + " " + code + " - processed.csv"
    c=0
    with open(filename, 'rt') as fp:
        with open(resultname, 'wt') as p:
            for line in fp:
                c+=1
                print(c)
                line = line.split(',')[:-1]
                line = list(map(float, line))

                p.write(str(line[0]) + ',' +  str(line[1]))
                data = np.array(line[2:])
                data = func_wrapper(data)
                for i in range(len(data)):
                    p.write(',' + str(data[i]))
                p.write('\n')