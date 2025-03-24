from flask import Flask, request, jsonify
import re
from flask_cors import CORS
from typing import Dict, List, Any

app = Flask(__name__)
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

# 符号映射
SYMBOL_MAP = {
    'A': 'SYM0', 'B': 'SYM1', 'C': 'SYM2', 'D': 'SYM3', 'E': 'SYM4',
    'F': 'SYM5', 'G': 'SYM6', 'H': 'SYM7', 'I': 'SYM8', 'J': 'SYM9',
    'K': 'SYM10', 'L': 'SYM11', 'M': 'SYM12', 'N': 'SYM32', 'O': 'SYM33',
    'P': 'MINI', 'Q': 'MINOR', 'R': 'MAJOR', 'S': 'MEGA'
}

def replace_letters_with_sym(letters: List[str]) -> List[str]:
    try:
        return [SYMBOL_MAP.get(letter, letter) for letter in letters]
    except Exception as e:
        raise ValueError(f"Error in symbol replacement: {str(e)}")

def parse_string(input_str: str) -> List[Dict[str, Any]]:
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
                        letters[i].split(Constants.FIELD_SEPARATOR))

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
                "input": "1:A;B;C#D;E;F#G;H;I#J;K;L#R;M#N#MG;100#MV;10#MT;2"
            }
        }), 200

    try:
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({
                "error": "Missing 'input' field in request body"
            }), 400

        parsed_data = parse_string(data['input'])
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

if __name__ == '__main__':
    app.run(debug=True)
