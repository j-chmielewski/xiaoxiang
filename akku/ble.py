import asyncio
from dataclasses import dataclass
from bleak import BleakClient, BleakScanner

BASIC_INFO_SERVICE = "0000ff00-0000-1000-8000-00805f9b34fb"
# EXTENDED_INFO_SERVICE = "0000fa00-0000-1000-8000-00805f9b34fb"
EXTENDED_INFO_SERVICE = "0000ff01-0000-1000-8000-00805f9b34fb"

CHAR_UUID_TX = "0000ff02-0000-1000-8000-00805f9b34fb"
CHAR_UUID_RX = "0000ff01-0000-1000-8000-00805f9b34fb"
HEADER_SIZE = 4
CELLS = 4
DATA_OFFSET = 4

INFO_3 = bytearray([0xdd, 0xa5, 0x3, 0x0, 0xff, 0xfd, 0x77])
INFO_4 = bytearray([0xdd, 0xa5, 0x4, 0x0, 0xff, 0xfc, 0x77])

DEBUG = False

HEADER_03 = bytearray([0xdd, 0x03])
HEADER_04 = bytearray([0xdd, 0x04])

print(INFO_3)
print(INFO_4)

def dbg(*msg):
    if DEBUG:
        print(*msg)


@dataclass
class BasicInfo:
    voltage: int
    current: int
    capacity: int  # percent

async def notify_cb(_char, data: bytearray):
    dbg(":: Notify, received characteristic:", data)
    if data.startswith(HEADER_03):
        dbg(":: Recognized header 03")
        parse_info_3(data)
    elif data.startswith(HEADER_04):
        dbg(":: Recognized header 04")
        parse_info_4(data)


async def main(address: str):
    async with BleakClient(address) as client:
        if not client.is_connected:
            dbg(f":: Connecting to {address}")
            status = await client.connect()
            dbg(f":: Connected to {address}: {status}")
        else:
            dbg(f":: Client already connected to {address}")

        await client.start_notify(CHAR_UUID_RX, notify_cb)
        while True:
            await get_info_4(client)
            await get_info_3(client)
            await asyncio.sleep(1)


async def get_info_4(client: BleakClient):
    dbg(":: Retrieving info 4")
    await client.write_gatt_char(CHAR_UUID_TX, INFO_4)
    data = await client.read_gatt_char(CHAR_UUID_RX)
    dbg(":: Retrieved info 4, data:", data)


async def get_info_3(client: BleakClient):
    dbg(":: Retrieving info 3")
    await client.write_gatt_char(CHAR_UUID_TX, INFO_3)
    data1 = await client.read_gatt_char(CHAR_UUID_RX)
    await client.write_gatt_char(CHAR_UUID_TX, INFO_3)
    data2 = await client.read_gatt_char(CHAR_UUID_RX)
    await client.write_gatt_char(CHAR_UUID_TX, INFO_3)
    data3 = await client.read_gatt_char(CHAR_UUID_RX)
    dbg(":: Retrieved info 3")
    # dbg(":: data1:", data1)
    # dbg(":: data2:", data2)
    # dbg(":: data3:", data3)


def parse_info_3(data: bytearray):
    data = data[DATA_OFFSET:]
    voltage = bytearray([0, 0, data[0], data[1]])
    voltage = int.from_bytes(voltage, signed=False) * 0.01
    print(f":: Total voltage: {voltage:.2f}V")
    current = bytearray([data[2] & 0b10000000, 0, data[2] & 0b01111111, data[3]])
    current = int.from_bytes(current, signed=True) * 0.01
    print(f":: Current: {current:.2f}A")
    capacity = bytearray([0, 0, 0, data[19]])
    capacity = int.from_bytes(capacity)
    print(f":: Remaining capacity: {capacity}%")


def parse_info_4(data):
    data = data[DATA_OFFSET:]
    for c in range(CELLS):
        voltage = bytearray([0, 0, data[c * 2], data[c * 2 + 1]])
        voltage = int.from_bytes(voltage, signed=False, byteorder="big")
        print(f"Cell {c} voltage: {voltage * .001}")

