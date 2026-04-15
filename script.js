let dictionary = [];
let possibleWords = [];
let currentWordLength = 0;
let guessedLetters = new Set();
let wrongGuesses = 0;
const TOTAL_PARTS = 19; // Total body parts available (0-18)
let maxErrors = 10;     // Configurable by user, min 6
let isAdversarial = true;
let godMode = false;
let gamesWon = 0;
let gamesPlayed = 0;
let regularWord = "";
let currentPattern = [];
let gameOver = false;

const modeToggle = document.getElementById('modeToggle');
const godToggle = document.getElementById('godToggle');
const guessesInput = document.getElementById('guessesInput');
const recordLabel = document.getElementById('recordLabel');
const btnRefresh = document.getElementById('btnRefreshBot');
const btnRestart = document.getElementById('btnRestart');
const keyboardContainer = document.getElementById('keyboard');
const wordDisplay = document.getElementById('wordDisplay');
const statusMessage = document.getElementById('statusMessage');
const toggleLabels = document.querySelectorAll('.toggle-label');

// Initialize Keyboard
function buildKeyboard() {
    keyboardContainer.innerHTML = '';
    'abcdefghijklmnopqrstuvwxyz'.split('').forEach(letter => {
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
    if (/^[a-z]$/.test(key)) handleGuess(key);
});

modeToggle.addEventListener('change', () => {
    updateToggleLabels();
    refreshGame();
});

godToggle.addEventListener('change', () => {
    godMode = godToggle.checked;
    toggleLabels[0].classList.toggle('active', godMode);
    checkGameEnd();
    updateUI();
});

guessesInput.addEventListener('change', () => {
    let val = parseInt(guessesInput.value);
    if (isNaN(val) || val < 6) val = 6;
    if (val > TOTAL_PARTS) val = TOTAL_PARTS;
    guessesInput.value = val;
    maxErrors = val;
    refreshGame();
});

btnRefresh.addEventListener('click', refreshGame);
btnRestart.addEventListener('click', initGame);

function refreshGame() {
    initGame();
}

function updateToggleLabels() {
    isAdversarial = modeToggle.checked;
    toggleLabels[1].classList.toggle('active', !isAdversarial);
    toggleLabels[2].classList.toggle('active', isAdversarial);
}

async function loadDictionary() {
    try {
        const response = await fetch('dict.txt');
        if (!response.ok) throw new Error("Could not load dict.txt");
        const text = await response.text();
        dictionary = text.split(/\r?\n/).map(w => w.trim().toLowerCase()).filter(w => /^[a-z]+$/.test(w));
    } catch (e) {
        console.warn("Using fallback dictionary:", e);
        dictionary = ['apple', 'banana', 'orange', 'grape', 'peach', 'lemon', 'melon',
                      'strawberry', 'blueberry', 'blackberry', 'kiwi', 'pineapple', 'watermelon'];
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
    maxErrors = Math.max(6, Math.min(TOTAL_PARTS, parseInt(guessesInput.value) || 10));

    btnRestart.style.display = 'none';
    btnRefresh.style.display = 'inline-block';

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
                pattern += currentPattern[i] !== '_' ? currentPattern[i]
                         : word[i] === letter       ? letter
                         : '_';
            }
            if (!groups[pattern]) groups[pattern] = [];
            groups[pattern].push(word);
        }

        const alpha = 1.5;
        const patterns = Object.keys(groups);
        const rawWeights = patterns.map(p => Math.pow(groups[p].length, alpha));
        const totalWeight = rawWeights.reduce((a, v) => a + v, 0);

        // Debug logging
        console.log(`--- Adversarial Selection (Alpha=${alpha}) ---`);
        patterns.forEach((p, i) => console.log(`Pattern: ${p} | Size: ${groups[p].length} | Prob: ${(rawWeights[i]/totalWeight*100).toFixed(2)}%`));

        let r = Math.random() * totalWeight;
        let cum = 0;
        let chosen = patterns[patterns.length - 1];
        for (let i = 0; i < patterns.length; i++) {
            cum += rawWeights[i];
            if (r <= cum) { chosen = patterns[i]; break; }
        }

        possibleWords = groups[chosen];
        for (let i = 0; i < currentWordLength; i++) {
            if (chosen[i] === letter) { hit = true; currentPattern[i] = letter; }
        }
    } else {
        for (let i = 0; i < currentWordLength; i++) {
            if (regularWord[i] === letter) { hit = true; currentPattern[i] = letter; }
        }
    }

    const keyBtn = document.getElementById(`key-${letter}`);
    if (keyBtn) {
        keyBtn.disabled = true;
        keyBtn.classList.add(hit ? 'correct' : 'incorrect');
    }
    if (!hit) wrongGuesses++;

    checkGameEnd();
    updateUI();
}

function checkGameEnd() {
    if (!currentPattern.includes('_') && !gameOver) {
        gameOver = true;
        gamesWon++;
        gamesPlayed++;
        statusMessage.textContent = "You Win! 🎉";
        statusMessage.className = "status-message status-win";
        btnRestart.style.display = 'inline-block';
        btnRefresh.style.display = 'none';
    } else if (wrongGuesses >= maxErrors && !godMode && !gameOver) {
        gameOver = true;
        gamesPlayed++;
        const answer = isAdversarial
            ? possibleWords[Math.floor(Math.random() * possibleWords.length)]
            : regularWord;
        statusMessage.textContent = `Game Over. The word was: ${answer}`;
        statusMessage.className = "status-message status-lose";
        btnRestart.style.display = 'inline-block';
        btnRefresh.style.display = 'none';

        // Reveal missed letters
        for (let i = 0; i < currentWordLength; i++) {
            if (currentPattern[i] === '_') {
                currentPattern[i] = `<span style="color:var(--error-color)">${answer[i]}</span>`;
            }
        }
    }
}

function updateUI() {
    recordLabel.textContent = `Record: ${gamesWon}/${gamesPlayed}`;

    // Word display
    wordDisplay.innerHTML = '';
    for (let i = 0; i < currentWordLength; i++) {
        const box = document.createElement('div');
        box.classList.add('letter-box');
        const char = currentPattern[i];
        if (char !== '_') {
            box.innerHTML = char;
            box.classList.add(char.includes('span') ? 'missed' : 'revealed');
        }
        wordDisplay.appendChild(box);
    }

    // Body parts — show part-N if wrongGuesses > N
    const isGodSaving = wrongGuesses >= maxErrors && godMode;
    const partColor = isGodSaving ? "#f59e0b" : "var(--error-color)";

    for (let i = 0; i < TOTAL_PARTS; i++) {
        document.querySelectorAll(`.part-${i}`).forEach(el => {
            const show = i < wrongGuesses;
            el.classList.toggle('hidden', !show);
            if (show) el.style.stroke = partColor;
            else el.style.stroke = 'var(--error-color)';
        });
    }

    // Halo
    const halo = document.querySelector('.part-halo');
    if (halo) halo.classList.toggle('hidden', !isGodSaving);

    if (gameOver) {
        document.querySelectorAll('.key').forEach(btn => btn.disabled = true);
    }
}

updateToggleLabels();
loadDictionary();
