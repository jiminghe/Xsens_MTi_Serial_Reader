# Xsens_MTi_Serial_Reader
Use Python Serial library to config/read data from Xsens MTi

You need to change the COM and baudrate to your own sensor's COM name and baudrate(default is 115200, but could be configured in MT Manager - Device Settings)
```
self.serial_port = 'COM4'
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



This code has been checked with MTi-680 in Windows 11, not all other models.

