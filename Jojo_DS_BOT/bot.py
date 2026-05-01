# -*- coding: utf-8 -*-
import discord
from discord import app_commands
from discord.ext import commands
import json, os, random, asyncio
from datetime import datetime, timedelta
from stands import (STANDS, TIER_COLORS, TIER_EMOJI, TIER_WEIGHTS,
                    EVOLUTION_CHAINS, ABILITY_UPGRADES,
                    get_stand_by_tier, can_evolve, get_evolution)

# в”Ђв”Ђв”Ђ CONFIG в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
TOKEN    = "����_�����_����"
DB_FILE  = "players.json"
GUILD_ID = 1003592872098021396  

STAT_BAR = {
    "A": "[A]", "B": "[B]", "C": "[C]",
    "D": "[D]", "E": "[E]", "Z": "[Z]"
}
STAT_UP = {"E": "D", "D": "C", "C": "B", "B": "A", "A": "Z"}

ITEM_ICONS = {
    "money": "рџ’°", "regular_arrow": "рџЏ№", "requiem_arrow": "вњЁ",
    "overheaven_arrow": "вљЎ", "crystal": "рџ’Ћ", "rokakaka": "рџЌ€",
    "common_crate": "рџ“¦", "rare_crate": "рџџ¦", "epic_crate": "рџџЈ",
    "legendary_crate": "рџЊџ", "stone_mask": "рџЋ­",
}

CRATE_CONFIG = {
    "common":    {"name": "Common Crate",    "icon": "рџ“¦", "color": 0x95a5a6, "money_min": 100,  "money_max": 300,  "regular_arrow_chance": 20.0, "requiem_arrow_chance": 0.1,  "stone_mask_chance": 0.0, "rokakaka_chance": 0.0},
    "rare":      {"name": "Rare Crate",      "icon": "рџџ¦", "color": 0x3498db, "money_min": 300,  "money_max": 700,  "regular_arrow_chance": 35.0, "requiem_arrow_chance": 0.3,  "stone_mask_chance": 0.0, "rokakaka_chance": 0.0},
    "epic":      {"name": "Epic Crate",      "icon": "рџџЈ", "color": 0x9b59b6, "money_min": 700,  "money_max": 1500, "regular_arrow_chance": 49.0, "requiem_arrow_chance": 0.5,  "stone_mask_chance": 0.0, "rokakaka_chance": 5.0},
    "legendary": {"name": "Legendary Crate", "icon": "рџЊџ", "color": 0xf1c40f, "money_min": 1500, "money_max": 3000, "regular_arrow_chance": 70.0, "requiem_arrow_chance": 1.5,  "stone_mask_chance": 1.5, "rokakaka_chance": 9.0},
}

EVOLVE_CHANCES = {"D": 15.0, "C": 12.0, "B": 10.0, "A": 8.0, "S": 5.0, "SS": 3.0}

UPGRADE_COST = {
    2: {"crystals": 5,  "money": 1000},
    3: {"crystals": 15, "money": 3000},
}

ARROW_POOLS = {
    "regular":    {"D": 30, "C": 28, "B": 20, "A": 13, "S": 6,  "SS": 3},
    "requiem":    {"D":  2, "C":  8, "B": 15, "A": 30, "S": 35, "SS": 10},
    "overheaven": {"D":  0, "C":  2, "B":  8, "A": 20, "S": 40, "SS": 30},
}

JOBS = [
    ("РїСЂРѕРґР°РІР°Р» РµРґСѓ РІРµСЃСЊ РґРµРЅСЊ",                   100,  250, 90, "easy"),
    ("РґРѕСЃС‚Р°РІР»СЏР» РїРѕСЃС‹Р»РєРё",                         120,  280, 85, "easy"),
    ("С‡РёСЃС‚РёР» СѓР»РёС†С‹ Morioh",                        80,  200, 95, "easy"),
    ("РїРѕРјРѕРіР°Р» РІ РјР°СЃС‚РµСЂСЃРєРѕР№",                      100,  300, 85, "easy"),
    ("РѕС…СЂР°РЅСЏР» СЃРєР»Р°Рґ РЅРѕС‡СЊСЋ",                       250,  500, 70, "medium"),
    ("СЂР°Р±РѕС‚Р°Р» РЅР° СЃС‚СЂРѕР№РєРµ",                        300,  550, 65, "medium"),
    ("РїРѕРјРѕРіР°Р» РІ СЂРµСЃС‚РѕСЂР°РЅРµ Trattoria Trussardi",   350,  600, 70, "medium"),
    ("СЂР°Р±РѕС‚Р°Р» РІС‹С€РёР±Р°Р»РѕР№ РІ Р±Р°СЂРµ",                  280,  520, 65, "medium"),
    ("РЅР°С€С‘Р» СЂР°Р±РѕС‚Сѓ РІ Passione",                   500, 1000, 50, "hard"),
    ("РІС‹РїРѕР»РЅСЏР» Р·Р°РґР°РЅРёРµ РѕС‚ Speedwagon Foundation", 600, 1200, 45, "hard"),
    ("РѕС…РѕС‚РёР»СЃСЏ РЅР° РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ СЃС‚РµРЅРґР°",           700, 1500, 40, "hard"),
    ("СЂР°Р±РѕС‚Р°Р» РЅР° DIO",                            800, 1800, 35, "hard"),
]
JOB_FAIL = [
    "РўРµР±СЏ РїРѕР№РјР°Р»Рё вЂ” РїСЂРёС€Р»РѕСЃСЊ СЃР±РµР¶Р°С‚СЊ!", "Р‘РѕСЃСЃ СѓРІРѕР»РёР» С‚РµР±СЏ Р·Р° Р»РµРЅСЊ...",
    "РўС‹ РїСЂРѕРІР°Р»РёР» Р·Р°РґР°РЅРёРµ!", "РќРµ РїРѕРІРµР·Р»Рѕ вЂ” СЂР°Р±РѕС‚Сѓ РїРµСЂРµС…РІР°С‚РёР» РєС‚Рѕ-С‚Рѕ РґСЂСѓРіРѕР№.",
    "Р’СЂР°Р¶РµСЃРєРёР№ СЃС‚РµРЅРґ РїРѕРјРµС€Р°Р» С‚РµР±Рµ!", "РљР»РёРµРЅС‚ РѕС‚РєР°Р·Р°Р»СЃСЏ РїР»Р°С‚РёС‚СЊ!",
    "РџРѕР»РёС†РёСЏ СЂР°Р·РѕРіРЅР°Р»Р° РІСЃРµС… вЂ” С‚С‹ РЅРёС‡РµРіРѕ РЅРµ Р·Р°СЂР°Р±РѕС‚Р°Р».",
]
JOBS_REQUIRED = 3

SHOP_ITEMS = {
    "arrow":   {"name": "Regular Arrow", "icon": "рџЏ№", "price": 500,  "type": "regular_arrow"},
    "crystal": {"name": "Crystal",       "icon": "рџ’Ћ", "price": 800,  "type": "crystal"},
    "common":  {"name": "Common Crate",  "icon": "рџ“¦", "price": 1000, "type": "common_crate"},
    "rare":    {"name": "Rare Crate",    "icon": "рџџ¦", "price": 2500, "type": "rare_crate"},
}

