import os
import json
import secrets
import random
import asyncio
import discord
from datetime import datetime, date
from discord import app_commands, Embed, Color

# ==================== BOT SETUP ====================

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ==================== CONFIG ====================

DAILY_FILE = "daily_counter.json"
BOT_VERSION = "1.2"
DEVELOPER = "RealFitrex"
GROUP = "Zjednoczone Idee"

# ==================== TOKEN FIX (RAILWAY SAFE) ====================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("❌ Brak DISCORD_TOKEN w Railway Variables!")

# ==================== FILE HELPERS ====================

def load_settings():
    with open('settings.json') as f:
        return json.load(f)

def load_proxies():
    if not os.path.exists('proxy.txt'):
        return []
    with open('proxy.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def get_today_key():
    return date.today().isoformat()

def get_daily_data():
    if not os.path.exists(DAILY_FILE):
        return {"date": get_today_key(), "count": 0}

    try:
        with open(DAILY_FILE, 'r') as f:
            data = json.load(f)

        if data
