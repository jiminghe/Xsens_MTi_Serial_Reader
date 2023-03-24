import sys
import logging
import struct
import numpy as np
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')

class XbusReconstructor:
    def __init__(self):
        self.total_payload_length = None
        #incomplete_msg_buffer is used to bring over bytes from an incomplete message to the next iteration
        self.incomplete_msg_buffer = b''
        self.did_sync_with_stream = False

        #prebuffer is used to make sure that we atleast have 4 bytes to read out the total length
        self.prebuffer = b''

    def calculate_checksum(self, msg_bytes_without_cs):
        """Calculates checksum for xbus message

        Args:
            msg_bytes_without_cs (byte_string): msg bytes without the checksum

        Returns:
            np.uint8: checksum of provided msg bytes
        """
        checksum = 0
        for idx, msg_byte in enumerate(msg_bytes_without_cs):
            if idx == 0:
                #skip preamble bytes
                continue
            checksum -= msg_byte
        return np.uint8(checksum)


    def __find_start_of_xbus_data(self, msg_bytes):
        """Removes all prepended bytes that could arrive on first read.

        Args:
            msg_bytes (byte_array): Byte array containing received bytes
        Returns:
            byte_array: Byte array with the prepended bytes stripped from it
        """

        if not self.did_sync_with_stream and msg_bytes[0] != 0xfa:
            #Find the first full message
            for idx, msg_byte in enumerate(msg_bytes):
                if msg_byte == 0xfa:
                    #Start of message found
                    logging.warning('Had to cut out part of message since it did not start with preamble!')
                    return msg_bytes[idx:]
        return msg_bytes

    def _reconstruct_xbus_data(self, msg_bytes):
        if msg_bytes == b'':
            logging.warning('Received an empty message!')
            return []
        xbus_delimited_message = self.__find_start_of_xbus_data(msg_bytes)
        self.prebuffer += xbus_delimited_message
        self.did_sync_with_stream = True

        if len(self.prebuffer) < 4:
            print('Message is too small, cannot get the length! Buffering for now')
            return []

        reconstructed_messages = []
        while len(self.prebuffer) >= 4:
            if self.incomplete_msg_buffer == b'':
                self.total_payload_length = int(self.prebuffer[3])
                #Total payload length also needs to include preamble, BID, MID, LEN and checksum bytes
                self.total_payload_length += 5

            #We do not support extended packet lenghts yet
            assert self.total_payload_length < 255

            payload_bytes_left = self.total_payload_length - len(self.incomplete_msg_buffer)
            partial_payload_bytes = self.incomplete_msg_buffer + self.prebuffer[:payload_bytes_left]
            self.prebuffer = self.prebuffer[payload_bytes_left:]


            if len(partial_payload_bytes) == self.total_payload_length:
                assert partial_payload_bytes[-1] == self.calculate_checksum(partial_payload_bytes[:-1])
                reconstructed_messages.append(partial_payload_bytes)
                self.incomplete_msg_buffer = b''
            elif len(partial_payload_bytes) < self.total_payload_length:
                self.incomplete_msg_buffer = partial_payload_bytes
            elif len(partial_payload_bytes) > self.total_payload_length:
                sys.exit('ERROR: Cannot have a partial payload bigger than amount of payload bytes, check your code!')

        return reconstructed_messages

    def parse_xbus_data(self, msg_bytes):
        parsed_msgs = []
        reconstructed_messages = self._reconstruct_xbus_data(msg_bytes)
        for reconstructed_msg in reconstructed_messages:
            message_identifier = reconstructed_msg[2]
            if message_identifier == 0x36:
                parsed_msgs.append(self.__parse_mtdata2_message(reconstructed_msg))
        return parsed_msgs



    def __parse_mtdata2_message(self, reconstruced_msg):
        parsed_data_dict = {}
        data_part = reconstruced_msg[4:-1]
        bytes_offset = 0

        while bytes_offset < len(data_part):
            #2bytes used for data id
            data_id = data_part[bytes_offset + 0: bytes_offset + 2]
            #1byte used for data len
            data_len = int.from_bytes(data_part[bytes_offset + 2:bytes_offset + 3], 'big')

            packet_data = data_part[bytes_offset + 3: bytes_offset + 3 + data_len]

            if data_id == bytes.fromhex('1020'):
                # 2 bytes, UInt16
                parsed_data_dict['packetCounter'] = struct.unpack('>H', packet_data)[0]
            elif data_id == bytes.fromhex('1060'):
                # 4 bytes, UInt32
                parsed_data_dict['sampleTimeFine'] = struct.unpack('>I', packet_data)[0]
            elif data_id == bytes.fromhex('1010'):
                # 12 bytes, UInt32, UInt16, Uint8.....
                utc_nano = struct.unpack('>I', packet_data[:4])[0]
                year = struct.unpack('>H', packet_data[4:6])[0]
                month = struct.unpack('>B', packet_data[6:7])[0]
                day = struct.unpack('>B', packet_data[7:8])[0]
                hour = struct.unpack('>B', packet_data[8:9])[0]
                minute = struct.unpack('>B', packet_data[9:10])[0]
                second = struct.unpack('>B', packet_data[10:11])[0]
                parsed_data_dict['utctime'] = f"{year}_{month}_{day}_{hour}_{minute}_{second}.{utc_nano}"
            elif data_id == bytes.fromhex('2030'):
                #4 bytes each, float32
                parsed_data_dict['roll'] = struct.unpack('>f', packet_data[:4])[0]
                parsed_data_dict['pitch'] = struct.unpack('>f', packet_data[4:8])[0]
                parsed_data_dict['yaw'] = struct.unpack('>f', packet_data[8:])[0]
            elif data_id == bytes.fromhex('2010'):
                #quaternion
                parsed_data = struct.unpack('>4f', packet_data[:16])
                parsed_data_dict['q0'] = parsed_data[0]
                parsed_data_dict['q1'] = parsed_data[1]
                parsed_data_dict['q2'] = parsed_data[2]
                parsed_data_dict['q3'] = parsed_data[3]
            elif data_id == bytes.fromhex('4020'):
                #calibrated acceleration
                parsed_data_dict['accX'] = struct.unpack('>f', packet_data[:4])[0]
                parsed_data_dict['accY'] = struct.unpack('>f', packet_data[4:8])[0]
                parsed_data_dict['accZ'] = struct.unpack('>f', packet_data[8:])[0]
            elif data_id == bytes.fromhex('4030'):
                #free acceleration
                parsed_data_dict['freeAccX'] = struct.unpack('>f', packet_data[:4])[0]
                parsed_data_dict['freeAccY'] = struct.unpack('>f', packet_data[4:8])[0]
                parsed_data_dict['freeAccZ'] = struct.unpack('>f', packet_data[8:])[0]
            elif data_id == bytes.fromhex('8020'):
                #angular velocity
                parsed_data_dict['angularVelocityX'] = struct.unpack('>f', packet_data[:4])[0]
                parsed_data_dict['angularVelocityY'] = struct.unpack('>f', packet_data[4:8])[0]
                parsed_data_dict['angularVelocityZ'] = struct.unpack('>f', packet_data[8:])[0]
            elif data_id == bytes.fromhex('C020'):
                #magnetic field
                parsed_data_dict['magX'] = struct.unpack('>f', packet_data[:4])[0]
                parsed_data_dict['magY'] = struct.unpack('>f', packet_data[4:8])[0]
                parsed_data_dict['magZ'] = struct.unpack('>f', packet_data[8:])[0]
            elif data_id == bytes.fromhex('E0 20'):
                # parsed_data_dict['statusWord'] = "{:032b}".format(int.from_bytes(packet_data, 'big'))
                parsed_data_dict['statusWord'] = self.get_status(packet_data)
            elif data_id == bytes.fromhex('5042'):
                lat = self.get_data_fp1632(packet_data,0)
                long = self.get_data_fp1632(packet_data, 6)
                parsed_data_dict['lat'] = lat
                parsed_data_dict['long'] = long
            elif data_id == bytes.fromhex('5022'):
                altitudeEllipsoid = self.get_data_fp1632(packet_data,0)
                parsed_data_dict['altitudeEllipsoid'] = altitudeEllipsoid
            elif data_id == bytes.fromhex('D012'):
                velocityX = self.get_data_fp1632(packet_data,0)
                velocityY = self.get_data_fp1632(packet_data, 6)
                velocityZ = self.get_data_fp1632(packet_data, 12)
                parsed_data_dict['velocityX'] = velocityX
                parsed_data_dict['velocityY'] = velocityY
                parsed_data_dict['velocityZ'] = velocityZ
            else:
                # parsed_data_dict['unknown'] = packet_data
                string_data = str(reconstruced_msg)
                # print(f"raw data: {string_data}")

            bytes_offset += data_len + 3 # 2bytes used for data id and 1 byte for size field

        return parsed_data_dict

    def get_data_fp1632(self, message, offset):
        fpfrac = struct.unpack_from('>i', message, offset)[0]
        fpint = struct.unpack_from('>h', message, offset + 4)[0]

        fp_i64 = (fpint << 32) | (fpfrac & 0xffffffff)

        rv_d = np.float64(fp_i64) / 4294967296.0
        return rv_d

    def get_status(self, packet):
        status_msg = ""
        status = int.from_bytes(packet, byteorder='big')

        filter_valid = status & (1 << 1)
        status_msg += "Filter: Valid, | " if filter_valid else "Filter: Invalid, | "

        gnss_fix = status & (1 << 2)
        status_msg += "GNSS: Fix, | " if gnss_fix else "GNSS: No, | "

        no_rotation_status = status & 0x18
        if no_rotation_status == 0:
            status_msg += "MGBE: No, | "
        elif no_rotation_status == 0x10:
            status_msg += "MGBE: rotation detected abort, | "
        elif no_rotation_status == 0x18:
            status_msg += "MGBE: Running, |  "

        sync_in_marker = status & (1 << 21)
        if sync_in_marker:
            status_msg += "syncIn: Yes, | time: "

        sync_out_marker = status & (1 << 22)
        if sync_out_marker:
            status_msg += "syncOut: Yes, | time: "
        else:
            status_msg += "SyncOut: No, | "

        filter_mode = status & 0x03800000
        if filter_mode == 0:
            status_msg += "filterMode: withoutGNSS, | "
        elif filter_mode == 0x800000:
            status_msg += "filterMode: Coasting, | "
        elif filter_mode == 0x1800000:
            status_msg += "filterMode: with GNSS, | "

        have_gnss_time_pulse = status & (1 << 26)
        status_msg += "GnssPPS: Yes, | " if have_gnss_time_pulse else "GnssPPS: No, | "

        rtk_status = status & 0x18000000
        if rtk_status == 0:
            status_msg += "rtk: No."
        elif rtk_status == 0X8000000:
            status_msg += "rtk: Floating."
        elif rtk_status == 0x10000000:
            status_msg += "rtk: Fixed."

        return status_msg

