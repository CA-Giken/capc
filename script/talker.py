#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float32 as Float
from serials.cabinet import Cabinet_serial
from serials.ups import Ups_serial

class main():
  def __init__(self):
    # Config loader
    try:
      self.config = {
        "dev_cab": "/dev/ttyACM0",
        "dev_ups": "/dev/ttyUSB0",
        "baudrate": 9600,
        "timeout": 1 # 秒？ミリ秒？
      }
      self.config.update(rospy.get_param("/config/watchdog"))
    except Exception as e:
      print("get_param exception:",e.args)

    self.cabinet = Cabinet_serial(self.config)
    self.ups = Ups_serial(self.config, self.cabinet.errorUpdate)
    self.pub = rospy.Publisher('/watchdog/inner_temp',Float,queue_size=1)
    self.talker()
    
  """Publisher用メソッド
  """
  def cb_cyclic(self, ev):
    print("watchdog::cyclic call back")
    t1=Float()
    t1.data = self.cabinet.get_temperature()
    self.pub.publish(t1)
    rospy.set_param("/watchdog/inner_temp",t1.data)

  """Talker立ち上げ用メソッド
  """
  def talker(self):
    rospy.init_node('talker', anonymous=True)
    
    # Connection
    self.cabinet.connect()
    self.ups.connect()
    
    rospy.Timer(rospy.Duration(2), self.cb_cyclic)

    while not rospy.is_shutdown():
      print("watchdog::main loop")

      # シリアル通信の再接続処理
      try:
        if self.cabinet.is_alive == False:
          self.cabinet.connect()
        if self.ups.is_alive == False:
          self.ups.connect()
      except Exception as e:
        print(e)
      
      # バッテリーモードへの変更を検知してシャットダウン処理を実行
      mode = self.ups.is_battery_mode()
      if mode == True:
        self.ups.shutdown()

      # バッテリー残量低下をキャビネット前面に通知
      bat_state = self.ups.is_battery_fine()
      self.cabinet.set_battery_state(bat_state)
      
      rospy.sleep(1)
      
    # FIXME: ROSが落ちたらシリアル接続も解除する？　その場合はここ？
    self.dispose()

  """UPS Manager終了処理
  """
  def dispose(self):
    # 自動シャットダウンスクリプトの停止をキャビネット前面に通知
    self.cabinet.set_shutdowner_state(False)
    
    self.ups.disconnect()
    self.cabinet.disconnect()
    # FIXME: ROSまわりでデストラクタ処理必要？

if __name__ == '__main__':
  try:
    main()
  except rospy.ROSInterruptException: pass
