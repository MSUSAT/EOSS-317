from subprocess import run

# 1. all necessary imports
import sys
import smbus
import struct
import RPi.GPIO as GPIO
import time
import os
from subprocess import run
import board
import adafruit_bme680
import adafruit_tmp117
import adafruit_icm20x
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
import psutil
import busio
from time import sleep
from picamera import PiCamera
from datetime import datetime
#from gps3 import agps3

# 2. setup all components
GPIO_PORT = 26          # psu
I2C_ADDR = 0x36         # psu

bus = smbus.SMBus(1)    # psu

TELEMETRY_FILENAME = "/home/pi/jan28_flight_prep/data_log.csv"
telemetry_file =open(TELEMETRY_FILENAME,"a")

i2c = board.I2C()  # uses board.SCL and board.SDA

bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
tmp117 = adafruit_tmp117.TMP117(i2c)
icm = adafruit_icm20x.ICM20948(i2c)
ina = INA219(i2c)

#GPSDSocket creates a GPSD socket connection & request/retrieve GPSD output.
#gps_socket = agps3.GPSDSocket()

#DataStream unpacks the streamed gpsd data into python dictionaries.
#data_stream = agps3.DataStream()
#gps_socket.connect()
#gps_socket.watch()

#gcj02_lng_lat = [0.0,0.0]
#bd09_lng_lat = [0.0,0.0]

# for new_data in gps_socket:
#     if new_data:
#         data_stream.unpack(new_data)

bme680.sea_level_pressure = 1013.25
temperature_offset = -5

def read_voltage(bus):
    address = I2C_ADDR
    read = bus.read_word_data(address, 2)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    voltage = swapped * 1.25 /1000 /16
    return voltage

def read_capacity(bus):
    address = I2C_ADDR
    read = bus.read_word_data(address, 4)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    capacity = swapped /256
    return capacity


def cpu_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    temp = temp.replace("'C","")
    temp = temp.replace("\n","")
    return (temp.replace("temp=",""))

# if os.stat("/home/pi/lawn_demo/data_log.cvs").st_size == 0:
#     file.write("time,to,ti,gas,hum,press,alt,accx,accy,accz," +
#         "gyrox,gyroy,gyroz,magnx,magny,magnz,vbus,ibus,pbus,tc,lat,lon\n")
if os.stat(TELEMETRY_FILENAME).st_size == 0:
    telemetry_file.write("time,to,ti,gas,hum,press,alt,accx,accy,accz," +
        "gyrox,gyroy,gyroz,magnx,magny,magnz,vbus,ibus,pbus,tc\n")

# 3. start wifi hot spot and streaming as a separate process
#       systemctl enable hostapd 
#       systemctl enable dnsmasq

# 4. while loop running with 10 seconds delay after last iteration
#        check power levels (voltage and capacity %)
#        if low
#            attempt to send message over iridium
#            if unsuccessful
#                alert to streaming webpage (???)
#            stop all spawned processes
#            shutdown     
#        read all telemetry values and log them
#        every minute (or every 6th iteration) attempt to send them over iridium

shut_down = False
while True:
    # check for low voltage
    voltage = read_voltage(bus)
    print("Voltage: ", voltage)
    capacity = read_capacity(bus)
    print("Capacity: ", capacity)
    if voltage < 3.00 or capacity < 20:
        msg = "Battery low (vol<3.00V or cap<20%) vol=" + str(voltage) + " cap=" + str(capacity)
        telemetry_file.write(msg)
        print(msg)
        shut_down = True
        break

    # get timestamp w/o microseconds
    now = datetime.now()
    now = now.replace(microsecond=0)  # truncate ms
    now.strftime('%y-%m-%d %H:%M:&S')
    # print(now)

    # get sensor data points
    # data_points = [tmp117.temperature, bme680.temperature, bme680.gas, 
    #     bme680.relative_humidity, bme680.pressure, bme680.altitude, 
    #     *icm.acceleration, *icm.gyro, *icm.magnetic, ina.bus_voltage, 
    #     ina.current, ina.power,data_stream.lat,data_stream.lon]
    data_points = [tmp117.temperature, bme680.temperature, bme680.gas, 
        bme680.relative_humidity, bme680.pressure, bme680.altitude, 
        *icm.acceleration, *icm.gyro, *icm.magnetic, ina.bus_voltage, 
        ina.current, ina.power]

    # truncate to 2 decimal places
    as_string = ','.join([str(round(d, 2)) for d in data_points])

    # compose data line
    line = str(now) + ',' + as_string + ',' + cpu_temp() + '\n'
    # print(len(line))  # 126 w/ tmp117

    # append line to telemetry file
    telemetry_file.write(line)
    telemetry_file.flush()

    time.sleep(30)

# close telemetry file
telemetry_file.close()

# shut down
if shut_down:
    print("Shutting down in 60 sec")
    run("shutdown --poweroff 1", shell=True)
else:
    print("Not shutting down. Exiting...")