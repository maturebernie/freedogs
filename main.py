import os
import time
import random
import hashlib
import requests
from colorama import Fore, Style, init

import ssl 

import aiohttp
import aiocfscrape
import asyncio
from aiohttp_socks import ProxyConnector
import logging
import urllib.parse

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def art():
    print("\033[0m\n\033[1;96m ----------[ t.me/scriptsharing ]----------")

def countdown_timer(seconds):
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        print(f"{Fore.CYAN + Style.BRIGHT}Wait {hours:02}:{mins:02}:{secs:02}", end='\r')
        time.sleep(1)
        seconds -= 1
    print("Wait 00:00:00          ", end='\r')

def load_tokens(filename):
    with open(filename, 'r') as file:
        # Strip and URL-encode each line
        return [line.strip() for line in file if line.strip()]

def load_proxies(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def get_headers(token):
    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-ch-ua": "\"Chromium\";v=\"111\", \"Not(A:Brand\";v=\"8\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }

async def make_request(http_client, method, endpoint=None, url=None, **kwargs):
    response = await http_client.request(method, url or f"https://api.catshouse.club{endpoint or ''}", **kwargs)
    response.raise_for_status()
    return await response.json()

async def login(http_client, query, proxy=None):
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.freedogs.bot/miniapps/api/user/telegram_auth?inviteCode=&initData={encoded_query}"
    headers = get_headers("")
    body = {"initData": query, "inviteCode": ""}
    print(f"{random_color()}{Style.BRIGHT}Logging in with proxy: {url}  {body}")

    try:
        data = await make_request(http_client, 'POST', url=url, json=body)
        print(data)
        # response = requests.post(url, headers=headers, json=body, proxies=proxy, allow_redirects=True)
        # response.raise_for_status()
        # data = response.json()
        token = data.get("data").get("token")
        return token

    except requests.exceptions.RequestException as e:
        print(f"{random_color()}{Style.BRIGHT}Request failed: {e}{Style.RESET_ALL}")
        return None

async def data(http_client, token, proxy=None):
    url_1 = "https://api.freedogs.bot/miniapps/api/mine/getMineInfo?"
    url_2 = "https://api.freedogs.bot/miniapps/api/user_game_level/GetGameInfo?"
    http_client.headers["authorization"] = token

    try:
        # response_1 = requests.get(url_1, headers=headers, proxies=proxy, allow_redirects=True)
        # response_2 = requests.get(url_2, headers=headers, proxies=proxy, allow_redirects=True)
        data_1 = await make_request(http_client, 'GET', url=url_1)
        data_2 = await make_request(http_client, 'GET', url=url_2)
        # response_1.raise_for_status()
        # response_2.raise_for_status()
        
        # data_1 = response_1.json()
        # data_2 = response_2.json()
        
        balance = data_1.get("data").get("getCoin")
        collect_seq_no = data_2.get("data").get("collectSeqNo")
        
        print(f"{random_color()}{Style.BRIGHT}Balance: {balance}{Style.RESET_ALL}")
        
        return collect_seq_no

    except requests.exceptions.RequestException as e:
        print(f"{random_color()}{Style.BRIGHT}Request failed: {e}{Style.RESET_ALL}")
        return None

async def friends(http_client, token, proxy=None):
    url = f"https://api.freedogs.bot/miniapps/api/user_game/friends?page=1&pageSize=50"
    http_client.headers["authorization"] = token
    body = {"page": 1, "pageSize": 50}

    try:
        data = await make_request(http_client, 'POST', url=url, json=body)
        # response = requests.post(url, headers=headers, json=body, proxies=proxy, allow_redirects=True)
        # response.raise_for_status()
        # data = response.json()
        friends = data.get("data").get("count")
        print(f"{random_color()}{Style.BRIGHT}Total Friends: {friends}{Style.RESET_ALL}")

    except requests.exceptions.RequestException as e:
        print(f"{random_color()}{Style.BRIGHT}Request failed: {e}{Style.RESET_ALL}")
        return None

def generate_hash(collect_amount, collect_seq_no):
    static_string = "7be2a16a82054ee58398c5edb7ac4a5a"
    combined = str(collect_amount) + str(collect_seq_no) + static_string
    return hashlib.md5(combined.encode()).hexdigest()

async def collect_coins(http_client, token, collect_seq_no, total_collect, proxy=None):
    collect_amount = random.randint(60, 70)
    hash_code = generate_hash(collect_amount, collect_seq_no)
    
    url = f"https://api.freedogs.bot/miniapps/api/user_game/collectCoin?collectAmount={collect_amount}&hashCode={hash_code}&collectSeqNo={collect_seq_no}"
    
    http_client.headers["authorization"] = token

    try:
        # response = requests.post(url, headers=headers, proxies=proxy, allow_redirects=True)
        # response.raise_for_status()
        
        response_data = await make_request(http_client, 'POST', url=url)
        total_collect += collect_amount
        print(f"{random_color()}{Style.BRIGHT}Tapped: {collect_amount} | Total Tapped: {total_collect}/500{Style.RESET_ALL}")
        
        new_collect_seq_no = response_data.get("data", {}).get("collectSeqNo")
        if new_collect_seq_no:
            return new_collect_seq_no, total_collect
        
    except requests.exceptions.RequestException as e:
        print(f"{random_color()}{Style.BRIGHT}Request failed: {e}{Style.RESET_ALL}")
    
    return collect_seq_no, total_collect

async def tasks(http_client, token, proxy=None):
    url_task_list = "https://api.freedogs.bot/miniapps/api/task/lists?"
    task_complete_url = "https://api.freedogs.bot/miniapps/api/task/finish_task?id={task_id}"
    http_client.headers["authorization"] = token
    body = {"page": 1, "pageSize": 50}

    try:
        # response = requests.get(url_task_list, headers=headers, json=body, proxies=proxy, allow_redirects=True)
        # response.raise_for_status()
        

        data = await make_request(http_client, 'GET', url=url_task_list, json=body)
        # data = response.json()
        tasks = data.get("data", {}).get("lists", [])
        print(tasks)
        
        for task in tasks:
            task_id = task.get("id")
            name = task.get("name")
            is_finished = task.get("isFinish")
            print("finishing task...")

            if not is_finished:
                complete_url = task_complete_url.format(task_id=task_id)
                complete_body = {"id": task_id}
                time.sleep(10)
                # complete_response = requests.post(complete_url, headers=headers, json=complete_body, proxies=proxy)
                try:
                    complete_response = await make_request(http_client, 'POST', url=complete_url, json=complete_body)
                except Exception as e:
                    print("task failed") 
                # if complete_response.status_code == 200:
                #     print(f"{random_color()}{Style.BRIGHT}Task {name} completed successfully!{Style.RESET_ALL}")
                # else:
                #     print(f"{random_color()}{Style.BRIGHT}Failed to complete task '{name}'. Status code: {complete_response.status_code}{Style.RESET_ALL}")
            else:
                print(f"{random_color()}{Style.BRIGHT}Task '{name}' is already completed.{Style.RESET_ALL}")

    except requests.exceptions.RequestException as e:
        print(f"{random_color()}{Style.BRIGHT}Request failed: {e}{Style.RESET_ALL}")

def random_color():
    colors = [Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA]
    return random.choice(colors)

def check_proxy(proxy: dict):
    """Check if the SOCKS proxy is working by verifying the IP address."""
    test_url = 'https://api.ipify.org?format=json'
    try:
        # Send a request to the external IP-check service using the proxy
        response = requests.get(test_url, proxies=proxy, timeout=5)
        
        # Check if the request was successful
        if response.status_code == 200:
            ip_info = response.json()
            print(f"Proxy is working. IP returned: {ip_info.get('ip')}")
        else:
            print(f"Failed to connect through proxy. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while checking proxy: {e}")

async def main():
    clear_terminal()
    art()
    
    tokens = load_tokens('data.txt')
    proxies = load_proxies('proxy.txt') if os.path.exists('proxy.txt') else None
    total_accounts = len(tokens)
    use_proxy = 'y'
    run_task = 'y'
    
    clear_terminal()
    art()
    
    while True:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}Total Accounts: {total_accounts}{Style.RESET_ALL}\n")
        
        for i, query in enumerate(tokens, start=1):
            print(f"{Fore.CYAN}{Style.BRIGHT}------Account No.{i}------{Style.RESET_ALL}")
            proxy = proxies[i % len(proxies)]
            
            CIPHERS = [
                "ECDHE-ECDSA-AES128-GCM-SHA256", "ECDHE-RSA-AES128-GCM-SHA256",
                "ECDHE-ECDSA-AES256-GCM-SHA384", "ECDHE-RSA-AES256-GCM-SHA384",
                "ECDHE-ECDSA-CHACHA20-POLY1305", "ECDHE-RSA-CHACHA20-POLY1305",
                "ECDHE-RSA-AES128-SHA", "ECDHE-RSA-AES256-SHA",
                "AES128-GCM-SHA256", "AES256-GCM-SHA384", "AES128-SHA", "AES256-SHA", "DES-CBC3-SHA",
                "TLS_AES_128_GCM_SHA256", "TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256",
                "TLS_AES_128_CCM_SHA256", "TLS_AES_256_CCM_8_SHA256"
            ]
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ssl_context.set_ciphers(':'.join(CIPHERS))
            ssl_context.set_ecdh_curve("prime256v1")
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
            ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
            print("Proxy is " + proxy)


            proxy_conn = ProxyConnector().from_url(url=proxy, rdns=True, ssl=ssl_context)


            async with aiocfscrape.CloudflareScraper(headers=get_headers(""), connector=proxy_conn) as http_client:
                if proxy:
                    print("checking")
                    try:
                        response = await http_client.get(url='https://api.ipify.org?format=json', timeout=aiohttp.ClientTimeout(5))
                        ip = (await response.json()).get('ip')
                        print(f"Proxy IP: {ip}")
                    except Exception as error:
                        print(f"Proxy: {proxy} | Error: {error}")

                # token = await login(http_client, query, proxy)
                # print(token)
                # return None
 
                try:
                    
                    token = await login(http_client, query, proxy)
                    print(token)
                    if token:
                        print("login successful")

                        collect_seq_no = await data(http_client, token, proxy)
                        print(collect_seq_no)
                        await friends(http_client, token, proxy)
                        
                        # if run_task == 'y':
                        await tasks(http_client, token, proxy)
                        # return None
                        total_collect = 0
                        if collect_seq_no:
                            while total_collect < 500:
                                collect_seq_no, total_collect = await collect_coins(http_client, token, collect_seq_no, total_collect, proxy)
                                countdown_timer(60)
                            
                except Exception as e:
                    print(f"{random_color()}{Style.BRIGHT}Error processing account {i}: {e}{Style.RESET_ALL} - Waiting for next Account")
                    countdown_timer(random.randint(60, 70))
                    continue
            
            
        
        countdown_timer(random.randint(5 * 60* 60, 6 * 60* 60))
        clear_terminal()
        art()

if __name__ == "__main__":
    init()
    asyncio.run(main())