from flask import Flask, request

app = Flask(__name__)

@app.route('/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    # Extract the incoming message data
    data = request.get_json()

    # Process the incoming message data
    # Here you can integrate with a WhatsApp API or service to handle the message

    # Return a response
    return 'Message received!', 200

if __name__ == '__main__':
    app.run(debug=True)
