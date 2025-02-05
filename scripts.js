const express = require('express');
const app = express();
app.use(express.json());

// 定义符号映射
const symMap = {
    'A': 'SYM0', 'B': 'SYM1', 'C': 'SYM2', 'D': 'SYM3', 'E': 'SYM4',
    'F': 'SYM5', 'G': 'SYM6', 'H': 'SYM7', 'I': 'SYM8', 'J': 'SYM9',
    'K': 'SYM10', 'L': 'SYM11', 'M': 'SYM12', 'N': 'SYM32', 'O': 'SYM33',
    'P': 'MINI', 'Q': 'MINOR', 'R': 'MAJOR', 'S': 'MEGA'
};

// 替换字母为符号的函数
function replaceLettersWithSym(letters) {
    return letters.map(letter => symMap[letter] || letter);
}

// 解析字符串的函数
function parseString(inputStr) {
    const result = [];
    const spins = inputStr.split(/(?=\d:)/).filter(spin => spin);

    for (const spin of spins) {
        const spinDict = {};
        const spinParts = spin.split(':', 2);
        if (spinParts.length < 2 || spinParts[1].trim() === '') {
            continue;
        }
        spinDict.SPIN = spinParts[0];
        const data = spinParts[1];
        const letters = data.split('#');

        if (letters.length >= 4) {
            spinDict['Row 1'] = replaceLettersWithSym(letters[0].split(';'));
            spinDict['Row 2'] = replaceLettersWithSym(letters[1].split(';'));
            spinDict['Row 3'] = replaceLettersWithSym(letters[2].split(';'));
            spinDict['Row 4'] = replaceLettersWithSym(letters[3].split(';'));
        }

        const remainingParts = data.split('#');
        const winningSyms = [];
        const winningPositions = [];
        spinDict['WIN AMOUNT'] = [];

        for (let i = 0; i < remainingParts.length; i++) {
            const part = remainingParts[i];
            if (part === 'R' && i + 1 < remainingParts.length) {
                winningSyms.push(remainingParts[i + 1]);
                if (i + 2 < remainingParts.length) {
                    winningPositions.push(remainingParts[i + 2]);
                }
            }
            if (part === 'MG' && i + 1 < remainingParts.length) {
                spinDict['WIN AMOUNT'].push(remainingParts[i + 1]);
            }
        }

        if (winningSyms.length === 0) {
            winningSyms.push('N/A');
            winningPositions.push('N/A');
        }

        spinDict['WINNING SYM'] = winningSyms.join(', ');
        spinDict['WINNING SYM Position'] = winningPositions.join(', ');

        for (let i = 0; i < remainingParts.length; i++) {
            const part = remainingParts[i];
            if (part === 'MV' && i + 1 < remainingParts.length) {
                spinDict.BET = remainingParts[i + 1];
            } else if (part === 'MT' && i + 1 < remainingParts.length) {
                spinDict.MULTIPLIER = remainingParts[i + 1];
            }
        }

        spinDict.BET = spinDict.BET || 'N/A';
        spinDict.MULTIPLIER = spinDict.MULTIPLIER || 'N/A';

        result.push(spinDict);
    }

    return result;
}

// 处理 /parse 路由
app.route('/parse')
  .get((req, res) => {
        res.status(200).send("This endpoint supports POST requests. Please send a POST request with data to parse.");
    })
  .post((req, res) => {
        const inputText = req.body.input;
        if (!inputText) {
            return res.status(400).json({ error: 'Input data is missing' });
        }
        try {
            const parsedData = parseString(inputText);
            res.json({ message: "Parsed successfully", data: parsedData });
        } catch (error) {
            res.status(500).json({ error: 'An error occurred during parsing' });
        }
    });

// 启动服务器
const port = 3000;
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
