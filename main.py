import os
import json
import secrets
import random
import asyncio
import discord
from datetime import datetime, date
from discord import app_commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

DAILY_FILE = "daily_counter.json"

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

def get_daily_count():
    if not os.path.exists(DAILY_FILE):
        return 0
    try:
        with open(DAILY_FILE, 'r') as f:
            data = json.load(f)
            if data.get("date") == get_today_key():
                return data.get("count", 0)
            else:
                return 0
    except:
        return 0

def save_daily_count(count):
    data = {
        "date": get_today_key(),
        "count": count
    }
    with open(DAILY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_daily_count_and_increment():
    current = get_daily_count()
    new_count = current + 1
    save_daily_count(new_count)
    return current, new_count

def get_random_proxy(proxies):
    return random.choice(proxies) if proxies else None

def generate_random_username():
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(10))

def generate_strong_password():
    return secrets.token_urlsafe(20)

def write_to_file(username, password, proxy_used="Brak"):
    with open('accounts.txt', 'a', encoding='utf-8') as f:
        f.write(f"{username}:{password} | Proxy: {proxy_used} | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

async def human_like_delay(min_sec=8, max_sec=20):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def create_roblox_account():
    settings = load_settings()
    proxies = load_proxies()
    proxy = get_random_proxy(proxies)

    username = generate_random_username()
    password = generate_strong_password()

    options = webdriver.ChromeOptions()
    if settings.get("headless", True):
        options.add_argument('--headless=new')
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--incognito')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://www.roblox.com/CreateAccount")
        
        await human_like_delay(3, 6)
        driver.execute_script("window.scrollBy(0, 300);")
        await human_like_delay(1, 3)

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "MonthDropdown")))

        Select(driver.find_element(By.ID, "MonthDropdown")).select_by_value("Jan")
        await human_like_delay(0.8, 1.8)
        Select(driver.find_element(By.ID, "DayDropdown")).select_by_value("01")
        await human_like_delay(0.8, 1.8)
        Select(driver.find_element(By.ID, "YearDropdown")).select_by_value("2000")
        await human_like_delay(1, 2.5)

        driver.find_element(By.ID, "signup-username").send_keys(username)
        await human_like_delay(1.2, 2.5)
        driver.find_element(By.ID, "signup-password").send_keys(password)
        await human_like_delay(1.2, 2.5)

        driver.find_element(By.CLASS_NAME, "gender-male").click()
        await human_like_delay(2, 4)

        signup_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "signup-button"))
        )
        ActionChains(driver).move_to_element(signup_button).perform()
        await human_like_delay(1.5, 3)
        signup_button.click()

        await human_like_delay(10, 18)

        write_to_file(username, password, proxy if proxy else "Brak")
        return username, password, proxy, True

    except Exception as e:
        return username, password, proxy, f"Błąd: {str(e)}"
    finally:
        if driver:
            driver.quit()

@tree.command(name="generate", description="Wygeneruj konto Roblox (max 2 dziennie)")
@app_commands.describe(amount="Ile kont (1-2)")
async def generate(interaction: discord.Interaction, amount: int = 1):
    settings = load_settings()
    amount = min(max(amount, 1), 2)   # twardy limit 2

    current_count, new_count = load_daily_count_and_increment()

    if current_count >= 2:
        await interaction.response.send_message("❌ **Osiągnięto dzienny limit (2 konta/dzień)**\nSpróbuj jutro.")
        return

    remaining = 2 - current_count
    if amount > remaining:
        amount = remaining

    await interaction.response.defer()
    await interaction.followup.send(f"🔄 Tworzę **{amount}** konto/a... (dzisiaj już {current_count}/2)")

    success = 0
    for i in range(amount):
        await interaction.followup.send(f"⏳ Tworzę konto {i+1}/{amount}...")

        username, password, proxy, result = await create_roblox_account()
        proxy_info = f"Proxy: {proxy}" if proxy else "Proxy: Brak"

        if result is True:
            success += 1
            await interaction.followup.send(
                f"✅ **Konto {i+1} gotowe!**\n"
                f"**User:** `{username}`\n"
                f"**Pass:** `{password}`\n"
                f"{proxy_info}"
            )
        else:
            await interaction.followup.send(f"❌ Konto {i+1} nieudane — {result}")

        if i < amount - 1:
            await asyncio.sleep(random.uniform(15, 30))

    await interaction.followup.send(f"**Zakończono!** Sukces: {success}/{amount} | Dzisiaj: {new_count}/2")

@tree.command(name="status", description="Status bota i limitu")
async def status(interaction: discord.Interaction):
    proxies = load_proxies()
    today_count = get_daily_count()
    await interaction.response.send_message(
        f"🟢 **Bot działa**\n"
        f"**Dzisiaj utworzono:** {today_count}/2 kont\n"
        f"**Załadowanych proxy:** {len(proxies)}\n"
        f"Użyj `/generate amount:1`"
    )

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot zalogowany jako {bot.user} | Dzienny limit: 2 konta")

bot.run(os.getenv("DISCORD_TOKEN"))
