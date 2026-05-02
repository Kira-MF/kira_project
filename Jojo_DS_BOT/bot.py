# -*- coding: utf-8 -*-
import discord
from discord import app_commands
from discord.ext import commands
import json, os, random, asyncio
from datetime import datetime, timedelta
from stands import (STANDS, TIER_COLORS, TIER_EMOJI, TIER_WEIGHTS,
                    EVOLUTION_CHAINS, ABILITY_UPGRADES,
                    get_stand_by_tier, can_evolve, get_evolution)

# РІвЂќР‚РІвЂќР‚РІвЂќР‚ CONFIG РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚
TOKEN    = "ТВОЙ_ТОКЕН_СЮДА"
DB_FILE  = "players.json"
GUILD_ID = 1003592872098021396  

STAT_BAR = {
    "A": "[A]", "B": "[B]", "C": "[C]",
    "D": "[D]", "E": "[E]", "Z": "[Z]"
}
STAT_UP = {"E": "D", "D": "C", "C": "B", "B": "A", "A": "Z"}

ITEM_ICONS = {
    "money": "СЂСџвЂ™В°", "regular_arrow": "СЂСџРЏв„–", "requiem_arrow": "РІСљРЃ",
    "overheaven_arrow": "РІС™РЋ", "crystal": "СЂСџвЂ™Р‹", "rokakaka": "СЂСџРЊв‚¬",
    "common_crate": "СЂСџвЂњВ¦", "rare_crate": "СЂСџСџВ¦", "epic_crate": "СЂСџСџР€",
    "legendary_crate": "СЂСџРЉСџ", "stone_mask": "СЂСџР‹В­",
}

CRATE_CONFIG = {
    "common":    {"name": "Common Crate",    "icon": "СЂСџвЂњВ¦", "color": 0x95a5a6, "money_min": 100,  "money_max": 300,  "regular_arrow_chance": 20.0, "requiem_arrow_chance": 0.1,  "stone_mask_chance": 0.0, "rokakaka_chance": 0.0},
    "rare":      {"name": "Rare Crate",      "icon": "СЂСџСџВ¦", "color": 0x3498db, "money_min": 300,  "money_max": 700,  "regular_arrow_chance": 35.0, "requiem_arrow_chance": 0.3,  "stone_mask_chance": 0.0, "rokakaka_chance": 0.0},
    "epic":      {"name": "Epic Crate",      "icon": "СЂСџСџР€", "color": 0x9b59b6, "money_min": 700,  "money_max": 1500, "regular_arrow_chance": 49.0, "requiem_arrow_chance": 0.5,  "stone_mask_chance": 0.0, "rokakaka_chance": 5.0},
    "legendary": {"name": "Legendary Crate", "icon": "СЂСџРЉСџ", "color": 0xf1c40f, "money_min": 1500, "money_max": 3000, "regular_arrow_chance": 70.0, "requiem_arrow_chance": 1.5,  "stone_mask_chance": 1.5, "rokakaka_chance": 9.0},
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
    ("Р С—РЎР‚Р С•Р Т‘Р В°Р Р†Р В°Р В» Р ВµР Т‘РЎС“ Р Р†Р ВµРЎРѓРЎРЉ Р Т‘Р ВµР Р…РЎРЉ",                   100,  250, 90, "easy"),
    ("Р Т‘Р С•РЎРѓРЎвЂљР В°Р Р†Р В»РЎРЏР В» Р С—Р С•РЎРѓРЎвЂ№Р В»Р С”Р С‘",                         120,  280, 85, "easy"),
    ("РЎвЂЎР С‘РЎРѓРЎвЂљР С‘Р В» РЎС“Р В»Р С‘РЎвЂ РЎвЂ№ Morioh",                        80,  200, 95, "easy"),
    ("Р С—Р С•Р СР С•Р С–Р В°Р В» Р Р† Р СР В°РЎРѓРЎвЂљР ВµРЎР‚РЎРѓР С”Р С•Р в„–",                      100,  300, 85, "easy"),
    ("Р С•РЎвЂ¦РЎР‚Р В°Р Р…РЎРЏР В» РЎРѓР С”Р В»Р В°Р Т‘ Р Р…Р С•РЎвЂЎРЎРЉРЎР‹",                       250,  500, 70, "medium"),
    ("РЎР‚Р В°Р В±Р С•РЎвЂљР В°Р В» Р Р…Р В° РЎРѓРЎвЂљРЎР‚Р С•Р в„–Р С”Р Вµ",                        300,  550, 65, "medium"),
    ("Р С—Р С•Р СР С•Р С–Р В°Р В» Р Р† РЎР‚Р ВµРЎРѓРЎвЂљР С•РЎР‚Р В°Р Р…Р Вµ Trattoria Trussardi",   350,  600, 70, "medium"),
    ("РЎР‚Р В°Р В±Р С•РЎвЂљР В°Р В» Р Р†РЎвЂ№РЎв‚¬Р С‘Р В±Р В°Р В»Р С•Р в„– Р Р† Р В±Р В°РЎР‚Р Вµ",                  280,  520, 65, "medium"),
    ("Р Р…Р В°РЎв‚¬РЎвЂР В» РЎР‚Р В°Р В±Р С•РЎвЂљРЎС“ Р Р† Passione",                   500, 1000, 50, "hard"),
    ("Р Р†РЎвЂ№Р С—Р С•Р В»Р Р…РЎРЏР В» Р В·Р В°Р Т‘Р В°Р Р…Р С‘Р Вµ Р С•РЎвЂљ Speedwagon Foundation", 600, 1200, 45, "hard"),
    ("Р С•РЎвЂ¦Р С•РЎвЂљР С‘Р В»РЎРѓРЎРЏ Р Р…Р В° Р С—Р С•Р В»РЎРЉР В·Р С•Р Р†Р В°РЎвЂљР ВµР В»РЎРЏ РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В°",           700, 1500, 40, "hard"),
    ("РЎР‚Р В°Р В±Р С•РЎвЂљР В°Р В» Р Р…Р В° DIO",                            800, 1800, 35, "hard"),
]
JOB_FAIL = [
    "Р СћР ВµР В±РЎРЏ Р С—Р С•Р в„–Р СР В°Р В»Р С‘ РІР‚вЂќ Р С—РЎР‚Р С‘РЎв‚¬Р В»Р С•РЎРѓРЎРЉ РЎРѓР В±Р ВµР В¶Р В°РЎвЂљРЎРЉ!", "Р вЂР С•РЎРѓРЎРѓ РЎС“Р Р†Р С•Р В»Р С‘Р В» РЎвЂљР ВµР В±РЎРЏ Р В·Р В° Р В»Р ВµР Р…РЎРЉ...",
    "Р СћРЎвЂ№ Р С—РЎР‚Р С•Р Р†Р В°Р В»Р С‘Р В» Р В·Р В°Р Т‘Р В°Р Р…Р С‘Р Вµ!", "Р СњР Вµ Р С—Р С•Р Р†Р ВµР В·Р В»Р С• РІР‚вЂќ РЎР‚Р В°Р В±Р С•РЎвЂљРЎС“ Р С—Р ВµРЎР‚Р ВµРЎвЂ¦Р Р†Р В°РЎвЂљР С‘Р В» Р С”РЎвЂљР С•-РЎвЂљР С• Р Т‘РЎР‚РЎС“Р С–Р С•Р в„–.",
    "Р вЂ™РЎР‚Р В°Р В¶Р ВµРЎРѓР С”Р С‘Р в„– РЎРѓРЎвЂљР ВµР Р…Р Т‘ Р С—Р С•Р СР ВµРЎв‚¬Р В°Р В» РЎвЂљР ВµР В±Р Вµ!", "Р С™Р В»Р С‘Р ВµР Р…РЎвЂљ Р С•РЎвЂљР С”Р В°Р В·Р В°Р В»РЎРѓРЎРЏ Р С—Р В»Р В°РЎвЂљР С‘РЎвЂљРЎРЉ!",
    "Р СџР С•Р В»Р С‘РЎвЂ Р С‘РЎРЏ РЎР‚Р В°Р В·Р С•Р С–Р Р…Р В°Р В»Р В° Р Р†РЎРѓР ВµРЎвЂ¦ РІР‚вЂќ РЎвЂљРЎвЂ№ Р Р…Р С‘РЎвЂЎР ВµР С–Р С• Р Р…Р Вµ Р В·Р В°РЎР‚Р В°Р В±Р С•РЎвЂљР В°Р В».",
]
JOBS_REQUIRED = 3

SHOP_ITEMS = {
    "arrow":   {"name": "Regular Arrow", "icon": "СЂСџРЏв„–", "price": 500,  "type": "regular_arrow"},
    "crystal": {"name": "Crystal",       "icon": "СЂСџвЂ™Р‹", "price": 800,  "type": "crystal"},
    "common":  {"name": "Common Crate",  "icon": "СЂСџвЂњВ¦", "price": 1000, "type": "common_crate"},
    "rare":    {"name": "Rare Crate",    "icon": "СЂСџСџВ¦", "price": 2500, "type": "rare_crate"},
}

