#!/usr/bin/env python3
# encoding: utf-8

import os
import subprocess
import time 

# [NS3 INFO]
ns3Scenario = 'tap1-scenario'
ns3Path = '/home/administrator/ns-allinone-3.35/ns-3.35'

#####################################################
# Setup functions
#####################################################
def RunDockers ():
  cmd = 'docker-compose up'
  pr = subprocess.Popen(cmd, shell=True)

def CreateAndAttachTaps ():
  os.system('sudo tunctl -t tap-left')
  os.system('sudo tunctl -t tap-right')
  os.system('sudo ip link set tap-left promisc on')
  os.system('sudo ip link set tap-right promisc on')
  os.system('sudo ip link set tap-left up')
  os.system('sudo ip link set tap-right up')
  while True:
    print('-- Attaching tap-left to br-left')
    ret = os.system('sudo brctl addif br-left tap-left')
    if ret == 0: 
      break
    time.sleep(5)  
  while True:
    print('-- Attaching tap-right to br-right')
    ret = os.system('sudo brctl addif br-right tap-right')
    if ret == 0: 
      break
    time.sleep(5)  

def RunNs3 (ns3Path, scenario):
  cmd = 'cd {} && sudo ./waf'.format(ns3Path)
  os.system(cmd)
  cmd = 'cd {} && sudo ./waf --run {}'.format(ns3Path, scenario)
  print(cmd)
  pr = subprocess.Popen(cmd, shell=True)    
  return pr

#####################################################
# Tear down functions
#####################################################
def ClearDockers ():
  '''
  Clear all docker-related stuff
  - Stop containers
  - Remove containers
  - Remove docker networks (virtual birdges)
  '''
  os.system ('docker kill $(docker ps -q)')
  os.system ('docker rm $(docker ps -a -q)')
  os.system ('docker network prune -f')

def DetachAndRemoveTaps ():
  '''
  Clear setup related to taps
  - Detach from virtual bridges (if docker networks do not exist, it throughs a message error)
  - Set down the tap devices
  - Remove the tap devices
  '''
  os.system('sudo brctl delif br-left tap-left')
  os.system('sudo brctl delif br-right tap-right')
  os.system('sudo ip link set dev tap-left down')  
  os.system('sudo ip link set dev tap-right down')  
  os.system('sudo tunctl -d tap-left')
  os.system('sudo tunctl -d tap-right')

def StopNs3 (scenario) :
  '''
  Step the ns-3 scenario
  '''
  cmd = 'sudo killall {}'.format(scenario)
  print(cmd)
  os.system (cmd)

def main():
  # Setup virtual networks and ns-3  
  RunDockers()
  CreateAndAttachTaps()
  RunNs3(ns3Path, ns3Scenario)
  time.sleep(1)
  #####################################################
  # Call your programs here for the docker containers
  # --> sender (10.1.0.2)
  # --> receiver (10.2.0.2)
  #####################################################
  # [PROGRAMS]
  os.system('docker exec -it sender python3 /home/programs/SenderProgram.py')
  os.system('docker exec -it receiver python3 /home/programs/ReceiverProgram.py')
  
  # #####################################################
  # # Tear down virtual network and ns-3
  StopNs3(ns3Scenario)
  ClearDockers()
  DetachAndRemoveTaps()
  
if __name__ == '__main__':
  main()