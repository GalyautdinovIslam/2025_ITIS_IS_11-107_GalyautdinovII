from flask import Flask, render_template, request

from demo.system import System

app = Flask(__name__)
system = System()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search_route():
    query = request.form['query']
    response = system.find(query)
    return render_template('results.html', query=query, results=response[:10])


if __name__ == '__main__':
    app.run(debug=True)
