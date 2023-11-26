### Ref: https://mtidocs.movella.com/messages
### You could also get this message from MT Manager - Device Data View, select "SetOutputConfiguration", then click "edit" to select some message

def set_output_conf(serial):
    """Configures the Imu to the following:
    example1. configure for MTi-680(GNSS/INS)
    FA FF C0 30 10 20 FF FF 10 60 FF FF 10 10 FF FF 20 10 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF 50 42 01 90 50 22 01 90 D0 12 01 90
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
    98 Checksum (calculated by the send_with_checksum )

    example2. configure for MTi-680(GNSS/INS) same as above example but with euler angle output instead(no checksum)
    FA FF C0 30 10 20 FF FF 10 60 FF FF 10 10 FF FE 20 30 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF 50 42 01 90 50 22 01 90 D0 12 01 90

    example3. configure for MTi-680 or MTi-8(GNSS/INS) same as above example1 but with euler angle output, and all at 100Hz (no checksum)
    FA FF C0 30 10 20 FF FF 10 60 FF FF 10 10 FF FE 20 30 00 64 40 20 00 64 40 30 00 64 80 20 00 64 C0 20 00 64 E0 20 FF FF 50 42 00 64 50 22 FF FF D0 12 00 64


    example4 configuration for MTi-630(AHRS), 400Hz, packetCounter + sampleTimeFine + Quaternion + Acc + FreeAcc + RateOfTurn + MagneticField + StatusWord
    FA FF C0 20 10 20 FF FF 10 60 FF FF 20 10 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF

    example5 configuration for MTi-630(AHRS), 400Hz, packetCounter + sampleTimeFine + EulerAngle + Acc + FreeAcc + RateOfTurn + MagneticField + StatusWord
    FA FF C0 20 10 20 FF FF 10 60 FF FF 20 30 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF

    example6 configuration for MTi-630 or MTi-3(AHRS), 100Hz, packetCounter + sampleTimeFine + EulerAngle + Acc + FreeAcc + RateOfTurn + MagneticField + StatusWord
    FA FF C0 20 10 20 FF FF 10 60 FF FF 20 30 00 64 40 20 00 64 40 30 00 64 80 20 00 64 C0 20 00 64 E0 20 FF FF

    example7 configuration for MTi-630 or MTi-3(AHRS), 100Hz, packetCounter + sampleTimeFine + Quaternion + Acc + FreeAcc + RateOfTurn + MagneticField + StatusWord
    FA FF C0 20 10 20 FF FF 10 60 FF FF 20 10 00 64 40 20 00 64 40 30 00 64 80 20 00 64 C0 20 00 64 E0 20 FF FF
    """
    option1_gnssins_quat_400hz = 'FA FF C0 30 10 20 FF FF 10 60 FF FF 10 10 FF FE 20 30 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF 50 42 01 90 50 22 01 90 D0 12 01 90'
    option2_gnssins_euler_400hz = 'FA FF C0 30 10 20 FF FF 10 60 FF FF 10 10 FF FE 20 30 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF 50 42 01 90 50 22 01 90 D0 12 01 90'
    option3_gnssins_euler_100hz = 'FA FF C0 30 10 20 FF FF 10 60 FF FF 10 10 FF FE 20 30 00 64 40 20 00 64 40 30 00 64 80 20 00 64 C0 20 00 64 E0 20 FF FF 50 42 00 64 50 22 FF FF D0 12 00 64'
    option4_gnssins_euler_pvt_100hz = 'FA FF C0 34 10 20 FF FF 10 60 FF FF 10 10 FF FE 20 30 00 64 40 20 00 64 40 30 00 64 80 20 00 64 C0 20 00 64 E0 20 FF FF 50 42 00 64 50 22 FF FF D0 12 00 64 70 10 FF FF '
    option5_ahrs_quat_400hz = 'FA FF C0 20 10 20 FF FF 10 60 FF FF 20 10 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF'
    option6_ahrs_euler_400hz = 'FA FF C0 20 10 20 FF FF 10 60 FF FF 20 30 01 90 40 20 01 90 40 30 01 90 80 20 01 90 C0 20 00 64 E0 20 FF FF'
    option7_ahrs_euler_100hz = 'FA FF C0 20 10 20 FF FF 10 60 FF FF 20 30 00 64 40 20 00 64 40 30 00 64 80 20 00 64 C0 20 00 64 E0 20 FF FF'
    option8_ahrs_quat_100hz = 'FA FF C0 20 10 20 FF FF 10 60 FF FF 20 10 00 64 40 20 00 64 40 30 00 64 80 20 00 64 C0 20 00 64 E0 20 FF FF'

    serial.send_with_checksum(bytes.fromhex(option4_gnssins_euler_pvt_100hz))

