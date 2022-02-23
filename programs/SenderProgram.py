#!/usr/bin/env python3
# encoding: utf-8

import os
import time

if __name__ == '__main__':
  #tail -F anything
  print('Running Sender program!!\n')
  while True:
    ret = os.system('ping -c 10 -W 2 10.2.0.2')
    if ret == 0:
      break
    print('Receiver is not ready yet')
  print('+++++++++++++++ Receiver responded!!!!!!!!')  
  time.sleep(5)
  print('Finished program!!\n')
