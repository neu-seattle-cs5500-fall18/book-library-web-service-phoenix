from flask import Flask

app = Flask(__name__)


@app.route('/')
def start_service():
    return "Welcome to BookVector", 200


@app.route('/swagger')
def swagger_api():
    return


@app.route('/support')
def support():
    return "Please contact yu.jiah@husky.neu.edu; chen.xiany@husky.neu.edu", 200


if __name__ == '__main__':
    app.run(debug=True)
