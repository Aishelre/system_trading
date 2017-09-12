import multiprocessing
from multiprocessing import Process
from datetime import datetime
import time


class test():
    def __init__(self):
        self.proc = Process(target=self.run, args=())
        self.exit = multiprocessing.Event()

        self.proc.start()

    def run(self):
        print("타임 체크 쓰레드 진입123sdasdadsa")

        self.proc.terminate()
        while True:
            print(self.exit.is_set())
            hour = int(datetime.now().strftime("%H%M"))
            print(hour)
            if hour >= 100:
                print("통과")
                break
            else:
                print("sleep")
        while True:
            hour = int(datetime.now().strftime("%H%M"))
            print(hour)
            if hour >= 300:
                print("통과")
                break
            else:
                print("sleep")
        print("asd")
        self.shutdown()
        print(" 탈출 ")

    def shutdown(self):
        print("123123")
        print(self.exit.set())


if __name__ == '__main__':
    process = test()
    time.sleep(2)
    process.shutdown()
