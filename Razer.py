import time
import usb.core
import usb.util
from usb.backend import libusb1

# declare constants
# 1. product ID
# see README.md for instruction to find the device ID for your mouse
WIRELESS_RECEIVER = 0x00AB
WIRED_MOUSE = 0x00AA
# 2. transaction_id.id
# see README.md for instruction to find the correct transaction_id.id for your mouse
TRAN_ID = b"\x1f"


def get_mouse():
    # declare backend: libusb1.0
    backend = libusb1.get_backend()
    # find the mouse by PyUSB
    mouse = usb.core.find(idVendor=0x1532, idProduct=WIRELESS_RECEIVER, backend=backend)
    # if the receiver is not found, mouse would be None
    if not mouse:
        # try finding the wired mouse
        mouse = usb.core.find(idVendor=0x1532, idProduct=WIRED_MOUSE, backend=backend)
        # still not found, then the mouse is not plugged in, log error
        if not mouse:
            print(f"The specified mouse (PID:{WIRELESS_RECEIVER} or {WIRED_MOUSE}) cannot be found.")
    
    return mouse


def battery_msg():
    # adapted from https://github.com/rsmith-nl/scripts/blob/main/set-ornata-chroma-rgb.py
    # the first 8 bytes in order from left to right
    # status + transaction_id.id + remaining packets (\x00\x00) + protocol_type + command_class + command_id + data_size
    msg = b"\x00" + TRAN_ID + b"\x00\x00\x00\x02\x07\x80"
    crc = 0
    for i in msg[2:]:
        crc ^= i
    # the next 80 bytes would be storing the data to be sent, but for getting the battery no data is sent
    msg += bytes(80)
    # the last 2 bytes would be the crc and a zero byte
    msg += bytes([crc, 0])
    return msg


def get_battery():
    try:
        # find the mouse and the state, see get_mouse() for detail
        mouse = get_mouse()
        if not mouse:
            return None
        # the message to be sent to the mouse, see battery_msg() for detail
        msg = battery_msg()
        # needed by PyUSB
        # if Linux, need to detach kernel driver
        mouse.set_configuration()
        usb.util.claim_interface(mouse, 0)
        # send request (battery), see razer_send_control_msg in razercommon.c in OpenRazer driver for detail
        mouse.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x300, data_or_wLength=msg, wIndex=0x00)
        # needed by PyUSB
        usb.util.dispose_resources(mouse)
        # if the mouse is wireless, need to wait before getting response
        time.sleep(0.3305)
        # receive response
        result = mouse.ctrl_transfer(bmRequestType=0xa1, bRequest=0x01, wValue=0x300, data_or_wLength=90, wIndex=0x00)
        usb.util.dispose_resources(mouse)
        usb.util.release_interface(mouse, 0)
        # the raw battery level is in 0 - 255, scale it to 100 for human, correct to 2 decimal places
    except Exception as e:
        print(e)
        return None
    
    if (result[-2] <= 122):
        return f"{result[9] / 255 * 100:.0f}"
    else:
        return None

if __name__ == "__main__":
    battery = get_battery()
    print(f"Battery level obtained: {battery}")