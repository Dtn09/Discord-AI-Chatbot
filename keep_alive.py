"""
Keep-alive web server for Replit
This creates a simple web server that UptimeRobot can ping to keep the Repl alive
"""

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "Discord AI Chatbot"}

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Start the web server in a separate thread"""
    t = Thread(target=run)
    t.start()
