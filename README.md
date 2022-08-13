# mt-sevenexcellence-python

Read raw usb data from Mettler-Toledo SevenExcellence ph and orp sensor on linux.


## MT7, pH, ORP, Conductivity
### setup (one time only, already done):
make 'method' of type 'interval'. Set all required measurements in 'method->configuration'.
make sure sensors with temperature sensor included have temperature to 'internal' and sensors without temp. sensor to 'manual'.
do not use 'overlapping temperature capture'

'method->measurement type; interval' setup the sensors. 
All (ALL!) sensors should have maximum decimal places and endpoint type to 'Manual'.
This way the endpoint is not set, so the measurement runs indefenitely.
Do not set threshold. Set interval time to wanted value (usually 1s.)

Connect using USB. Each 'interval' a USB telegram is received with sensor values, this can be read by db-mt7.py
Furthermore, if network connection is setup, a web interface is available at host:8080 when in communication mode 'Transfer to LabX direct'.
The web interface allows to view logs and remote shutdown of device.
When in mode 'remote control at startup', the device sends raw information to a user defined port (default: 8016).
When connected to this port with TelNet, commmands can be sent, but i don't know the commands.
Also, software LabX or EasyDirect PH can be used. For EasyDirect PH a tryout version is used from www.mt.com/EasyDirectpH. 

To have python libusb work without root: https://stackoverflow.com/questions/53125118/why-is-python-pyusb-usb-core-access-denied-due-to-permissions-and-why-wont-the
Add /etc/udev/rules.d/10-local.rules with content:
`SUBSYSTEMS=="usb", ENV{DEVTYPE}=="usb_device", ATTRS{idVendor}=="0eb8", ATTRS{idProduct}=="ea02", GROUP="sys", MODE="0666"`
and make sure user is in group `sys`

### enable
press the home screen button with '3 sens 1 sec' and the running man icon, measurements should start immediately.

### Calibrate
Click on Sensor name right top of homescreen.
Conductivity: 1 point calibration
pH: 3-point calibration: pH 2, 4, and 7
