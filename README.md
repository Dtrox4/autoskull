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
