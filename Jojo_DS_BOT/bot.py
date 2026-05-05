# -*- coding: utf-8 -*-
import discord
from discord import app_commands
from discord.ext import commands
import json, os, random, asyncio
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta
from stands import (STANDS, TIER_COLORS, TIER_EMOJI, TIER_WEIGHTS,
                    EVOLUTION_CHAINS, ABILITY_UPGRADES,
                    get_stand_by_tier, can_evolve, get_evolution)

# ─── CONFIG ───────────────────────────────────────────────────────
TOKEN    = os.getenv("TOKEN")
DB_FILE  = "players.json"
GUILD_ID = None 

STAT_BAR = {
    "A": "[A]", "B": "[B]", "C": "[C]",
    "D": "[D]", "E": "[E]", "Z": "[Z]"
}
STAT_UP = {"E": "D", "D": "C", "C": "B", "B": "A", "A": "Z"}

ITEM_ICONS = {
    "money": "💰", "regular_arrow": "🏹", "requiem_arrow": "✨",
    "overheaven_arrow": "⚡", "crystal": "💎", "rokakaka": "🍈",
    "common_crate": "📦", "rare_crate": "🟦", "epic_crate": "🟣",
    "legendary_crate": "🌟", "stone_mask": "🎭",
}

CRATE_CONFIG = {
    "common":    {"name": "Common Crate",    "icon": "📦", "color": 0x95a5a6, "money_min": 100,  "money_max": 300,  "regular_arrow_chance": 20.0, "requiem_arrow_chance": 0.1,  "stone_mask_chance": 0.0, "rokakaka_chance": 0.0},
    "rare":      {"name": "Rare Crate",      "icon": "🟦", "color": 0x3498db, "money_min": 300,  "money_max": 700,  "regular_arrow_chance": 35.0, "requiem_arrow_chance": 0.3,  "stone_mask_chance": 0.0, "rokakaka_chance": 0.0},
    "epic":      {"name": "Epic Crate",      "icon": "🟣", "color": 0x9b59b6, "money_min": 700,  "money_max": 1500, "regular_arrow_chance": 49.0, "requiem_arrow_chance": 0.5,  "stone_mask_chance": 0.0, "rokakaka_chance": 5.0},
    "legendary": {"name": "Legendary Crate", "icon": "🌟", "color": 0xf1c40f, "money_min": 1500, "money_max": 3000, "regular_arrow_chance": 70.0, "requiem_arrow_chance": 1.5,  "stone_mask_chance": 1.5, "rokakaka_chance": 9.0},
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
    ("продавал еду весь день",                   100,  250, 90, "easy"),
    ("доставлял посылки",                         120,  280, 85, "easy"),
    ("чистил улицы Morioh",                        80,  200, 95, "easy"),
    ("помогал в мастерской",                      100,  300, 85, "easy"),
    ("охранял склад ночью",                       250,  500, 70, "medium"),
    ("работал на стройке",                        300,  550, 65, "medium"),
    ("помогал в ресторане Trattoria Trussardi",   350,  600, 70, "medium"),
    ("работал вышибалой в баре",                  280,  520, 65, "medium"),
    ("нашёл работу в Passione",                   500, 1000, 50, "hard"),
    ("выполнял задание от Speedwagon Foundation", 600, 1200, 45, "hard"),
    ("охотился на пользователя стенда",           700, 1500, 40, "hard"),
    ("работал на DIO",                            800, 1800, 35, "hard"),
]
JOB_FAIL = [
    "Тебя поймали — пришлось сбежать!", "Босс уволил тебя за лень...",
    "Ты провалил задание!", "Не повезло — работу перехватил кто-то другой.",
    "Вражеский стенд помешал тебе!", "Клиент отказался платить!",
    "Полиция разогнала всех — ты ничего не заработал.",
]
JOBS_REQUIRED = 3

SHOP_ITEMS = {
    "arrow":   {"name": "Regular Arrow", "icon": "🏹", "price": 500,  "type": "regular_arrow"},
    "crystal": {"name": "Crystal",       "icon": "💎", "price": 800,  "type": "crystal"},
    "common":  {"name": "Common Crate",  "icon": "📦", "price": 1000, "type": "common_crate"},
    "rare":    {"name": "Rare Crate",    "icon": "🟦", "price": 2500, "type": "rare_crate"},
}