QUESTS = [
    {"id": "worker",     "name": "Р Р°Р±РѕС‚СЏРіР°",    "desc": "Р’С‹РїРѕР»РЅРё 5 СЂР°Р±РѕС‚",          "type": "jobs_done_total", "goal": 5,    "reward": {"crystals": 3},           "reward_text": "рџ’Ћ 3 РєСЂРёСЃС‚Р°Р»Р»Р°"},
    {"id": "searcher",   "name": "Р�СЃРєР°С‚РµР»СЊ",    "desc": "Р�СЃРїРѕР»СЊР·СѓР№ /search 3 СЂР°Р·Р°", "type": "searches_done",  "goal": 3,    "reward": {"money": 500},            "reward_text": "рџ’° $500"},
    {"id": "collector",  "name": "РљРѕР»Р»РµРєС†РёРѕРЅРµСЂ","desc": "Р’С‹РїРѕР»РЅРё 10 СЂР°Р±РѕС‚",         "type": "jobs_done_total", "goal": 10,   "reward": {"crystals": 8},           "reward_text": "рџ’Ћ 8 РєСЂРёСЃС‚Р°Р»Р»РѕРІ"},
    {"id": "lucky",      "name": "РЈРґР°С‡Р°",       "desc": "РћС‚РєСЂРѕР№ 3 Р»СЋР±С‹С… РєРµР№СЃР°",     "type": "crates_opened",  "goal": 3,    "reward": {"money": 1500},           "reward_text": "рџ’° $1500"},
    {"id": "rich",       "name": "Р‘РѕРіР°С‡",       "desc": "РќР°РєРѕРїРё $3000",             "type": "money_reach",    "goal": 3000, "reward": {"crates": {"common": 2}}, "reward_text": "рџ“¦ 2 Common Crate"},
    {"id": "shooter",    "name": "РЎС‚СЂРµР»РѕРє",     "desc": "Р�СЃРїРѕР»СЊР·СѓР№ СЃС‚СЂРµР»Сѓ 3 СЂР°Р·Р°", "type": "arrows_used",    "goal": 3,    "reward": {"crystals": 5, "money": 1000}, "reward_text": "рџ’Ћ 5 + рџ’° $1000"},
    {"id": "epic_hunter","name": "РћС…РѕС‚РЅРёРє",     "desc": "РћС‚РєСЂРѕР№ 1 Epic РєРµР№СЃ",       "type": "epic_opened",    "goal": 1,    "reward": {"crystals": 15},          "reward_text": "рџ’Ћ 15 РєСЂРёСЃС‚Р°Р»Р»РѕРІ"},
]

# в”Ђв”Ђв”Ђ DATABASE в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_player(db, user_id):
    uid = str(user_id)
    if uid not in db:
        db[uid] = {
            "stand": None,
            "money": 500,
            "arrows": {"regular": 0, "requiem": 0, "overheaven": 0},
            "crates": {"common": 0, "rare": 0, "epic": 0, "legendary": 0},
            "crystals": 0, "fruits": 0, "stone_masks": 0,
            "jobs_done": 0, "last_job": None,
            "ability_tier": 1, "is_vampire": False,
            "stand_stats": None, "sub_ability": None,
            "quest": None, "quest_progress": 0,
            "searches_done": 0, "arrows_used": 0,
            "crates_opened": 0, "epic_opened": 0,
            "jobs_done_total": 0,
            "storage": [],  # list of stand objects max 2
        }
    p = db[uid]
    defaults = {
        "jobs_done": 0, "ability_tier": 1, "is_vampire": False,
        "stand_stats": None, "stone_masks": 0, "sub_ability": None,
        "quest": None, "quest_progress": 0, "searches_done": 0,
        "arrows_used": 0, "crates_opened": 0, "epic_opened": 0,
        "jobs_done_total": 0, "storage": [],
    }
    for key, val in defaults.items():
        if key not in p:
            p[key] = val
    if "normal" in p.get("crates", {}):
        old = p["crates"]
        p["crates"] = {"common": old.get("normal",0)+old.get("money",0), "rare": old.get("arrow",0), "epic": old.get("crystal",0), "legendary": 0}
    p.pop("last_search", None)
    return p

# в”Ђв”Ђв”Ђ STAND OBJECT в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
def make_stand_obj(name, ability_tier=1, is_vampire=False, stand_stats=None, sub_ability=None):
    """Create a stand storage object."""
    return {
        "name": name,
        "ability_tier": ability_tier,
        "is_vampire": is_vampire,
        "stand_stats": stand_stats,
        "sub_ability": sub_ability,
    }

def get_active_stand_obj(player):
    """Get active stand as an object."""
    if not player["stand"]:
        return None
    return make_stand_obj(
        player["stand"],
        player.get("ability_tier", 1),
        player.get("is_vampire", False),
        player.get("stand_stats"),
        player.get("sub_ability"),
    )

def set_active_stand(player, stand_obj):
    """Set active stand from object."""
    if stand_obj is None:
        player["stand"] = None
        player["ability_tier"] = 1
        player["is_vampire"] = False
        player["stand_stats"] = None
        player["sub_ability"] = None
    else:
        player["stand"]        = stand_obj["name"]
        player["ability_tier"] = stand_obj.get("ability_tier", 1)
        player["is_vampire"]   = stand_obj.get("is_vampire", False)
        player["stand_stats"]  = stand_obj.get("stand_stats")
        player["sub_ability"]  = stand_obj.get("sub_ability")

# в”Ђв”Ђв”Ђ HELPERS в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
def get_stand_stats(player, stand_name):
    if player.get("stand_stats") and player.get("stand") == stand_name:
        return player["stand_stats"]
    return dict(STANDS[stand_name]["stats"])

def stand_embed(stand_name, player=None, user_obj=None):
    stand = STANDS[stand_name]
    tier  = stand["tier"]
    color = TIER_COLORS.get(tier, 0xffffff)
    emoji = TIER_EMOJI.get(tier, "")

    embed = discord.Embed(title=f"{emoji} {stand_name}", color=color)
    embed.add_field(name="Master", value=stand["user"],            inline=True)
    embed.add_field(name="Part",   value=f"Part {stand['part']}", inline=True)
    embed.add_field(name="Tier",   value=f"{emoji} **{tier}**",   inline=True)

    stats = get_stand_stats(player, stand_name) if player else dict(stand["stats"])
    stats_text = "\n".join([
        f"Destructive Power: **{stats['destructive_power']}** {STAT_BAR.get(stats['destructive_power'],'?')}",
        f"Speed:             **{stats['speed']}**             {STAT_BAR.get(stats['speed'],'?')}",
        f"Range:             **{stats['range']}**             {STAT_BAR.get(stats['range'],'?')}",
        f"Durability:        **{stats['durability']}**        {STAT_BAR.get(stats['durability'],'?')}",
        f"Precision:         **{stats['precision']}**         {STAT_BAR.get(stats['precision'],'?')}",
        f"Potential:         **{stats['potential']}**         {STAT_BAR.get(stats['potential'],'?')}",
    ])
    embed.add_field(name="Stats", value=stats_text, inline=False)
    embed.add_field(name="Power", value=f"**{stand['power']}**", inline=True)

    atier    = player["ability_tier"] if player else 1
    upgrades = ABILITY_UPGRADES.get(stand_name, {})
    ability_text = upgrades.get(atier, stand["ability"])
    embed.add_field(name=f"Ability {'в­ђ'*atier}", value=ability_text, inline=False)

    if stand.get("ability2"):
        embed.add_field(name="Ability 2", value=stand["ability2"], inline=False)
    if player and player.get("is_vampire"):
        embed.add_field(name="рџ§› Vampire", value="Vampiric Freeze вЂ” Р·Р°РјРѕСЂР°Р¶РёРІР°РµС‚ РІСЂР°РіР° РїСЂРё РєР°СЃР°РЅРёРё", inline=False)
    if player and player.get("sub_ability"):
        embed.add_field(name="рџЌ€ Sub-Ability", value=player["sub_ability"], inline=False)
    if stand.get("evolves_to"):
        embed.add_field(name="в¬†пёЏ Evolves to", value=f"**{stand['evolves_to']}**", inline=False)
    if stand.get("image"):
        embed.set_thumbnail(url=stand["image"])
    if user_obj:
        embed.set_footer(text=f"Owner: {user_obj.display_name}")
    return embed

