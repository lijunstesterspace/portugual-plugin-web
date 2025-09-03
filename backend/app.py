from flask import Flask, request, jsonify, send_from_directory, redirect
import re
import os
import json
from flask_cors import CORS
from typing import Dict, List, Any

# 设置静态文件目录
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
app = Flask(__name__, static_folder=frontend_dir)
CORS(app)

# 常量定义
class Constants:
    SPIN_MARKER = ':'
    ROW_SEPARATOR = '#'
    FIELD_SEPARATOR = ';'
    WINNING_SYM_MARKER = 'R'
    WIN_AMOUNT_MARKER = 'MG'
    BET_MARKER = 'MV'
    MULTIPLIER_MARKER = 'MT'

# 游戏配置目录
GAMES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'games')

# 默认符号映射
DEFAULT_SYMBOL_MAP = {
    'A': 'SYM0', 'B': 'SYM1', 'C': 'SYM2', 'D': 'SYM3', 'E': 'SYM4',
    'F': 'SYM5', 'G': 'SYM6', 'H': 'SYM7', 'I': 'SYM8', 'J': 'SYM9',
    'K': 'SYM10', 'L': 'SYM11', 'M': 'SYM12', 'N': 'SYM32', 'O': 'SYM33',
    'P': 'MINI', 'Q': 'MINOR', 'R': 'MAJOR', 'S': 'MEGA'
}

