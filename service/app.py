import flask


app = flask.Flask(__name__)


@app.route('/')
def index():
    return flask.jsonify({'status': 'alive'})


def main():
    app.run(host='0.0.0.0', port=80)


if __name__ == '__main__':
    main()