def open_crate(crate_type):
    cfg = CRATE_CONFIG[crate_type]
    rewards = [{"type": "money", "amount": random.randint(cfg["money_min"], cfg["money_max"])}]
    if random.uniform(0,100) < cfg["regular_arrow_chance"]:
        rewards.append({"type": "regular_arrow", "amount": 1})
    if random.uniform(0,100) < cfg["requiem_arrow_chance"]:
        rewards.append({"type": "requiem_arrow", "amount": 1})
    if cfg.get("stone_mask_chance",0) > 0 and random.uniform(0,100) < cfg["stone_mask_chance"]:
        rewards.append({"type": "stone_mask", "amount": 1})
    if cfg.get("rokakaka_chance",0) > 0 and random.uniform(0,100) < cfg["rokakaka_chance"]:
        rewards.append({"type": "rokakaka", "amount": 1})
    return rewards

def roll_crate_type():
    r = random.randint(1,100)
    if r<=55: return "common"
    elif r<=80: return "rare"
    elif r<=90: return "epic"
    elif r<=95: return "legendary"
    return None

def assign_quest(player):
    q = random.choice(QUESTS)
    player["quest"] = q["id"]
    player["quest_progress"] = 0
    ctype = q["type"]
    if ctype in ["jobs_done_total","searches_done","arrows_used","crates_opened","epic_opened"]:
        player[ctype] = 0

def get_quest_progress(player, quest):
    qtype = quest["type"]
    if qtype == "money_reach":
        return player.get("money", 0)
    return player.get(qtype, 0)

# в”Ђв”Ђв”Ђ BOT SETUP в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    print(f"[+] {bot.user} is online! Stands: {len(STANDS)}")
    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID)
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
        print(f"[+] Slash commands synced to guild {GUILD_ID}")
    else:
        await tree.sync()
        print("[+] Slash commands synced globally (may take up to 1 hour)")

# в”Ђв”Ђв”Ђ SLASH COMMANDS в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

@tree.command(name="job", description="Р Р°Р±РѕС‚Р° вЂ” Р·Р°СЂР°Р±Р°С‚С‹РІР°Р№ РґРµРЅСЊРіРё (РєРґ: 30 РјРёРЅ)")
async def job(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    now = datetime.utcnow()
    if player["last_job"]:
        last = datetime.fromisoformat(player["last_job"])
        diff = now - last
        if diff < timedelta(minutes=30):
            rem = timedelta(minutes=30) - diff
            await interaction.response.send_message(
                f"вЏі РџРѕРґРѕР¶РґРё **{int(rem.total_seconds()//60)}Рј {int(rem.total_seconds()%60)}СЃ** РґРѕ СЃР»РµРґСѓСЋС‰РµР№ СЂР°Р±РѕС‚С‹.",
                ephemeral=True
            ); return

    job_name, mn, mx, sc, diff = random.choice(JOBS)
    de = {"easy":"рџџў","medium":"рџџЎ","hard":"рџ”ґ"}
    dt = {"easy":"Р›С‘РіРєР°СЏ","medium":"РЎСЂРµРґРЅСЏСЏ","hard":"РЎР»РѕР¶РЅР°СЏ"}
    player["last_job"] = now.isoformat()

    if random.randint(1,100) <= sc:
        earned = random.randint(mn, mx)
        player["money"] += earned
        player["jobs_done"] += 1
        player["jobs_done_total"] = player.get("jobs_done_total", 0) + 1
        bonus_crate = None
        if diff == "hard" and random.uniform(0,100) < 5.0:
            bonus_crate = random.choice(["epic","legendary"])
            player["crates"][bonus_crate] += 1
        save_db(db)
        embed = discord.Embed(title="вњ… Р Р°Р±РѕС‚Р° РІС‹РїРѕР»РЅРµРЅР°!", color=0x2ecc71)
        embed.add_field(name=f"{de[diff]} {dt[diff]}", value=f"РўС‹ **{job_name}** Рё Р·Р°СЂР°Р±РѕС‚Р°Р» **${earned}**!", inline=False)
        embed.add_field(name="рџ’° Р‘Р°Р»Р°РЅСЃ", value=f"**${player['money']:,}**", inline=True)
        embed.add_field(name="рџ”Ё Jobs",   value=f"**{player['jobs_done']}/{JOBS_REQUIRED}**", inline=True)
        if bonus_crate:
            cfg = CRATE_CONFIG[bonus_crate]
            embed.add_field(name="рџЋЃ Р‘РѕРЅСѓСЃ!", value=f"{cfg['icon']} **{cfg['name']}** РЅР°С€С‘Р» РІРѕ РІСЂРµРјСЏ СЂР°Р±РѕС‚С‹!", inline=False)
        if player["jobs_done"] >= JOBS_REQUIRED:
            embed.add_field(name="рџ”Ќ Search РіРѕС‚РѕРІ!", value="Р�СЃРїРѕР»СЊР·СѓР№ `/search`!", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        save_db(db)
        embed = discord.Embed(title="вќЊ Р Р°Р±РѕС‚Р° РїСЂРѕРІР°Р»РµРЅР°!", color=0xe74c3c)
        embed.add_field(name=f"{de[diff]} {dt[diff]}", value=f"**{job_name}**\n{random.choice(JOB_FAIL)}", inline=False)
        embed.add_field(name="рџ”Ё Jobs", value=f"**{player['jobs_done']}/{JOBS_REQUIRED}**", inline=True)
        embed.set_footer(text="РџСЂРѕРІР°Р» РЅРµ СЃС‡РёС‚Р°РµС‚СЃСЏ вЂ” РїРѕРїСЂРѕР±СѓР№ С‡РµСЂРµР· 30 РјРёРЅ")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="search", description="РќР°Р№С‚Рё РєРµР№СЃ (РЅСѓР¶РЅРѕ 3 РІС‹РїРѕР»РЅРµРЅРЅС‹С… СЂР°Р±РѕС‚С‹)")
async def search(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    if player["jobs_done"] < JOBS_REQUIRED:
        await interaction.response.send_message(
            f"вќЊ РќСѓР¶РЅРѕ РµС‰С‘ **{JOBS_REQUIRED-player['jobs_done']}** СЂР°Р±РѕС‚!\nрџ”Ё **{player['jobs_done']}/{JOBS_REQUIRED}**",
            ephemeral=True
        ); return

    player["jobs_done"] = 0
    player["searches_done"] = player.get("searches_done",0) + 1
    crate_type = roll_crate_type()
    if not crate_type:
        save_db(db)
        await interaction.response.send_message(
            embed=discord.Embed(title="рџ”Ќ РџРѕРёСЃРє", description="РќРёС‡РµРіРѕ РЅРµ РЅР°С€С‘Р»...", color=0x95a5a6),
            ephemeral=True
        ); return

    player["crates"][crate_type] += 1
    save_db(db)
    cfg = CRATE_CONFIG[crate_type]
    embed = discord.Embed(title="рџ”Ќ РќР°С…РѕРґРєР°!", description=f"РўС‹ РЅР°С€С‘Р» {cfg['icon']} **{cfg['name']}**!", color=cfg["color"])
    embed.set_footer(text="Р�СЃРїРѕР»СЊР·СѓР№ /crate open")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="arrow", description="Р�СЃРїРѕР»СЊР·РѕРІР°С‚СЊ СЃС‚СЂРµР»Сѓ РґР»СЏ РїРѕР»СѓС‡РµРЅРёСЏ СЃС‚РµРЅРґР°")
@app_commands.describe(arrow_type="РўРёРї СЃС‚СЂРµР»С‹: regular, requiem, overheaven")
@app_commands.choices(arrow_type=[
    app_commands.Choice(name="regular",    value="regular"),
    app_commands.Choice(name="requiem",    value="requiem"),
    app_commands.Choice(name="overheaven", value="overheaven"),
])
async def arrow(interaction: discord.Interaction, arrow_type: str = "regular"):
    db = load_db(); player = get_player(db, interaction.user.id)
    if player["arrows"][arrow_type] <= 0:
        await interaction.response.send_message(
            f"вќЊ РЈ С‚РµР±СЏ РЅРµС‚ **{arrow_type}** СЃС‚СЂРµР»С‹! РљСѓРїРё РІ `/shop` РёР»Рё РЅР°Р№РґРё С‡РµСЂРµР· `/search`.",
            ephemeral=True
        ); return

    pool = ARROW_POOLS[arrow_type]
    weighted = []
    for tier, w in pool.items(): weighted.extend([tier]*w)
    chosen_tier = random.choice(weighted)
    candidates = get_stand_by_tier(chosen_tier)
    stand_name = random.choice(candidates)
    player["arrows"][arrow_type] -= 1
    player["arrows_used"] = player.get("arrows_used",0) + 1

    if player["stand"] and player["stand"] != stand_name:
        # offer to store old stand
        storage = player.get("storage", [])
        old_stand_obj = get_active_stand_obj(player)
        new_embed = stand_embed(stand_name)
        new_embed.set_author(name=f"РќРѕРІС‹Р№ СЃС‚РµРЅРґ!")

        if len(storage) < 2:
            new_embed.set_footer(text=f"РЈ С‚РµР±СЏ СѓР¶Рµ РµСЃС‚СЊ СЃС‚РµРЅРґ. РќР°Р¶РјРё вњ… СЃРјРµРЅРёС‚СЊ | рџ“¦ СЃРѕС…СЂР°РЅРёС‚СЊ СЃС‚Р°СЂС‹Р№ РІ storage")
            await interaction.response.send_message(embed=new_embed, ephemeral=True)
            msg = await interaction.original_response()
            await msg.add_reaction("вњ…")
            await msg.add_reaction("рџ“¦")

            def check(r, u): return u == interaction.user and str(r.emoji) in ["вњ…","рџ“¦"] and r.message.id == msg.id
            try:
                reaction, _ = await bot.wait_for("reaction_add", timeout=30.0, check=check)
                if str(reaction.emoji) == "рџ“¦":
                    storage.append(old_stand_obj)
                    player["storage"] = storage
                player["stand"] = stand_name
                player["ability_tier"] = 1
                player["is_vampire"] = False
                player["stand_stats"] = None
                player["sub_ability"] = None
                save_db(db)
                action = "СЃРѕС…СЂР°РЅС‘РЅ РІ storage, СЃС‚РµРЅРґ СЃРјРµРЅС‘РЅ" if str(reaction.emoji) == "рџ“¦" else "СЃРјРµРЅС‘РЅ"
                await msg.edit(content=f"вњ… РЎС‚РµРЅРґ {action}: **{stand_name}**!")
            except asyncio.TimeoutError:
                save_db(db)
                await msg.edit(content="вќЊ Р’СЂРµРјСЏ РІС‹С€Р»Рѕ вЂ” СЃС‚РµРЅРґ РЅРµ СЃРјРµРЅС‘РЅ.")
        else:
            new_embed.set_footer(text="РЈ С‚РµР±СЏ СѓР¶Рµ РµСЃС‚СЊ СЃС‚РµРЅРґ. РќР°Р¶РјРё вњ… С‡С‚РѕР±С‹ СЃРјРµРЅРёС‚СЊ (storage РїРѕР»РѕРЅ)")
            await interaction.response.send_message(embed=new_embed, ephemeral=True)
            msg = await interaction.original_response()
            await msg.add_reaction("вњ…")
            def check(r, u): return u == interaction.user and str(r.emoji) == "вњ…" and r.message.id == msg.id
            try:
                await bot.wait_for("reaction_add", timeout=30.0, check=check)
                player["stand"] = stand_name
                player["ability_tier"] = 1
                player["is_vampire"] = False
                player["stand_stats"] = None
                player["sub_ability"] = None
                save_db(db)
                await msg.edit(content=f"вњ… РЎС‚РµРЅРґ СЃРјРµРЅС‘РЅ РЅР° **{stand_name}**!")
            except asyncio.TimeoutError:
                save_db(db)
                await msg.edit(content="вќЊ Р’СЂРµРјСЏ РІС‹С€Р»Рѕ.")
        return

    player["stand"] = stand_name
    player["ability_tier"] = 1
    player["is_vampire"] = False
    player["stand_stats"] = None
    player["sub_ability"] = None
    save_db(db)
    embed = stand_embed(stand_name, player, interaction.user)
    embed.set_author(name=f"{interaction.user.display_name} РїРѕР»СѓС‡РёР» СЃС‚РµРЅРґ!")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="stand", description="РџРѕСЃРјРѕС‚СЂРµС‚СЊ СЃРІРѕР№ СЃС‚РµРЅРґ РёР»Рё СЃС‚РµРЅРґ РґСЂСѓРіРѕРіРѕ РёРіСЂРѕРєР°")
