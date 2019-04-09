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

with open('./data/bandwidth/bw_sh1_%s_%s' % (cca, delay)) as csvfile:
    plots = csv.reader(csvfile, delimiter=' ')
    for i in range(6):
        next(plots)

    time = 0
    for row in plots:
        h1Data.append(float(row[len(row)-2]))
        h1time.append(time)
        time = time + 1

with open('./data/bandwidth/bw_sh2_%s_%s' % (cca, delay)) as csvfile:
    plots = csv.reader(csvfile, delimiter=' ')
    for i in range(6):
        next(plots)

    time = 250
    for row in plots:
        h2Data.append(float(row[len(row)-2]))
        h2time.append(time)
        time = time + 1
        
    
plt.plot(h1time, h1Data, label="h1")
plt.plot(h2time, h2Data, label="h2")
plt.ylabel('bandwidth(Mbps)')
plt.xlabel('time(s)')
plt.title('Bandwidth fairness %s w/ %sms delay' % (cca, delay))
plt.rc('lines', linewidth=1)
plt.rcParams["figure.figsize"] = (20,7)
axes = plt.gca()
axes.set_ylim([0,300])
plt.legend()
plt.grid(True)
plt.show()