#!/usr/bin/env python3
"""
notify.py "<message>" [--channel general]

Send a message to Polrea via BLE (Polrea/bitchat-mini protocol).
Scans for the Polrea Mac app peripheral and writes a channel packet.
"""

import sys
import asyncio
import struct
import time
import os

SERVICE_UUID  = "4F91BCC5-4D0E-4BCF-A6E5-E65DEF64E754"
WRITE_UUID    = "4F91BCC6-4D0E-4BCF-A6E5-E65DEF64E754"

VERSION: int  = 1
MSG_CHANNEL   = 0x07
DEFAULT_TTL   = 7
SENDER_ID     = bytes.fromhex("deadbeefcafe0001")  # fixed fake peer ID for Claude


def encode_channel_packet(channel: str, content: str) -> bytes:
    """Build a Polrea wire-format channel packet."""
    # ChannelPayload: [1-byte channel len][channel UTF-8][content UTF-8]
    ch_bytes  = channel.encode()[:64]
    ct_bytes  = content.encode()
    payload   = bytes([len(ch_bytes)]) + ch_bytes + ct_bytes

    # Header: [version:1][type:1][ttl:1][timestamp:8][flags:1][payloadLen:2][senderID:8]
    timestamp = int(time.time() * 1000)
    flags     = 0x00  # no recipient, no signature, no compression
    header    = struct.pack(
        ">BBBQBh8s",
        VERSION,
        MSG_CHANNEL,
        DEFAULT_TTL,
        timestamp,
        flags,
        len(payload),
        SENDER_ID,
    )
    return header + payload


async def send(message: str, channel: str = "general"):
    from bleak import BleakScanner, BleakClient

    print(f"Scanning for Polrea…", flush=True)
    device = await BleakScanner.find_device_by_filter(
        lambda d, _: d.name and "polrea" in d.name.lower(),
        timeout=8.0
    )

    if not device:
        # Fallback: find any device advertising our service UUID
        device = await BleakScanner.find_device_by_filter(
            lambda d, adv: SERVICE_UUID.lower() in [str(u).lower() for u in (adv.service_uuids or [])],
            timeout=8.0
        )

    if not device:
        print("Polrea device not found via BLE. Is the Mac app running?", flush=True)
        sys.exit(1)

    print(f"Found: {device.name} ({device.address})", flush=True)

    packet = encode_channel_packet(channel, message)

    async with BleakClient(device) as client:
        await client.write_gatt_char(WRITE_UUID, packet, response=False)
        print(f"Sent to #{channel}: {message}", flush=True)


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: notify.py '<message>' [--channel <name>]")
        sys.exit(1)

    channel = "general"
    if "--channel" in args:
        i = args.index("--channel")
        channel = args[i + 1]
        args = args[:i] + args[i + 2:]

    message = " ".join(args)
    asyncio.run(send(message, channel))


if __name__ == "__main__":
    main()
