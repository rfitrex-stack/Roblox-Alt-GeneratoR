import os
import json
import secrets
import random
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

def load_proxies():
    if not os.path.exists('proxy.txt'):
        return []
    with open('proxy.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def get_random_proxy(proxies):
    return random.choice(proxies) if proxies else None

def generate_random_username():
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(10))

def generate_strong_password():
    return secrets.token_urlsafe(20)

def write_to_file(username, password, proxy_used="Brak"):
    with open('accounts.txt', 'a', encoding='utf-8') as f:
        f.write(f"{username}:{password} | Proxy: {proxy_used}\n")

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

        await asyncio.sleep(settings.get("delay", 4))

        write_to_file(username, password, proxy if proxy else "Brak")
        return username, password, proxy, True

    except Exception
