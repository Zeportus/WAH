import json
from time import sleep
import requests
from random import randint
import db

def send_msg(userId, msg):
    data = {
        'chatId' : userId,
        'text' : msg,
        'session' : 'default'
    }

    response = requests.post('http://waha:3000/api/sendText', json= data)

    return response.json()

def start_spam(phones, msg, delay):
    for phone in phones:
        send_msg(phone + '@c.us', msg)
        sleep(delay + randint(1, 10) / 10)

def main(userId, userMsg, auto_info: list[list[str]]):
    userMsg = userMsg.lower()
    for info in auto_info:
        if info[0].lower() in userMsg:
            send_msg(userId, info[1])
            sleep(randint(5, 15) / 10)
        

    