QUESTS = [
    {"id": "worker",     "name": "Р В Р В°Р В±Р С•РЎвЂљРЎРЏР С–Р В°",    "desc": "Р вЂ™РЎвЂ№Р С—Р С•Р В»Р Р…Р С‘ 5 РЎР‚Р В°Р В±Р С•РЎвЂљ",          "type": "jobs_done_total", "goal": 5,    "reward": {"crystals": 3},           "reward_text": "СЂСџвЂ™Р‹ 3 Р С”РЎР‚Р С‘РЎРѓРЎвЂљР В°Р В»Р В»Р В°"},
    {"id": "searcher",   "name": "Р пїЅРЎРѓР С”Р В°РЎвЂљР ВµР В»РЎРЉ",    "desc": "Р пїЅРЎРѓР С—Р С•Р В»РЎРЉР В·РЎС“Р в„– /search 3 РЎР‚Р В°Р В·Р В°", "type": "searches_done",  "goal": 3,    "reward": {"money": 500},            "reward_text": "СЂСџвЂ™В° $500"},
    {"id": "collector",  "name": "Р С™Р С•Р В»Р В»Р ВµР С”РЎвЂ Р С‘Р С•Р Р…Р ВµРЎР‚","desc": "Р вЂ™РЎвЂ№Р С—Р С•Р В»Р Р…Р С‘ 10 РЎР‚Р В°Р В±Р С•РЎвЂљ",         "type": "jobs_done_total", "goal": 10,   "reward": {"crystals": 8},           "reward_text": "СЂСџвЂ™Р‹ 8 Р С”РЎР‚Р С‘РЎРѓРЎвЂљР В°Р В»Р В»Р С•Р Р†"},
    {"id": "lucky",      "name": "Р Р€Р Т‘Р В°РЎвЂЎР В°",       "desc": "Р С›РЎвЂљР С”РЎР‚Р С•Р в„– 3 Р В»РЎР‹Р В±РЎвЂ№РЎвЂ¦ Р С”Р ВµР в„–РЎРѓР В°",     "type": "crates_opened",  "goal": 3,    "reward": {"money": 1500},           "reward_text": "СЂСџвЂ™В° $1500"},
    {"id": "rich",       "name": "Р вЂР С•Р С–Р В°РЎвЂЎ",       "desc": "Р СњР В°Р С”Р С•Р С—Р С‘ $3000",             "type": "money_reach",    "goal": 3000, "reward": {"crates": {"common": 2}}, "reward_text": "СЂСџвЂњВ¦ 2 Common Crate"},
    {"id": "shooter",    "name": "Р РЋРЎвЂљРЎР‚Р ВµР В»Р С•Р С”",     "desc": "Р пїЅРЎРѓР С—Р С•Р В»РЎРЉР В·РЎС“Р в„– РЎРѓРЎвЂљРЎР‚Р ВµР В»РЎС“ 3 РЎР‚Р В°Р В·Р В°", "type": "arrows_used",    "goal": 3,    "reward": {"crystals": 5, "money": 1000}, "reward_text": "СЂСџвЂ™Р‹ 5 + СЂСџвЂ™В° $1000"},
    {"id": "epic_hunter","name": "Р С›РЎвЂ¦Р С•РЎвЂљР Р…Р С‘Р С”",     "desc": "Р С›РЎвЂљР С”РЎР‚Р С•Р в„– 1 Epic Р С”Р ВµР в„–РЎРѓ",       "type": "epic_opened",    "goal": 1,    "reward": {"crystals": 15},          "reward_text": "СЂСџвЂ™Р‹ 15 Р С”РЎР‚Р С‘РЎРѓРЎвЂљР В°Р В»Р В»Р С•Р Р†"},
]

# РІвЂќР‚РІвЂќР‚РІвЂќР‚ DATABASE РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚
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

# РІвЂќР‚РІвЂќР‚РІвЂќР‚ STAND OBJECT РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚
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

# РІвЂќР‚РІвЂќР‚РІвЂќР‚ HELPERS РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚
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
    embed.add_field(name=f"Ability {'РІВ­С’'*atier}", value=ability_text, inline=False)

    if stand.get("ability2"):
        embed.add_field(name="Ability 2", value=stand["ability2"], inline=False)
    if player and player.get("is_vampire"):
        embed.add_field(name="СЂСџВ§вЂє Vampire", value="Vampiric Freeze РІР‚вЂќ Р В·Р В°Р СР С•РЎР‚Р В°Р В¶Р С‘Р Р†Р В°Р ВµРЎвЂљ Р Р†РЎР‚Р В°Р С–Р В° Р С—РЎР‚Р С‘ Р С”Р В°РЎРѓР В°Р Р…Р С‘Р С‘", inline=False)
    if player and player.get("sub_ability"):
        embed.add_field(name="СЂСџРЊв‚¬ Sub-Ability", value=player["sub_ability"], inline=False)
    if stand.get("evolves_to"):
        embed.add_field(name="РІВ¬вЂ РїС‘РЏ Evolves to", value=f"**{stand['evolves_to']}**", inline=False)
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

# РІвЂќР‚РІвЂќР‚РІвЂќР‚ BOT SETUP РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚
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

# РІвЂќР‚РІвЂќР‚РІвЂќР‚ SLASH COMMANDS РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚

@tree.command(name="job", description="Р В Р В°Р В±Р С•РЎвЂљР В° РІР‚вЂќ Р В·Р В°РЎР‚Р В°Р В±Р В°РЎвЂљРЎвЂ№Р Р†Р В°Р в„– Р Т‘Р ВµР Р…РЎРЉР С–Р С‘ (Р С”Р Т‘: 30 Р СР С‘Р Р…)")
async def job(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    now = datetime.utcnow()
    if player["last_job"]:
        last = datetime.fromisoformat(player["last_job"])
        diff = now - last
        if diff < timedelta(minutes=30):
            rem = timedelta(minutes=30) - diff
            await interaction.response.send_message(
                f"РІРЏС– Р СџР С•Р Т‘Р С•Р В¶Р Т‘Р С‘ **{int(rem.total_seconds()//60)}Р С {int(rem.total_seconds()%60)}РЎРѓ** Р Т‘Р С• РЎРѓР В»Р ВµР Т‘РЎС“РЎР‹РЎвЂ°Р ВµР в„– РЎР‚Р В°Р В±Р С•РЎвЂљРЎвЂ№.",
                ephemeral=True
            ); return

    job_name, mn, mx, sc, diff = random.choice(JOBS)
    de = {"easy":"СЂСџСџСћ","medium":"СЂСџСџРЋ","hard":"СЂСџвЂќТ‘"}
    dt = {"easy":"Р вЂєРЎвЂР С–Р С”Р В°РЎРЏ","medium":"Р РЋРЎР‚Р ВµР Т‘Р Р…РЎРЏРЎРЏ","hard":"Р РЋР В»Р С•Р В¶Р Р…Р В°РЎРЏ"}
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
        embed = discord.Embed(title="РІСљвЂ¦ Р В Р В°Р В±Р С•РЎвЂљР В° Р Р†РЎвЂ№Р С—Р С•Р В»Р Р…Р ВµР Р…Р В°!", color=0x2ecc71)
        embed.add_field(name=f"{de[diff]} {dt[diff]}", value=f"Р СћРЎвЂ№ **{job_name}** Р С‘ Р В·Р В°РЎР‚Р В°Р В±Р С•РЎвЂљР В°Р В» **${earned}**!", inline=False)
        embed.add_field(name="СЂСџвЂ™В° Р вЂР В°Р В»Р В°Р Р…РЎРѓ", value=f"**${player['money']:,}**", inline=True)
        embed.add_field(name="СЂСџвЂќРЃ Jobs",   value=f"**{player['jobs_done']}/{JOBS_REQUIRED}**", inline=True)
        if bonus_crate:
            cfg = CRATE_CONFIG[bonus_crate]
            embed.add_field(name="СЂСџР‹Рѓ Р вЂР С•Р Р…РЎС“РЎРѓ!", value=f"{cfg['icon']} **{cfg['name']}** Р Р…Р В°РЎв‚¬РЎвЂР В» Р Р†Р С• Р Р†РЎР‚Р ВµР СРЎРЏ РЎР‚Р В°Р В±Р С•РЎвЂљРЎвЂ№!", inline=False)
        if player["jobs_done"] >= JOBS_REQUIRED:
            embed.add_field(name="СЂСџвЂќРЊ Search Р С–Р С•РЎвЂљР С•Р Р†!", value="Р пїЅРЎРѓР С—Р С•Р В»РЎРЉР В·РЎС“Р в„– `/search`!", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        save_db(db)
        embed = discord.Embed(title="РІСњРЉ Р В Р В°Р В±Р С•РЎвЂљР В° Р С—РЎР‚Р С•Р Р†Р В°Р В»Р ВµР Р…Р В°!", color=0xe74c3c)
        embed.add_field(name=f"{de[diff]} {dt[diff]}", value=f"**{job_name}**\n{random.choice(JOB_FAIL)}", inline=False)
        embed.add_field(name="СЂСџвЂќРЃ Jobs", value=f"**{player['jobs_done']}/{JOBS_REQUIRED}**", inline=True)
        embed.set_footer(text="Р СџРЎР‚Р С•Р Р†Р В°Р В» Р Р…Р Вµ РЎРѓРЎвЂЎР С‘РЎвЂљР В°Р ВµРЎвЂљРЎРѓРЎРЏ РІР‚вЂќ Р С—Р С•Р С—РЎР‚Р С•Р В±РЎС“Р в„– РЎвЂЎР ВµРЎР‚Р ВµР В· 30 Р СР С‘Р Р…")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="search", description="Р СњР В°Р в„–РЎвЂљР С‘ Р С”Р ВµР в„–РЎРѓ (Р Р…РЎС“Р В¶Р Р…Р С• 3 Р Р†РЎвЂ№Р С—Р С•Р В»Р Р…Р ВµР Р…Р Р…РЎвЂ№РЎвЂ¦ РЎР‚Р В°Р В±Р С•РЎвЂљРЎвЂ№)")
async def search(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    if player["jobs_done"] < JOBS_REQUIRED:
        await interaction.response.send_message(
            f"РІСњРЉ Р СњРЎС“Р В¶Р Р…Р С• Р ВµРЎвЂ°РЎвЂ **{JOBS_REQUIRED-player['jobs_done']}** РЎР‚Р В°Р В±Р С•РЎвЂљ!\nСЂСџвЂќРЃ **{player['jobs_done']}/{JOBS_REQUIRED}**",
            ephemeral=True
        ); return

    player["jobs_done"] = 0
    player["searches_done"] = player.get("searches_done",0) + 1
    crate_type = roll_crate_type()
    if not crate_type:
        save_db(db)
        await interaction.response.send_message(
            embed=discord.Embed(title="СЂСџвЂќРЊ Р СџР С•Р С‘РЎРѓР С”", description="Р СњР С‘РЎвЂЎР ВµР С–Р С• Р Р…Р Вµ Р Р…Р В°РЎв‚¬РЎвЂР В»...", color=0x95a5a6),
            ephemeral=True
        ); return

    player["crates"][crate_type] += 1
    save_db(db)
    cfg = CRATE_CONFIG[crate_type]
    embed = discord.Embed(title="СЂСџвЂќРЊ Р СњР В°РЎвЂ¦Р С•Р Т‘Р С”Р В°!", description=f"Р СћРЎвЂ№ Р Р…Р В°РЎв‚¬РЎвЂР В» {cfg['icon']} **{cfg['name']}**!", color=cfg["color"])
    embed.set_footer(text="Р пїЅРЎРѓР С—Р С•Р В»РЎРЉР В·РЎС“Р в„– /crate open")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="arrow", description="Р пїЅРЎРѓР С—Р С•Р В»РЎРЉР В·Р С•Р Р†Р В°РЎвЂљРЎРЉ РЎРѓРЎвЂљРЎР‚Р ВµР В»РЎС“ Р Т‘Р В»РЎРЏ Р С—Р С•Р В»РЎС“РЎвЂЎР ВµР Р…Р С‘РЎРЏ РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В°")
@app_commands.describe(arrow_type="Р СћР С‘Р С— РЎРѓРЎвЂљРЎР‚Р ВµР В»РЎвЂ№: regular, requiem, overheaven")
@app_commands.choices(arrow_type=[
    app_commands.Choice(name="regular",    value="regular"),
    app_commands.Choice(name="requiem",    value="requiem"),
    app_commands.Choice(name="overheaven", value="overheaven"),
])
async def arrow(interaction: discord.Interaction, arrow_type: str = "regular"):
    db = load_db(); player = get_player(db, interaction.user.id)
    if player["arrows"][arrow_type] <= 0:
        await interaction.response.send_message(
            f"РІСњРЉ Р Р€ РЎвЂљР ВµР В±РЎРЏ Р Р…Р ВµРЎвЂљ **{arrow_type}** РЎРѓРЎвЂљРЎР‚Р ВµР В»РЎвЂ№! Р С™РЎС“Р С—Р С‘ Р Р† `/shop` Р С‘Р В»Р С‘ Р Р…Р В°Р в„–Р Т‘Р С‘ РЎвЂЎР ВµРЎР‚Р ВµР В· `/search`.",
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
        new_embed.set_author(name=f"Р СњР С•Р Р†РЎвЂ№Р в„– РЎРѓРЎвЂљР ВµР Р…Р Т‘!")

        if len(storage) < 2:
            new_embed.set_footer(text=f"Р Р€ РЎвЂљР ВµР В±РЎРЏ РЎС“Р В¶Р Вµ Р ВµРЎРѓРЎвЂљРЎРЉ РЎРѓРЎвЂљР ВµР Р…Р Т‘. Р СњР В°Р В¶Р СР С‘ РІСљвЂ¦ РЎРѓР СР ВµР Р…Р С‘РЎвЂљРЎРЉ | СЂСџвЂњВ¦ РЎРѓР С•РЎвЂ¦РЎР‚Р В°Р Р…Р С‘РЎвЂљРЎРЉ РЎРѓРЎвЂљР В°РЎР‚РЎвЂ№Р в„– Р Р† storage")
            await interaction.response.send_message(embed=new_embed, ephemeral=True)
            msg = await interaction.original_response()
            await msg.add_reaction("РІСљвЂ¦")
            await msg.add_reaction("СЂСџвЂњВ¦")

            def check(r, u): return u == interaction.user and str(r.emoji) in ["РІСљвЂ¦","СЂСџвЂњВ¦"] and r.message.id == msg.id
            try:
                reaction, _ = await bot.wait_for("reaction_add", timeout=30.0, check=check)
                if str(reaction.emoji) == "СЂСџвЂњВ¦":
                    storage.append(old_stand_obj)
                    player["storage"] = storage
                player["stand"] = stand_name
                player["ability_tier"] = 1
                player["is_vampire"] = False
                player["stand_stats"] = None
                player["sub_ability"] = None
                save_db(db)
                action = "РЎРѓР С•РЎвЂ¦РЎР‚Р В°Р Р…РЎвЂР Р… Р Р† storage, РЎРѓРЎвЂљР ВµР Р…Р Т‘ РЎРѓР СР ВµР Р…РЎвЂР Р…" if str(reaction.emoji) == "СЂСџвЂњВ¦" else "РЎРѓР СР ВµР Р…РЎвЂР Р…"
                await msg.edit(content=f"РІСљвЂ¦ Р РЋРЎвЂљР ВµР Р…Р Т‘ {action}: **{stand_name}**!")
            except asyncio.TimeoutError:
                save_db(db)
                await msg.edit(content="РІСњРЉ Р вЂ™РЎР‚Р ВµР СРЎРЏ Р Р†РЎвЂ№РЎв‚¬Р В»Р С• РІР‚вЂќ РЎРѓРЎвЂљР ВµР Р…Р Т‘ Р Р…Р Вµ РЎРѓР СР ВµР Р…РЎвЂР Р….")
        else:
            new_embed.set_footer(text="Р Р€ РЎвЂљР ВµР В±РЎРЏ РЎС“Р В¶Р Вµ Р ВµРЎРѓРЎвЂљРЎРЉ РЎРѓРЎвЂљР ВµР Р…Р Т‘. Р СњР В°Р В¶Р СР С‘ РІСљвЂ¦ РЎвЂЎРЎвЂљР С•Р В±РЎвЂ№ РЎРѓР СР ВµР Р…Р С‘РЎвЂљРЎРЉ (storage Р С—Р С•Р В»Р С•Р Р…)")
            await interaction.response.send_message(embed=new_embed, ephemeral=True)
            msg = await interaction.original_response()
            await msg.add_reaction("РІСљвЂ¦")
            def check(r, u): return u == interaction.user and str(r.emoji) == "РІСљвЂ¦" and r.message.id == msg.id
            try:
                await bot.wait_for("reaction_add", timeout=30.0, check=check)
                player["stand"] = stand_name
                player["ability_tier"] = 1
                player["is_vampire"] = False
                player["stand_stats"] = None
                player["sub_ability"] = None
                save_db(db)
                await msg.edit(content=f"РІСљвЂ¦ Р РЋРЎвЂљР ВµР Р…Р Т‘ РЎРѓР СР ВµР Р…РЎвЂР Р… Р Р…Р В° **{stand_name}**!")
            except asyncio.TimeoutError:
                save_db(db)
                await msg.edit(content="РІСњРЉ Р вЂ™РЎР‚Р ВµР СРЎРЏ Р Р†РЎвЂ№РЎв‚¬Р В»Р С•.")
        return

    player["stand"] = stand_name
    player["ability_tier"] = 1
    player["is_vampire"] = False
    player["stand_stats"] = None
    player["sub_ability"] = None
    save_db(db)
    embed = stand_embed(stand_name, player, interaction.user)
    embed.set_author(name=f"{interaction.user.display_name} Р С—Р С•Р В»РЎС“РЎвЂЎР С‘Р В» РЎРѓРЎвЂљР ВµР Р…Р Т‘!")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="stand", description="Р СџР С•РЎРѓР СР С•РЎвЂљРЎР‚Р ВµРЎвЂљРЎРЉ РЎРѓР Р†Р С•Р в„– РЎРѓРЎвЂљР ВµР Р…Р Т‘ Р С‘Р В»Р С‘ РЎРѓРЎвЂљР ВµР Р…Р Т‘ Р Т‘РЎР‚РЎС“Р С–Р С•Р С–Р С• Р С‘Р С–РЎР‚Р С•Р С”Р В°")
@app_commands.describe(user="Р пїЅР С–РЎР‚Р С•Р С” (Р Р…Р ВµР С•Р В±РЎРЏР В·Р В°РЎвЂљР ВµР В»РЎРЉР Р…Р С•)")
async def stand(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    db = load_db(); player = get_player(db, target.id)
    if not player["stand"]:
        await interaction.response.send_message(f"РІСњРЉ Р Р€ **{target.display_name}** Р Р…Р ВµРЎвЂљ РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В°!", ephemeral=True); return
    embed = stand_embed(player["stand"], player, target)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="inv", description="Р пїЅР Р…Р Р†Р ВµР Р…РЎвЂљР В°РЎР‚РЎРЉ")
@app_commands.describe(user="Р пїЅР С–РЎР‚Р С•Р С” (Р Р…Р ВµР С•Р В±РЎРЏР В·Р В°РЎвЂљР ВµР В»РЎРЉР Р…Р С•)")
async def inv(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    db = load_db(); player = get_player(db, target.id)

    embed = discord.Embed(title=f"СЂСџР‹вЂ™ {target.display_name}", color=0x2c2f33)
    embed.add_field(name="СЂСџРЏв„– Arrows", value=(
        f"СЂСџРЏв„– **{player['arrows']['regular']}** Regular\n"
        f"РІСљРЃ **{player['arrows']['requiem']}** Requiem\n"
        f"РІС™РЋ **{player['arrows']['overheaven']}** Overheaven"
    ), inline=True)
    embed.add_field(name="СЂСџвЂњВ¦ Crates", value=(
        f"СЂСџвЂњВ¦ **{player['crates']['common']}** Common\n"
        f"СЂСџСџВ¦ **{player['crates']['rare']}** Rare\n"
        f"СЂСџСџР€ **{player['crates']['epic']}** Epic\n"
        f"СЂСџРЉСџ **{player['crates']['legendary']}** Legendary"
    ), inline=True)
    embed.add_field(name="СЂСџвЂ™Р‹ Other", value=(
        f"СЂСџвЂ™Р‹ **{player['crystals']}** Crystals\n"
        f"СЂСџРЊв‚¬ **{player['fruits']}** Rokakaka\n"
        f"СЂСџР‹В­ **{player.get('stone_masks',0)}** Stone Mask"
    ), inline=True)

    stand_text = "None"
    if player["stand"]:
        sn = player["stand"]
        tier = STANDS[sn]["tier"]
        emoji = TIER_EMOJI.get(tier,"")
        vamp = " СЂСџВ§вЂє" if player.get("is_vampire") else ""
        stand_text = f"{emoji} **{sn}**{vamp}\nAbility Tier: {'РІВ­С’'*player['ability_tier']}"
        if can_evolve(sn):
            evo = get_evolution(sn)
            chance = EVOLVE_CHANCES.get(tier, 5.0)
            stand_text += f"\nРІВ¬вЂ РїС‘РЏ РІвЂ вЂ™ **{evo}** ({chance}%)"

    embed.add_field(name="РІС™вЂќРїС‘РЏ Stand", value=stand_text, inline=False)

    storage = player.get("storage", [])
    if storage:
        storage_text = ""
        for i, s in enumerate(storage, 1):
            st = STANDS[s["name"]]["tier"]
            em = TIER_EMOJI.get(st,"")
            vamp = " СЂСџВ§вЂє" if s.get("is_vampire") else ""
            storage_text += f"{i}. {em} **{s['name']}**{vamp} (Tier {'РІВ­С’'*s.get('ability_tier',1)})\n"
        embed.add_field(name="СЂСџвЂ”вЂћРїС‘РЏ Storage", value=storage_text, inline=False)
    else:
        embed.add_field(name="СЂСџвЂ”вЂћРїС‘РЏ Storage", value="Р СџРЎС“РЎРѓРЎвЂљР С• (Р СР В°Р С”РЎРѓ. 2 РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В°)", inline=False)

    embed.add_field(name="СЂСџвЂ™В° Money", value=f"**${player['money']:,}**", inline=True)
    embed.add_field(name="СЂСџвЂќРЃ Jobs",  value=f"**{player['jobs_done']}/{JOBS_REQUIRED}** Р Т‘Р В»РЎРЏ search", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="storage", description="Р Р€Р С—РЎР‚Р В°Р Р†Р В»Р ВµР Р…Р С‘Р Вµ РЎвЂ¦РЎР‚Р В°Р Р…Р С‘Р В»Р С‘РЎвЂ°Р ВµР С РЎРѓРЎвЂљР ВµР Р…Р Т‘Р С•Р Р†")
@app_commands.describe(action="store/swap/drop", slot="Р РЋР В»Р С•РЎвЂљ 1 Р С‘Р В»Р С‘ 2 (Р Т‘Р В»РЎРЏ swap)")
@app_commands.choices(action=[
    app_commands.Choice(name="store РІР‚вЂќ Р С—Р С•Р В»Р С•Р В¶Р С‘РЎвЂљРЎРЉ Р В°Р С”РЎвЂљР С‘Р Р†Р Р…РЎвЂ№Р в„– РЎРѓРЎвЂљР ВµР Р…Р Т‘", value="store"),
    app_commands.Choice(name="swap  РІР‚вЂќ Р С—Р С•Р СР ВµР Р…РЎРЏРЎвЂљРЎРЉ РЎРѓ Р В°Р С”РЎвЂљР С‘Р Р†Р Р…РЎвЂ№Р С",     value="swap"),
    app_commands.Choice(name="drop  РІР‚вЂќ Р Р†РЎвЂ№Р В±РЎР‚Р С•РЎРѓР С‘РЎвЂљРЎРЉ Р В°Р С”РЎвЂљР С‘Р Р†Р Р…РЎвЂ№Р в„– РЎРѓРЎвЂљР ВµР Р…Р Т‘", value="drop"),
])
async def storage(interaction: discord.Interaction, action: str, slot: int = 1):
    db = load_db(); player = get_player(db, interaction.user.id)
    store = player.get("storage", [])

    # РІвЂќР‚РІвЂќР‚ STORE РІвЂќР‚РІвЂќР‚
    if action == "store":
        if not player["stand"]:
            await interaction.response.send_message("РІСњРЉ Р Р€ РЎвЂљР ВµР В±РЎРЏ Р Р…Р ВµРЎвЂљ Р В°Р С”РЎвЂљР С‘Р Р†Р Р…Р С•Р С–Р С• РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В°!", ephemeral=True); return
        if len(store) >= 2:
            await interaction.response.send_message("РІСњРЉ Storage Р С—Р С•Р В»Р С•Р Р… (Р СР В°Р С”РЎРѓ. 2 РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В°)! Р пїЅРЎРѓР С—Р С•Р В»РЎРЉР В·РЎС“Р в„– `/storage swap`.", ephemeral=True); return
        obj = get_active_stand_obj(player)
        store.append(obj)
        player["storage"] = store
        set_active_stand(player, None)
        save_db(db)
        await interaction.response.send_message(
            f"СЂСџвЂњВ¦ **{obj['name']}** РЎРѓР С•РЎвЂ¦РЎР‚Р В°Р Р…РЎвЂР Р… Р Р† storage (РЎРѓР В»Р С•РЎвЂљ {len(store)}).",
            ephemeral=True
        ); return

    # РІвЂќР‚РІвЂќР‚ SWAP РІвЂќР‚РІвЂќР‚
    if action == "swap":
        if not store:
            await interaction.response.send_message("РІСњРЉ Storage Р С—РЎС“РЎРѓРЎвЂљ!", ephemeral=True); return
        idx = slot - 1
        if idx < 0 or idx >= len(store):
            await interaction.response.send_message(f"РІСњРЉ Р РЋР В»Р С•РЎвЂљ {slot} Р Р…Р Вµ РЎРѓРЎС“РЎвЂ°Р ВµРЎРѓРЎвЂљР Р†РЎС“Р ВµРЎвЂљ. Р вЂ™ storage {len(store)} РЎРѓРЎвЂљР ВµР Р…Р Т‘(Р В°).", ephemeral=True); return

        stored_obj = store[idx]
        active_obj = get_active_stand_obj(player)

        # swap
        store[idx] = active_obj if active_obj else None
        if store[idx] is None:
            store.pop(idx)
        set_active_stand(player, stored_obj)
        player["storage"] = store
        save_db(db)

        embed = discord.Embed(title="СЂСџвЂќвЂћ Р РЋРЎвЂљР ВµР Р…Р Т‘РЎвЂ№ Р С—Р С•Р СР ВµР Р…РЎРЏР Р…РЎвЂ№!", color=0x3498db)
        embed.add_field(name="РІС™вЂќРїС‘РЏ Р С’Р С”РЎвЂљР С‘Р Р†Р Р…РЎвЂ№Р в„– РЎвЂљР ВµР С—Р ВµРЎР‚РЎРЉ", value=f"**{stored_obj['name']}**", inline=True)
        if active_obj:
            embed.add_field(name="СЂСџвЂњВ¦ Р вЂ™ storage РЎвЂљР ВµР С—Р ВµРЎР‚РЎРЉ", value=f"**{active_obj['name']}**", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # РІвЂќР‚РІвЂќР‚ DROP РІвЂќР‚РІвЂќР‚
    if action == "drop":
        if not player["stand"]:
            await interaction.response.send_message("РІСњРЉ Р Р€ РЎвЂљР ВµР В±РЎРЏ Р Р…Р ВµРЎвЂљ Р В°Р С”РЎвЂљР С‘Р Р†Р Р…Р С•Р С–Р С• РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В°!", ephemeral=True); return
        sn = player["stand"]
        await interaction.response.send_message(
            f"РІС™В РїС‘РЏ Р СћРЎвЂ№ РЎС“Р Р†Р ВµРЎР‚Р ВµР Р… РЎвЂЎРЎвЂљР С• РЎвЂ¦Р С•РЎвЂЎР ВµРЎв‚¬РЎРЉ Р Р†РЎвЂ№Р В±РЎР‚Р С•РЎРѓР С‘РЎвЂљРЎРЉ **{sn}**? Р В­РЎвЂљР С• Р Т‘Р ВµР в„–РЎРѓРЎвЂљР Р†Р С‘Р Вµ Р Р…Р ВµР С•Р В±РЎР‚Р В°РЎвЂљР С‘Р СР С•!\nР СњР В°Р В¶Р СР С‘ РІСљвЂ¦ Р Т‘Р В»РЎРЏ Р С—Р С•Р Т‘РЎвЂљР Р†Р ВµРЎР‚Р В¶Р Т‘Р ВµР Р…Р С‘РЎРЏ.",
            ephemeral=True
        )
        msg = await interaction.original_response()
        await msg.add_reaction("РІСљвЂ¦")
        def check(r, u): return u == interaction.user and str(r.emoji) == "РІСљвЂ¦" and r.message.id == msg.id
        try:
            await bot.wait_for("reaction_add", timeout=20.0, check=check)
            set_active_stand(player, None)
            save_db(db)
            await msg.edit(content=f"СЂСџвЂ”вЂРїС‘РЏ Р РЋРЎвЂљР ВµР Р…Р Т‘ **{sn}** Р Р†РЎвЂ№Р В±РЎР‚Р С•РЎв‚¬Р ВµР Р….")
        except asyncio.TimeoutError:
            await msg.edit(content="РІСњРЉ Р С›РЎвЂљР СР ВµР Р…Р ВµР Р…Р С•.")


@tree.command(name="evolve", description="Р В­Р Р†Р С•Р В»РЎР‹РЎвЂ Р С‘РЎРЏ РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В°")
@app_commands.describe(evo_type="requiem (РЎвЂЎР ВµРЎР‚Р ВµР В· Requiem Arrow) Р С‘Р В»Р С‘ vampire (РЎвЂЎР ВµРЎР‚Р ВµР В· Stone Mask)")
@app_commands.choices(evo_type=[
    app_commands.Choice(name="requiem РІР‚вЂќ РЎРЊР Р†Р С•Р В»РЎР‹РЎвЂ Р С‘РЎРЏ РЎвЂЎР ВµРЎР‚Р ВµР В· Requiem Arrow", value="requiem"),
    app_commands.Choice(name="vampire РІР‚вЂќ Р Р†Р В°Р СР С—Р С‘РЎР‚ РЎвЂЎР ВµРЎР‚Р ВµР В· Stone Mask",       value="vampire"),
])
async def evolve(interaction: discord.Interaction, evo_type: str = "requiem"):
    db = load_db(); player = get_player(db, interaction.user.id)
    if not player["stand"]:
        await interaction.response.send_message("РІСњРЉ Р Р€ РЎвЂљР ВµР В±РЎРЏ Р Р…Р ВµРЎвЂљ РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В°!", ephemeral=True); return

    if evo_type == "vampire":
        if player.get("is_vampire"):
            await interaction.response.send_message("РІСњРЉ Р РЋРЎвЂљР ВµР Р…Р Т‘ РЎС“Р В¶Р Вµ РЎРЏР Р†Р В»РЎРЏР ВµРЎвЂљРЎРѓРЎРЏ Р Р†Р В°Р СР С—Р С‘РЎР‚Р С•Р С!", ephemeral=True); return
        if player.get("stone_masks", 0) <= 0:
            await interaction.response.send_message("РІСњРЉ Р СњРЎС“Р В¶Р Р…Р В° СЂСџР‹В­ **Stone Mask**! Р вЂ™РЎвЂ№Р В±Р С‘Р Р†Р В°Р ВµРЎвЂљРЎРѓРЎРЏ Р С‘Р В· Legendary Crate (1.5%).", ephemeral=True); return

        player["stone_masks"] -= 1
        stand_name = player["stand"]
        base_stats = get_stand_stats(player, stand_name)
        all_z = all(v == "A" for v in base_stats.values())
        new_stats = {k: "Z" if all_z else STAT_UP.get(v, v) for k, v in base_stats.items()}
        player["stand_stats"] = new_stats
        player["is_vampire"] = True
        save_db(db)

        embed = discord.Embed(title="СЂСџВ§вЂє Vampire Evolution!", description=f"**{stand_name}** Р С—РЎР‚Р С•Р Р…Р В·РЎвЂР Р… Р С™Р В°Р СР ВµР Р…Р Р…Р С•Р в„– Р СљР В°РЎРѓР С”Р С•Р в„–!", color=0x8e0000)
        stats_text = "\n".join([f"{k.replace('_',' ').title()}: **{base_stats[k]}** РІвЂ вЂ™ **{new_stats[k]}**" for k in new_stats])
        embed.add_field(name="СЂСџвЂњР‰ Р пїЅР В·Р СР ВµР Р…Р ВµР Р…Р С‘Р Вµ РЎРѓРЎвЂљР В°РЎвЂљР С•Р Р†", value=stats_text, inline=False)
        embed.add_field(name="СЂСџВ§вЂє Р СњР С•Р Р†Р В°РЎРЏ РЎРѓР С—Р С•РЎРѓР С•Р В±Р Р…Р С•РЎРѓРЎвЂљРЎРЉ", value="Vampiric Freeze РІР‚вЂќ Р В·Р В°Р СР С•РЎР‚Р В°Р В¶Р С‘Р Р†Р В°Р ВµРЎвЂљ Р Р†РЎР‚Р В°Р С–Р В°", inline=False)
        if all_z:
            embed.add_field(name="СЂСџвЂ™Р‚ GODLIKE", value="Р вЂ™РЎРѓР Вµ РЎРѓРЎвЂљР В°РЎвЂљРЎвЂ№ **Z**!", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # requiem
    stand_name = player["stand"]
    if not can_evolve(stand_name):
        await interaction.response.send_message(f"РІСњРЉ **{stand_name}** Р Р…Р Вµ Р СР С•Р В¶Р ВµРЎвЂљ РЎРЊР Р†Р С•Р В»РЎР‹РЎвЂ Р С‘Р С•Р Р…Р С‘РЎР‚Р С•Р Р†Р В°РЎвЂљРЎРЉ РЎвЂЎР ВµРЎР‚Р ВµР В· Requiem.", ephemeral=True); return
    if player["arrows"]["requiem"] <= 0:
        await interaction.response.send_message("РІСњРЉ Р СњРЎС“Р В¶Р Р…Р В° РІСљРЃ **Requiem Arrow**!", ephemeral=True); return

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
        embed.set_author(name=f"РІСљРЃ {interaction.user.display_name} РЎРЊР Р†Р С•Р В»РЎР‹РЎвЂ Р С‘Р С•Р Р…Р С‘РЎР‚Р С•Р Р†Р В°Р В» РЎРѓРЎвЂљР ВµР Р…Р Т‘!")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        save_db(db)
        embed = discord.Embed(
            title="СЂСџвЂ™вЂќ Р В­Р Р†Р С•Р В»РЎР‹РЎвЂ Р С‘РЎРЏ Р С—РЎР‚Р С•Р Р†Р В°Р В»Р С‘Р В»Р В°РЎРѓРЎРЉ!",
            description=f"**{stand_name}** Р Р…Р Вµ Р С—РЎР‚Р С‘Р Р…РЎРЏР В» РЎРѓРЎвЂљРЎР‚Р ВµР В»РЎС“...\nР РЃР В°Р Р…РЎРѓ Р В±РЎвЂ№Р В» **{chance}%**\nР РЋРЎвЂљРЎР‚Р ВµР В»Р В° Р С—Р С•РЎвЂљРЎР‚Р В°РЎвЂЎР ВµР Р…Р В°.",
            color=0xe74c3c
        )
        embed.add_field(name="РІВ¬вЂ РїС‘РЏ Р В¦Р ВµР В»РЎРЉ",        value=f"**{evolution_name}**",              inline=True)
        embed.add_field(name="РІСљРЃ Р С›РЎРѓРЎвЂљР В°Р В»Р С•РЎРѓРЎРЉ",    value=f"**{player['arrows']['requiem']}**", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="upgrade", description="Р СџРЎР‚Р С•Р С”Р В°РЎвЂЎР В°РЎвЂљРЎРЉ РЎРѓР С—Р С•РЎРѓР С•Р В±Р Р…Р С•РЎРѓРЎвЂљРЎРЉ РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В° (Tier 1РІвЂ вЂ™2РІвЂ вЂ™3)")
async def upgrade(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    if not player["stand"]:
        await interaction.response.send_message("РІСњРЉ Р Р€ РЎвЂљР ВµР В±РЎРЏ Р Р…Р ВµРЎвЂљ РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В°!", ephemeral=True); return

    stand_name = player["stand"]
    cur_tier   = player["ability_tier"]
    if cur_tier >= 3:
        await interaction.response.send_message("РІСљвЂ¦ Р РЋР С—Р С•РЎРѓР С•Р В±Р Р…Р С•РЎРѓРЎвЂљРЎРЉ РЎС“Р В¶Р Вµ Р Р…Р В° Р СР В°Р С”РЎРѓР С‘Р СРЎС“Р СР Вµ (Tier 3)!", ephemeral=True); return

    next_tier = cur_tier + 1
    cost      = UPGRADE_COST[next_tier]
    upgrades  = ABILITY_UPGRADES.get(stand_name, {})
    current_ability = upgrades.get(cur_tier,  STANDS[stand_name]["ability"])
    next_ability    = upgrades.get(next_tier, STANDS[stand_name]["ability"])

    if player["crystals"] < cost["crystals"] or player["money"] < cost["money"]:
        await interaction.response.send_message(
            f"РІСњРЉ Р СњР ВµР Т‘Р С•РЎРѓРЎвЂљР В°РЎвЂљР С•РЎвЂЎР Р…Р С• РЎР‚Р ВµРЎРѓРЎС“РЎР‚РЎРѓР С•Р Р†!\nР СњРЎС“Р В¶Р Р…Р С•: СЂСџвЂ™Р‹ **{cost['crystals']}** + СЂСџвЂ™В° **${cost['money']:,}**\nР Р€ РЎвЂљР ВµР В±РЎРЏ: СЂСџвЂ™Р‹ **{player['crystals']}** + СЂСџвЂ™В° **${player['money']:,}**",
            ephemeral=True
        ); return

    embed = discord.Embed(title=f"РІВ¬вЂ РїС‘РЏ Р С’Р С—Р С–РЎР‚Р ВµР в„–Р Т‘ РІР‚вЂќ {stand_name}", color=TIER_COLORS.get(STANDS[stand_name]["tier"], 0xffffff))
    embed.add_field(name=f"{'РІВ­С’'*cur_tier} Р РЋР ВµР в„–РЎвЂЎР В°РЎРѓ", value=current_ability, inline=False)
    embed.add_field(name=f"{'РІВ­С’'*next_tier} Р СџР С•РЎРѓР В»Р Вµ",  value=next_ability,   inline=False)
    embed.add_field(name="СЂСџвЂ™В° Р РЋРЎвЂљР С•Р С‘Р СР С•РЎРѓРЎвЂљРЎРЉ", value=f"СЂСџвЂ™Р‹ **{cost['crystals']}** + СЂСџвЂ™В° **${cost['money']:,}**", inline=False)
    embed.set_footer(text="Р СњР В°Р В¶Р СР С‘ РІСљвЂ¦ Р Т‘Р В»РЎРЏ Р С—Р С•Р Т‘РЎвЂљР Р†Р ВµРЎР‚Р В¶Р Т‘Р ВµР Р…Р С‘РЎРЏ")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    msg = await interaction.original_response()
    await msg.add_reaction("РІСљвЂ¦")

    def check(r, u): return u == interaction.user and str(r.emoji) == "РІСљвЂ¦" and r.message.id == msg.id
    try:
        await bot.wait_for("reaction_add", timeout=30.0, check=check)
        player["crystals"] -= cost["crystals"]
        player["money"]    -= cost["money"]
        player["ability_tier"] = next_tier
        save_db(db)
        await msg.edit(content=f"РІСљвЂ¦ Р РЋР С—Р С•РЎРѓР С•Р В±Р Р…Р С•РЎРѓРЎвЂљРЎРЉ Р С—РЎР‚Р С•Р С”Р В°РЎвЂЎР В°Р Р…Р В° Р Т‘Р С• Tier {next_tier}! {'РІВ­С’'*next_tier}\n{next_ability}")
    except asyncio.TimeoutError:
        await msg.edit(content="РІСњРЉ Р вЂ™РЎР‚Р ВµР СРЎРЏ Р Р†РЎвЂ№РЎв‚¬Р В»Р С•.")


@tree.command(name="rokakaka", description="Р РЋР С”РЎР‚Р ВµРЎРѓРЎвЂљР С‘РЎвЂљРЎРЉ РЎРѓРЎвЂљР ВµР Р…Р Т‘ РЎРѓ Р Т‘РЎР‚РЎС“Р С–Р С‘Р С Р С‘ РЎС“Р С”РЎР‚Р В°РЎРѓРЎвЂљРЎРЉ РЎРѓР С—Р С•РЎРѓР С•Р В±Р Р…Р С•РЎРѓРЎвЂљРЎРЉ")
@app_commands.describe(stand_name="Р СњР В°Р В·Р Р†Р В°Р Р…Р С‘Р Вµ РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В° Р Т‘Р В»РЎРЏ РЎРѓР С”РЎР‚Р ВµРЎвЂ°Р С‘Р Р†Р В°Р Р…Р С‘РЎРЏ")
async def rokakaka(interaction: discord.Interaction, stand_name: str):
    db = load_db(); player = get_player(db, interaction.user.id)
    if not player["stand"]:
        await interaction.response.send_message("РІСњРЉ Р Р€ РЎвЂљР ВµР В±РЎРЏ Р Р…Р ВµРЎвЂљ РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В°!", ephemeral=True); return
    if player.get("fruits", 0) <= 0:
        await interaction.response.send_message("РІСњРЉ Р СњР ВµРЎвЂљ СЂСџРЊв‚¬ Rokakaka! Р вЂќРЎР‚Р С•Р С—: СЂСџСџР€ Epic 5% | СЂСџРЉСџ Legendary 9%", ephemeral=True); return

    target_stand = None
    for name in STANDS:
        if name.lower() == stand_name.lower():
            target_stand = name; break
    if not target_stand:
        matches = [n for n in STANDS if stand_name.lower() in n.lower()]
        if len(matches) == 1: target_stand = matches[0]
        elif len(matches) > 1:
            await interaction.response.send_message(f"РІСњРЉ Р СњР ВµРЎРѓР С”Р С•Р В»РЎРЉР С”Р С• РЎРѓР С•Р Р†Р С—Р В°Р Т‘Р ВµР Р…Р С‘Р в„–: {', '.join(matches[:5])}", ephemeral=True); return
        else:
            await interaction.response.send_message(f"РІСњРЉ Р РЋРЎвЂљР ВµР Р…Р Т‘ **{stand_name}** Р Р…Р Вµ Р Р…Р В°Р в„–Р Т‘Р ВµР Р….", ephemeral=True); return

    if target_stand == player["stand"]:
        await interaction.response.send_message("РІСњРЉ Р СњР ВµР В»РЎРЉР В·РЎРЏ РЎРѓР С”РЎР‚Р ВµРЎвЂ°Р С‘Р Р†Р В°РЎвЂљРЎРЉ РЎРѓ РЎРѓР С•Р В±Р С•Р в„–!", ephemeral=True); return

    target_data    = STANDS[target_stand]
    stolen_ability = target_data["ability"]
    is_evo         = not target_data.get("obtainable", True)
    chance         = 10.0 if is_evo else 40.0
    has_sub        = player.get("sub_ability") is not None

    embed = discord.Embed(title="СЂСџРЊв‚¬ Rokakaka РІР‚вЂќ Р РЋР С”РЎР‚Р ВµРЎвЂ°Р С‘Р Р†Р В°Р Р…Р С‘Р Вµ", color=0x2ecc71)
    embed.add_field(name="РІС™вЂќРїС‘РЏ Р СћР Р†Р С•Р в„– РЎРѓРЎвЂљР ВµР Р…Р Т‘", value=f"**{player['stand']}**",    inline=True)
    embed.add_field(name="СЂСџР‹Р‡ Р В¦Р ВµР В»РЎРЉ",        value=f"**{target_stand}**",        inline=True)
    embed.add_field(name="СЂСџвЂњР‰ Р РЃР В°Р Р…РЎРѓ",        value=f"**{chance}%**",             inline=True)
    embed.add_field(name="СЂСџвЂ™В« Р РЋР С—Р С•РЎРѓР С•Р В±Р Р…Р С•РЎРѓРЎвЂљРЎРЉ", value=stolen_ability,               inline=False)
    if has_sub:
        embed.add_field(name="РІС™В РїС‘РЏ Р вЂ”Р В°Р СР ВµР Р…Р В°", value=f"~~{player['sub_ability']}~~", inline=False)
    embed.set_footer(text="Р СњР В°Р В¶Р СР С‘ РІСљвЂ¦ РЎвЂЎРЎвЂљР С•Р В±РЎвЂ№ Р С‘РЎРѓР С—Р С•Р В»РЎРЉР В·Р С•Р Р†Р В°РЎвЂљРЎРЉ Rokakaka")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    msg = await interaction.original_response()
    await msg.add_reaction("РІСљвЂ¦")

    def check(r, u): return u == interaction.user and str(r.emoji) == "РІСљвЂ¦" and r.message.id == msg.id
    try:
        await bot.wait_for("reaction_add", timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await msg.edit(content="РІСњРЉ Р вЂ™РЎР‚Р ВµР СРЎРЏ Р Р†РЎвЂ№РЎв‚¬Р В»Р С•."); return

    player["fruits"] -= 1
    if random.uniform(0, 100) < chance:
        player["sub_ability"] = stolen_ability
        save_db(db)
        await msg.edit(content=f"РІСљвЂ¦ Р РЋР С”РЎР‚Р ВµРЎвЂ°Р С‘Р Р†Р В°Р Р…Р С‘Р Вµ РЎС“РЎРѓР С—Р ВµРЎв‚¬Р Р…Р С•! **{player['stand']}** Р С—Р С•Р В»РЎС“РЎвЂЎР С‘Р В»: {stolen_ability}")
    else:
        save_db(db)
        await msg.edit(content=f"СЂСџвЂ™вЂќ Р СџРЎР‚Р С•Р Р†Р В°Р В»! Р РЃР В°Р Р…РЎРѓ Р В±РЎвЂ№Р В» {chance}%. Р В¤РЎР‚РЎС“Р С”РЎвЂљ Р С—Р С•РЎвЂљРЎР‚Р В°РЎвЂЎР ВµР Р…. Р С›РЎРѓРЎвЂљР В°Р В»Р С•РЎРѓРЎРЉ: **{player['fruits']}** СЂСџРЊв‚¬")


@tree.command(name="shop", description="Р СљР В°Р С–Р В°Р В·Р С‘Р Р… РІР‚вЂќ Р С”РЎС“Р С—Р С‘РЎвЂљРЎРЉ РЎРѓРЎвЂљРЎР‚Р ВµР В»РЎвЂ№, Р С”РЎР‚Р С‘РЎРѓРЎвЂљР В°Р В»Р В»РЎвЂ№, Р С”Р ВµР в„–РЎРѓРЎвЂ№")
@app_commands.describe(item="Р В§РЎвЂљР С• Р С”РЎС“Р С—Р С‘РЎвЂљРЎРЉ: arrow, crystal, common, rare")
@app_commands.choices(item=[
    app_commands.Choice(name="СЂСџРЏв„– Regular Arrow РІР‚вЂќ $500",  value="arrow"),
    app_commands.Choice(name="СЂСџвЂ™Р‹ Crystal РІР‚вЂќ $800",        value="crystal"),
    app_commands.Choice(name="СЂСџвЂњВ¦ Common Crate РІР‚вЂќ $1000",  value="common"),
    app_commands.Choice(name="СЂСџСџВ¦ Rare Crate РІР‚вЂќ $2500",   value="rare"),
])
async def shop(interaction: discord.Interaction, item: str = None):
    db = load_db(); player = get_player(db, interaction.user.id)

    if not item:
        embed = discord.Embed(title="СЂСџРЏР„ JoJo Shop", color=0xe67e22)
        for key, d in SHOP_ITEMS.items():
            embed.add_field(name=f"{d['icon']} {d['name']}", value=f"СЂСџвЂ™В° **${d['price']:,}**\n`/shop {key}`", inline=True)
        embed.add_field(name="РІС™В РїС‘РЏ Р СњР Вµ Р С—РЎР‚Р С•Р Т‘Р В°РЎвЂРЎвЂљРЎРѓРЎРЏ", value="РІСљРЃ Requiem Arrow\nСЂСџРЊв‚¬ Rokakaka\nСЂСџСџР€ Epic / СЂСџРЉСџ Legendary Crate", inline=False)
        embed.set_footer(text=f"Р СћР Р†Р С•Р в„– Р В±Р В°Р В»Р В°Р Р…РЎРѓ: ${player['money']:,}")
        await interaction.response.send_message(embed=embed, ephemeral=True); return

    d = SHOP_ITEMS[item]
    if player["money"] < d["price"]:
        await interaction.response.send_message(f"РІСњРЉ Р СњРЎС“Р В¶Р Р…Р С• СЂСџвЂ™В° **${d['price']:,}**, РЎС“ РЎвЂљР ВµР В±РЎРЏ **${player['money']:,}**", ephemeral=True); return

    player["money"] -= d["price"]
    itype = d["type"]
    if itype == "regular_arrow":   player["arrows"]["regular"] += 1
    elif itype == "crystal":       player["crystals"] += 1
    elif itype == "common_crate":  player["crates"]["common"] += 1
    elif itype == "rare_crate":    player["crates"]["rare"] += 1
    save_db(db)

    await interaction.response.send_message(
        f"РІСљвЂ¦ Р С™РЎС“Р С—Р В»Р ВµР Р…Р С•: {d['icon']} **{d['name']}**!\nСЂСџвЂ™В° Р СџР С•РЎвЂљРЎР‚Р В°РЎвЂЎР ВµР Р…Р С•: **${d['price']:,}** | Р вЂР В°Р В»Р В°Р Р…РЎРѓ: **${player['money']:,}**",
        ephemeral=True
    )


@tree.command(name="crate", description="Р С›РЎвЂљР С”РЎР‚РЎвЂ№РЎвЂљРЎРЉ Р С”Р ВµР в„–РЎРѓ Р С‘Р В»Р С‘ Р С—Р С•РЎРѓР СР С•РЎвЂљРЎР‚Р ВµРЎвЂљРЎРЉ РЎРѓР С•Р Т‘Р ВµРЎР‚Р В¶Р С‘Р СР С•Р Вµ")
@app_commands.describe(crate_type="Р СћР С‘Р С— Р С”Р ВµР в„–РЎРѓР В°: common, rare, epic, legendary")
@app_commands.choices(crate_type=[
    app_commands.Choice(name="СЂСџвЂњВ¦ Common",    value="common"),
    app_commands.Choice(name="СЂСџСџВ¦ Rare",      value="rare"),
    app_commands.Choice(name="СЂСџСџР€ Epic",      value="epic"),
    app_commands.Choice(name="СЂСџРЉСџ Legendary", value="legendary"),
])
async def crate(interaction: discord.Interaction, crate_type: str = None):
    db = load_db(); player = get_player(db, interaction.user.id)

    if not crate_type:
        embed = discord.Embed(title="СЂСџвЂњВ¦ Р СћР Р†Р С•Р С‘ Р С”Р ВµР в„–РЎРѓРЎвЂ№", color=0x2c2f33)
        ct_text = "\n".join([f"{c['icon']} **{player['crates'].get(k,0)}** {c['name']}" for k,c in CRATE_CONFIG.items()])
        embed.add_field(name="Р С™Р ВµР в„–РЎРѓРЎвЂ№", value=ct_text, inline=False)
        ch_text = ""
        for k, c in CRATE_CONFIG.items():
            ch_text += f"{c['icon']} **{c['name']}**: СЂСџвЂ™В°${c['money_min']}-${c['money_max']} | СЂСџРЏв„–{c['regular_arrow_chance']}% | РІСљРЃ{c['requiem_arrow_chance']}%"
            if c.get("stone_mask_chance",0) > 0: ch_text += f" | СЂСџР‹В­{c['stone_mask_chance']}%"
            if c.get("rokakaka_chance",0) > 0:   ch_text += f" | СЂСџРЊв‚¬{c['rokakaka_chance']}%"
            ch_text += "\n"
        embed.add_field(name="СЂСџвЂњР‰ Р РЃР В°Р Р…РЎРѓРЎвЂ№", value=ch_text, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True); return

    if player["crates"].get(crate_type, 0) <= 0:
        await interaction.response.send_message(f"РІСњРЉ Р СњР ВµРЎвЂљ **{CRATE_CONFIG[crate_type]['name']}**!", ephemeral=True); return

    player["crates"][crate_type] -= 1
    player["crates_opened"] = player.get("crates_opened",0) + 1
    if crate_type == "epic": player["epic_opened"] = player.get("epic_opened",0) + 1
    rewards = open_crate(crate_type)
    rewards_text = ""
    for r in rewards:
        if r["type"] == "money":
            player["money"] += r["amount"]; rewards_text += f"СЂСџвЂ™В° **${r['amount']:,}**\n"
        elif r["type"] == "regular_arrow":
            player["arrows"]["regular"] += r["amount"]; rewards_text += f"СЂСџРЏв„– **Regular Arrow** x{r['amount']}\n"
        elif r["type"] == "requiem_arrow":
            player["arrows"]["requiem"] += r["amount"]; rewards_text += f"РІСљРЃ **Requiem Arrow** x{r['amount']} РІС™В РїС‘РЏ Р В Р вЂўР вЂќР С™Р пїЅР в„ў!\n"
        elif r["type"] == "stone_mask":
            player["stone_masks"] = player.get("stone_masks",0) + r["amount"]; rewards_text += f"СЂСџР‹В­ **Stone Mask** x{r['amount']} СЂСџвЂ™Р‚ Р Р€Р вЂєР В¬Р СћР В Р С’ Р В Р вЂўР вЂќР С™Р пїЅР в„ў!\n"
        elif r["type"] == "rokakaka":
            player["fruits"] = player.get("fruits",0) + r["amount"]; rewards_text += f"СЂСџРЊв‚¬ **Rokakaka** x{r['amount']} Р В Р вЂўР вЂќР С™Р пїЅР в„ў!\n"
    save_db(db)

    cfg = CRATE_CONFIG[crate_type]
    embed = discord.Embed(title=f"{cfg['icon']} {cfg['name']}!", color=cfg["color"])
    embed.add_field(name="СЂСџР‹Рѓ Р СњР В°Р С–РЎР‚Р В°Р Т‘РЎвЂ№", value=rewards_text, inline=False)
    embed.add_field(name="СЂСџвЂ™В° Р вЂР В°Р В»Р В°Р Р…РЎРѓ",  value=f"**${player['money']:,}**", inline=True)
    embed.set_footer(text=f"Р С›РЎРѓРЎвЂљР В°Р В»Р С•РЎРѓРЎРЉ {player['crates'][crate_type]} {cfg['name']}")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="money", description="Р СџР С•РЎРѓР СР С•РЎвЂљРЎР‚Р ВµРЎвЂљРЎРЉ Р В±Р В°Р В»Р В°Р Р…РЎРѓ")
async def money(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    embed = discord.Embed(title="СЂСџвЂ™В° Balance", color=0xf1c40f)
    embed.add_field(name="Money", value=f"**${player['money']:,}**", inline=False)
    embed.set_footer(text=interaction.user.display_name)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="quest", description="Р СџР С•РЎРѓР СР С•РЎвЂљРЎР‚Р ВµРЎвЂљРЎРЉ Р С”Р Р†Р ВµРЎРѓРЎвЂљ Р С‘Р В»Р С‘ Р В·Р В°Р В±РЎР‚Р В°РЎвЂљРЎРЉ Р Р…Р В°Р С–РЎР‚Р В°Р Т‘РЎС“")
@app_commands.describe(action="claim РІР‚вЂќ Р В·Р В°Р В±РЎР‚Р В°РЎвЂљРЎРЉ Р Р…Р В°Р С–РЎР‚Р В°Р Т‘РЎС“")
@app_commands.choices(action=[
    app_commands.Choice(name="show  РІР‚вЂќ Р С—Р С•РЎРѓР СР С•РЎвЂљРЎР‚Р ВµРЎвЂљРЎРЉ Р С—РЎР‚Р С•Р С–РЎР‚Р ВµРЎРѓРЎРѓ", value="show"),
    app_commands.Choice(name="claim РІР‚вЂќ Р В·Р В°Р В±РЎР‚Р В°РЎвЂљРЎРЉ Р Р…Р В°Р С–РЎР‚Р В°Р Т‘РЎС“",     value="claim"),
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
            await interaction.response.send_message(f"РІСњРЉ Р С™Р Р†Р ВµРЎРѓРЎвЂљ Р Р…Р Вµ Р Р†РЎвЂ№Р С—Р С•Р В»Р Р…Р ВµР Р…! **{min(progress,goal)}/{goal}**", ephemeral=True); return
        reward = quest_data["reward"]
        if "money"    in reward: player["money"]    += reward["money"]
        if "crystals" in reward: player["crystals"] += reward["crystals"]
        if "crates"   in reward:
            for ctype, amt in reward["crates"].items(): player["crates"][ctype] += amt
        assign_quest(player)
        new_quest = next(q for q in QUESTS if q["id"] == player["quest"])
        save_db(db)
        embed = discord.Embed(title=f"СЂСџР‹вЂ° Р С™Р Р†Р ВµРЎРѓРЎвЂљ Р Р†РЎвЂ№Р С—Р С•Р В»Р Р…Р ВµР Р…: {quest_data['name']}!", color=0xf1c40f)
        embed.add_field(name="СЂСџР‹Рѓ Р СњР В°Р С–РЎР‚Р В°Р Т‘Р В°",     value=quest_data["reward_text"],             inline=False)
        embed.add_field(name="СЂСџвЂњвЂ№ Р СњР С•Р Р†РЎвЂ№Р в„– Р С”Р Р†Р ВµРЎРѓРЎвЂљ", value=f"**{new_quest['name']}** РІР‚вЂќ {new_quest['desc']}", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True); return

    bar_filled = int((min(progress,goal)/goal)*10)
    bar    = "РІвЂ“в‚¬"*bar_filled + "РІвЂ“вЂ"*(10-bar_filled)
    status = "РІСљвЂ¦ Р вЂ™Р В«Р СџР С›Р вЂєР СњР вЂўР Сњ РІР‚вЂќ `/quest claim`!" if done else f"[{bar}] {min(progress,goal)}/{goal}"
    embed  = discord.Embed(title="СЂСџвЂњвЂ№ Р СћР ВµР С”РЎС“РЎвЂ°Р С‘Р в„– Р С”Р Р†Р ВµРЎРѓРЎвЂљ", color=0xf1c40f if done else 0x3498db)
    embed.add_field(name=f"СЂСџР‹Р‡ {quest_data['name']}", value=quest_data["desc"],       inline=False)
    embed.add_field(name="СЂСџвЂњР‰ Р СџРЎР‚Р С•Р С–РЎР‚Р ВµРЎРѓРЎРѓ",              value=status,                    inline=False)
    embed.add_field(name="СЂСџРЏвЂ  Р СњР В°Р С–РЎР‚Р В°Р Т‘Р В°",               value=quest_data["reward_text"], inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="help", description="Р РЋР С—Р С‘РЎРѓР С•Р С” Р Р†РЎРѓР ВµРЎвЂ¦ Р С”Р С•Р СР В°Р Р…Р Т‘")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="СЂСџвЂњвЂ“ JoJo Bot РІР‚вЂќ Р С™Р С•Р СР В°Р Р…Р Т‘РЎвЂ№", color=0x9b59b6)
    embed.add_field(name="/job",              value="Р В Р В°Р В±Р С•РЎвЂљР В° (Р С”Р Т‘:30Р СР С‘Р Р…) СЂСџСџСћСЂСџСџРЋСЂСџвЂќТ‘", inline=False)
    embed.add_field(name="/search",           value=f"Р СњР В°Р в„–РЎвЂљР С‘ Р С”Р ВµР в„–РЎРѓ (Р Р…РЎС“Р В¶Р Р…Р С• {JOBS_REQUIRED} РЎР‚Р В°Р В±Р С•РЎвЂљРЎвЂ№)", inline=False)
    embed.add_field(name="/crate [РЎвЂљР С‘Р С—]",      value="Р С›РЎвЂљР С”РЎР‚РЎвЂ№РЎвЂљРЎРЉ Р С”Р ВµР в„–РЎРѓ", inline=False)
    embed.add_field(name="/arrow [РЎвЂљР С‘Р С—]",      value="Р пїЅРЎРѓР С—Р С•Р В»РЎРЉР В·Р С•Р Р†Р В°РЎвЂљРЎРЉ РЎРѓРЎвЂљРЎР‚Р ВµР В»РЎС“", inline=False)
    embed.add_field(name="/evolve [РЎвЂљР С‘Р С—]",     value="Р В­Р Р†Р С•Р В»РЎР‹РЎвЂ Р С‘РЎРЏ РЎРѓРЎвЂљР ВµР Р…Р Т‘Р В° (requiem/vampire)", inline=False)
    embed.add_field(name="/upgrade",          value="Р СџРЎР‚Р С•Р С”Р В°РЎвЂЎР В°РЎвЂљРЎРЉ РЎРѓР С—Р С•РЎРѓР С•Р В±Р Р…Р С•РЎРѓРЎвЂљРЎРЉ (Tier 1РІвЂ вЂ™2РІвЂ вЂ™3)", inline=False)
    embed.add_field(name="/rokakaka [РЎРѓРЎвЂљР ВµР Р…Р Т‘]", value="Р РЋР С”РЎР‚Р ВµРЎРѓРЎвЂљР С‘РЎвЂљРЎРЉ РЎРѓРЎвЂљР ВµР Р…Р Т‘ (Р Р…РЎС“Р В¶Р Р…Р В° СЂСџРЊв‚¬ Rokakaka)", inline=False)
    embed.add_field(name="/storage [action]", value="Р ТђРЎР‚Р В°Р Р…Р С‘Р В»Р С‘РЎвЂ°Р Вµ РЎРѓРЎвЂљР ВµР Р…Р Т‘Р С•Р Р† (store/swap/drop)", inline=False)
    embed.add_field(name="/shop [Р С—РЎР‚Р ВµР Т‘Р СР ВµРЎвЂљ]",   value="Р СљР В°Р С–Р В°Р В·Р С‘Р Р…", inline=False)
    embed.add_field(name="/quest [action]",   value="Р С™Р Р†Р ВµРЎРѓРЎвЂљРЎвЂ№ (show/claim)", inline=False)
    embed.add_field(name="/stand [@user]",    value="Р СџР С•РЎРѓР СР С•РЎвЂљРЎР‚Р ВµРЎвЂљРЎРЉ РЎРѓРЎвЂљР ВµР Р…Р Т‘", inline=False)
    embed.add_field(name="/inv [@user]",      value="Р пїЅР Р…Р Р†Р ВµР Р…РЎвЂљР В°РЎР‚РЎРЉ", inline=False)
    embed.add_field(name="/money",            value="Р вЂР В°Р В»Р В°Р Р…РЎРѓ", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# РІвЂќР‚РІвЂќР‚РІвЂќР‚ RUN РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚РІвЂќР‚
bot.run(TOKEN)

