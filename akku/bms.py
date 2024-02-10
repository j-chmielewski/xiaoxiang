import asyncio
from asyncio import Queue
from dataclasses import dataclass
from bleak import BleakClient

CHAR_UUID_TX = "0000ff02-0000-1000-8000-00805f9b34fb"
CHAR_UUID_RX = "0000ff01-0000-1000-8000-00805f9b34fb"
DATA_OFFSET = 4

INFO_3 = bytearray([0xdd, 0xa5, 0x3, 0x0, 0xff, 0xfd, 0x77])
INFO_4 = bytearray([0xdd, 0xa5, 0x4, 0x0, 0xff, 0xfc, 0x77])

HEADER_03 = bytearray([0xdd, 0x03])
HEADER_04 = bytearray([0xdd, 0x04])


@dataclass
class BmsData:
    voltage: float
    current: float
    capacity: int  # percent


class Bms:

    def __init__(self, address: str, debug: bool = False):
        self.address = address
        self.debug = debug
        self.data = bytearray()
        self.queue: Queue[BmsData] = Queue()
        self.counter = 0

    async def read(self):
        async with BleakClient(self.address) as client:
            # connect to bms
            if not client.is_connected:
                self._dbg(f":: Connecting to {self.address}")
                status = await client.connect()
                self._dbg(f":: Connected to {self.address}: {status}")
            else:
                self._dbg(f":: Client already connected to {self.address}")

            # register to notifications
            await client.start_notify(CHAR_UUID_RX, self._notify_cb)

            # start bms-reading loop
            asyncio.create_task(self._read_loop(client))

            # wait for objects to appear in queue and yield them to consumer
            while True:
                yield await self.queue.get()


    async def _read_loop(self, client):
        while True:
            await client.write_gatt_char(CHAR_UUID_TX, INFO_3)
            await client.read_gatt_char(CHAR_UUID_RX)
            await asyncio.sleep(1)

    async def _notify_cb(self, _characteristic, data: bytearray):
        self._dbg(":: Notify, received characteristic:", data)
        if data.startswith(HEADER_03):
            self._dbg(f":: Recognized header 03, counter: {self.counter}")
            await self._parse_data()
            self.counter = 0
            self.data = data
        else:
            self._dbg(f":: Received packet {self.counter}")
            self.counter += 1
            self.data += data

    async def _parse_data(self):
        data = self.data[DATA_OFFSET:]
        voltage = bytearray([0, 0, data[0], data[1]])
        voltage = int.from_bytes(voltage, signed=False) * 0.01
        self._dbg(f":: Total voltage: {voltage:.2f}V")
        current = bytearray([data[2] & 0b10000000, 0, data[2] & 0b01111111, data[3]])
        current = int.from_bytes(current, signed=True) * 0.01
        self._dbg(f":: Current: {current:.2f}A")
        capacity = bytearray([0, 0, 0, data[19]])
        capacity = int.from_bytes(capacity)
        self._dbg(f":: Remaining capacity: {capacity}%")
        await self.queue.put(BmsData(voltage=voltage, current=current, capacity=capacity))


    def _dbg(self, *msg):
        if self.debug:
            print(*msg)
