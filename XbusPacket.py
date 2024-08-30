class XbusPacket:
    def __init__(self, on_data_available=None):
        self.on_data_available = on_data_available
        self.reset()

    def reset(self):
        self.buffer = []
        self.extended_length = False
        self.expected_length = 0
        self.length_valid = False
        self.got_first_byte = False
        self.got_second_byte = False

    def feed_byte(self, byte):
        # print(f"raw byte comes in: 0x{byte.hex()}")
        # Add the first byte if it's 0xFA
        if not self.buffer and byte == b'\xfa':
            self.buffer.append(byte)
            # print(f"feed raw byte to buffer: 0x{byte.hex()}")
            self.got_first_byte = True
            return

        # Add the second byte if it's 0xFF and the first byte was 0xFA
        if self.got_first_byte and not self.got_second_byte:
            if byte == b'\xff':
                self.buffer.append(byte)
                # print(f"feed raw byte to buffer: 0x{byte.hex()}")
                self.got_second_byte = True
            else:
                # If the second byte is not 0xFF, reset the packet
                self.reset()
            return

        # Add the third byte if it's 0x36 and the first two bytes were 0xFA and 0xFF
        if self.got_first_byte and self.got_second_byte and len(self.buffer) == 2:
            if byte == b'\x36':
                self.buffer.append(byte)
                # print(f"ok feed raw byte to buffer: 0x{byte.hex()}")
            else:
                # If the third byte is not 0x36, reset the packet
                self.reset()
            return

        # If we have the first three bytes, we can start appending the data_length and the data
        if self.got_first_byte and self.got_second_byte and len(self.buffer) >= 3:
            self.buffer.append(byte)
            # print(f"ok2 feed raw byte to buffer: 0x{byte.hex()}")

            # Once we have the data_length byte, we can determine the expected packet length
            if len(self.buffer) == 4:
                self.expected_length = int.from_bytes(byte, 'big')  # Convert byte to integer
                self.length_valid = True

            # If the packet is complete, pass it to onDataAvailable and reset the packet
            if self.is_packet_complete():
                # Pass the complete packet to the external user
                self.on_data_available(self.buffer)
                # print("data available")
                # Reset the packet for the next data stream
                self.reset()


    def is_packet_complete(self):
        # Check if we have a valid length before proceeding
        if not self.length_valid:
            return False
        # print("is packet complete")
        # Calculate the total length of the packet
        # 3 bytes for the header (FA FF 36), 1 byte for data_length, data bytes, and 1 byte for checksum
        total_length = 3 + 1 + self.expected_length + 1
        # Check if the buffer has reached the total length
        return len(self.buffer) == total_length

    def onDataAvailable(self):
        # Here you would handle the complete packet, e.g., print it or pass it to another method
        # print(f"Packet data: {self.buffer}")
        pass

    def compute_checksum(self, packet):
        # negative summation of all bytes in the message, excluding the first byte(premable) and taking the lower byte
        return (-sum(result[1:])) & 0xFF

    def validate_checksum(self):
        if not self.is_packet_complete():
            return False
        checksum = self.compute_checksum(self.buffer)
        print("validate checksum")
        # The checksum byte is the last byte in the buffer
        return checksum == self.buffer[-1]
