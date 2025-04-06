from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def start_flask():
    Thread(target=lambda: app.run(host='0.0.0.0', port=3000)).start()
