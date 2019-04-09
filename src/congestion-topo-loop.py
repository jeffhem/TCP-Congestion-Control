#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.util import quietRun
import argparse
import time
import os, signal
from subprocess import Popen

H1_TOTAL_RUNTIME = 1000
H2_TOTAL_RUNTIME = 750
TCP_PROBE_RUNTIME = H1_TOTAL_RUNTIME + 10
RUNTIME_OFFSET = H1_TOTAL_RUNTIME - H2_TOTAL_RUNTIME
DELAYS = [21, 81, 162]

class congestionTopo( Topo ):
  "Dumbbell topology with 4 routers and 4 hosts."

  def build( self, delay ):
    backboneBDP = 82 * delay
    accessBDP = 21 * delay * 0.2

    backboneRouter1 = self.addSwitch('br1')
    backboneRouter2 = self.addSwitch('br2')
    accessRouter1 = self.addSwitch('ar1')
    accessRouter2 = self.addSwitch('ar2')

    self.addLink(backboneRouter1, backboneRouter2, bw=984, delay=str('%sms' % delay), loss=0, max_queue_size=backboneBDP, use_htb=True )
    self.addLink(accessRouter1, backboneRouter1, bw=252, loss=0, max_queue_size=accessBDP, use_htb=True )
    self.addLink(accessRouter2, backboneRouter2, bw=252, loss=0, max_queue_size=accessBDP, use_htb=True )

    for n in range(2):
      sourceHost = self.addHost('sh%s' % (n + 1))
      receiverHost = self.addHost('rh%s' % ( n + 1))

      self.addLink( sourceHost, accessRouter1, bw=960)
      self.addLink( receiverHost, accessRouter2, bw=960)

def congestionTest(delay, cca):
  "Create network and run congestion test"

  # # Select TCP Reno, using iperf -Z instead
  # output = quietRun( 'sysctl -w net.ipv4.tcp_congestion_control=%s' % cca )
  # assert cca in output

  os.system("rmmod tcp_probe; modprobe tcp_probe full=1 port=7979; mn -c")
  tcp_proc = Popen("exec cat /proc/net/tcpprobe > data/data_%s_%s" % (cca, delay), shell=True)

  topo = congestionTopo(delay)
  net = Mininet( topo=topo, link=TCLink )
  net.start()
  print('')
  print("==================================================")
  print("started %sms delay test for %s" % (delay, cca))

  popens = {}
  rh1 = net['rh1']
  rh2 = net['rh2']
  sh1 = net['sh1']
  sh2 = net['sh2']
  # set tcp window size to BDP*RRT
  TCP_WINDOW_SIZE = 252.0/8*1024*delay*2/1000

  print("window size")
  print(TCP_WINDOW_SIZE)

  # using iperf script to create 2 servers and hosts
  popens[rh1] = rh1.popen('iperf -s -p 7979 -w %sk' % TCP_WINDOW_SIZE)
  popens[rh2] = rh2.popen('iperf -s -p 7979 -w %sk' % TCP_WINDOW_SIZE)

  sh1.cmd('iperf -c 10.0.0.1 -p 7979 -w %sk -i 1 -t %s -Z %s>data/bw_sh1_%s_%s&' % (TCP_WINDOW_SIZE, H1_TOTAL_RUNTIME, cca, cca, delay))
  print("h1 has started sending data...")

  time.sleep(RUNTIME_OFFSET)

  sh2.cmd('iperf -c 10.0.0.2 -p 7979 -w %sk -i 1 -t %s -Z %s>data/bw_sh2_%s_%s&' % (TCP_WINDOW_SIZE, H2_TOTAL_RUNTIME, cca, cca, delay))
  print("h2 has started sending data...")

  time.sleep(H2_TOTAL_RUNTIME)

  # terminate server and tcp probe process
  popens[rh1].kill()
  popens[rh2].kill()
  tcp_proc.kill()

  net.stop()
  print("Finished %sms delay test for %s " % (delay, cca))
  print("==================================================")
  print('')

if __name__ == '__main__':
    # Take name[s] of the congestion control algorithm as args
    # e.g.: reno or reno,cubic
    parser = argparse.ArgumentParser("Congestion Topo")
    parser.add_argument("cca", help="congestion control algorithm", type=str)
    args = parser.parse_args()

    congestionAlgors = args.cca.split(',')

    # loop through the args and the propagation delay
    for cca in congestionAlgors:
      for delay in DELAYS:
        congestionTest(delay, cca)
        time.sleep(10)

