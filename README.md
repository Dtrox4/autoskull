# ☠️ Skull Bot

A Discord bot for skull-reacting users and managing authorization. Created using `discord.py`, deployed on Render.

## 🔧 Features

- `!skull <@user>`: Add skull to a user
- `!skull stop <@user>`: Remove skull from a user
- `!skull list`: View all skull-targets (with pagination)
- `!skull authorize <@user>`: Allow someone to use skull commands
- `!skull unauthorize <@user>`: Revoke permission
- `!skull authorized`: List of authorized users

## 🚀 Deploying to Render

1. Create a new Web Service on [Render](https://render.com)
2. Set your `start command` to: python main.py
3. Add your environment variable:
- `DISCORD_TOKEN` = `your-bot-token-here`

4. That's it! Your bot should be running.

## 📁 Project Structure
 
 ├── main.py 
 ├── skull_list.json 
 ├── authorized_users.json 
 ├── requirements.txt 
 ├── render.yaml (optional) 
 └── README.md

## ✅ To Run Locally

```bash
pip install -r requirements.txt
echo DISCORD_TOKEN=your_token > .env
python main.py

## NEED A WORKING VERSION?

ADD THIS TO YOUR SERVER! ITS FREE
https://discord.com/oauth2/authorize?client_id=1359483119186612435


