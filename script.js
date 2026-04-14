let dictionary = [];
let possibleWords = [];
let currentWordLength = 0;
let guessedLetters = new Set();
let wrongGuesses = 0;
const MAX_ERRORS = 6;
let isAdversarial = true; // Set adversarial as default
let godMode = false;
let gamesWon = 0;
let gamesPlayed = 0;
let regularWord = "";
let currentPattern = [];
let gameOver = false;

const modeToggle = document.getElementById('modeToggle');
const godToggle = document.getElementById('godToggle');
const recordLabel = document.getElementById('recordLabel');
const btnRefresh = document.getElementById('btnRefreshBot');

const keyboardContainer = document.getElementById('keyboard');
const wordDisplay = document.getElementById('wordDisplay');
const statusMessage = document.getElementById('statusMessage');
const btnRestart = document.getElementById('btnRestart');
const toggleLabels = document.querySelectorAll('.toggle-label');

// Initialize Keyboard
function buildKeyboard() {
    keyboardContainer.innerHTML = '';
    const letters = 'abcdefghijklmnopqrstuvwxyz'.split('');
    letters.forEach(letter => {
        const btn = document.createElement('button');
        btn.classList.add('key');
        btn.textContent = letter;
        btn.id = `key-${letter}`;
        btn.addEventListener('click', () => handleGuess(letter));
        keyboardContainer.appendChild(btn);
    });
}

// Physical keyboard listener
document.addEventListener('keydown', (e) => {
    if (gameOver) return;
    const key = e.key.toLowerCase();
    if (/^[a-z]$/.test(key)) {
        handleGuess(key);
    }
});

modeToggle.addEventListener('change', () => {
    updateToggleLabels();
    refreshGame();
});

godToggle.addEventListener('change', () => {
    godMode = godToggle.checked;
    if (godMode) {
        toggleLabels[0].classList.add('active'); // God Mode label
    } else {
        toggleLabels[0].classList.remove('active');
    }
    checkGameEnd();
    updateUI();
});

btnRefresh.addEventListener('click', refreshGame);
btnRestart.addEventListener('click', initGame);

function refreshGame() {
    initGame();
}

function updateToggleLabels() {
    isAdversarial = modeToggle.checked;
    if (isAdversarial) {
        toggleLabels[1].classList.remove('active'); // Regular
        toggleLabels[2].classList.add('active'); // Adversarial
    } else {
        toggleLabels[1].classList.add('active');
        toggleLabels[2].classList.remove('active');
    }
}

async function loadDictionary() {
    try {
        const response = await fetch('dict.txt');
        if (!response.ok) throw new Error("Could not load dict.txt");
        const text = await response.text();
        dictionary = text.split(/\r?\n/).map(w => w.trim().toLowerCase()).filter(w => /^[a-z]+$/.test(w));
    } catch (e) {
        console.warn("Using fallback dictionary: ", e);
        dictionary = ['apple', 'banana', 'orange', 'grape', 'peach', 'lemon', 'melon', 'strawberry', 'blueberry', 'blackberry', 'kiwi', 'pineapple', 'watermelon'];
    }
    initGame();
}

function initGame() {
    if (dictionary.length === 0) return;

    guessedLetters.clear();
    wrongGuesses = 0;
    gameOver = false;
    isAdversarial = modeToggle.checked;
    godMode = godToggle.checked;

    btnRestart.style.display = 'none'; // hide Next Word
    btnRefresh.style.display = 'inline-block'; // show refresh button

    const randomSeedWord = dictionary[Math.floor(Math.random() * dictionary.length)];
    currentWordLength = randomSeedWord.length;

    possibleWords = dictionary.filter(w => w.length === currentWordLength);

    if (!isAdversarial) {
        regularWord = possibleWords[Math.floor(Math.random() * possibleWords.length)];
    }

    currentPattern = Array(currentWordLength).fill('_');
    statusMessage.textContent = "Ready to play?";
    statusMessage.className = "status-message";

    buildKeyboard();
    updateUI();
}

