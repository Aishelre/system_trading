file = "test.csv"

with open(file, 'rt') as ori:
    with open("result.csv", 'wt') as re:
        ori_line = ori.readlines()
        length = len(ori_line)
        print(length)  # 19872
        #print(ori_line)

        for i in range(int(length / 3)):
            print(i)
            quotes = list(map(int, ori_line[3 * i].strip().split(',')))
            quotes = list(map(abs, quotes))
            datas = ori_line[3 * i + 1].strip().split(',')
            mores = ori_line[3 * i + 2].strip().split(',')

            now = quotes[10]
            print(now)


            re.write('time,now,')
            for i in quotes[1:]:
                re.write(str(i) + ',')
            re.write('\n')

            re.write(str(quotes[0]) + "," + str(now))
            for i in datas:
                re.write(i + ',')
            re.write('\n,')

            for i in mores:
                re.write(i + ',')
            re.write('\n')

