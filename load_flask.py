def load_flask():
  @app.route('/')
def home():
    return "Bot is running!"

app = Flask(__name__)

if __name__ == '__main__':
    def run_flask():
        app.run(host='0.0.0.0', port=3000)

    Thread(target=run_flask).start()
