import os
import json
import secrets
import random
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
BOT_VERSION = "1.2"
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

# ==================== GENERATORS ====================

def generate_password(length=16):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return "".join(secrets.choice(chars) for _ in range(length))

def generate_email():
    names = ["user", "player", "gamer", "pro", "dark", "light", "shadow", "storm", "fire", "ice"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "proton.me"]
    name = random.choice(names) + str(random.randint(100, 9999))
    domain = random.choice(domains)
    return f"{name}@{domain}"

def generate_username():
    prefixes = ["Dark", "Light", "Shadow", "Storm", "Fire", "Ice", "Night", "Swift", "Iron", "Gold"]
    suffixes = ["Wolf", "Eagle", "Tiger", "Dragon", "Hawk", "Fox", "Bear", "Lion", "Viper", "Ghost"]
    return random.choice(prefixes) + random.choice(suffixes) + str(random.randint(10, 999))

# ==================== EVENTS ====================

@bot.event
async def on_ready():
    await tree.sync()
    await bot.change_presence(activity=discord.Game(name=f"/generate | v{BOT_VERSION}"))
    print(f"Developer: {DEVELOPER} | Grupa: {GROUP}")
    print(f"Bot Generator Multikow jest online!")

# ==================== COMMANDS ====================

@tree.command(name="generate", description="Generuje losowe konto (email + haslo + login)")
async def generate(interaction: discord.Interaction):
    current_count, new_count = load_daily_count_and_increment()

    email = generate_email()
    password = generate_password()
    username = generate_username()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    embed = Embed(
        title="🎰 Wygenerowane Konto",
        color=Color.blurple()
    )
    embed.add_field(name="📧 Email", value=f"`{email}`", inline=False)
    embed.add_field(name="🔑 Haslo", value=f"`{password}`", inline=False)
    embed.add_field(name="👤 Login", value=f"`{username}`", inline=False)
    embed.add_field(name="📊 Dzisiaj wygenerowano", value=f"`{new_count}` kont", inline=True)
    embed.set_footer(text=f"Bot v{BOT_VERSION} | {GROUP} | {timestamp}")

    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="stats", description="Pokazuje statystyki bota")
async def stats(interaction: discord.Interaction):
    data = get_daily_data()
    count = data["count"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    embed = Embed(
        title="📊 Statystyki Bota",
        color=Color.green()
    )
    embed.add_field(name="🤖 Wersja", value=f"`{BOT_VERSION}`", inline=True)
    embed.add_field(name="👨‍💻 Developer", value=f"`{DEVELOPER}`", inline=True)
    embed.add_field(name="🏢 Grupa", value=f"`{GROUP}`", inline=True)
    embed.add_field(name="📅 Wygenerowano dzis", value=f"`{count}` kont", inline=False)
    embed.set_footer(text=f"Bot v{BOT_VERSION} | {timestamp}")

    await interaction.response.send_message(embed=embed)


@tree.command(name="help", description="Pokazuje liste komend")
async def help_command(interaction: discord.Interaction):
    embed = Embed(
        title="📖 Pomoc - Generator Multikow",
        description="Lista dostepnych komend:",
        color=Color.blue()
    )
    embed.add_field(name="/generate", value="Generuje losowe konto (widoczne tylko dla ciebie)", inline=False)
    embed.add_field(name="/stats", value="Pokazuje statystyki bota", inline=False)
    embed.add_field(name="/help", value="Pokazuje te wiadomosc", inline=False)
    embed.set_footer(text=f"Bot v{BOT_VERSION} | {GROUP} | Developer: {DEVELOPER}")

    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==================== RUN ====================

bot.run(TOKEN)

