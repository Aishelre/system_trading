filename = 'test.csv'
import numpy as np


def MinMaxScaler(data):
    numerator = data - np.min(data, 0)
    denominator = np.max(data, 0) - np.min(data, 0)
    return numerator / (denominator + 1e-7)

with open(filename, 'rt') as fp:
    with open('processed.csv', 'wt') as p:
        for line in fp:
            line = line.split(',')[:-1]
            line = list(map(float, line))

            p.write(str(line[0]) + ',' +  str(line[1]) + ',')
            data = np.array(line[2:])
            print(data)
            data = MinMaxScaler(data)
            print(data)
            for i in range(len(data)):
                p.write(str(data[i]) + ',')
            p.write('\n')