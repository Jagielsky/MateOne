from flask import Flask, jsonify, render_template, request
from engine import engine_response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

#Odebranie stanu planszy z frontendu
@app.route('/fen', methods=['POST'])
def fen():
    data = request.get_json()
    fen = data.get('fen')
    response = engine_response(fen)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)