function handleGuess(letter) {
    if (gameOver || guessedLetters.has(letter)) return;

    guessedLetters.add(letter);
    let hit = false;

    if (isAdversarial) {
        const groups = {};
        for (const word of possibleWords) {
            let pattern = '';
            for (let i = 0; i < currentWordLength; i++) {
                if (currentPattern[i] !== '_') {
                    pattern += currentPattern[i];
                } else if (word[i] === letter) {
                    pattern += letter;
                } else {
                    pattern += '_';
                }
            }
            if (!groups[pattern]) groups[pattern] = [];
            groups[pattern].push(word);
        }

        // Probabilistic adversarial selection
        const alpha = 1.5;
        const patterns = Object.keys(groups);
        const rawWeights = patterns.map(p => Math.pow(groups[p].length, alpha));
        const totalWeight = rawWeights.reduce((acc, val) => acc + val, 0);
        
        // Debug logging
        console.log(`--- Adversarial Selection (Alpha=${alpha}) ---`);
        patterns.forEach((p, index) => {
            const prob = (rawWeights[index] / totalWeight * 100).toFixed(2);
            console.log(`Pattern: ${p} | Size: ${groups[p].length} | Prob: ${prob}%`);
        });

        let r = Math.random() * totalWeight;
        let cumulativeWeight = 0;
        let chosenPatternStr = patterns[patterns.length - 1];
        
        for (let i = 0; i < patterns.length; i++) {
            cumulativeWeight += rawWeights[i];
            if (r <= cumulativeWeight) {
                chosenPatternStr = patterns[i];
                break;
            }
        }
        
        possibleWords = groups[chosenPatternStr];

        for (let i = 0; i < currentWordLength; i++) {
            if (chosenPatternStr[i] === letter) {
                hit = true;
                currentPattern[i] = letter;
            }
        }
    } else {
        for (let i = 0; i < currentWordLength; i++) {
            if (regularWord[i] === letter) {
                hit = true;
                currentPattern[i] = letter;
            }
        }
    }

    const keyBtn = document.getElementById(`key-${letter}`);
    if (keyBtn) {
        keyBtn.disabled = true;
        if (hit) {
            keyBtn.classList.add('correct');
        } else {
            keyBtn.classList.add('incorrect');
            wrongGuesses++;
        }
    } else if (!hit) {
        wrongGuesses++;
    }

    checkGameEnd();
    updateUI();
}

function checkGameEnd() {
    if (!currentPattern.includes('_') && !gameOver) {
        gameOver = true;
        gamesWon++;
        gamesPlayed++;
        statusMessage.textContent = "You Win!";
        statusMessage.className = "status-message status-win";
        btnRestart.style.display = 'inline-block';
        btnRefresh.style.display = 'none';
    } else if (wrongGuesses >= MAX_ERRORS && !godMode && !gameOver) {
        gameOver = true;
        gamesPlayed++;
        let answer = isAdversarial ? possibleWords[Math.floor(Math.random() * possibleWords.length)] : regularWord;
        statusMessage.textContent = `Game Over. Word was: ${answer}`;
        statusMessage.className = "status-message status-lose";
        btnRestart.style.display = 'inline-block';
        btnRefresh.style.display = 'none';

        for (let i = 0; i < currentWordLength; i++) {
            if (currentPattern[i] === '_') {
                currentPattern[i] = `<span style="color:var(--error-color)">${answer[i]}</span>`;
            }
        }
    }
}

function updateUI() {
    recordLabel.textContent = `Record: ${gamesWon}/${gamesPlayed}`;
    
    wordDisplay.innerHTML = '';
    for (let i = 0; i < currentWordLength; i++) {
        const box = document.createElement('div');
        box.classList.add('letter-box');

        const char = currentPattern[i];
        if (char !== '_') {
            box.innerHTML = char;
            if (typeof char === 'string' && !char.includes('span')) {
                box.classList.add('revealed');
            } else {
                box.classList.add('missed');
            }
        }
        wordDisplay.appendChild(box);
    }

    for (let i = 0; i <= MAX_ERRORS; i++) {
        const part = document.querySelector(`.part-${i}`);
        if (part) {
            if (i < wrongGuesses) {
                part.classList.remove('hidden');
                // Give it a gold stroke if saved by god mode
                if (wrongGuesses >= 6 && godMode) {
                    part.style.stroke = "#f59e0b";
                } else {
                    part.style.stroke = "var(--error-color)";
                }
            } else {
                part.classList.add('hidden');
                part.style.stroke = "var(--error-color)";
            }
        }
    }

    // Toggle Halo
    const halo = document.querySelector('.part-halo');
    if (halo) {
        if (wrongGuesses >= 6 && godMode) {
            halo.classList.remove('hidden');
        } else {
            halo.classList.add('hidden');
        }
    }

    if (gameOver) {
        document.querySelectorAll('.key').forEach(btn => {
            btn.disabled = true;
        });
    }
}

updateToggleLabels();
loadDictionary();