QUESTS = [
    {"id": "worker",     "name": "Работяга",    "desc": "Выполни 5 работ",          "type": "jobs_done_total", "goal": 5,    "reward": {"crystals": 3},           "reward_text": "💎 3 кристалла"},
    {"id": "searcher",   "name": "Искатель",    "desc": "Используй /search 3 раза", "type": "searches_done",  "goal": 3,    "reward": {"money": 500},            "reward_text": "💰 $500"},
    {"id": "collector",  "name": "Коллекционер","desc": "Выполни 10 работ",         "type": "jobs_done_total", "goal": 10,   "reward": {"crystals": 8},           "reward_text": "💎 8 кристаллов"},
    {"id": "lucky",      "name": "Удача",       "desc": "Открой 3 любых кейса",     "type": "crates_opened",  "goal": 3,    "reward": {"money": 1500},           "reward_text": "💰 $1500"},
    {"id": "rich",       "name": "Богач",       "desc": "Накопи $3000",             "type": "money_reach",    "goal": 3000, "reward": {"crates": {"common": 2}}, "reward_text": "📦 2 Common Crate"},
    {"id": "shooter",    "name": "Стрелок",     "desc": "Используй стрелу 3 раза", "type": "arrows_used",    "goal": 3,    "reward": {"crystals": 5, "money": 1000}, "reward_text": "💎 5 + 💰 $1000"},
    {"id": "epic_hunter","name": "Охотник",     "desc": "Открой 1 Epic кейс",       "type": "epic_opened",    "goal": 1,    "reward": {"crystals": 15},          "reward_text": "💎 15 кристаллов"},
]

# ─── DATABASE ─────────────────────────────────────────────────────
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

# ─── STAND OBJECT ─────────────────────────────────────────────────
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

# ─── HELPERS ──────────────────────────────────────────────────────
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
    embed.add_field(name=f"Ability {'⭐'*atier}", value=ability_text, inline=False)

    if stand.get("ability2"):
        embed.add_field(name="Ability 2", value=stand["ability2"], inline=False)
    if player and player.get("is_vampire"):
        embed.add_field(name="🧛 Vampire", value="Vampiric Freeze — замораживает врага при касании", inline=False)
    if player and player.get("sub_ability"):
        embed.add_field(name="🍈 Sub-Ability", value=player["sub_ability"], inline=False)
    if stand.get("evolves_to"):
        embed.add_field(name="⬆️ Evolves to", value=f"**{stand['evolves_to']}**", inline=False)
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

# ─── BOT SETUP ────────────────────────────────────────────────────
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

# ─── SLASH COMMANDS ───────────────────────────────────────────────

