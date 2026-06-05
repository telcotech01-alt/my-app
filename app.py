from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>আমার লিংক</h1><a href="https://facebook.com">আমার Facebook পেজ</a>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)