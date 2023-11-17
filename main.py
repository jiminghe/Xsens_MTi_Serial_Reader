from SerialHandler import SerialHandler
from XbusPacket import XbusPacket
from DataPacketParser import DataPacketParser, XsDataPacket
from SetOutput import set_output_conf
import time


def on_live_data_available(packet):
    xbus_data = XsDataPacket() 
    DataPacketParser.parse_data_packet(packet, xbus_data)

    if xbus_data.packetCounterAvailable:
        print(f"\npacketCounter: {xbus_data.packetCounter}, ", end='')

    if xbus_data.sampleTimeFineAvailable:
        print(f"sampleTimeFine: {xbus_data.sampleTimeFine}, ", end='')

    if xbus_data.utcTimeAvailable:
        print(f"utctime epochSeconds: {xbus_data.utcTime:.9f}")

    if xbus_data.eulerAvailable:
        print(f"\nRoll, Pitch, Yaw: [{xbus_data.euler[0]:.2f}, {xbus_data.euler[1]:.2f}, {xbus_data.euler[2]:.2f}], ", end='')

    if xbus_data.quaternionAvailable:
        print(f"q0, q1, q2, q3: [{xbus_data.quat[0]:.4f}, {xbus_data.quat[1]:.4f}, {xbus_data.quat[2]:.4f}, {xbus_data.quat[3]:.4f}], ", end='')

    if xbus_data.rotAvailable:
        rate_of_turn_degree = [
            xbus_data.rad2deg * xbus_data.rot[0],
            xbus_data.rad2deg * xbus_data.rot[1],
            xbus_data.rad2deg * xbus_data.rot[2]
        ]
        print(f"\nRateOfTurn: [{rate_of_turn_degree[0]:.2f}, {rate_of_turn_degree[1]:.2f}, {rate_of_turn_degree[2]:.2f}], ", end='')

    if xbus_data.accAvailable:
        print(f"Acceleration: [{xbus_data.acc[0]:.2f}, {xbus_data.acc[1]:.2f}, {xbus_data.acc[2]:.2f}], ", end='')

    if xbus_data.magAvailable:
        print(f"Magnetic Field: [{xbus_data.mag[0]:.2f}, {xbus_data.mag[1]:.2f}, {xbus_data.mag[2]:.2f}]")

    if xbus_data.latlonAvailable and xbus_data.altitudeAvailable:
        print(f"\nLat, Lon, Alt: [{xbus_data.latlon[0]:.9f}, {xbus_data.latlon[1]:.9f}, {xbus_data.altitude:.9f}]")

    if xbus_data.velocityAvailable:
        print(f"Vel E, N, U: [{xbus_data.vel[0]:.9f}, {xbus_data.vel[1]:.9f}, {xbus_data.vel[2]:.9f}]")


def main():
    try:
        serial = SerialHandler("COM12", 115200) ##change the port and baudrate to your own MTi's baudrate.
        packet = XbusPacket(on_data_available=on_live_data_available)

        go_to_config = bytes.fromhex('FA FF 30 00')
        go_to_measurement = bytes.fromhex('FA FF 10 00')
        ###if you want to configure your sensor's output, check the set_output_conf function.
        ##serial.send_with_checksum(go_to_config)
        ##set_output_conf(serial)
        ##time.sleep(0.1)  # Sleep for 0.1 sec
        serial.send_with_checksum(go_to_measurement)

        print("Listening for packets...")

        while True:
            byte = serial.read_byte()
            # print(f"raw byte: 0x{byte.hex()}")
            packet.feed_byte(byte)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == '__main__':
    main()
