import requests
import time
import logging
import re
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv


#==============配置区=============

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HTTP_PROXY = os.getenv("HTTP_PROXY")

proxies = {'http' : HTTP_PROXY,
           'https' : HTTP_PROXY}

headers = {'Authorization' : f'{DISCORD_TOKEN}',
           'User-Agent' :'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

logging.basicConfig(filename = 'script_logs', level = logging.ERROR, format = '%(asctime)s - %(message)s')

#==============================

while True:
    try:           
        response = requests.get('https://discord.com/api/v9/channels/1317547287827709992/messages' ,
                                headers = headers,
                                proxies = proxies,
                                timeout = 10)

        if response.status_code != 200:
            logging.error(f'请求失败，状态码：{response.status_code}')
            time.sleep(5)
            continue

        data = response.json()
        if not data:
            continue
        new_id = data[0]['id']

        try:
            with open('last_id.txt', 'r') as f:
                last_id = f.read().strip()

        except FileNotFoundError:
            last_id = ''


        if new_id != last_id:
            last_id = new_id
            with open('last_id.txt', 'w') as f:
                f.write(last_id)

            clean_text = re.sub(r'<:[^>]+>', '', data[0]['content'])

            utc_time = datetime.strptime(data[0]['timestamp'][:19], '%Y-%m-%dT%H:%M:%S')
            beijing_time = utc_time + timedelta(hours = 8)
            readable_time = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            
            complete_text = (f"✍️发信人: {data[0]['author']['global_name']}\n"
                            f"🕒发送时间: {readable_time}\n"
                            f"📝内容: {clean_text}")
                
        
            requests.post(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage', 
                        json = {'chat_id' : TELEGRAM_CHAT_ID, 'text' : complete_text},
                        proxies = proxies, 
                        timeout = 10)
    
    except Exception as e:
        logging.error(f'运行错误。错误原因:', exc_info = True)
        time.sleep(10)
        continue

    time.sleep(30)

