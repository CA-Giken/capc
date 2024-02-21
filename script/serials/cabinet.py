#!/usr/bin/env python3

import serial
from serial.tools import list_ports
import time


__SERIAL_NAME__ = "Arduino cabinet monitor"

""" キャビネット監視用Arduino通信管理クラス
"""
class Cabinet_serial:
  def __init__(self, config):
    self.config = config
    self.is_alive = False
    self.temperature = 0 # 内部温度
    self.__error = {
      "shutdowner": False # Falseはエラー状態とする
    }
  
  # エラー管理
  "getter"
  @property
  def error(self):
    return self.__error
  
  "setter"
  def errorUpdate(self, dict):
    for k in dict.keys():
      self.__error[k] = dict[k]
    # Python側で点灯ルールを指定、Arduino側で点灯パターン列挙のみ
    errorCount = 0
    for k in self.error.keys():
      if self.error[k] == False:
        errorCount += 1
    msg = ""
    if errorCount > 0:
      msg = "error=1"
    else:
      msg = "error=0"
    self.serial.write(bytes(msg,'UTF-8'))
    
  """ シリアル接続
  """
  def connect(self):
    print("[LOG] Connecting to " + __SERIAL_NAME__ + "...")
    try:
      self.serial = serial.Serial(
        port=self.config["dev_cab"],
        baudrate=self.config["baudrate"],
        timeout=self.config["timeout"]
      )
      if(self.serial.is_open == False):
        self.serial.open()
      self.is_alive = True
      print("[LOG] Success to connect to " + __SERIAL_NAME__)
    except Exception as e:
      self.is_alive = False
      print("[LOGError] Failed to connect to " + __SERIAL_NAME__)
      print(e)
      
  """ シリアル接続解除
  """
  def disconnect(self):
    self.is_alive = False
    self.serial.close()
    print("[LOG] Disconnected to " + __SERIAL_NAME__)
  
  """ 温度取得
  """
  def get_temperature(self):
    if self.is_alive == True:
      # シリアルから送られてきたデータの最終行を取得
      lines = []
      while True:
          line = self.serial.readline()
          lines.append(line.decode('utf-8').rstrip())

          # wait for new data after each line
          timeout = time.time() + 0.1
          while not self.serial.inWaiting() and timeout > time.time():
              pass
          if not self.serial.inWaiting():
              break 
      # シリアル通信が来ない場合に例外処理を行う
      if len(lines) == 0:
        print("[LOG] No data has been sent from " + __SERIAL_NAME__)
        return 0
      lastline = lines[-1]
      self.temperature = float(lastline.replace("inner_temp=", ""))
      return self.temperature
    else:
      print("[LOG] Please connect first.")
      return 0
  
  """ バッテリー残量低下
  """
  # Python側で点灯ルールを指定、Arduino側で点灯パターン列挙のみ
  def set_battery_state(self, state):
    msg = "battery="+str(int(state))
    self.serial.write(bytes(msg,'UTF-8'))
  

