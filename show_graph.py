import matplotlib.pyplot as plt
from datetime import datetime

x = []
y1 = []
y2 = []

cord = "0"

today = datetime.now().strftime("%m.%d ")

filename = today + cord + " - STR processed.csv"

now = 66900
with open(filename, 'rt') as fp:
    for line in fp:
        line = line.split(',')
        x.append(line[0])
        y1.append(line[2])
        y2.append(int(line[1]) - int(now))
        now = line[1]

fig, ax1 = plt.subplots()
#ax1.plot(x, y1, 'b-')
ax1.scatter(x, y1)
ax1.set_xlabel('time')
ax1.set_ylabel('strength')
ax1.tick_params('y', colors='b')


ax2 = ax1.twinx()
ax2.plot(x, y2, 'r.')
#ax2.scatter(x, y2)
ax2.set_ylabel('variable')
ax2.tick_params('y', colors='r')


#plt.scatter(x, y1)
#plt.scatter(x, y2)

fig.tight_layout()
plt.show()