@app_commands.describe(user="Р�РіСЂРѕРє (РЅРµРѕР±СЏР·Р°С‚РµР»СЊРЅРѕ)")
async def stand(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    db = load_db(); player = get_player(db, target.id)
    if not player["stand"]:
        await interaction.response.send_message(f"вќЊ РЈ **{target.display_name}** РЅРµС‚ СЃС‚РµРЅРґР°!", ephemeral=True); return
    embed = stand_embed(player["stand"], player, target)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="inv", description="Р�РЅРІРµРЅС‚Р°СЂСЊ")
@app_commands.describe(user="Р�РіСЂРѕРє (РЅРµРѕР±СЏР·Р°С‚РµР»СЊРЅРѕ)")
async def inv(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    db = load_db(); player = get_player(db, target.id)

    embed = discord.Embed(title=f"рџЋ’ {target.display_name}", color=0x2c2f33)
    embed.add_field(name="рџЏ№ Arrows", value=(
        f"рџЏ№ **{player['arrows']['regular']}** Regular\n"
        f"вњЁ **{player['arrows']['requiem']}** Requiem\n"
        f"вљЎ **{player['arrows']['overheaven']}** Overheaven"
    ), inline=True)
    embed.add_field(name="рџ“¦ Crates", value=(
        f"рџ“¦ **{player['crates']['common']}** Common\n"
        f"рџџ¦ **{player['crates']['rare']}** Rare\n"
        f"рџџЈ **{player['crates']['epic']}** Epic\n"
        f"рџЊџ **{player['crates']['legendary']}** Legendary"
    ), inline=True)
    embed.add_field(name="рџ’Ћ Other", value=(
        f"рџ’Ћ **{player['crystals']}** Crystals\n"
        f"рџЌ€ **{player['fruits']}** Rokakaka\n"
        f"рџЋ­ **{player.get('stone_masks',0)}** Stone Mask"
    ), inline=True)

    stand_text = "None"
    if player["stand"]:
        sn = player["stand"]
        tier = STANDS[sn]["tier"]
        emoji = TIER_EMOJI.get(tier,"")
        vamp = " рџ§›" if player.get("is_vampire") else ""
        stand_text = f"{emoji} **{sn}**{vamp}\nAbility Tier: {'в­ђ'*player['ability_tier']}"
        if can_evolve(sn):
            evo = get_evolution(sn)
            chance = EVOLVE_CHANCES.get(tier, 5.0)
            stand_text += f"\nв¬†пёЏ в†’ **{evo}** ({chance}%)"

    embed.add_field(name="вљ”пёЏ Stand", value=stand_text, inline=False)

    storage = player.get("storage", [])
    if storage:
        storage_text = ""
        for i, s in enumerate(storage, 1):
            st = STANDS[s["name"]]["tier"]
            em = TIER_EMOJI.get(st,"")
            vamp = " рџ§›" if s.get("is_vampire") else ""
            storage_text += f"{i}. {em} **{s['name']}**{vamp} (Tier {'в­ђ'*s.get('ability_tier',1)})\n"
        embed.add_field(name="рџ—„пёЏ Storage", value=storage_text, inline=False)
    else:
        embed.add_field(name="рџ—„пёЏ Storage", value="РџСѓСЃС‚Рѕ (РјР°РєСЃ. 2 СЃС‚РµРЅРґР°)", inline=False)

    embed.add_field(name="рџ’° Money", value=f"**${player['money']:,}**", inline=True)
    embed.add_field(name="рџ”Ё Jobs",  value=f"**{player['jobs_done']}/{JOBS_REQUIRED}** РґР»СЏ search", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="storage", description="РЈРїСЂР°РІР»РµРЅРёРµ С…СЂР°РЅРёР»РёС‰РµРј СЃС‚РµРЅРґРѕРІ")
@app_commands.describe(action="store/swap/drop", slot="РЎР»РѕС‚ 1 РёР»Рё 2 (РґР»СЏ swap)")
@app_commands.choices(action=[
    app_commands.Choice(name="store вЂ” РїРѕР»РѕР¶РёС‚СЊ Р°РєС‚РёРІРЅС‹Р№ СЃС‚РµРЅРґ", value="store"),
    app_commands.Choice(name="swap  вЂ” РїРѕРјРµРЅСЏС‚СЊ СЃ Р°РєС‚РёРІРЅС‹Рј",     value="swap"),
    app_commands.Choice(name="drop  вЂ” РІС‹Р±СЂРѕСЃРёС‚СЊ Р°РєС‚РёРІРЅС‹Р№ СЃС‚РµРЅРґ", value="drop"),
])
async def storage(interaction: discord.Interaction, action: str, slot: int = 1):
    db = load_db(); player = get_player(db, interaction.user.id)
    store = player.get("storage", [])

    # в”Ђв”Ђ STORE в”Ђв”Ђ
    if action == "store":
        if not player["stand"]:
            await interaction.response.send_message("вќЊ РЈ С‚РµР±СЏ РЅРµС‚ Р°РєС‚РёРІРЅРѕРіРѕ СЃС‚РµРЅРґР°!", ephemeral=True); return
        if len(store) >= 2:
            await interaction.response.send_message("вќЊ Storage РїРѕР»РѕРЅ (РјР°РєСЃ. 2 СЃС‚РµРЅРґР°)! Р�СЃРїРѕР»СЊР·СѓР№ `/storage swap`.", ephemeral=True); return
        obj = get_active_stand_obj(player)
        store.append(obj)
        player["storage"] = store
        set_active_stand(player, None)
        save_db(db)
        await interaction.response.send_message(
            f"рџ“¦ **{obj['name']}** СЃРѕС…СЂР°РЅС‘РЅ РІ storage (СЃР»РѕС‚ {len(store)}).",
            ephemeral=True
        ); return

    # в”Ђв”Ђ SWAP в”Ђв”Ђ
    if action == "swap":
        if not store:
            await interaction.response.send_message("вќЊ Storage РїСѓСЃС‚!", ephemeral=True); return
        idx = slot - 1
        if idx < 0 or idx >= len(store):
            await interaction.response.send_message(f"вќЊ РЎР»РѕС‚ {slot} РЅРµ СЃСѓС‰РµСЃС‚РІСѓРµС‚. Р’ storage {len(store)} СЃС‚РµРЅРґ(Р°).", ephemeral=True); return

        stored_obj = store[idx]
        active_obj = get_active_stand_obj(player)

        # swap
        store[idx] = active_obj if active_obj else None
        if store[idx] is None:
            store.pop(idx)
        set_active_stand(player, stored_obj)
        player["storage"] = store
        save_db(db)

        embed = discord.Embed(title="рџ”„ РЎС‚РµРЅРґС‹ РїРѕРјРµРЅСЏРЅС‹!", color=0x3498db)
        embed.add_field(name="вљ”пёЏ РђРєС‚РёРІРЅС‹Р№ С‚РµРїРµСЂСЊ", value=f"**{stored_obj['name']}**", inline=True)
        if active_obj:
            embed.add_field(name="рџ“¦ Р’ storage С‚РµРїРµСЂСЊ", value=f"**{active_obj['name']}**", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # в”Ђв”Ђ DROP в”Ђв”Ђ
    if action == "drop":
        if not player["stand"]:
            await interaction.response.send_message("вќЊ РЈ С‚РµР±СЏ РЅРµС‚ Р°РєС‚РёРІРЅРѕРіРѕ СЃС‚РµРЅРґР°!", ephemeral=True); return
        sn = player["stand"]
        await interaction.response.send_message(
            f"вљ пёЏ РўС‹ СѓРІРµСЂРµРЅ С‡С‚Рѕ С…РѕС‡РµС€СЊ РІС‹Р±СЂРѕСЃРёС‚СЊ **{sn}**? Р­С‚Рѕ РґРµР№СЃС‚РІРёРµ РЅРµРѕР±СЂР°С‚РёРјРѕ!\nРќР°Р¶РјРё вњ… РґР»СЏ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ.",
            ephemeral=True
        )
        msg = await interaction.original_response()
        await msg.add_reaction("вњ…")
        def check(r, u): return u == interaction.user and str(r.emoji) == "вњ…" and r.message.id == msg.id
        try:
            await bot.wait_for("reaction_add", timeout=20.0, check=check)
            set_active_stand(player, None)
            save_db(db)
            await msg.edit(content=f"рџ—‘пёЏ РЎС‚РµРЅРґ **{sn}** РІС‹Р±СЂРѕС€РµРЅ.")
        except asyncio.TimeoutError:
            await msg.edit(content="вќЊ РћС‚РјРµРЅРµРЅРѕ.")


@tree.command(name="evolve", description="Р­РІРѕР»СЋС†РёСЏ СЃС‚РµРЅРґР°")
@app_commands.describe(evo_type="requiem (С‡РµСЂРµР· Requiem Arrow) РёР»Рё vampire (С‡РµСЂРµР· Stone Mask)")
@app_commands.choices(evo_type=[
    app_commands.Choice(name="requiem вЂ” СЌРІРѕР»СЋС†РёСЏ С‡РµСЂРµР· Requiem Arrow", value="requiem"),
    app_commands.Choice(name="vampire вЂ” РІР°РјРїРёСЂ С‡РµСЂРµР· Stone Mask",       value="vampire"),
])
async def evolve(interaction: discord.Interaction, evo_type: str = "requiem"):
    db = load_db(); player = get_player(db, interaction.user.id)
    if not player["stand"]:
        await interaction.response.send_message("вќЊ РЈ С‚РµР±СЏ РЅРµС‚ СЃС‚РµРЅРґР°!", ephemeral=True); return

    if evo_type == "vampire":
        if player.get("is_vampire"):
            await interaction.response.send_message("вќЊ РЎС‚РµРЅРґ СѓР¶Рµ СЏРІР»СЏРµС‚СЃСЏ РІР°РјРїРёСЂРѕРј!", ephemeral=True); return
        if player.get("stone_masks", 0) <= 0:
            await interaction.response.send_message("вќЊ РќСѓР¶РЅР° рџЋ­ **Stone Mask**! Р’С‹Р±РёРІР°РµС‚СЃСЏ РёР· Legendary Crate (1.5%).", ephemeral=True); return

        player["stone_masks"] -= 1
        stand_name = player["stand"]
        base_stats = get_stand_stats(player, stand_name)
        all_z = all(v == "A" for v in base_stats.values())
        new_stats = {k: "Z" if all_z else STAT_UP.get(v, v) for k, v in base_stats.items()}
        player["stand_stats"] = new_stats
        player["is_vampire"] = True
        save_db(db)

        embed = discord.Embed(title="рџ§› Vampire Evolution!", description=f"**{stand_name}** РїСЂРѕРЅР·С‘РЅ РљР°РјРµРЅРЅРѕР№ РњР°СЃРєРѕР№!", color=0x8e0000)
        stats_text = "\n".join([f"{k.replace('_',' ').title()}: **{base_stats[k]}** в†’ **{new_stats[k]}**" for k in new_stats])
        embed.add_field(name="рџ“Љ Р�Р·РјРµРЅРµРЅРёРµ СЃС‚Р°С‚РѕРІ", value=stats_text, inline=False)
        embed.add_field(name="рџ§› РќРѕРІР°СЏ СЃРїРѕСЃРѕР±РЅРѕСЃС‚СЊ", value="Vampiric Freeze вЂ” Р·Р°РјРѕСЂР°Р¶РёРІР°РµС‚ РІСЂР°РіР°", inline=False)
        if all_z:
            embed.add_field(name="рџ’Ђ GODLIKE", value="Р’СЃРµ СЃС‚Р°С‚С‹ **Z**!", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # requiem
    stand_name = player["stand"]
    if not can_evolve(stand_name):
        await interaction.response.send_message(f"вќЊ **{stand_name}** РЅРµ РјРѕР¶РµС‚ СЌРІРѕР»СЋС†РёРѕРЅРёСЂРѕРІР°С‚СЊ С‡РµСЂРµР· Requiem.", ephemeral=True); return
    if player["arrows"]["requiem"] <= 0:
        await interaction.response.send_message("вќЊ РќСѓР¶РЅР° вњЁ **Requiem Arrow**!", ephemeral=True); return

    evolution_name = get_evolution(stand_name)
    current_tier   = STANDS[stand_name]["tier"]
    chance         = EVOLVE_CHANCES.get(current_tier, 5.0)
    player["arrows"]["requiem"] -= 1

    if random.uniform(0, 100) < chance:
        player["stand"] = evolution_name
        player["ability_tier"] = 1
        player["is_vampire"] = False
        player["stand_stats"] = None
        player["sub_ability"] = None
        save_db(db)
        embed = stand_embed(evolution_name, player, interaction.user)
        embed.set_author(name=f"вњЁ {interaction.user.display_name} СЌРІРѕР»СЋС†РёРѕРЅРёСЂРѕРІР°Р» СЃС‚РµРЅРґ!")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        save_db(db)
        embed = discord.Embed(
            title="рџ’” Р­РІРѕР»СЋС†РёСЏ РїСЂРѕРІР°Р»РёР»Р°СЃСЊ!",
            description=f"**{stand_name}** РЅРµ РїСЂРёРЅСЏР» СЃС‚СЂРµР»Сѓ...\nРЁР°РЅСЃ Р±С‹Р» **{chance}%**\nРЎС‚СЂРµР»Р° РїРѕС‚СЂР°С‡РµРЅР°.",
            color=0xe74c3c
        )
        embed.add_field(name="в¬†пёЏ Р¦РµР»СЊ",        value=f"**{evolution_name}**",              inline=True)
        embed.add_field(name="вњЁ РћСЃС‚Р°Р»РѕСЃСЊ",    value=f"**{player['arrows']['requiem']}**", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="upgrade", description="РџСЂРѕРєР°С‡Р°С‚СЊ СЃРїРѕСЃРѕР±РЅРѕСЃС‚СЊ СЃС‚РµРЅРґР° (Tier 1в†’2в†’3)")
async def upgrade(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    if not player["stand"]:
        await interaction.response.send_message("вќЊ РЈ С‚РµР±СЏ РЅРµС‚ СЃС‚РµРЅРґР°!", ephemeral=True); return

    stand_name = player["stand"]
    cur_tier   = player["ability_tier"]
    if cur_tier >= 3:
        await interaction.response.send_message("вњ… РЎРїРѕСЃРѕР±РЅРѕСЃС‚СЊ СѓР¶Рµ РЅР° РјР°РєСЃРёРјСѓРјРµ (Tier 3)!", ephemeral=True); return

    next_tier = cur_tier + 1
    cost      = UPGRADE_COST[next_tier]
    upgrades  = ABILITY_UPGRADES.get(stand_name, {})
    current_ability = upgrades.get(cur_tier,  STANDS[stand_name]["ability"])
    next_ability    = upgrades.get(next_tier, STANDS[stand_name]["ability"])

    if player["crystals"] < cost["crystals"] or player["money"] < cost["money"]:
        await interaction.response.send_message(
            f"вќЊ РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ СЂРµСЃСѓСЂСЃРѕРІ!\nРќСѓР¶РЅРѕ: рџ’Ћ **{cost['crystals']}** + рџ’° **${cost['money']:,}**\nРЈ С‚РµР±СЏ: рџ’Ћ **{player['crystals']}** + рџ’° **${player['money']:,}**",
            ephemeral=True
        ); return

    embed = discord.Embed(title=f"в¬†пёЏ РђРїРіСЂРµР№Рґ вЂ” {stand_name}", color=TIER_COLORS.get(STANDS[stand_name]["tier"], 0xffffff))
    embed.add_field(name=f"{'в­ђ'*cur_tier} РЎРµР№С‡Р°СЃ", value=current_ability, inline=False)
    embed.add_field(name=f"{'в­ђ'*next_tier} РџРѕСЃР»Рµ",  value=next_ability,   inline=False)
    embed.add_field(name="рџ’° РЎС‚РѕРёРјРѕСЃС‚СЊ", value=f"рџ’Ћ **{cost['crystals']}** + рџ’° **${cost['money']:,}**", inline=False)
    embed.set_footer(text="РќР°Р¶РјРё вњ… РґР»СЏ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    msg = await interaction.original_response()
    await msg.add_reaction("вњ…")

    def check(r, u): return u == interaction.user and str(r.emoji) == "вњ…" and r.message.id == msg.id
    try:
        await bot.wait_for("reaction_add", timeout=30.0, check=check)
        player["crystals"] -= cost["crystals"]
        player["money"]    -= cost["money"]
        player["ability_tier"] = next_tier
        save_db(db)
        await msg.edit(content=f"вњ… РЎРїРѕСЃРѕР±РЅРѕСЃС‚СЊ РїСЂРѕРєР°С‡Р°РЅР° РґРѕ Tier {next_tier}! {'в­ђ'*next_tier}\n{next_ability}")
    except asyncio.TimeoutError:
        await msg.edit(content="вќЊ Р’СЂРµРјСЏ РІС‹С€Р»Рѕ.")


@tree.command(name="rokakaka", description="РЎРєСЂРµСЃС‚РёС‚СЊ СЃС‚РµРЅРґ СЃ РґСЂСѓРіРёРј Рё СѓРєСЂР°СЃС‚СЊ СЃРїРѕСЃРѕР±РЅРѕСЃС‚СЊ")
@app_commands.describe(stand_name="РќР°Р·РІР°РЅРёРµ СЃС‚РµРЅРґР° РґР»СЏ СЃРєСЂРµС‰РёРІР°РЅРёСЏ")
async def rokakaka(interaction: discord.Interaction, stand_name: str):
    db = load_db(); player = get_player(db, interaction.user.id)
    if not player["stand"]:
        await interaction.response.send_message("вќЊ РЈ С‚РµР±СЏ РЅРµС‚ СЃС‚РµРЅРґР°!", ephemeral=True); return
    if player.get("fruits", 0) <= 0:
        await interaction.response.send_message("вќЊ РќРµС‚ рџЌ€ Rokakaka! Р”СЂРѕРї: рџџЈ Epic 5% | рџЊџ Legendary 9%", ephemeral=True); return

    target_stand = None
    for name in STANDS:
        if name.lower() == stand_name.lower():
            target_stand = name; break
    if not target_stand:
        matches = [n for n in STANDS if stand_name.lower() in n.lower()]
        if len(matches) == 1: target_stand = matches[0]
        elif len(matches) > 1:
            await interaction.response.send_message(f"вќЊ РќРµСЃРєРѕР»СЊРєРѕ СЃРѕРІРїР°РґРµРЅРёР№: {', '.join(matches[:5])}", ephemeral=True); return
        else:
            await interaction.response.send_message(f"вќЊ РЎС‚РµРЅРґ **{stand_name}** РЅРµ РЅР°Р№РґРµРЅ.", ephemeral=True); return

    if target_stand == player["stand"]:
        await interaction.response.send_message("вќЊ РќРµР»СЊР·СЏ СЃРєСЂРµС‰РёРІР°С‚СЊ СЃ СЃРѕР±РѕР№!", ephemeral=True); return

    target_data    = STANDS[target_stand]
    stolen_ability = target_data["ability"]
    is_evo         = not target_data.get("obtainable", True)
    chance         = 10.0 if is_evo else 40.0
    has_sub        = player.get("sub_ability") is not None

    embed = discord.Embed(title="рџЌ€ Rokakaka вЂ” РЎРєСЂРµС‰РёРІР°РЅРёРµ", color=0x2ecc71)
    embed.add_field(name="вљ”пёЏ РўРІРѕР№ СЃС‚РµРЅРґ", value=f"**{player['stand']}**",    inline=True)
    embed.add_field(name="рџЋЇ Р¦РµР»СЊ",        value=f"**{target_stand}**",        inline=True)
    embed.add_field(name="рџ“Љ РЁР°РЅСЃ",        value=f"**{chance}%**",             inline=True)
    embed.add_field(name="рџ’« РЎРїРѕСЃРѕР±РЅРѕСЃС‚СЊ", value=stolen_ability,               inline=False)
    if has_sub:
        embed.add_field(name="вљ пёЏ Р—Р°РјРµРЅР°", value=f"~~{player['sub_ability']}~~", inline=False)
    embed.set_footer(text="РќР°Р¶РјРё вњ… С‡С‚РѕР±С‹ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ Rokakaka")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    msg = await interaction.original_response()
    await msg.add_reaction("вњ…")

    def check(r, u): return u == interaction.user and str(r.emoji) == "вњ…" and r.message.id == msg.id
    try:
        await bot.wait_for("reaction_add", timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await msg.edit(content="вќЊ Р’СЂРµРјСЏ РІС‹С€Р»Рѕ."); return

    player["fruits"] -= 1
    if random.uniform(0, 100) < chance:
        player["sub_ability"] = stolen_ability
        save_db(db)
        await msg.edit(content=f"вњ… РЎРєСЂРµС‰РёРІР°РЅРёРµ СѓСЃРїРµС€РЅРѕ! **{player['stand']}** РїРѕР»СѓС‡РёР»: {stolen_ability}")
    else:
        save_db(db)
        await msg.edit(content=f"рџ’” РџСЂРѕРІР°Р»! РЁР°РЅСЃ Р±С‹Р» {chance}%. Р¤СЂСѓРєС‚ РїРѕС‚СЂР°С‡РµРЅ. РћСЃС‚Р°Р»РѕСЃСЊ: **{player['fruits']}** рџЌ€")


@tree.command(name="shop", description="РњР°РіР°Р·РёРЅ вЂ” РєСѓРїРёС‚СЊ СЃС‚СЂРµР»С‹, РєСЂРёСЃС‚Р°Р»Р»С‹, РєРµР№СЃС‹")
@app_commands.describe(item="Р§С‚Рѕ РєСѓРїРёС‚СЊ: arrow, crystal, common, rare")
@app_commands.choices(item=[
    app_commands.Choice(name="рџЏ№ Regular Arrow вЂ” $500",  value="arrow"),
    app_commands.Choice(name="рџ’Ћ Crystal вЂ” $800",        value="crystal"),
    app_commands.Choice(name="рџ“¦ Common Crate вЂ” $1000",  value="common"),
    app_commands.Choice(name="рџџ¦ Rare Crate вЂ” $2500",   value="rare"),
])
async def shop(interaction: discord.Interaction, item: str = None):
    db = load_db(); player = get_player(db, interaction.user.id)

    if not item:
        embed = discord.Embed(title="рџЏЄ JoJo Shop", color=0xe67e22)
        for key, d in SHOP_ITEMS.items():
            embed.add_field(name=f"{d['icon']} {d['name']}", value=f"рџ’° **${d['price']:,}**\n`/shop {key}`", inline=True)
        embed.add_field(name="вљ пёЏ РќРµ РїСЂРѕРґР°С‘С‚СЃСЏ", value="вњЁ Requiem Arrow\nрџЌ€ Rokakaka\nрџџЈ Epic / рџЊџ Legendary Crate", inline=False)
        embed.set_footer(text=f"РўРІРѕР№ Р±Р°Р»Р°РЅСЃ: ${player['money']:,}")
        await interaction.response.send_message(embed=embed, ephemeral=True); return

    d = SHOP_ITEMS[item]
    if player["money"] < d["price"]:
        await interaction.response.send_message(f"вќЊ РќСѓР¶РЅРѕ рџ’° **${d['price']:,}**, Сѓ С‚РµР±СЏ **${player['money']:,}**", ephemeral=True); return

    player["money"] -= d["price"]
    itype = d["type"]
    if itype == "regular_arrow":   player["arrows"]["regular"] += 1
    elif itype == "crystal":       player["crystals"] += 1
    elif itype == "common_crate":  player["crates"]["common"] += 1
    elif itype == "rare_crate":    player["crates"]["rare"] += 1
    save_db(db)

    await interaction.response.send_message(
        f"вњ… РљСѓРїР»РµРЅРѕ: {d['icon']} **{d['name']}**!\nрџ’° РџРѕС‚СЂР°С‡РµРЅРѕ: **${d['price']:,}** | Р‘Р°Р»Р°РЅСЃ: **${player['money']:,}**",
        ephemeral=True
    )


@tree.command(name="crate", description="РћС‚РєСЂС‹С‚СЊ РєРµР№СЃ РёР»Рё РїРѕСЃРјРѕС‚СЂРµС‚СЊ СЃРѕРґРµСЂР¶РёРјРѕРµ")
@app_commands.describe(crate_type="РўРёРї РєРµР№СЃР°: common, rare, epic, legendary")
@app_commands.choices(crate_type=[
    app_commands.Choice(name="рџ“¦ Common",    value="common"),
    app_commands.Choice(name="рџџ¦ Rare",      value="rare"),
    app_commands.Choice(name="рџџЈ Epic",      value="epic"),
    app_commands.Choice(name="рџЊџ Legendary", value="legendary"),
])
async def crate(interaction: discord.Interaction, crate_type: str = None):
    db = load_db(); player = get_player(db, interaction.user.id)

    if not crate_type:
        embed = discord.Embed(title="рџ“¦ РўРІРѕРё РєРµР№СЃС‹", color=0x2c2f33)
        ct_text = "\n".join([f"{c['icon']} **{player['crates'].get(k,0)}** {c['name']}" for k,c in CRATE_CONFIG.items()])
        embed.add_field(name="РљРµР№СЃС‹", value=ct_text, inline=False)
        ch_text = ""
        for k, c in CRATE_CONFIG.items():
            ch_text += f"{c['icon']} **{c['name']}**: рџ’°${c['money_min']}-${c['money_max']} | рџЏ№{c['regular_arrow_chance']}% | вњЁ{c['requiem_arrow_chance']}%"
            if c.get("stone_mask_chance",0) > 0: ch_text += f" | рџЋ­{c['stone_mask_chance']}%"
            if c.get("rokakaka_chance",0) > 0:   ch_text += f" | рџЌ€{c['rokakaka_chance']}%"
            ch_text += "\n"
        embed.add_field(name="рџ“Љ РЁР°РЅСЃС‹", value=ch_text, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True); return

    if player["crates"].get(crate_type, 0) <= 0:
        await interaction.response.send_message(f"вќЊ РќРµС‚ **{CRATE_CONFIG[crate_type]['name']}**!", ephemeral=True); return

    player["crates"][crate_type] -= 1
    player["crates_opened"] = player.get("crates_opened",0) + 1
    if crate_type == "epic": player["epic_opened"] = player.get("epic_opened",0) + 1
    rewards = open_crate(crate_type)
    rewards_text = ""
    for r in rewards:
        if r["type"] == "money":
            player["money"] += r["amount"]; rewards_text += f"рџ’° **${r['amount']:,}**\n"
        elif r["type"] == "regular_arrow":
            player["arrows"]["regular"] += r["amount"]; rewards_text += f"рџЏ№ **Regular Arrow** x{r['amount']}\n"
        elif r["type"] == "requiem_arrow":
            player["arrows"]["requiem"] += r["amount"]; rewards_text += f"вњЁ **Requiem Arrow** x{r['amount']} вљ пёЏ Р Р•Р”РљР�Р™!\n"
        elif r["type"] == "stone_mask":
            player["stone_masks"] = player.get("stone_masks",0) + r["amount"]; rewards_text += f"рџЋ­ **Stone Mask** x{r['amount']} рџ’Ђ РЈР›Р¬РўР Рђ Р Р•Р”РљР�Р™!\n"
        elif r["type"] == "rokakaka":
            player["fruits"] = player.get("fruits",0) + r["amount"]; rewards_text += f"рџЌ€ **Rokakaka** x{r['amount']} Р Р•Р”РљР�Р™!\n"
    save_db(db)

    cfg = CRATE_CONFIG[crate_type]
    embed = discord.Embed(title=f"{cfg['icon']} {cfg['name']}!", color=cfg["color"])
    embed.add_field(name="рџЋЃ РќР°РіСЂР°РґС‹", value=rewards_text, inline=False)
    embed.add_field(name="рџ’° Р‘Р°Р»Р°РЅСЃ",  value=f"**${player['money']:,}**", inline=True)
    embed.set_footer(text=f"РћСЃС‚Р°Р»РѕСЃСЊ {player['crates'][crate_type]} {cfg['name']}")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="money", description="РџРѕСЃРјРѕС‚СЂРµС‚СЊ Р±Р°Р»Р°РЅСЃ")
async def money(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    embed = discord.Embed(title="рџ’° Balance", color=0xf1c40f)
    embed.add_field(name="Money", value=f"**${player['money']:,}**", inline=False)
    embed.set_footer(text=interaction.user.display_name)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="quest", description="РџРѕСЃРјРѕС‚СЂРµС‚СЊ РєРІРµСЃС‚ РёР»Рё Р·Р°Р±СЂР°С‚СЊ РЅР°РіСЂР°РґСѓ")
@app_commands.describe(action="claim вЂ” Р·Р°Р±СЂР°С‚СЊ РЅР°РіСЂР°РґСѓ")
@app_commands.choices(action=[
    app_commands.Choice(name="show  вЂ” РїРѕСЃРјРѕС‚СЂРµС‚СЊ РїСЂРѕРіСЂРµСЃСЃ", value="show"),
    app_commands.Choice(name="claim вЂ” Р·Р°Р±СЂР°С‚СЊ РЅР°РіСЂР°РґСѓ",     value="claim"),
])
async def quest_cmd(interaction: discord.Interaction, action: str = "show"):
    db = load_db(); player = get_player(db, interaction.user.id)
    if not player.get("quest"):
        assign_quest(player); save_db(db)

    quest_data = next((q for q in QUESTS if q["id"] == player["quest"]), None)
    if not quest_data:
        assign_quest(player); save_db(db)
        quest_data = next(q for q in QUESTS if q["id"] == player["quest"])

    progress = get_quest_progress(player, quest_data)
    goal     = quest_data["goal"]
    done     = progress >= goal

    if action == "claim":
        if not done:
            await interaction.response.send_message(f"вќЊ РљРІРµСЃС‚ РЅРµ РІС‹РїРѕР»РЅРµРЅ! **{min(progress,goal)}/{goal}**", ephemeral=True); return
        reward = quest_data["reward"]
        if "money"    in reward: player["money"]    += reward["money"]
        if "crystals" in reward: player["crystals"] += reward["crystals"]
        if "crates"   in reward:
            for ctype, amt in reward["crates"].items(): player["crates"][ctype] += amt
        assign_quest(player)
        new_quest = next(q for q in QUESTS if q["id"] == player["quest"])
        save_db(db)
        embed = discord.Embed(title=f"рџЋ‰ РљРІРµСЃС‚ РІС‹РїРѕР»РЅРµРЅ: {quest_data['name']}!", color=0xf1c40f)
        embed.add_field(name="рџЋЃ РќР°РіСЂР°РґР°",     value=quest_data["reward_text"],             inline=False)
        embed.add_field(name="рџ“‹ РќРѕРІС‹Р№ РєРІРµСЃС‚", value=f"**{new_quest['name']}** вЂ” {new_quest['desc']}", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True); return

    bar_filled = int((min(progress,goal)/goal)*10)
    bar    = "в–€"*bar_filled + "в–‘"*(10-bar_filled)
    status = "вњ… Р’Р«РџРћР›РќР•Рќ вЂ” `/quest claim`!" if done else f"[{bar}] {min(progress,goal)}/{goal}"
    embed  = discord.Embed(title="рџ“‹ РўРµРєСѓС‰РёР№ РєРІРµСЃС‚", color=0xf1c40f if done else 0x3498db)
    embed.add_field(name=f"рџЋЇ {quest_data['name']}", value=quest_data["desc"],       inline=False)
    embed.add_field(name="рџ“Љ РџСЂРѕРіСЂРµСЃСЃ",              value=status,                    inline=False)
    embed.add_field(name="рџЏ† РќР°РіСЂР°РґР°",               value=quest_data["reward_text"], inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="help", description="РЎРїРёСЃРѕРє РІСЃРµС… РєРѕРјР°РЅРґ")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="рџ“– JoJo Bot вЂ” РљРѕРјР°РЅРґС‹", color=0x9b59b6)
    embed.add_field(name="/job",              value="Р Р°Р±РѕС‚Р° (РєРґ:30РјРёРЅ) рџџўрџџЎрџ”ґ", inline=False)
    embed.add_field(name="/search",           value=f"РќР°Р№С‚Рё РєРµР№СЃ (РЅСѓР¶РЅРѕ {JOBS_REQUIRED} СЂР°Р±РѕС‚С‹)", inline=False)
    embed.add_field(name="/crate [С‚РёРї]",      value="РћС‚РєСЂС‹С‚СЊ РєРµР№СЃ", inline=False)
    embed.add_field(name="/arrow [С‚РёРї]",      value="Р�СЃРїРѕР»СЊР·РѕРІР°С‚СЊ СЃС‚СЂРµР»Сѓ", inline=False)
    embed.add_field(name="/evolve [С‚РёРї]",     value="Р­РІРѕР»СЋС†РёСЏ СЃС‚РµРЅРґР° (requiem/vampire)", inline=False)
    embed.add_field(name="/upgrade",          value="РџСЂРѕРєР°С‡Р°С‚СЊ СЃРїРѕСЃРѕР±РЅРѕСЃС‚СЊ (Tier 1в†’2в†’3)", inline=False)
    embed.add_field(name="/rokakaka [СЃС‚РµРЅРґ]", value="РЎРєСЂРµСЃС‚РёС‚СЊ СЃС‚РµРЅРґ (РЅСѓР¶РЅР° рџЌ€ Rokakaka)", inline=False)
    embed.add_field(name="/storage [action]", value="РҐСЂР°РЅРёР»РёС‰Рµ СЃС‚РµРЅРґРѕРІ (store/swap/drop)", inline=False)
    embed.add_field(name="/shop [РїСЂРµРґРјРµС‚]",   value="РњР°РіР°Р·РёРЅ", inline=False)
    embed.add_field(name="/quest [action]",   value="РљРІРµСЃС‚С‹ (show/claim)", inline=False)
    embed.add_field(name="/stand [@user]",    value="РџРѕСЃРјРѕС‚СЂРµС‚СЊ СЃС‚РµРЅРґ", inline=False)
    embed.add_field(name="/inv [@user]",      value="Р�РЅРІРµРЅС‚Р°СЂСЊ", inline=False)
    embed.add_field(name="/money",            value="Р‘Р°Р»Р°РЅСЃ", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# в”Ђв”Ђв”Ђ RUN в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
bot.run(TOKEN)
