import asyncio
from akku.ble import main


ADDRESS = "A4:C1:37:30:8D:90"


if __name__ == '__main__':
    asyncio.run(main(ADDRESS))