# 加载所有游戏配置
def load_game_configs():
    games = {}
    try:
        for filename in os.listdir(GAMES_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(GAMES_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    game_config = json.load(f)
                    game_id = game_config.get('game_id')
                    if game_id:
                        games[game_id] = game_config
        return games
    except Exception as e:
        print(f"Error loading game configs: {str(e)}")
        return {}

# 获取指定游戏的符号映射
def get_symbol_map(game_id=None):
    if not game_id:
        return DEFAULT_SYMBOL_MAP
        
    games = load_game_configs()
    game_config = games.get(game_id)
    
    if game_config and 'letter_mapping' in game_config:
        return game_config['letter_mapping']
    return DEFAULT_SYMBOL_MAP

def replace_letters_with_sym(letters: List[str], game_id=None) -> List[str]:
    try:
        symbol_map = get_symbol_map(game_id)
        return [symbol_map.get(letter, letter) for letter in letters]
    except Exception as e:
        raise ValueError(f"Error in symbol replacement: {str(e)}")

def parse_string(input_str: str, game_id=None) -> List[Dict[str, Any]]:
    if not input_str or not isinstance(input_str, str):
        raise ValueError("Invalid input: Input must be a non-empty string")
        
    try:
        result = []
        spins = re.split(r'(?=\d:)', input_str)
        
        for spin in spins:
            spin_dict = {}
            spin_parts = spin.split(Constants.SPIN_MARKER, 1)
            
            if len(spin_parts) < 2 or not spin_parts[1].strip():
                continue
                
            spin_dict['SPIN'] = spin_parts[0]
            data = spin_parts[1]
            letters = data.split(Constants.ROW_SEPARATOR)

            if len(letters) >= 4:
                for i in range(4):
                    spin_dict[f'Row {i+1}'] = replace_letters_with_sym(
                        letters[i].split(Constants.FIELD_SEPARATOR), game_id)

            remaining_parts = data.split(Constants.ROW_SEPARATOR)
            winning_syms, winning_positions = [], []
            spin_dict['WIN AMOUNT'] = []

            for i, part in enumerate(remaining_parts):
                if part == Constants.WINNING_SYM_MARKER and i + 1 < len(remaining_parts):
                    winning_syms.append(remaining_parts[i + 1])
                    if i + 2 < len(remaining_parts):
                        winning_positions.append(remaining_parts[i + 2])

                if part == Constants.WIN_AMOUNT_MARKER and i + 1 < len(remaining_parts):
                    spin_dict['WIN AMOUNT'].append(remaining_parts[i + 1])

            if not winning_syms:
                winning_syms.append('N/A')
                winning_positions.append('N/A')

            spin_dict['WINNING SYM'] = ', '.join(winning_syms)
            spin_dict['WINNING SYM Position'] = ', '.join(winning_positions)

            for i in range(len(remaining_parts)):
                part = remaining_parts[i]
                if part == Constants.BET_MARKER and i + 1 < len(remaining_parts):
                    spin_dict['BET'] = remaining_parts[i + 1]
                elif part == Constants.MULTIPLIER_MARKER and i + 1 < len(remaining_parts):
                    spin_dict['MULTIPLIER'] = remaining_parts[i + 1]

            spin_dict.setdefault('BET', 'N/A')
            spin_dict.setdefault('MULTIPLIER', 'N/A')

            result.append(spin_dict)

        return result
    except Exception as e:
        raise ValueError(f"Error parsing string: {str(e)}")

@app.route('/parse', methods=['GET', 'POST'])
def parse():
    if request.method == 'GET':
        return jsonify({
            "message": "This endpoint supports POST requests. Please send a POST request with data to parse.",
            "example": {
                "input": "1:A;B;C#D;E;F#G;H;I#J;K;L#R;M#N#MG;100#MV;10#MT;2",
                "game_id": "DarkWater2"
            }
        }), 200

    try:
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({
                "error": "Missing 'input' field in request body"
            }), 400

        game_id = data.get('game_id')
        parsed_data = parse_string(data['input'], game_id)
        return jsonify({
            "message": "Parsed successfully",
            "data": parsed_data
        }), 200
    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/games', methods=['GET'])
def get_games():
    games = load_game_configs()
    game_list = []
    for game_id, game_config in games.items():
        game_list.append({
            'game_id': game_id,
            'game_name': game_config.get('game_name', game_id),
            'description': game_config.get('description', '')
        })
    return jsonify({
        "message": "Games loaded successfully",
        "data": game_list
    }), 200

@app.route('/games/<game_id>', methods=['GET'])
def get_game(game_id):
    games = load_game_configs()
    game_config = games.get(game_id)
    
    if not game_config:
        return jsonify({
            "error": f"Game with ID '{game_id}' not found"
        }), 404
        
    return jsonify({
        "message": "Game loaded successfully",
        "data": game_config
    }), 200

@app.route('/games/<game_id>', methods=['PUT'])
def update_game(game_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # 确保game_id一致
        data['game_id'] = game_id
        
        file_path = os.path.join(GAMES_DIR, f"{game_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return jsonify({
            "message": f"Game '{game_id}' updated successfully",
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/games', methods=['POST'])
def create_game():
    try:
        data = request.get_json()
        if not data or 'game_id' not in data:
            return jsonify({"error": "Missing game_id in request body"}), 400
            
        game_id = data['game_id']
        games = load_game_configs()
        
        if game_id in games:
            return jsonify({"error": f"Game with ID '{game_id}' already exists"}), 409
            
        file_path = os.path.join(GAMES_DIR, f"{game_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return jsonify({
            "message": f"Game '{game_id}' created successfully",
            "data": data
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/games/<game_id>', methods=['DELETE'])
def delete_game(game_id):
    try:
        file_path = os.path.join(GAMES_DIR, f"{game_id}.json")
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"Game with ID '{game_id}' not found"}), 404
            
        os.remove(file_path)
        return jsonify({"message": f"Game '{game_id}' deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 根路径处理
@app.route('/')
def index():
    return send_from_directory(frontend_dir, 'index.html')

# 处理静态文件
@app.route('/<path:path>')
def serve_static(path):
    if path == 'admin.html':
        return send_from_directory(frontend_dir, 'admin.html')
    elif path in ['style.css', 'script.js']:
        return send_from_directory(frontend_dir, path)
    else:
        return redirect('/')

if __name__ == '__main__':
    # 确保games目录存在
    if not os.path.exists(GAMES_DIR):
        os.makedirs(GAMES_DIR)
    app.run(debug=True)
