from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

PORT = int(os.environ.get('PORT', 5000))
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# Railway provides DATABASE_URL automatically when you add PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')

# Fix Railway's postgres:// to postgresql:// for psycopg2
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def get_db_connection():
    if not DATABASE_URL:
        raise Exception('DATABASE_URL not set. Please add PostgreSQL in Railway Dashboard.')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def init_db():
    """Create tables and insert default data"""
    if not DATABASE_URL:
        print('WARNING: No DATABASE_URL. Add PostgreSQL in Railway Dashboard.')
        return

    conn = get_db_connection()
    cur = conn.cursor()

    # Create table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_data (
            key VARCHAR(50) PRIMARY KEY,
            data JSONB NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Default data
    defaults = {
        'questions': [],
        'stages': [
            {"id": 1, "title": "التدريب الأول", "description": "أسئلة سهلة لتبدأ رحلتك.", "difficultyLevels": [1], "questionsCount": 5, "passPercent": 60, "unlocked": True},
            {"id": 2, "title": "التحدي المتوسط", "description": "أسئلة متوسطة لتثبت معلوماتك.", "difficultyLevels": [2], "questionsCount": 5, "passPercent": 60, "unlocked": False},
            {"id": 3, "title": "المستوى المتقدم", "description": "أسئلة صعبة تتطلب تركيزاً.", "difficultyLevels": [3], "questionsCount": 5, "passPercent": 60, "unlocked": False},
            {"id": 4, "title": "خبير الفيزياء", "description": "أصعب الأسئلة، جاهز؟", "difficultyLevels": [4], "questionsCount": 5, "passPercent": 70, "unlocked": False}
        ],
        'leaderboard': [],
        'logo': {},
        'audio': {},
        'gamename': {'name': '⚡ مليون فيزياء ⚡'}
    }

    for key, data in defaults.items():
        cur.execute("""
            INSERT INTO game_data (key, data)
            VALUES (%s, %s)
            ON CONFLICT (key) DO NOTHING
        """, (key, json.dumps(data)))

    conn.commit()
    cur.close()
    conn.close()
    print('PostgreSQL database initialized!')

def db_load(key):
    if not DATABASE_URL:
        return None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT data FROM game_data WHERE key = %s", (key,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f'DB load error: {e}')
        return None

def db_save(key, data):
    if not DATABASE_URL:
        print(f'ERROR: No DATABASE_URL. Cannot save {key}.')
        return False
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO game_data (key, data, updated_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (key)
            DO UPDATE SET data = EXCLUDED.data, updated_at = CURRENT_TIMESTAMP
        """, (key, json.dumps(data)))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f'DB save error: {e}')
        return False

# Initialize
init_db()

# ========== API Routes ==========

@app.route('/api/questions', methods=['GET'])
def get_questions():
    data = db_load('questions')
    if data is None: data = []
    response = jsonify(data)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/api/questions', methods=['POST'])
def save_questions():
    data = request.get_json()
    success = db_save('questions', data)
    return jsonify({'success': success})

@app.route('/api/stages', methods=['GET'])
def get_stages():
    data = db_load('stages')
    if data is None:
        data = [
            {"id": 1, "title": "التدريب الأول", "description": "أسئلة سهلة لتبدأ رحلتك.", "difficultyLevels": [1], "questionsCount": 5, "passPercent": 60, "unlocked": True},
            {"id": 2, "title": "التحدي المتوسط", "description": "أسئلة متوسطة لتثبت معلوماتك.", "difficultyLevels": [2], "questionsCount": 5, "passPercent": 60, "unlocked": False},
            {"id": 3, "title": "المستوى المتقدم", "description": "أسئلة صعبة تتطلب تركيزاً.", "difficultyLevels": [3], "questionsCount": 5, "passPercent": 60, "unlocked": False},
            {"id": 4, "title": "خبير الفيزياء", "description": "أصعب الأسئلة، جاهز؟", "difficultyLevels": [4], "questionsCount": 5, "passPercent": 70, "unlocked": False}
        ]
    response = jsonify(data)
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/api/stages', methods=['POST'])
def save_stages():
    data = request.get_json()
    success = db_save('stages', data)
    return jsonify({'success': success})

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    data = db_load('leaderboard')
    if data is None: data = []
    response = jsonify(data)
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/api/leaderboard', methods=['POST'])
def save_leaderboard():
    data = request.get_json()
    success = db_save('leaderboard', data)
    return jsonify({'success': success})

@app.route('/api/logo', methods=['GET'])
def get_logo():
    data = db_load('logo')
    if data is None: data = {}
    return jsonify(data)

@app.route('/api/logo', methods=['POST'])
def save_logo():
    data = request.get_json()
    success = db_save('logo', data)
    return jsonify({'success': success})

@app.route('/api/audio', methods=['GET'])
def get_audio():
    data = db_load('audio')
    if data is None: data = {}
    return jsonify(data)

@app.route('/api/audio', methods=['POST'])
def save_audio():
    data = request.get_json()
    success = db_save('audio', data)
    return jsonify({'success': success})

@app.route('/api/gamename', methods=['GET'])
def get_gamename():
    data = db_load('gamename')
    if data is None: data = {'name': '⚡ مليون فيزياء ⚡'}
    return jsonify(data)

@app.route('/api/gamename', methods=['POST'])
def save_gamename():
    data = request.get_json()
    success = db_save('gamename', data)
    return jsonify({'success': success})

@app.route('/')
def index():
    return send_from_directory(DATA_DIR, 'physics_millionaire_game.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)