"""Symphony BDK core package

There is an outstanding issue with aiohttp and Python 3.8+ on Windows. This affects our client when using a
proxy on Windows with Python 3.8+. As known workaround, the following code is meant to avoid this issue by detecting the
operating system and setting WindowsSelectorEventLoopPolicy as event loop policy.
"""
import asyncio
import os

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
