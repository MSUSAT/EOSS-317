import time
import os
import board
import adafruit_bme680
import adafruit_tmp117
import adafruit_icm20x
import psutil
from time import sleep
from picamera import PiCamera
from datetime import datetime

file =open("/home/pi/EOSS-317/data_log.cvs","a")
i2c = board.I2C()  # uses board.SCL and board.SDA
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
i2c = board.I2C()  # uses board.SCL and board.SDA
tmp117 = adafruit_tmp117.TMP117(i2c)
i2c = board.I2C()  # uses board.SCL and board.SDA
icm = adafruit_icm20x.ICM20948(i2c)
camera = PiCamera()
loop_counter = 1
bme680.sea_level_pressure = 1013.25
i = 0
video_count = 0
temperature_offset = -5

if os.stat("/home/pi/EOSS-317/data_log.cvs").st_size == 0:
    file.write("Time,TMP,Env_temp,gas,humidity,pressure,altitude,acceleration,gyro,magnitometer,\n")

camera.start_recording('/home/pi/EOSS-317/testvideo%s.h264' % video_count)

while True:
#     print("Temperature: %.2f degrees C" % tmp117.temperature)
#     print("Environmental Temperature : %.2f degrees C" % bme680.temperature)
#     print("Gas: %d ohm" % bme680.gas)
#     print("Humidity: %0.1f %%" % bme680.relative_humidity)
#     print("Pressure: %0.3f hPa" % bme680.pressure)
#     print("Altitude = %0.2f meters" % bme680.altitude)
#     print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (icm.acceleration))
#     print("Gyro X:%.2f, Y: %.2f, Z: %.2f rads/s" % (icm.gyro))
#     print("Magnetometer X:%.2f, Y: %.2f, Z: %.2f uT" % (icm.magnetic))
    now = datetime.now()           
    file.write(str(now)+","+str(tmp117.temperature)+","+str(bme680.temperature)+","+str(bme680.gas)+","+str(bme680.relative_humidity)+","+str(bme680.pressure)+","+str(bme680.altitude)+","+str(icm.acceleration)+","+str(icm.gyro)+","+str(icm.magnetic)+"\n")
    file.flush()
    i = i+1
    if (i == 500):
        camera.stop_recording()
        i = 0
        video_count += 1
        gigabytes_avail = psutil.disk_usage('/').free / 1024 / 1024 / 1024
        print("GB Available = %s" % gigabytes_avail)
        if (video_count == 5):
            break
        camera.start_recording('/home/pi/EOSS-317/testvideo%s.h264' % video_count)
    
    
#time.sleep(1)
#camera.stop_recording()
file.close()

