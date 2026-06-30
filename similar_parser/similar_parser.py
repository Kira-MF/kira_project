# -*- coding: utf-8 -*-
import asyncio
import csv
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.channels import GetChannelRecommendationsRequest

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")

DEPTH = 3

if not API_ID:
    raise RuntimeError("API_ID не задан в .env")

if not API_HASH:
    raise RuntimeError("API_HASH не задан в .env")

async def get_similar(client, channel, depth, visited=None):
    if visited is None:
        visited = set()

    if depth == 0 or channel in visited:
        return []

    visited.add(channel)
    results = []

    try:
        entity = await client.get_entity(channel)
        recommended = await client(GetChannelRecommendationsRequest(channel=entity))

        for ch in recommended.chats:
            username = getattr(ch, "username", None)
            title = getattr(ch, "title", "")
            members = getattr(ch, "participants_count", 0)
            link = f"https://t.me/{username}" if username else "no link"

            print(f"[+] Found: {title} | {link} | {members} subscribers")

            results.append({
                "title": title,
                "link": link,
                "subscribers": members,
            })

            if username and depth > 1:
                deeper = await get_similar(client, username, depth - 1, visited)
                results.extend(deeper)

    except Exception as e:
        print(f"[!] Error for {channel}: {e}")

    return results


async def main():
    channel_input = input("Enter channel link or @username: ").strip()
    if channel_input.startswith("https://t.me/"):
        channel_input = channel_input.replace("https://t.me/", "")

    print(f"\n[*] Starting with depth {DEPTH}...\n")

    async with TelegramClient("session", API_ID, API_HASH) as client:
        results = await get_similar(client, channel_input, DEPTH)

    seen = set()
    unique = []
    for item in results:
        if item["link"] not in seen:
            seen.add(item["link"])
            unique.append(item)

    unique.sort(key=lambda x: x["subscribers"] or 0, reverse=True)

    output_file = "similar_channels.csv"
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "link", "subscribers"])
        writer.writeheader()
        writer.writerows(unique)

    print(f"\n[+] Done! Found: {len(unique)} channels")
    print(f"[+] Saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
