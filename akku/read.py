import asyncio
from bleak import BleakClient, BleakScanner

ADDRESS = "A4:C1:37:30:8D:90"
BASIC_INFO_SERVICE = "0000ff00-0000-1000-8000-00805f9b34fb"
# EXTENDED_INFO_SERVICE = "0000fa00-0000-1000-8000-00805f9b34fb"
EXTENDED_INFO_SERVICE = "0000ff01-0000-1000-8000-00805f9b34fb"

CHAR_UUID_TX = "0000ff02-0000-1000-8000-00805f9b34fb"
CHAR_UUID_RX = "0000ff01-0000-1000-8000-00805f9b34fb"
HEADER_SIZE = 4
CELLS = 4
CELL_VOLTAGE_OFFSET = 4

GET_INFO_3 = bytearray([0xdd, 0xa5, 0x3, 0x0, 0xff, 0xfd, 0x77])

async def notify_cb(_char, data):
    print(":: Notify, received characteristic:", data)


def parse_basic_info(data):
    # data = data[HEADER_SIZE:]
    print(f"data[0]: {data[0]}")
    print(f"data[1]: {data[1]}")
    voltage = bytearray([0, 0, data[1], data[0]])
    voltage = int.from_bytes(voltage, signed=False, byteorder="big")
    print(f"voltage: {voltage}")

    # capacity_percent = int.from_bytes(bytearray([data[19]]), signed=False)
    # print(f"capacity_percent: {capacity_percent}")

    for c in range(CELLS):
        voltage = bytearray(
            [
                0, 0,
                data[CELL_VOLTAGE_OFFSET + c * 2],
                data[CELL_VOLTAGE_OFFSET + c * 2 + 1],
            ])
        voltage = int.from_bytes(voltage, signed=False, byteorder="big")
        print(f"Cell {c} voltage: {voltage * .001}")


    return voltage


async def main(address):
    # print(":: Scanning for BLE devices")
    # devices = await BleakScanner.discover()
    # for device in devices:
    #     print(device)


    async with BleakClient(address) as client:
        # await client.pair(pin="000000")
        if not client.is_connected:
            print(f":: Connecting to {address}")
            status = await client.connect()
            print(f":: Connected to {address}: {status}")
        else:
            print(f":: Client already connected to {address}")

        print(f":: Retrieving services")
        services = client.services
        print(f":: Retrieved services:")
        for service in services:
            print(service)

        # s0 = services[0]
        # s1 = services[1]
        # s2 = services[2]
        # s3 = services[3]
        # import ipdb; ipdb.set_trace()

        service = services.get_service(BASIC_INFO_SERVICE)
        if service:
            characteristic = service.get_characteristic(CHAR_UUID_RX)
            print("basic info characteristic:", characteristic)
            for c in service.characteristics:
                print(c)
            if characteristic:
                await client.start_notify(characteristic, notify_cb)
            # characteristic = service.get_characteristic(CHAR_UUID_TX)
            # print("extended info characteristic:", characteristic)
            # for c in service.characteristics:
            #     print(c)

        # service = services.get_service(EXTENDED_INFO_SERVICE)
        # if service:
        #     characteristic = service.get_characteristic(CHAR_UUID_RX)
        #     print("extended info characteristic:", characteristic)
        #     for c in service.characteristics:
        #         print(c)


        # print(":: Reading basic characteristic")
        # data = await client.read_gatt_char(CHAR_UUID_RX)
        # print(":: Read basic characteristic:")
        # print(data, len(data))
        # info = parse_basic_info(data)

        # print(":: Registering for characteristic notification")

        # print(":: Reading extended characteristic")
        # data = await client.read_gatt_char(CHAR_UUID_TX)
        # print(":: Read extended characteristic:")
        # print(data)
        # print(f"Voltage: {info}")

        # await client.start_notify(CHAR_UUID_RX, notify_cb)

        while True:
            await asyncio.sleep(1)

asyncio.run(main(ADDRESS))
