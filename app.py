from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("html/index.html")


@app.route('/loggedin')
def logged_in():
    return render_template("html/loggedin.html")


if __name__ == '__main__':
    app.run()
