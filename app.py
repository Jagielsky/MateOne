from flask import Flask, jsonify, render_template, request
from src.engine import engine_response, get_position_analysis

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fen', methods=['POST'])
def fen():
    data = request.get_json()
    fen = data.get('fen')
    depth = data.get('depth', 4)
    
    try:
        response = engine_response(fen, depth)
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'fen': fen,
            'error': f'Engine error: {str(e)}'
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    fen = data.get('fen')
    
    try:
        analysis = get_position_analysis(fen)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({
            'fen': fen,
            'error': f'Analysis error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)