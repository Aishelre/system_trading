"""
저장 데이터의 시간적 연속성 검정

"""
def testing(filename):
    print("{} 검정".format(filename))
    with open(filename, "rt") as fp:
        time = 0
        t = 0
        for line in fp:
            time = (line.split(","))[0]
            if time == 'time':
                continue
            if time == "":
                continue

            if t == 0:
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

            print(time, t)
            t += 1


if __name__ == "__main__":
    testing("output.csv")
    #testing("test.csv")


"""
def processing(a, b):
    line = []
    a = list(map(int, a[:-1]))
    b = list(map(int, b[:-1]))
    for i in range(len(a)):
        pre = a[i] - b[i]
        if pre == 0:  #
            line.append(0)
            continue
        if b[i] == 0:  # 주문량 0
            line.append(0)
            continue
        asd = a[i] / pre * 100
        line.append(asd)
    line = list(map(str, line))
    return line


with open("output.csv", 'rt') as fp:
    with open("asdf.csv", 'at') as ap:
        for i in range(693):
            line = fp.readline()
            line1 = fp.readline()
            line2 = fp.readline()

            ap.write(line1)
            ap.write(line2)
            line3 = processing(line1.split(','), line2.split(','))
            line3 = ','.join(line3)
            print(line3)
            ap.write(line3+'\n,\n')
        ap.close()
    fp.close()



"""