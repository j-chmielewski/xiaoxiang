import asyncio
from akku.bms import Bms


ADDRESS = "A4:C1:37:30:8D:90"

async def main(address):
    bms = Bms(address)
    async for data in bms.read():
        print(data)


if __name__ == '__main__':
    asyncio.run(main(ADDRESS))

