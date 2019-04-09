import numpy as np
import matplotlib.pyplot as plt
import csv
import argparse

parser = argparse.ArgumentParser("Congestion Topo")
parser.add_argument("cca", help="congestion control algorithm", type=str)
parser.add_argument("delay", help="propagation delay", type=int)
args = parser.parse_args()
delay = args.delay
cca = args.cca

h1time = []
h1Data = []
h2time = []
h2Data = []
yrange = 2000

if (delay == 81):
    yrange = 5600
if (delay == 162):
    yrange = 12000

with open('./data/tcpprobe/data_%s_%s' % (cca, delay)) as csvfile:
    plots = csv.reader(csvfile, delimiter=' ')
    for row in plots:
        if(row[2] == '10.0.0.1:7979'):
            h1Data.append(int(row[6]))
            h1time.append(float(row[0]))
        if(row[2] == '10.0.0.2:7979'):
            h2Data.append(int(row[6]))
            h2time.append(float(row[0]))

    
plt.plot(h1time, h1Data, label="h1 to s1")
plt.plot(h2time, h2Data, label="h2 to s2")
plt.ylabel('cwnd(mss)')
plt.xlabel('time(s)')
plt.title('iperf test %s w/ %sms delay' % (cca, delay))
plt.rc('lines', linewidth=1)
axes = plt.gca()
axes.set_ylim([0,yrange])
plt.rcParams["figure.figsize"] = (20,8)
plt.legend()
plt.grid(True)
plt.show()