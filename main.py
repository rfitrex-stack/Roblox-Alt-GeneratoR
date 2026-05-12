import os
import json
import secrets
import asyncio
import discord
from discord import app_commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

def load_settings():
    with open('settings.json') as f:
        return json.load(f)

def generate_random_username():
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(10))

def generate_strong_password():
    return secrets.token_urlsafe(20)

def write_to_file(username, password):
    with open('accounts.txt', 'a', encoding='utf-8') as f:
        f.write(f"{username}:{password}\n")

async def create_roblox_account():
    settings = load_settings()
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

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://www.roblox.com/CreateAccount")

        # Czekamy na załadowanie dropdownów
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "MonthDropdown"))
        )

        Select(driver.find_element(By.ID, "MonthDropdown")).select_by_value("Jan")
        Select(driver.find_element(By.ID, "DayDropdown")).select_by_value("01")
        Select(driver.find_element(By.ID, "YearDropdown")).select_by_value("2000")

        driver.find_element(By.ID, "signup-username").send_keys(username)
        driver.find_element(By.ID, "signup-password").send_keys(password)

        driver.find_element(By.CLASS_NAME, "gender-male").click()

        signup_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "signup-button"))
        )
        signup_button.click()

        await asyncio.sleep(settings.get("delay", 3))

        write_to_file(username, password)
        return username, password, True

    except Exception as e:
        return username, password, f"Błąd: {str(e)}"
    finally:
        if driver:
            driver.quit()

@tree.command(name="generate", description="Wygeneruj 1 konto Roblox (edukacyjnie)")
async def generate(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send("🔄 Tworzę konto... (może potrwać 10-30s)")

    username, password, result = await create_roblox_account()

    if result is True:
        await interaction.followup.send(
            f"✅ **Konto utworzone!**\n"
            f"**Username:** `{username}`\n"
            f"**Password:** `{password}`\n\n"
            f"Konto zapisane w `accounts.txt`"
        )
    else:
        await interaction.followup.send(
            f"❌ Nie udało się utworzyć konta.\n"
            f"**Username:** `{username}`\n"
            f"**Błąd:** {result}"
        )

@tree.command(name="status", description="Sprawdź status bota")
async def status(interaction: discord.Interaction):
    await interaction.response.send_message("🟢 Bot działa! Użyj `/generate` aby stworzyć konto.")

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot zalogowany jako {bot.user}")

# Uruchomienie bota
bot.run(os.getenv("DISCORD_TOKEN"))
