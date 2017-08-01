
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
            if t == 0:
                t = int(time)+1
                continue
            if time == "":
                continue

            if t % 100 == 60:
                t += 40

            if t > int(time):
                print(time)
                continue
            elif t < int(time):
                print(t)
                while t != int(time):
                    t += 1
                    if t < int(time):
                        print(t)

            t += 1


if __name__ == "__main__":
    testing("output.csv")
    #testing("test.csv")
