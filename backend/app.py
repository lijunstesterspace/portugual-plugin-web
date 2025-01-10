from flask import Flask, request, jsonify
import re

app = Flask(__name__)


def replace_letters_with_sym(letters):
    sym_map = {
        'A': 'SYM0', 'B': 'SYM1', 'C': 'SYM2', 'D': 'SYM3', 'E': 'SYM4',
        'F': 'SYM5', 'G': 'SYM6', 'H': 'SYM7', 'I': 'SYM8', 'J': 'SYM9',
        'K': 'SYM10', 'L': 'SYM11', 'M': 'SYM12', 'N': 'SYM32', 'O': 'SYM33',
        'P': 'MINI', 'Q': 'MINOR', 'R': 'MAJOR', 'S': 'MEGA'
    }
    return [sym_map.get(letter, letter) for letter in letters]


def parse_string(input_str):
    result = []
    spins = re.split(r'(?=\d:)', input_str)
    for spin in spins:
        spin_dict = {}
        spin_parts = spin.split(':', 1)
        if len(spin_parts) < 2 or not spin_parts[1].strip():
            continue
        spin_dict['SPIN'] = spin_parts[0]
        data = spin_parts[1]
        letters = data.split('#')

        if len(letters) >= 4:
            spin_dict['Row 1'] = replace_letters_with_sym(
                letters[0].split(';'))
            spin_dict['Row 2'] = replace_letters_with_sym(
                letters[1].split(';'))
            spin_dict['Row 3'] = replace_letters_with_sym(
                letters[2].split(';'))
            spin_dict['Row 4'] = replace_letters_with_sym(
                letters[3].split(';'))

        remaining_parts = data.split('#')
        winning_syms, winning_positions = [], []
        spin_dict['WIN AMOUNT'] = []

        for i, part in enumerate(remaining_parts):
            if part == 'R' and i + 1 < len(remaining_parts):
                winning_syms.append(remaining_parts[i + 1])
                if i + 2 < len(remaining_parts):
                    winning_positions.append(remaining_parts[i + 2])

            if part == 'MG' and i + 1 < len(remaining_parts):
                spin_dict['WIN AMOUNT'].append(remaining_parts[i + 1])

        if not winning_syms:
            winning_syms.append('N/A')
            winning_positions.append('N/A')

        spin_dict['WINNING SYM'] = ', '.join(winning_syms)
        spin_dict['WINNING SYM Position'] = ', '.join(winning_positions)

        for i in range(len(remaining_parts)):
            part = remaining_parts[i]
            if part == 'MV' and i + 1 < len(remaining_parts):
                spin_dict['BET'] = remaining_parts[i + 1]
            elif part == 'MT' and i + 1 < len(remaining_parts):
                spin_dict['MULTIPLIER'] = remaining_parts[i + 1]

        spin_dict.setdefault('BET', 'N/A')
        spin_dict.setdefault('MULTIPLIER', 'N/A')

        result.append(spin_dict)

    return result


@app.route('/parse', methods=['GET', 'POST'])
def parse():
    if request.method == 'GET':
        return "This endpoint supports POST requests. Please send a POST request with data to parse.", 200

    # Handle POST requests
    data = request.json
    # Your parsing logic here
    return jsonify({"message": "Parsed successfully", "data": data})



if __name__ == '__main__':
    app.run(debug=True)
