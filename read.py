import usb
import lxml
from lxml import etree

ID_VENDOR = 0x0eb8
ID_PRODUCT = 0xea02
try:
    dev = usb.core.find(idVendor=ID_VENDOR, idProduct=ID_PRODUCT)
except Exception as e:
    print(f'something went wrong finding device: {e}')
    exit(1)

if not dev:
    print(f'No device found with id {ID_VENDOR} and {ID_PRODUCT}')
    exit(1)


while True:
    ret = dev.read(0x81, 10000)
    sret = ''.join([chr(x) for x in ret])
    sret = sret.strip()
    etree.XML(sret.encode())
    obj = lxml.objectify.fromstring(sret.encode())
    print(obj.ResultMessage.result.__dict__)

