# 17.07.27 16:00

from datetime import datetime


def data_processing1(self, cur_data):
    """
    주문이 들어올 때마다
    같은 시간의 ...@#$% 좀 이상함
    """
    # cur_data, pre_data
    data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49, 55]

    if cur_data[0] == self.pre_data[0] and cur_data[1] == self.pre_data[1]:  # 같은 시간, 같은 호가창
        for i in data_seq:
            self.pre_data[i + 1] = int(self.pre_data[i + 2])
            cur_data[i + 2] = int(cur_data[i + 2])
            cur_data[i + 2] += self.pre_data[i + 2]
            self.pre_data[i + 1] = str(self.pre_data[i + 2])
            cur_data[i + 2] = str(cur_data[i + 2])
        self.output_result("p_output.csv", cur_data)
    elif cur_data[0] != self.pre_data[0]:
        self.output_result("p_output.csv", cur_data)
    else:  # [0]!=[0] (다른 시간), [1]!=[1] (호가창 변경)
        pass
    pre_data = cur_data


def output_batch(output_file, data, data_bat, bat_size):
    data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49,
                55]  # 호가 오름차순 +1 : 잔량, +2 : 추가주문량
    data_bat.append(data)

    try:
        if len(data_bat) >= bat_size:  # bat_size 개 정보가 들어 있으면
            print("출력")
            with open(output_file, "at") as fp:
                for i in range(0, bat_size):
                    fp.write((data_bat[i][0] + ","))
                    for k in data_seq:
                        fp.write((data_bat[i][k] + ","))
                    fp.write("\n,")
                    for k in data_seq:
                        fp.write((data_bat[i][k + 1] + ","))  # 주문 잔량
                    fp.write("\n,")
                    for k in data_seq:
                        fp.write((data_bat[i][k + 2] + ","))  # 추가 주문량
                    fp.write("\n")
                fp.close()
            del data_bat[:]
    except:
        # with open(output_file+"error.csv", "at") as fp:
        #    fp.write(str(datetime.now())+"\n")
        #    fp.close()
        print("Permissoin Error - {}".format(datetime.now()))
        with open(output_file + "err.csv", "at") as fp:
            for i in range(0, bat_size):
                fp.write((data_bat[i][0] + ","))
                for k in data_seq:
                    fp.write((data_bat[i][k] + ","))
                fp.write("\n,")
                for k in data_seq:
                    fp.write((data_bat[i][k + 1] + ","))  # 주문 잔량
                fp.write("\n,")
                for k in data_seq:
                    fp.write((data_bat[i][k + 2] + ","))  # 추가 주문량
                fp.write("\n")
            fp.close()
        del data_bat[:]


def output_result(output_file, data):
    print("※ 파일 출력 함수")
    data_seq = [58, 52, 46, 40, 34, 28, 22, 16, 10, 4, 1, 7, 13, 19, 25, 31, 37, 43, 49,
                55]  # 호가 오름차순 +1 : 잔량, +2 : 추가주문량
    try:
        with open(output_file, "at") as fp:
            fp.write(data[0] + ",")
            for i in data_seq:
                fp.write(data[i] + ",")  # 주문 가격
            fp.write("\n,")
            for i in data_seq:
                fp.write(data[i + 1] + ",")  # 주문 잔량
            fp.write("\n,")
            for i in data_seq:
                fp.write(data[i + 2] + ",")  # 추가 주문량
            fp.write("\n")
            fp.close()

    except PermissionError:
        print("************ PermissionError ************")
        with open(output_file + "_error.csv", "at") as fp:
            fp.write(data[0] + ",")
            for i in data_seq:
                fp.write(data[i] + ",")
            fp.write("\n,")
            for i in data_seq:
                fp.write(data[i + 1] + ",")
            fp.write("\n,")
            for i in data_seq:
                fp.write(data[i + 2] + ",")
            fp.write("\n")
            fp.close()
    print("* 데이터 출력 완료")
