from struct import unpack, unpack_from
from datetime import datetime, timezone
import calendar
import math
import numpy as np


class XsDataPacket:
    rad2deg = 57.295779513082320876798154814105
    minusHalfPi = -1.5707963267948966192313216916397514420985846996875529104874
    halfPi = 1.5707963267948966192313216916397514420985846996875529104874

    def __init__(self):
        self.euler = [0.0, 0.0, 0.0]
        self.eulerAvailable = False

        self.quat = [0.0, 0.0, 0.0, 0.0]
        self.quaternionAvailable = False

        self.acc = [0.0, 0.0, 0.0]
        self.accAvailable = False

        self.freeAcc = [0.0, 0.0, 0.0]
        self.freeAccAvailable = False

        self.rot = [0.0, 0.0, 0.0]
        self.rotAvailable = False

        self.latlon = [0.0, 0.0]
        self.latlonAvailable = False

        self.altitude = 0.0
        self.altitudeAvailable = False

        self.vel = [0.0, 0.0, 0.0]
        self.velocityAvailable = False

        self.mag = [0.0, 0.0, 0.0]
        self.magAvailable = False

        self.packetCounter = 0
        self.packetCounterAvailable = False

        self.sampleTimeFine = 0
        self.sampleTimeFineAvailable = False

        self.utcTime = 0.0
        self.utcTimeInfo = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.utcTimeAvailable = False

        self.statusWord = 0
        self.statusWordAvailable = False
        
        self.temperature = 0.0
        self.temperatureAvailable = False
        
        self.baropressure = 0
        self.baropressureAvailable = False
        
        self.deltaV = [0.0, 0.0, 0.0]
        self.deltaVAvailable = False
        
        self.deltaQ = [0.0, 0.0, 0.0, 0.0]
        self.deltaQAvailable = False

    @staticmethod
    def asin_clamped(x):
        if x <= -1.0:
            return XsDataPacket.minusHalfPi
        if x >= 1.0:
            return XsDataPacket.halfPi
        return math.asin(x)

    def convert_quat_to_euler(self):
        if not self.quaternionAvailable:
            # Handle error: Quaternion data not available.
            return

        sqw = self.quat[0] * self.quat[0]
        dphi = 2.0 * (sqw + self.quat[3] * self.quat[3]) - 1.0
        dpsi = 2.0 * (sqw + self.quat[1] * self.quat[1]) - 1.0

        self.euler[0] = math.atan2(2.0 * (self.quat[2] * self.quat[3] + self.quat[0] * self.quat[1]), dphi) * XsDataPacket.rad2deg
        self.euler[1] = -XsDataPacket.asin_clamped(2.0 * (self.quat[1] * self.quat[3] - self.quat[0] * self.quat[2])) * XsDataPacket.rad2deg
        self.euler[2] = math.atan2(2.0 * (self.quat[1] * self.quat[2] + self.quat[0] * self.quat[3]), dpsi) * XsDataPacket.rad2deg

        self.eulerAvailable = True


