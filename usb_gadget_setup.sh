#!/bin/bash -x

modprobe dwc2
modprobe libcomposite
modprobe usb_f_hid

mkdir -pv /sys/kernel/config/usb_gadget/g1
pushd /sys/kernel/config/usb_gadget/g1

echo 0x1d6b > idVendor # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget
#echo 0x0105 > idProduct # Multifunction Composite Gadget
echo 0x00 > bDeviceClass
echo 0x00 > bDeviceProtocol
echo 0x00 > bDeviceSubClass
echo 0x08 > bMaxPacketSize0
echo 0x0100 > bcdDevice # v1.0.0
echo 0x0200 > bcdUSB # USB2

mkdir -p strings/0x409
echo "deadbeef8675309" > strings/0x409/serialnumber
echo "PiLO Project" > strings/0x409/manufacturer
echo "Virtual Composite USB Device" > strings/0x409/product

#mkdir -p os_desc
#echo "1" > os_desc/use
#echo "0xbc" > os_desc/b_vendor_code
#echo "MSFT100" > os_desc/qw_sign

mkdir -p configs/c.1/strings/0x409
echo "PiLO HID Keyboard" > configs/c.1/strings/0x409/configuration
echo 0x80 > configs/c.1/bmAttributes
echo 2000 > configs/c.1/MaxPower # 200 mA

#keyboard
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol
echo 1 > functions/hid.usb0/subclass
echo 8 > functions/hid.usb0/report_length
echo "05010906a101050719e029e71500250175019508810275089501810175019503050819012903910275019505910175089506150026ff00050719002aff008100c0" | xxd -r -ps > functions/hid.usb0/report_desc
ln -sf functions/hid.usb0 configs/c.1

#mouse
#mkdir -p configs/c.2/strings/0x409
#echo "PiLO HID Mouse" > configs/c.2/strings/0x409/configuration
#echo 0x80 > configs/c.2/bmAttributes
#echo 2000 > configs/c.2/MaxPower # 200 mA
mkdir -p functions/hid.usb1
echo 2 > functions/hid.usb1/protocol
echo 1 > functions/hid.usb1/subclass
echo 8 > functions/hid.usb1/report_length
echo 05010902a1010901a100050919012903150025019503750181029501750581030501093009311581257f750895028106c0c0 | xxd -r -ps > functions/hid.usb1/report_desc
ln -sf functions/hid.usb1 configs/c.1

echo $(basename $(ls -d /sys/class/udc/*)) > UDC

popd
