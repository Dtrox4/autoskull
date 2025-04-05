# keep_alive.py
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/health')
def home():
    return "I'm alive!", 200

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

bot.run("DISCORD_TOKEN")
