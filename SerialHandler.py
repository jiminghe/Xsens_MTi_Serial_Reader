import serial

class SerialHandler:
    def __init__(self, port_name, baud_rate=115200):
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.serial_port = serial.Serial(port=port_name, baudrate=baud_rate, timeout=None)

    def __del__(self):
        if self.serial_port.is_open:
            self.serial_port.close()

    def read_byte(self):
        byte = self.serial_port.read(1)
        if not byte:
            raise RuntimeError("Failed to read from the serial port.")
        return byte

    def send_bytes(self, bytes_data):
        # Debugging: Print the bytes in hex format
        print("Sending bytes:", " ".join(f"{byte:02X}" for byte in bytes_data))
        self.serial_port.write(bytes_data)
        self.serial_port.flush()

    def send_with_checksum(self, bytes_data):
        # Calculate checksum
        checksum = (256 - sum(bytes_data[1:]) % 256) % 256
        # Convert checksum to a bytes object (assuming checksum is one byte)
        checksum_bytes = bytes([checksum])
        # Concatenate bytes_data with checksum_bytes
        message_with_checksum = bytes_data + checksum_bytes
        # Send the message with checksum
        self.send_bytes(message_with_checksum)
