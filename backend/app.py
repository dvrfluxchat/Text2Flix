from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_request():
    return 'Hello, World!'

@app.route('/', methods=['POST'])
def post_request():
    data = request.get_json()
    # Process the data as needed
    # ...

    response = {'message': 'Data received successfully'}
    return jsonify(response)

if __name__ == '__main__':
    app.run()
