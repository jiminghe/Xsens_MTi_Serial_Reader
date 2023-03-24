import serial
import logging
import threading
import queue
from xbus_reconstructor import XbusReconstructor

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')  

class ImuReader:
    def __init__(self):
        self.serial_port = 'COM4'
        self.baudrate = 115200
        self.send_queue = queue.Queue()
        #### if you want to configure the sensor, un-comment this line below####
        # self.go_to_config_mode()
        # self.set_output_conf()
        #### end comments####
        self.xbus_reconstructor = XbusReconstructor()
        self.go_to_measurement_mode()
        d = threading.Thread(name='daemon', target=self.connect)
        #d.setDaemon(True)
        d.start()  
    
    def connect(self):
        with serial.Serial(self.serial_port, self.baudrate, timeout=5) as ser:
            while True:
                data = ser.read_until(b'\xfa')
                parse_xbus_data_list = self.xbus_reconstructor.parse_xbus_data(data)
                if not len(parse_xbus_data_list) == 0:
                    logging.info(f'parsed: {parse_xbus_data_list}')
                while not self.send_queue.empty():
                    send_data = self.send_queue.get()
                    logging.info(f'sending to device: {send_data}')
                    ser.write(send_data)

    def go_to_measurement_mode(self):
        self.send_queue.put(bytes.fromhex('FAFF1000F1'))

    def go_to_config_mode(self):
        self.send_queue.put(bytes.fromhex('FAFF3000D1'))

    
    def set_output_conf(self):
        """Configures the Imu to the following:
        example1. configure for MTi-680(GNSS/INS)
        FA FF C0 30 10 20 FF FF 10 60 FF FF 10 10 FF FF 20 10 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF 50 42 01 90 50 22 01 90 D0 12 01 90 98
        FA FF C0 30 SetOutputConfig(0xC0), Size:0x30(46 bytes)
        10 20 FF FF PacketCounter(1020) at max output rate(0xff 0xff)
        10 60 FF FF SampleTimeFine(1060) at max output rate(0xff 0xff)
        10 10 FF FF UtcTime(1010) at max output rate(0xff 0xff)
        20 10 01 90 Quaternion(2010) at 400Hz(0x01 0x90)
        40 20 01 90 Acceleration(4020) at 400Hz
        40 30 01 90 FreeAcceleration(4030) at 400Hz
        80 20 01 90 RateOfTurn(8020) at 400Hz
        C0 20 00 64 MagneticField(C020) at 100Hz(0x64)
        E0 20 FF FF StatusWord(E020) at max output rate
        50 42 01 90 LatLon(5042) Fp1632 at 400Hz
        50 22 01 90 AltitudeEllipsoid Fp1632 at 400Hz
        D0 12 01 90 VelocityXYZ Fp1632 at 400Hz
        98 Checksum

        example2. configure for MTi-680(GNSS/INS) same as above example but with euler angle output instead
        FA FF C0 30 10 20 FF FF 10 60 FF FF 10 10 FF FE 20 30 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF 50 42 01 90 50 22 01 90 D0 12 01 90 79


        example3 configuration for MTi-630(AHRS), 400Hz, packetCounter + sampleTimeFine + Quaternion + Acc + FreeAcc + RateOfTurn + MagneticField + StatusWord
        FA FF C0 20 10 20 FF FF 10 60 FF FF 20 10 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF 5F

        example4 configuration for MTi-630(AHRS), 400Hz, packetCounter + sampleTimeFine + EulerAngle + Acc + FreeAcc + RateOfTurn + MagneticField + StatusWord
        FA FF C0 20 10 20 FF FF 10 60 FF FF 20 30 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF 3F

        example5 configuration for MTi-630 or MTi-3(AHRS), 100Hz, packetCounter + sampleTimeFine + EulerAngle + Acc + FreeAcc + RateOfTurn + MagneticField + StatusWord
        FA FF C0 20 10 20 FF FF 10 60 FF FF 20 30 00 64 40 20 00 64 40 30 00 64 80 20 00 64 C0 20 00 64 E0 20 FF FF F3

        example6 configuration for MTi-630 or MTi-3(AHRS), 100Hz, packetCounter + sampleTimeFine + Quaternion + Acc + FreeAcc + RateOfTurn + MagneticField + StatusWord
        FA FF C0 20 10 20 FF FF 10 60 FF FF 20 10 00 64 40 20 00 64 40 30 00 64 80 20 00 64 C0 20 00 64 E0 20 FF FF 13
        """

        self.send_queue.put(bytes.fromhex('FA FF C0 30 10 20 FF FF 10 60 FF FF 10 10 FF FE 20 30 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF 50 42 01 90 50 22 01 90 D0 12 01 90 79'))



if __name__ == '__main__':
    imu_reader = ImuReader()