class DataPacketParser:
    @staticmethod
    def parse_data_packet(packet, xbus_data):
        # Ensure packet is a list of bytes
        if not isinstance(packet, list) or not all(isinstance(b, bytes) for b in packet):
            raise ValueError("Packet must be a list of bytes.")

        # Ensure the packet has enough data to skip header
        if len(packet) < 5:
            print("Error: Packet too short.")
            return

        # Join bytes from the packet, skipping the first 4 bytes (header) and the last byte (checksum)
        data_part = b''.join(packet[4:-1])  
        bytes_offset = 0

        while bytes_offset < len(data_part):
            # Ensure there's enough data to read data_id and data_len
            if bytes_offset + 3 > len(data_part):
                print("Not enough data to read data_id and data_len.")
                break
            
            # 2 bytes used for data id
            data_id = data_part[bytes_offset:bytes_offset + 2]
            # 1 byte used for data len
            data_len = int.from_bytes(data_part[bytes_offset + 2:bytes_offset + 3], 'big')

            # Ensure there is enough data for packet_data
            if bytes_offset + 3 + data_len > len(data_part):
                print("Not enough data for packet_data.")
                break

            packet_data = data_part[bytes_offset + 3:bytes_offset + 3 + data_len]

            # Debug: Print details about the current data being parsed
            # print(f"Data ID: {data_id.hex().upper()}, Data Length: {data_len}, Packet Data: {packet_data.hex().upper()}")

            # Call the parsing function
            DataPacketParser.parse_mtdata2(xbus_data, data_id, packet_data)

            # Move offset for the next data segment
            bytes_offset += data_len + 3  # 2 bytes for data_id and 1 byte for size field


    @staticmethod
    def get_data_fp1632(message, offset):
        fpfrac = unpack_from('>i', message, offset)[0]
        fpint = unpack_from('>h', message, offset + 4)[0]

        fp_i64 = (fpint << 32) | (fpfrac & 0xffffffff)

        rv_d = np.float64(fp_i64) / 4294967296.0
        return rv_d

    @staticmethod
    def parse_mtdata2(xsdata, data_id, packet_data):
        if data_id == bytes.fromhex('1020'):
            xsdata.packetCounter = unpack('>H', packet_data)[0]
            xsdata.packetCounterAvailable = True
        
        elif data_id == bytes.fromhex('1060'):
            xsdata.sampleTimeFine = unpack('>I', packet_data)[0]
            xsdata.sampleTimeFineAvailable = True
        
        elif data_id == bytes.fromhex('1010'):
            # 12 bytes, UInt32, UInt16, Uint8.....
            utc_nano = unpack('>I', packet_data[:4])[0]
            year = unpack('>H', packet_data[4:6])[0]
            month = unpack('>B', packet_data[6:7])[0]
            day = unpack('>B', packet_data[7:8])[0]
            hour = unpack('>B', packet_data[8:9])[0]
            minute = unpack('>B', packet_data[9:10])[0]
            second = unpack('>B', packet_data[10:11])[0]
            # Create a time struct and convert to time_t
            xsdata.utcTimeInfo = calendar.timegm((year, month, day, hour, minute, second))
            xsdata.utcTime = xsdata.utcTimeInfo + utc_nano * 1e-9
            xsdata.utcTimeAvailable = True

        elif data_id == bytes.fromhex('2030'):
            #4 bytes each, float32
            xsdata.euler[0] = unpack('>f', packet_data[:4])[0]
            xsdata.euler[1]  = unpack('>f', packet_data[4:8])[0]
            xsdata.euler[2]  = unpack('>f', packet_data[8:])[0]
            xsdata.eulerAvailable = True
        
        elif data_id == bytes.fromhex('2010'):
            #quaternion
            parsed_data = unpack('>4f', packet_data[:16])
            xsdata.quat[0] = parsed_data[0]
            xsdata.quat[1] = parsed_data[1]
            xsdata.quat[2] = parsed_data[2]
            xsdata.quat[3] = parsed_data[3]
            xsdata.quaternionAvailable = True
            xsdata.convert_quat_to_euler()

        elif data_id == bytes.fromhex('4020'):
            #calibrated acceleration
            xsdata.acc[0] = unpack('>f', packet_data[:4])[0]
            xsdata.acc[1] = unpack('>f', packet_data[4:8])[0]
            xsdata.acc[2] = unpack('>f', packet_data[8:])[0]
            xsdata.accAvailable = True
        
        elif data_id == bytes.fromhex('4030'):
            #calibrated acceleration
            xsdata.freeAcc[0] = unpack('>f', packet_data[:4])[0]
            xsdata.freeAcc[1] = unpack('>f', packet_data[4:8])[0]
            xsdata.freeAcc[2] = unpack('>f', packet_data[8:])[0]
            xsdata.freeAccAvailable = True
        
        elif data_id == bytes.fromhex('8020'):
            #RateOfTurn, rad/sec
            xsdata.rot[0] = unpack('>f', packet_data[:4])[0]
            xsdata.rot[1] = unpack('>f', packet_data[4:8])[0]
            xsdata.rot[2] = unpack('>f', packet_data[8:])[0] 
            xsdata.rotAvailable = True
        
        elif data_id == bytes.fromhex('C020'):
            #magnetic field
            xsdata.mag[0] = unpack('>f', packet_data[:4])[0]
            xsdata.mag[1] = unpack('>f', packet_data[4:8])[0]
            xsdata.mag[2] = unpack('>f', packet_data[8:])[0]
            xsdata.magAvailable = True

        elif data_id == bytes.fromhex('5042'):
            xsdata.latlon[0] = DataPacketParser.get_data_fp1632(packet_data,0)
            xsdata.latlon[1] = DataPacketParser.get_data_fp1632(packet_data,6)
            xsdata.latlonAvailable = True
        
        elif data_id == bytes.fromhex('5022'):
            xsdata.altitude = DataPacketParser.get_data_fp1632(packet_data,0)
            xsdata.altitudeAvailable = True

        elif data_id == bytes.fromhex('E020'):
            # parsed_data_dict['statusWord'] = "{:032b}".format(int.from_bytes(packet_data, 'big'))
            xsdata.statusWord = int.from_bytes(packet_data, byteorder='big')
            xsdata.statusWordAvailable = True

        elif data_id == bytes.fromhex('D012'):
            xsdata.vel[0] = DataPacketParser.get_data_fp1632(packet_data,0)
            xsdata.vel[1] = DataPacketParser.get_data_fp1632(packet_data, 6)
            xsdata.vel[2] = DataPacketParser.get_data_fp1632(packet_data, 12)
            xsdata.velocityAvailable = True
        
        elif data_id == bytes.fromhex('0810'):
            xsdata.temperature = unpack('>f', packet_data[:4])[0]
            xsdata.temperatureAvailable = True
        
        elif data_id == bytes.fromhex('3010'):
            xsdata.baropressure = unpack('>I', packet_data)[0]
            xsdata.baropressureAvailable = True
            
        elif data_id == bytes.fromhex('4010'):
            xsdata.deltaV[0] = unpack('>f', packet_data[:4])[0]
            xsdata.deltaV[1] = unpack('>f', packet_data[4:8])[0]
            xsdata.deltaV[2] = unpack('>f', packet_data[8:])[0]
            xsdata.deltaVAvailable = True
        
        elif data_id == bytes.fromhex('8030'):
            xsdata.deltaQ[0] = unpack('>f', packet_data[:4])[0]
            xsdata.deltaQ[1] = unpack('>f', packet_data[4:8])[0]
            xsdata.deltaQ[2] = unpack('>f', packet_data[8:12])[0]
            xsdata.deltaQ[3] = unpack('>f', packet_data[12:])[0]
            xsdata.deltaQAvailable = True

        else:
            print(f"Unparsed Device ID: {', '.join(f'0x{byte:02X}' for byte in data_id)}\n")

            