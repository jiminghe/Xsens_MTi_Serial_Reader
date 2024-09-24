class XbusPacket:
    def __init__(self, on_data_available=None):
        self.on_data_available = on_data_available
        self.reset()

    def reset(self):
        self.buffer = []
        self.expected_length = 0
        self.length_valid = False

    def feed_byte(self, byte):
        # Start a new packet when we see 0xFA
        if len(self.buffer) == 0 and byte == b'\xfa':
            self.buffer.append(byte)
            return

        # Expecting 0xFF after 0xFA
        if len(self.buffer) == 1 and byte == b'\xff':
            self.buffer.append(byte)
            return

        # Expecting 0x36 after 0xFA 0xFF
        if len(self.buffer) == 2 and byte == b'\x36':
            self.buffer.append(byte)
            return

        # We should now be expecting the data length
        if len(self.buffer) == 3:
            self.buffer.append(byte)
            self.expected_length = byte[0]  # Get the data length as an integer
            self.length_valid = True
            return

        # Now we're expecting data bytes
        if self.length_valid and len(self.buffer) >= 4:
            self.buffer.append(byte)

            # Check if we have received all expected bytes
            total_length = 3 + 1 + self.expected_length + 1  # Header + length + data + checksum
            if len(self.buffer) == total_length:
                # Validate checksum
                # print("Packet is complete, current buffer:", " ".join(f"{b.hex().upper()}" for b in self.buffer))
                if self.validate_checksum():
                    self.on_data_available(self.buffer)
                else:
                    print("Checksum validation failed.")
                self.reset()  # Reset for the next packet
                return

        # If we get here, the packet is still incomplete
        # print("Packet not complete, current buffer:", " ".join(f"{b.hex().upper()}" for b in self.buffer))

    def is_packet_complete(self):
        # Ensure expected_length is an integer
        return self.length_valid and len(self.buffer) == (3 + 1 + self.expected_length + 1)

    def compute_checksum(self, packet):
        total = 0
        for byte in packet[1:-1]:  # Start from the second byte till the second last byte
            total += byte[0]  # Convert bytes to integer
        return (-total) & 0xFF

    def validate_checksum(self):
        if not self.is_packet_complete():
            return False
        # print("Validating checksum...")
        checksum = self.compute_checksum(self.buffer)
        #print the checksum in hex uppercase
        # print("Checksum:", f"{checksum:02X}")
        #return checksum == self.buffer[-1][0]
        if checksum == self.buffer[-1][0]:
            return True
        else:
            #print the self.buffer and checksum in hex uppercase
            print("Checksum failed. Buffer:", " ".join(f"{b.hex().upper()}" for b in self.buffer))
            print("Checksum:", f"{checksum:02X}")
            return False