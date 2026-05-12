import os
import json
import discord
from datetime import datetime, date
from discord import app_commands, Embed, Color

# ==================== BOT ====================

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ==================== CONFIG ====================

DAILY_FILE = "daily_counter.json"
ACCOUNTS_FILE = "accounts.txt"
INDEX_FILE = "account_index.json"
BOT_VERSION = "1.3"
DEVELOPER = "RealFitrex"
GROUP = "Zjednoczeni Ideą"

# ==================== TOKEN ====================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("❌ Brak DISCORD_TOKEN w Railway Variables!")

# ==================== DAILY SYSTEM ====================

def get_today_key():
    return date.today().isoformat()

def get_daily_data():
    if not os.path.exists(DAILY_FILE):
        return {"date": get_today_key(), "count": 0}
    try:
        with open(DAILY_FILE, "r") as f:
            data = json.load(f)
        if data.get("date") != get_today_key():
            return {"date": get_today_key(), "count": 0}
        return data
    except:
        return {"date": get_today_key(), "count": 0}

def save_daily_data(data):
    with open(DAILY_FILE, "w") as f:
        json.dump(data, f)

def load_daily_count_and_increment():
    data = get_daily_data()
    current_count = data["count"]
    new_count = current_count + 1
    data["count"] = new_count
    save_daily_data(data)
    return current_count, new_count

# ==================== ACCOUNT SYSTEM ====================

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    with open(ACCOUNTS_FILE, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    return lines

def get_current_index():
    if not os.path.exists(INDEX_FILE):
        return 0
    try:
        with open(INDEX_FILE, "r") as f:
            data = json.load(f)
        return data.get("index", 0)
    except:
        return 0

def save_current_index(index):
    with open(INDEX_FILE, "w") as f:
        json.dump({"index": index}, f)

def get_next_account():
    accounts = load_accounts()
    if not accounts:
        return None, 0, 0

    index = get_current_index()

    if index >= len(accounts):
        return None, index, len(accounts)

    account = accounts[index]
    save_current_index(index + 1)
    return account, index + 1, len(accounts)

# ==================== EVENTS ====================

@bot.event
async def on_ready():
    await tree.sync()
    await bot.change_presence(activity=discord.Game(name=f"/generate | v{BOT_VERSION}"))
    print(f"Developer: {DEVELOPER} | Grupa: {GROUP}")
    print(f"Bot Generator Multikow jest online!")

# ==================== COMMANDS ====================

@tree.command(name="generate", description="Pobiera konto z listy")
async def generate(interaction: discord.Interaction):
    account, used, total = get_next_account()

    if account is None and total == 0:
        embed = Embed(
            title="❌ Brak kont",
            description="Plik `accounts.txt` jest pusty lub nie istnieje.",
            color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if account is None:
        embed = Embed(
            title="❌ Brak kont",
            description=f"Wszystkie konta zostały rozdane! (`{total}/{total}`)",
            color=Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    current_count, new_count = load_daily_count_and_increment()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Parsuj username:haslo
    if ":" in account:
        parts = account.split(":", 1)
        username = parts[0]
        password = parts[1]
    else:
        username = account
        password = "brak"

    embed = Embed(
        title="🎰 Twoje Konto",
        color=Color.blurple()
    )
    embed.add_field(name="👤 Login", value=f"`{username}`", inline=False)
    embed.add_field(name="🔑 Hasło", value=f"`{password}`", inline=False)
    embed.add_field(name="📊 Kont pozostało", value=f"`{total - used}` z `{total}`", inline=True)
    embed.add_field(name="📅 Dziś wydano", value=f"`{new_count}` kont", inline=True)
    embed.set_footer(text=f"Bot v{BOT_VERSION} | {GROUP} | {timestamp}")

    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="stats", description="Pokazuje statystyki bota")
async def stats(interaction: discord.Interaction):
    data = get_daily_data()
    count = data["count"]
    accounts = load_accounts()
    index = get_current_index()
    remaining = max(0, len(accounts) - index)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    embed = Embed(
        title="📊 Statystyki Bota",
        color=Color.green()
    )
    embed.add_field(name="🤖 Wersja", value=f"`{BOT_VERSION}`", inline=True)
    embed.add_field(name="👨‍💻 Developer", value=f"`{DEVELOPER}`", inline=True)
    embed.add_field(name="🏢 Grupa", value=f"`{GROUP}`", inline=True)
    embed.add_field(name="📅 Wydano dziś", value=f"`{count}` kont", inline=False)
    embed.add_field(name="📦 Kont w stocku", value=f"`{remaining}` z `{len(accounts)}`", inline=False)
    embed.set_footer(text=f"Bot v{BOT_VERSION} | {timestamp}")

    await interaction.response.send_message(embed=embed)


@tree.command(name="help", description="Pokazuje liste komend")
async def help_command(interaction: discord.Interaction):
    embed = Embed(
        title="📖 Pomoc - Generator Multikow",
        description="Lista dostepnych komend:",
        color=Color.blue()
    )
    embed.add_field(name="/generate", value="Pobiera konto z listy (widoczne tylko dla ciebie)", inline=False)
    embed.add_field(name="/stats", value="Pokazuje statystyki i ile kont zostalo", inline=False)
    embed.add_field(name="/help", value="Pokazuje te wiadomosc", inline=False)
    embed.set_footer(text=f"Bot v{BOT_VERSION} | {GROUP} | Developer: {DEVELOPER}")

    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==================== RUN ====================

bot.run(TOKEN)