@tree.command(name="job", description="Работа — зарабатывай деньги (кд: 30 мин)")
async def job(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    now = datetime.utcnow()
    if player["last_job"]:
        last = datetime.fromisoformat(player["last_job"])
        diff = now - last
        if diff < timedelta(minutes=30):
            rem = timedelta(minutes=30) - diff
            await interaction.response.send_message(
                f"⏳ Подожди **{int(rem.total_seconds()//60)}м {int(rem.total_seconds()%60)}с** до следующей работы.",
                ephemeral=True
            ); return

    job_name, mn, mx, sc, diff = random.choice(JOBS)
    de = {"easy":"🟢","medium":"🟡","hard":"🔴"}
    dt = {"easy":"Лёгкая","medium":"Средняя","hard":"Сложная"}
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
        embed = discord.Embed(title="✅ Работа выполнена!", color=0x2ecc71)
        embed.add_field(name=f"{de[diff]} {dt[diff]}", value=f"Ты **{job_name}** и заработал **${earned}**!", inline=False)
        embed.add_field(name="💰 Баланс", value=f"**${player['money']:,}**", inline=True)
        embed.add_field(name="🔨 Jobs",   value=f"**{player['jobs_done']}/{JOBS_REQUIRED}**", inline=True)
        if bonus_crate:
            cfg = CRATE_CONFIG[bonus_crate]
            embed.add_field(name="🎁 Бонус!", value=f"{cfg['icon']} **{cfg['name']}** нашёл во время работы!", inline=False)
        if player["jobs_done"] >= JOBS_REQUIRED:
            embed.add_field(name="🔍 Search готов!", value="Используй `/search`!", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        save_db(db)
        embed = discord.Embed(title="❌ Работа провалена!", color=0xe74c3c)
        embed.add_field(name=f"{de[diff]} {dt[diff]}", value=f"**{job_name}**\n{random.choice(JOB_FAIL)}", inline=False)
        embed.add_field(name="🔨 Jobs", value=f"**{player['jobs_done']}/{JOBS_REQUIRED}**", inline=True)
        embed.set_footer(text="Провал не считается — попробуй через 30 мин")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="search", description="Найти кейс (нужно 3 выполненных работы)")
async def search(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    if player["jobs_done"] < JOBS_REQUIRED:
        await interaction.response.send_message(
            f"❌ Нужно ещё **{JOBS_REQUIRED-player['jobs_done']}** работ!\n🔨 **{player['jobs_done']}/{JOBS_REQUIRED}**",
            ephemeral=True
        ); return

    player["jobs_done"] = 0
    player["searches_done"] = player.get("searches_done",0) + 1
    crate_type = roll_crate_type()
    if not crate_type:
        save_db(db)
        await interaction.response.send_message(
            embed=discord.Embed(title="🔍 Поиск", description="Ничего не нашёл...", color=0x95a5a6),
            ephemeral=True
        ); return

    player["crates"][crate_type] += 1
    save_db(db)
    cfg = CRATE_CONFIG[crate_type]
    embed = discord.Embed(title="🔍 Находка!", description=f"Ты нашёл {cfg['icon']} **{cfg['name']}**!", color=cfg["color"])
    embed.set_footer(text="Используй /crate open")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="arrow", description="Использовать стрелу для получения стенда")
@app_commands.describe(arrow_type="Тип стрелы: regular, requiem, overheaven")
@app_commands.choices(arrow_type=[
    app_commands.Choice(name="regular",    value="regular"),
    app_commands.Choice(name="requiem",    value="requiem"),
    app_commands.Choice(name="overheaven", value="overheaven"),
])
async def arrow(interaction: discord.Interaction, arrow_type: str = "regular"):
    db = load_db(); player = get_player(db, interaction.user.id)
    if player["arrows"][arrow_type] <= 0:
        await interaction.response.send_message(
            f"❌ У тебя нет **{arrow_type}** стрелы! Купи в `/shop` или найди через `/search`.",
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
        new_embed.set_author(name=f"Новый стенд!")

        if len(storage) < 2:
            new_embed.set_footer(text=f"У тебя уже есть стенд. Нажми ✅ сменить | 📦 сохранить старый в storage")
            await interaction.response.send_message(embed=new_embed, ephemeral=True)
            msg = await interaction.original_response()
            await msg.add_reaction("✅")
            await msg.add_reaction("📦")

            def check(r, u): return u == interaction.user and str(r.emoji) in ["✅","📦"] and r.message.id == msg.id
            try:
                reaction, _ = await bot.wait_for("reaction_add", timeout=30.0, check=check)
                if str(reaction.emoji) == "📦":
                    storage.append(old_stand_obj)
                    player["storage"] = storage
                player["stand"] = stand_name
                player["ability_tier"] = 1
                player["is_vampire"] = False
                player["stand_stats"] = None
                player["sub_ability"] = None
                save_db(db)
                action = "сохранён в storage, стенд сменён" if str(reaction.emoji) == "📦" else "сменён"
                await msg.edit(content=f"✅ Стенд {action}: **{stand_name}**!")
            except asyncio.TimeoutError:
                save_db(db)
                await msg.edit(content="❌ Время вышло — стенд не сменён.")
        else:
            new_embed.set_footer(text="У тебя уже есть стенд. Нажми ✅ чтобы сменить (storage полон)")
            await interaction.response.send_message(embed=new_embed, ephemeral=True)
            msg = await interaction.original_response()
            await msg.add_reaction("✅")
            def check(r, u): return u == interaction.user and str(r.emoji) == "✅" and r.message.id == msg.id
            try:
                await bot.wait_for("reaction_add", timeout=30.0, check=check)
                player["stand"] = stand_name
                player["ability_tier"] = 1
                player["is_vampire"] = False
                player["stand_stats"] = None
                player["sub_ability"] = None
                save_db(db)
                await msg.edit(content=f"✅ Стенд сменён на **{stand_name}**!")
            except asyncio.TimeoutError:
                save_db(db)
                await msg.edit(content="❌ Время вышло.")
        return

    player["stand"] = stand_name
    player["ability_tier"] = 1
    player["is_vampire"] = False
    player["stand_stats"] = None
    player["sub_ability"] = None
    save_db(db)
    embed = stand_embed(stand_name, player, interaction.user)
    embed.set_author(name=f"{interaction.user.display_name} получил стенд!")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="stand", description="Посмотреть свой стенд или стенд другого игрока")
@app_commands.describe(user="Игрок (необязательно)")
async def stand(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    db = load_db(); player = get_player(db, target.id)
    if not player["stand"]:
        await interaction.response.send_message(f"❌ У **{target.display_name}** нет стенда!", ephemeral=True); return
    embed = stand_embed(player["stand"], player, target)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="inv", description="Инвентарь")
@app_commands.describe(user="Игрок (необязательно)")
async def inv(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    db = load_db(); player = get_player(db, target.id)

    embed = discord.Embed(title=f"🎒 {target.display_name}", color=0x2c2f33)
    embed.add_field(name="🏹 Arrows", value=(
        f"🏹 **{player['arrows']['regular']}** Regular\n"
        f"✨ **{player['arrows']['requiem']}** Requiem\n"
        f"⚡ **{player['arrows']['overheaven']}** Overheaven"
    ), inline=True)
    embed.add_field(name="📦 Crates", value=(
        f"📦 **{player['crates']['common']}** Common\n"
        f"🟦 **{player['crates']['rare']}** Rare\n"
        f"🟣 **{player['crates']['epic']}** Epic\n"
        f"🌟 **{player['crates']['legendary']}** Legendary"
    ), inline=True)
    embed.add_field(name="💎 Other", value=(
        f"💎 **{player['crystals']}** Crystals\n"
        f"🍈 **{player['fruits']}** Rokakaka\n"
        f"🎭 **{player.get('stone_masks',0)}** Stone Mask"
    ), inline=True)

    stand_text = "None"
    if player["stand"]:
        sn = player["stand"]
        tier = STANDS[sn]["tier"]
        emoji = TIER_EMOJI.get(tier,"")
        vamp = " 🧛" if player.get("is_vampire") else ""
        stand_text = f"{emoji} **{sn}**{vamp}\nAbility Tier: {'⭐'*player['ability_tier']}"
        if can_evolve(sn):
            evo = get_evolution(sn)
            chance = EVOLVE_CHANCES.get(tier, 5.0)
            stand_text += f"\n⬆️ → **{evo}** ({chance}%)"

    embed.add_field(name="⚔️ Stand", value=stand_text, inline=False)

    storage = player.get("storage", [])
    if storage:
        storage_text = ""
        for i, s in enumerate(storage, 1):
            st = STANDS[s["name"]]["tier"]
            em = TIER_EMOJI.get(st,"")
            vamp = " 🧛" if s.get("is_vampire") else ""
            storage_text += f"{i}. {em} **{s['name']}**{vamp} (Tier {'⭐'*s.get('ability_tier',1)})\n"
        embed.add_field(name="🗄️ Storage", value=storage_text, inline=False)
    else:
        embed.add_field(name="🗄️ Storage", value="Пусто (макс. 2 стенда)", inline=False)

    embed.add_field(name="💰 Money", value=f"**${player['money']:,}**", inline=True)
    embed.add_field(name="🔨 Jobs",  value=f"**{player['jobs_done']}/{JOBS_REQUIRED}** для search", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="storage", description="Управление хранилищем стендов")
@app_commands.describe(action="store/swap/drop", slot="Слот 1 или 2 (для swap)")
@app_commands.choices(action=[
    app_commands.Choice(name="store — положить активный стенд", value="store"),
    app_commands.Choice(name="swap  — поменять с активным",     value="swap"),
    app_commands.Choice(name="drop  — выбросить активный стенд", value="drop"),
])
async def storage(interaction: discord.Interaction, action: str, slot: int = 1):
    db = load_db(); player = get_player(db, interaction.user.id)
    store = player.get("storage", [])

    # ── STORE ──
    if action == "store":
        if not player["stand"]:
            await interaction.response.send_message("❌ У тебя нет активного стенда!", ephemeral=True); return
        if len(store) >= 2:
            await interaction.response.send_message("❌ Storage полон (макс. 2 стенда)! Используй `/storage swap`.", ephemeral=True); return
        obj = get_active_stand_obj(player)
        store.append(obj)
        player["storage"] = store
        set_active_stand(player, None)
        save_db(db)
        await interaction.response.send_message(
            f"📦 **{obj['name']}** сохранён в storage (слот {len(store)}).",
            ephemeral=True
        ); return

    # ── SWAP ──
    if action == "swap":
        if not store:
            await interaction.response.send_message("❌ Storage пуст!", ephemeral=True); return
        idx = slot - 1
        if idx < 0 or idx >= len(store):
            await interaction.response.send_message(f"❌ Слот {slot} не существует. В storage {len(store)} стенд(а).", ephemeral=True); return

        stored_obj = store[idx]
        active_obj = get_active_stand_obj(player)

        # swap
        store[idx] = active_obj if active_obj else None
        if store[idx] is None:
            store.pop(idx)
        set_active_stand(player, stored_obj)
        player["storage"] = store
        save_db(db)

        embed = discord.Embed(title="🔄 Стенды поменяны!", color=0x3498db)
        embed.add_field(name="⚔️ Активный теперь", value=f"**{stored_obj['name']}**", inline=True)
        if active_obj:
            embed.add_field(name="📦 В storage теперь", value=f"**{active_obj['name']}**", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # ── DROP ──
    if action == "drop":
        if not player["stand"]:
            await interaction.response.send_message("❌ У тебя нет активного стенда!", ephemeral=True); return
        sn = player["stand"]
        await interaction.response.send_message(
            f"⚠️ Ты уверен что хочешь выбросить **{sn}**? Это действие необратимо!\nНажми ✅ для подтверждения.",
            ephemeral=True
        )
        msg = await interaction.original_response()
        await msg.add_reaction("✅")
        def check(r, u): return u == interaction.user and str(r.emoji) == "✅" and r.message.id == msg.id
        try:
            await bot.wait_for("reaction_add", timeout=20.0, check=check)
            set_active_stand(player, None)
            save_db(db)
            await msg.edit(content=f"🗑️ Стенд **{sn}** выброшен.")
        except asyncio.TimeoutError:
            await msg.edit(content="❌ Отменено.")


@tree.command(name="evolve", description="Эволюция стенда")
@app_commands.describe(evo_type="requiem (через Requiem Arrow) или vampire (через Stone Mask)")
@app_commands.choices(evo_type=[
    app_commands.Choice(name="requiem — эволюция через Requiem Arrow", value="requiem"),
    app_commands.Choice(name="vampire — вампир через Stone Mask",       value="vampire"),
])
async def evolve(interaction: discord.Interaction, evo_type: str = "requiem"):
    db = load_db(); player = get_player(db, interaction.user.id)
    if not player["stand"]:
        await interaction.response.send_message("❌ У тебя нет стенда!", ephemeral=True); return

    if evo_type == "vampire":
        if player.get("is_vampire"):
            await interaction.response.send_message("❌ Стенд уже является вампиром!", ephemeral=True); return
        if player.get("stone_masks", 0) <= 0:
            await interaction.response.send_message("❌ Нужна 🎭 **Stone Mask**! Выбивается из Legendary Crate (1.5%).", ephemeral=True); return

        player["stone_masks"] -= 1
        stand_name = player["stand"]
        base_stats = get_stand_stats(player, stand_name)
        all_z = all(v == "A" for v in base_stats.values())
        new_stats = {k: "Z" if all_z else STAT_UP.get(v, v) for k, v in base_stats.items()}
        player["stand_stats"] = new_stats
        player["is_vampire"] = True
        save_db(db)

        embed = discord.Embed(title="🧛 Vampire Evolution!", description=f"**{stand_name}** пронзён Каменной Маской!", color=0x8e0000)
        stats_text = "\n".join([f"{k.replace('_',' ').title()}: **{base_stats[k]}** → **{new_stats[k]}**" for k in new_stats])
        embed.add_field(name="📊 Изменение статов", value=stats_text, inline=False)
        embed.add_field(name="🧛 Новая способность", value="Vampiric Freeze — замораживает врага", inline=False)
        if all_z:
            embed.add_field(name="💀 GODLIKE", value="Все статы **Z**!", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # requiem
    stand_name = player["stand"]
    if not can_evolve(stand_name):
        await interaction.response.send_message(f"❌ **{stand_name}** не может эволюционировать через Requiem.", ephemeral=True); return
    if player["arrows"]["requiem"] <= 0:
        await interaction.response.send_message("❌ Нужна ✨ **Requiem Arrow**!", ephemeral=True); return

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
        embed.set_author(name=f"✨ {interaction.user.display_name} эволюционировал стенд!")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        save_db(db)
        embed = discord.Embed(
            title="💔 Эволюция провалилась!",
            description=f"**{stand_name}** не принял стрелу...\nШанс был **{chance}%**\nСтрела потрачена.",
            color=0xe74c3c
        )
        embed.add_field(name="⬆️ Цель",        value=f"**{evolution_name}**",              inline=True)
        embed.add_field(name="✨ Осталось",    value=f"**{player['arrows']['requiem']}**", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="upgrade", description="Прокачать способность стенда (Tier 1→2→3)")
async def upgrade(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    if not player["stand"]:
        await interaction.response.send_message("❌ У тебя нет стенда!", ephemeral=True); return

    stand_name = player["stand"]
    cur_tier   = player["ability_tier"]
    if cur_tier >= 3:
        await interaction.response.send_message("✅ Способность уже на максимуме (Tier 3)!", ephemeral=True); return

    next_tier = cur_tier + 1
    cost      = UPGRADE_COST[next_tier]
    upgrades  = ABILITY_UPGRADES.get(stand_name, {})
    current_ability = upgrades.get(cur_tier,  STANDS[stand_name]["ability"])
    next_ability    = upgrades.get(next_tier, STANDS[stand_name]["ability"])

    if player["crystals"] < cost["crystals"] or player["money"] < cost["money"]:
        await interaction.response.send_message(
            f"❌ Недостаточно ресурсов!\nНужно: 💎 **{cost['crystals']}** + 💰 **${cost['money']:,}**\nУ тебя: 💎 **{player['crystals']}** + 💰 **${player['money']:,}**",
            ephemeral=True
        ); return

    embed = discord.Embed(title=f"⬆️ Апгрейд — {stand_name}", color=TIER_COLORS.get(STANDS[stand_name]["tier"], 0xffffff))
    embed.add_field(name=f"{'⭐'*cur_tier} Сейчас", value=current_ability, inline=False)
    embed.add_field(name=f"{'⭐'*next_tier} После",  value=next_ability,   inline=False)
    embed.add_field(name="💰 Стоимость", value=f"💎 **{cost['crystals']}** + 💰 **${cost['money']:,}**", inline=False)
    embed.set_footer(text="Нажми ✅ для подтверждения")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    msg = await interaction.original_response()
    await msg.add_reaction("✅")

    def check(r, u): return u == interaction.user and str(r.emoji) == "✅" and r.message.id == msg.id
    try:
        await bot.wait_for("reaction_add", timeout=30.0, check=check)
        player["crystals"] -= cost["crystals"]
        player["money"]    -= cost["money"]
        player["ability_tier"] = next_tier
        save_db(db)
        await msg.edit(content=f"✅ Способность прокачана до Tier {next_tier}! {'⭐'*next_tier}\n{next_ability}")
    except asyncio.TimeoutError:
        await msg.edit(content="❌ Время вышло.")


@tree.command(name="rokakaka", description="Скрестить стенд с другим и украсть способность")
@app_commands.describe(stand_name="Название стенда для скрещивания")
async def rokakaka(interaction: discord.Interaction, stand_name: str):
    db = load_db(); player = get_player(db, interaction.user.id)
    if not player["stand"]:
        await interaction.response.send_message("❌ У тебя нет стенда!", ephemeral=True); return
    if player.get("fruits", 0) <= 0:
        await interaction.response.send_message("❌ Нет 🍈 Rokakaka! Дроп: 🟣 Epic 5% | 🌟 Legendary 9%", ephemeral=True); return

    target_stand = None
    for name in STANDS:
        if name.lower() == stand_name.lower():
            target_stand = name; break
    if not target_stand:
        matches = [n for n in STANDS if stand_name.lower() in n.lower()]
        if len(matches) == 1: target_stand = matches[0]
        elif len(matches) > 1:
            await interaction.response.send_message(f"❌ Несколько совпадений: {', '.join(matches[:5])}", ephemeral=True); return
        else:
            await interaction.response.send_message(f"❌ Стенд **{stand_name}** не найден.", ephemeral=True); return

    if target_stand == player["stand"]:
        await interaction.response.send_message("❌ Нельзя скрещивать с собой!", ephemeral=True); return

    target_data    = STANDS[target_stand]
    stolen_ability = target_data["ability"]
    is_evo         = not target_data.get("obtainable", True)
    chance         = 10.0 if is_evo else 40.0
    has_sub        = player.get("sub_ability") is not None

    embed = discord.Embed(title="🍈 Rokakaka — Скрещивание", color=0x2ecc71)
    embed.add_field(name="⚔️ Твой стенд", value=f"**{player['stand']}**",    inline=True)
    embed.add_field(name="🎯 Цель",        value=f"**{target_stand}**",        inline=True)
    embed.add_field(name="📊 Шанс",        value=f"**{chance}%**",             inline=True)
    embed.add_field(name="💫 Способность", value=stolen_ability,               inline=False)
    if has_sub:
        embed.add_field(name="⚠️ Замена", value=f"~~{player['sub_ability']}~~", inline=False)
    embed.set_footer(text="Нажми ✅ чтобы использовать Rokakaka")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    msg = await interaction.original_response()
    await msg.add_reaction("✅")

    def check(r, u): return u == interaction.user and str(r.emoji) == "✅" and r.message.id == msg.id
    try:
        await bot.wait_for("reaction_add", timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await msg.edit(content="❌ Время вышло."); return

    player["fruits"] -= 1
    if random.uniform(0, 100) < chance:
        player["sub_ability"] = stolen_ability
        save_db(db)
        await msg.edit(content=f"✅ Скрещивание успешно! **{player['stand']}** получил: {stolen_ability}")
    else:
        save_db(db)
        await msg.edit(content=f"💔 Провал! Шанс был {chance}%. Фрукт потрачен. Осталось: **{player['fruits']}** 🍈")


@tree.command(name="shop", description="Магазин — купить стрелы, кристаллы, кейсы")
@app_commands.describe(item="Что купить: arrow, crystal, common, rare")
@app_commands.choices(item=[
    app_commands.Choice(name="🏹 Regular Arrow — $500",  value="arrow"),
    app_commands.Choice(name="💎 Crystal — $800",        value="crystal"),
    app_commands.Choice(name="📦 Common Crate — $1000",  value="common"),
    app_commands.Choice(name="🟦 Rare Crate — $2500",   value="rare"),
])
async def shop(interaction: discord.Interaction, item: str = None):
    db = load_db(); player = get_player(db, interaction.user.id)

    if not item:
        embed = discord.Embed(title="🏪 JoJo Shop", color=0xe67e22)
        for key, d in SHOP_ITEMS.items():
            embed.add_field(name=f"{d['icon']} {d['name']}", value=f"💰 **${d['price']:,}**\n`/shop {key}`", inline=True)
        embed.add_field(name="⚠️ Не продаётся", value="✨ Requiem Arrow\n🍈 Rokakaka\n🟣 Epic / 🌟 Legendary Crate", inline=False)
        embed.set_footer(text=f"Твой баланс: ${player['money']:,}")
        await interaction.response.send_message(embed=embed, ephemeral=True); return

    d = SHOP_ITEMS[item]
    if player["money"] < d["price"]:
        await interaction.response.send_message(f"❌ Нужно 💰 **${d['price']:,}**, у тебя **${player['money']:,}**", ephemeral=True); return

    player["money"] -= d["price"]
    itype = d["type"]
    if itype == "regular_arrow":   player["arrows"]["regular"] += 1
    elif itype == "crystal":       player["crystals"] += 1
    elif itype == "common_crate":  player["crates"]["common"] += 1
    elif itype == "rare_crate":    player["crates"]["rare"] += 1
    save_db(db)

    await interaction.response.send_message(
        f"✅ Куплено: {d['icon']} **{d['name']}**!\n💰 Потрачено: **${d['price']:,}** | Баланс: **${player['money']:,}**",
        ephemeral=True
    )


@tree.command(name="crate", description="Открыть кейс или посмотреть содержимое")
@app_commands.describe(crate_type="Тип кейса: common, rare, epic, legendary")
@app_commands.choices(crate_type=[
    app_commands.Choice(name="📦 Common",    value="common"),
    app_commands.Choice(name="🟦 Rare",      value="rare"),
    app_commands.Choice(name="🟣 Epic",      value="epic"),
    app_commands.Choice(name="🌟 Legendary", value="legendary"),
])
async def crate(interaction: discord.Interaction, crate_type: str = None):
    db = load_db(); player = get_player(db, interaction.user.id)

    if not crate_type:
        embed = discord.Embed(title="📦 Твои кейсы", color=0x2c2f33)
        ct_text = "\n".join([f"{c['icon']} **{player['crates'].get(k,0)}** {c['name']}" for k,c in CRATE_CONFIG.items()])
        embed.add_field(name="Кейсы", value=ct_text, inline=False)
        ch_text = ""
        for k, c in CRATE_CONFIG.items():
            ch_text += f"{c['icon']} **{c['name']}**: 💰${c['money_min']}-${c['money_max']} | 🏹{c['regular_arrow_chance']}% | ✨{c['requiem_arrow_chance']}%"
            if c.get("stone_mask_chance",0) > 0: ch_text += f" | 🎭{c['stone_mask_chance']}%"
            if c.get("rokakaka_chance",0) > 0:   ch_text += f" | 🍈{c['rokakaka_chance']}%"
            ch_text += "\n"
        embed.add_field(name="📊 Шансы", value=ch_text, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True); return

    if player["crates"].get(crate_type, 0) <= 0:
        await interaction.response.send_message(f"❌ Нет **{CRATE_CONFIG[crate_type]['name']}**!", ephemeral=True); return

    player["crates"][crate_type] -= 1
    player["crates_opened"] = player.get("crates_opened",0) + 1
    if crate_type == "epic": player["epic_opened"] = player.get("epic_opened",0) + 1
    rewards = open_crate(crate_type)
    rewards_text = ""
    for r in rewards:
        if r["type"] == "money":
            player["money"] += r["amount"]; rewards_text += f"💰 **${r['amount']:,}**\n"
        elif r["type"] == "regular_arrow":
            player["arrows"]["regular"] += r["amount"]; rewards_text += f"🏹 **Regular Arrow** x{r['amount']}\n"
        elif r["type"] == "requiem_arrow":
            player["arrows"]["requiem"] += r["amount"]; rewards_text += f"✨ **Requiem Arrow** x{r['amount']} ⚠️ РЕДКИЙ!\n"
        elif r["type"] == "stone_mask":
            player["stone_masks"] = player.get("stone_masks",0) + r["amount"]; rewards_text += f"🎭 **Stone Mask** x{r['amount']} 💀 УЛЬТРА РЕДКИЙ!\n"
        elif r["type"] == "rokakaka":
            player["fruits"] = player.get("fruits",0) + r["amount"]; rewards_text += f"🍈 **Rokakaka** x{r['amount']} РЕДКИЙ!\n"
    save_db(db)

    cfg = CRATE_CONFIG[crate_type]
    embed = discord.Embed(title=f"{cfg['icon']} {cfg['name']}!", color=cfg["color"])
    embed.add_field(name="🎁 Награды", value=rewards_text, inline=False)
    embed.add_field(name="💰 Баланс",  value=f"**${player['money']:,}**", inline=True)
    embed.set_footer(text=f"Осталось {player['crates'][crate_type]} {cfg['name']}")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="money", description="Посмотреть баланс")
async def money(interaction: discord.Interaction):
    db = load_db(); player = get_player(db, interaction.user.id)
    embed = discord.Embed(title="💰 Balance", color=0xf1c40f)
    embed.add_field(name="Money", value=f"**${player['money']:,}**", inline=False)
    embed.set_footer(text=interaction.user.display_name)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="quest", description="Посмотреть квест или забрать награду")
@app_commands.describe(action="claim — забрать награду")
@app_commands.choices(action=[
    app_commands.Choice(name="show  — посмотреть прогресс", value="show"),
    app_commands.Choice(name="claim — забрать награду",     value="claim"),
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
            await interaction.response.send_message(f"❌ Квест не выполнен! **{min(progress,goal)}/{goal}**", ephemeral=True); return
        reward = quest_data["reward"]
        if "money"    in reward: player["money"]    += reward["money"]
        if "crystals" in reward: player["crystals"] += reward["crystals"]
        if "crates"   in reward:
            for ctype, amt in reward["crates"].items(): player["crates"][ctype] += amt
        assign_quest(player)
        new_quest = next(q for q in QUESTS if q["id"] == player["quest"])
        save_db(db)
        embed = discord.Embed(title=f"🎉 Квест выполнен: {quest_data['name']}!", color=0xf1c40f)
        embed.add_field(name="🎁 Награда",     value=quest_data["reward_text"],             inline=False)
        embed.add_field(name="📋 Новый квест", value=f"**{new_quest['name']}** — {new_quest['desc']}", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True); return

    bar_filled = int((min(progress,goal)/goal)*10)
    bar    = "█"*bar_filled + "░"*(10-bar_filled)
    status = "✅ ВЫПОЛНЕН — `/quest claim`!" if done else f"[{bar}] {min(progress,goal)}/{goal}"
    embed  = discord.Embed(title="📋 Текущий квест", color=0xf1c40f if done else 0x3498db)
    embed.add_field(name=f"🎯 {quest_data['name']}", value=quest_data["desc"],       inline=False)
    embed.add_field(name="📊 Прогресс",              value=status,                    inline=False)
    embed.add_field(name="🏆 Награда",               value=quest_data["reward_text"], inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="help", description="Список всех команд")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 JoJo Bot — Команды", color=0x9b59b6)
    embed.add_field(name="/job",              value="Работа (кд:30мин) 🟢🟡🔴", inline=False)
    embed.add_field(name="/search",           value=f"Найти кейс (нужно {JOBS_REQUIRED} работы)", inline=False)
    embed.add_field(name="/crate [тип]",      value="Открыть кейс", inline=False)
    embed.add_field(name="/arrow [тип]",      value="Использовать стрелу", inline=False)
    embed.add_field(name="/evolve [тип]",     value="Эволюция стенда (requiem/vampire)", inline=False)
    embed.add_field(name="/upgrade",          value="Прокачать способность (Tier 1→2→3)", inline=False)
    embed.add_field(name="/rokakaka [стенд]", value="Скрестить стенд (нужна 🍈 Rokakaka)", inline=False)
    embed.add_field(name="/storage [action]", value="Хранилище стендов (store/swap/drop)", inline=False)
    embed.add_field(name="/shop [предмет]",   value="Магазин", inline=False)
    embed.add_field(name="/quest [action]",   value="Квесты (show/claim)", inline=False)
    embed.add_field(name="/stand [@user]",    value="Посмотреть стенд", inline=False)
    embed.add_field(name="/inv [@user]",      value="Инвентарь", inline=False)
    embed.add_field(name="/money",            value="Баланс", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ─── RUN ──────────────────────────────────────────────────────────
bot.run(TOKEN)