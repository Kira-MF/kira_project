# -*- coding: utf-8 -*-
import asyncio
import csv
from playwright.async_api import async_playwright

OUTPUT_FILE = "similar_channels.csv"

async def login(page):
    print("[*] Opening web.telegram.org...")
    await page.goto("https://web.telegram.org/k/")
    await page.wait_for_timeout(5000)
    print("[!] Log in to Telegram in the browser window.")
    print("[!] Press Enter here after you are logged in...")
    input()
    await page.wait_for_timeout(3000)

async def search_and_open(page, username):
    print(f"[*] Searching for: @{username}")
    try:
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(1000)

        search = page.locator('input.input-search-input').first
        await search.click()
        await search.fill("")
        await page.wait_for_timeout(500)
        await search.type(username, delay=150)
        await page.wait_for_timeout(3000)

        # look specifically in Global search section
        # Global search items have username starting with @
        rows = await page.locator('.row-clickable').all()
        
        clicked = False
        for row in rows:
            try:
                text = await row.inner_text()
                # only click if row contains @username (global search result)
                if f"@{username.lower()}" in text.lower():
                    await row.click()
                    await page.wait_for_timeout(3000)
                    print(f"[+] Opened: {text[:60].strip()}")
                    clicked = True
                    break
            except:
                continue

        if not clicked:
            print(f"[!] Could not find @{username} in global search")
            return False

        return True

    except Exception as e:
        print(f"[!] Search error: {e}")
        return False

async def get_similar_from_page(page):
    similar = []
    try:
        # click channel header to open profile
        header_selectors = [
            '.chat-info-container',
            '.chat-info',
            '.person',
        ]

        clicked = False
        for sel in header_selectors:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=1500):
                    await el.click()
                    clicked = True
                    break
            except:
                continue

        if not clicked:
            print("[!] Could not open channel profile")
            return similar

        await page.wait_for_timeout(2000)

        # scroll down to find similar channels section
        for _ in range(12):
            await page.keyboard.press("PageDown")
            await page.wait_for_timeout(300)

        cards = await page.locator('.similar-channel').all()
        print(f"[*] Similar channels found: {len(cards)}")

        for card in cards:
            try:
                title = await card.locator('.peer-title').first.inner_text()
                sub_el = card.locator('.row-subtitle')
                subs = await sub_el.first.inner_text() if await sub_el.count() > 0 else "unknown"
                link_el = card.locator('a')
                link = await link_el.first.get_attribute('href') if await link_el.count() > 0 else "unknown"

                if title.strip():
                    similar.append({
                        "title": title.strip(),
                        "link": link.strip() if link else "unknown",
                        "subscribers": subs.strip()
                    })
                    print(f"  [+] {title.strip()} | {subs.strip()}")
            except:
                continue

        await page.keyboard.press("Escape")
        await page.wait_for_timeout(1000)

    except Exception as e:
        print(f"[!] Error: {e}")
        try:
            await page.keyboard.press("Escape")
        except:
            pass

    return similar

async def main():
    channel_input = input("Enter channel @username (without @): ").strip()
    channel_input = channel_input.replace("https://t.me/", "").replace("@", "")

    all_results = []
    visited = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        await login(page)

        visited.add(channel_input)
        found = await search_and_open(page, channel_input)

        if not found:
            print("[!] Could not find channel.")
            await browser.close()
            return

        similar_1 = await get_similar_from_page(page)
        all_results.extend(similar_1)

        print(f"\n[*] Depth 2 - parsing similar of similar...\n")
        for item in similar_1:
            link = item.get("link", "")
            username = link.replace("https://t.me/", "").strip()
            if username and username != "unknown" and username not in visited:
                visited.add(username)
                if await search_and_open(page, username):
                    deeper = await get_similar_from_page(page)
                    all_results.extend(deeper)

        await browser.close()

    seen = set()
    unique = []
    for item in all_results:
        if item["link"] not in seen:
            seen.add(item["link"])
            unique.append(item)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "link", "subscribers"])
        writer.writeheader()
        writer.writerows(unique)

    print(f"\n[+] Done! Found {len(unique)} unique channels")
    print(f"[+] Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
