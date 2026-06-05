from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>আমার লিংক</h1><a href="এখানে_তোমার_লিংক_বসাও">এখানে ক্লিক করো</a>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)