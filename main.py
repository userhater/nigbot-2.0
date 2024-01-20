import threading
import requests
import json
import time
import random
from datetime import datetime, timedelta
from os import system

with open("config.json", "r") as file:
    data = json.load(file)

TOKEN = data['token']
headers = {"authorization": TOKEN}

local = requests.get('https://discordapp.com/api/v6/users/@me', headers=headers).json()
commands = {}

def cls():
    system("cls")
    print(f'''
    ███╗░░██╗██╗░██████╗░██████╗░░█████╗░████████╗  ██████╗░░░░░█████╗░    ┃    
    ████╗░██║██║██╔════╝░██╔══██╗██╔══██╗╚══██╔══╝  ╚════██╗░░░██╔══██╗    ┃    
    ██╔██╗██║██║██║░░██╗░██████╦╝██║░░██║░░░██║░░░  ░░███╔═╝░░░██║░░██║    ┃    USERNAME: {local['username']}
    ██║╚████║██║██║░░╚██╗██╔══██╗██║░░██║░░░██║░░░  ██╔══╝░░░░░██║░░██║    ┃    RUN HELP FOR COMMAND LIST
    ██║░╚███║██║╚██████╔╝██████╦╝╚█████╔╝░░░██║░░░  ███████╗██╗╚█████╔╝    ┃    
    ╚═╝░░╚══╝╚═╝░╚═════╝░╚═════╝░░╚════╝░░░░╚═╝░░░  ╚══════╝╚═╝░╚════╝░    ┃    
''')

def command(func):
    command_name = func.__name__
    commands[command_name] = func
    return func

def execute_command(command_name, *args):
    if command_name in commands:
        command_thread = threading.Thread(target=commands[command_name], args=args)
        command_thread.start()
    else:
        print(f"Unknown command: {command_name}")

def send(channelid, content):
    return requests.post(
        url=f"https://discord.com/api/v9/channels/{channelid}/messages",
        headers=headers,
        data={
            "content":content
        }
    )

def round_to_nearest_hour(dt):
    return (dt + timedelta(minutes=30)).replace(second=0, microsecond=0, minute=0)

def createevent(guild_id, description, location, name):
    start_time = round_to_nearest_hour(datetime.utcnow()) + timedelta(hours=2)
    end_time = start_time + timedelta(hours=2)
    return requests.post(
        f"https://discord.com/api/v9/guilds/{guild_id}/scheduled-events",
        headers=headers,
        json={
            "name": name,
            "description": description,
            "scheduled_start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "scheduled_end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "entity_metadata": {"location": location},
        }
    )

def change_status(status, text):
    return requests.patch("https://canary.discordapp.com/api/v6/users/@me/settings", headers=headers, json={
        'status': status,
        "custom_status": {"text": text}
    })

def create_gc(owner_id, target_id):
    r = requests.post("https://discord.com/api/v10/users/@me/channels", headers=headers, json={"recipients": [f"{owner_id}", f"{target_id}"]})
    return r

def rename_gc(guild_id, name):
    data = {'name': name}
    r = requests.patch(f"https://discord.com/api/v9/channels/{guild_id}", headers=headers, json=data)
    return r

def delete_gc(guild_id):
    r = requests.delete(f"https://discord.com/api/v9/channels/{guild_id}?silent=true", headers=headers)
    return r

@command
def gcspam(userid: int, count: int):
    rename = input("What rename GC?:")
    delete = input("Delete GCs? (y/n):")
    
    for i in range(int(count)):
        try:
            create_result = create_gc(local['id'], userid)
            data = create_result.json()
            guild_id = data.get('id')
            if rename != "":
                rename_gc(guild_id, rename)
            if delete == "y":
                delete_gc(guild_id)
        except:
            print("Rate limited. Wait 5 minutes.")
            break

spamming = False
@command
def spam(channelid: int, *message: str):
    global spamming
    if not spamming:
        spamming = True
        print(f"Spamming started with message: '{message}'")
        msg = " ".join(message)
        
        while spamming:
            try:
                send(channelid, msg)
            except:
                spamming = False

espam = False
@command
def eventspam(guildid: int):
    name = input("name:")
    description = input("description:")
    location = input("location:")
    
    global espam
    if not espam:
        espam = True
        print(f"Event spamming started!")
        
        while espam:
            try:
                createevent(guildid, description, location, name)
            except:
                espam = False
                cls()
    else:
        print(f"Already event spamming.")

@command
def uneventspam():
    global espam
    espam = False

@command
def unspam():
    global spamming
    spamming = False

@command
def clear():
    cls()

@command
def color(col):
    cls()
    system(f"color {col}")

@command
def help():
    print('''
    + spam <channel_id> <message>
    + eventspam <guild_id>
    + gcspam <user_id> <count>
    + color <0-9 + a-f>
    + uneventspam
    + unspam
    + clear
    + help
    + discord
''')

@command
def discord():
    system("start https://discord.com/invite/mjAvsQcpWE")

cls()

statuses = data['bio']
ordered = data['ordered']
swap = data['statusswap']
def status_changer():
    while swap:
        if ordered:
            for i in statuses:
                change_status("online", i)
                time.sleep(6)
        else:
            change_status("online", random.choice(ordered))
            time.sleep(6)

status_thread = threading.Thread(target=status_changer)
status_thread.start()

while True:
    user_input = input("> ").strip()
    
    if user_input.lower() == "exit":
        break
    
    parts = user_input.split()
    command_name = parts[0]
    command_args = parts[1:]
    
    execute_command(command_name, *command_args)
