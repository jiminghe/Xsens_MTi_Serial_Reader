# Xsens_MTi_Serial_Reader
Use Python Serial library to config/read data from Xsens MTi

Install the dependency libary
Windows:
```
pip install pyserial
```

ubuntu
```
sudo pip3 install pyserial
```
or
```
sudo apt-get update
sudo apt-get -y install python3-serial
```

You need to change the COM and baudrate to your own sensor's COM name and baudrate(default is 115200, but could be configured in MT Manager - Device Settings) in raw_xsens_comms.py:
```
self.serial_port = 'COM4' #for ubuntu, change to '/dev/ttyUSB0'
self.baudrate = 115200
```

#### if you want to configure the sensor, un-comment this line below:
```
self.go_to_config_mode()
self.set_output_conf()
```

check the set_output_conf() function to send the hex command for setting up to output configuration, you could compose this message at:
MT Manager - Device Data View - GoToConfig - SetOuputConfiguration, and click edit, to add the messages needed.


run the code in the CMD in Windows like this:
```
python raw_xsens_comms.py
```
for ubuntu:
```
python3 raw_xsens_comms.py
```



This code has been checked with MTi-680 in Windows 11, and MTi-300 in ubuntu 18.04LTS(nVidia Jetson Nano),  not all other MTi models were tested, by they share the same Xbus communication protocol.

For MTi-300 with cable model CA-USB-MTi, if you don't have 'dev/ttyUSB0', 
```
git clone https://github.com/xsens/xsens_mt.git
cd ~/xsens_mt
make HAVE_LIBUSB=1
sudo modprobe usbserial
sudo insmod ./xsens_mt.ko
```
