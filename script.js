let dictionary = [];
let possibleWords = [];
let currentWordLength = 0;
let guessedLetters = new Set();
let wrongGuesses = 0;
const TOTAL_PARTS = 26;
let maxErrors = 10;
let isAdversarial = true;
let godMode = false;
let gamesWon = 0;
let gamesPlayed = 0;
let regularWord = "";
let currentPattern = [];
let gameOver = false;

const modeToggle   = document.getElementById('modeToggle');
const godToggle    = document.getElementById('godToggle');
const guessesInput = document.getElementById('guessesInput');
const recordLabel  = document.getElementById('recordLabel');
const guessesLabel = document.getElementById('guessesLabel');
const btnRefresh   = document.getElementById('btnRefreshBot');
const btnRestart   = document.getElementById('btnRestart');
const keyboardEl   = document.getElementById('keyboard');
const wordDisplay  = document.getElementById('wordDisplay');
const statusMsg    = document.getElementById('statusMessage');
const toggleLabels = document.querySelectorAll('.toggle-label');

// ── Keyboard ──────────────────────────────────────────────────────────────────
function buildKeyboard() {
    keyboardEl.innerHTML = '';
    for (const letter of 'abcdefghijklmnopqrstuvwxyz') {
        const btn = document.createElement('button');
        btn.classList.add('key');
        btn.textContent = letter;
        btn.id = `key-${letter}`;
        btn.addEventListener('click', () => handleGuess(letter));
        keyboardEl.appendChild(btn);
    }
}

document.addEventListener('keydown', e => {
    if (gameOver) return;
    const k = e.key.toLowerCase();
    if (/^[a-z]$/.test(k)) handleGuess(k);
});

// ── Mode toggle (no full reset – mid-game switch is handled smartly) ──────────
modeToggle.addEventListener('change', () => {
    const wasAdversarial = isAdversarial;
    isAdversarial = modeToggle.checked;
    updateToggleLabels();

    if (guessedLetters.size === 0) {
        // No guesses yet – just flip mode; if switching to regular, commit a word now
        if (!isAdversarial) {
            regularWord = possibleWords[Math.floor(Math.random() * possibleWords.length)];
        }
        return; // No reset
    }

    // Mid-game switch
    if (!wasAdversarial && isAdversarial) {
        // Regular → Adversarial: recompute possibleWords from dictionary
        const revealed   = new Set(currentPattern.filter(c => c !== '_'));
        const wrongLetters = new Set([...guessedLetters].filter(l => !revealed.has(l)));
        possibleWords = dictionary.filter(w => {
            if (w.length !== currentWordLength) return false;
            for (let i = 0; i < currentWordLength; i++) {
                if (currentPattern[i] !== '_' && w[i] !== currentPattern[i]) return false;
            }
            for (const l of wrongLetters) { if (w.includes(l)) return false; }
            return true;
        });
    } else if (wasAdversarial && !isAdversarial) {
        // Adversarial → Regular: commit one word from the current possible set
        regularWord = possibleWords[Math.floor(Math.random() * possibleWords.length)];
    }
    // No game reset
});

// ── God toggle ────────────────────────────────────────────────────────────────
godToggle.addEventListener('change', () => {
    godMode = godToggle.checked;
    toggleLabels[0].classList.toggle('active', godMode);
    checkGameEnd();
    updateUI();
});

// ── Guesses input – lock after first guess ────────────────────────────────────
guessesInput.addEventListener('change', () => {
    if (guessedLetters.size > 0) {
        guessesInput.value = maxErrors; // revert
        return;
    }
    let val = Math.max(6, Math.min(TOTAL_PARTS, parseInt(guessesInput.value) || 10));
    guessesInput.value = val;
    maxErrors = val;
});

btnRefresh.addEventListener('click', refreshGame);
btnRestart.addEventListener('click', initGame);

function refreshGame() { initGame(); }

function updateToggleLabels() {
    isAdversarial = modeToggle.checked;
    toggleLabels[1].classList.toggle('active', !isAdversarial); // Regular
    toggleLabels[2].classList.toggle('active',  isAdversarial); // Adversarial
}

// ── Dictionary ────────────────────────────────────────────────────────────────
async function loadDictionary() {
    try {
        const r = await fetch('dict.txt');
        if (!r.ok) throw new Error();
        const text = await r.text();
        dictionary = text.split(/\r?\n/).map(w => w.trim().toLowerCase()).filter(w => /^[a-z]+$/.test(w));
    } catch {
        dictionary = ['apple','banana','orange','grape','peach','lemon','melon',
                      'strawberry','blueberry','blackberry','kiwi','pineapple','watermelon'];
    }
    initGame();
}

// ── Init / Reset ──────────────────────────────────────────────────────────────
function initGame() {
    if (!dictionary.length) return;

    guessedLetters.clear();
    wrongGuesses  = 0;
    gameOver      = false;
    isAdversarial = modeToggle.checked;
    godMode       = godToggle.checked;
    maxErrors     = Math.max(6, Math.min(TOTAL_PARTS, parseInt(guessesInput.value) || 10));

    // Reset guess label
    if (guessesLabel) guessesLabel.textContent = 'Guess Limit:';
    guessesInput.disabled      = false;
    guessesInput.style.opacity = '1';

    btnRestart.style.display = 'none';
    btnRefresh.style.display = 'inline-block';

    const seed = dictionary[Math.floor(Math.random() * dictionary.length)];
    currentWordLength = seed.length;
    possibleWords = dictionary.filter(w => w.length === currentWordLength);

    if (!isAdversarial) {
        regularWord = possibleWords[Math.floor(Math.random() * possibleWords.length)];
    }

    currentPattern = Array(currentWordLength).fill('_');
    statusMsg.textContent = 'Ready to play?';
    statusMsg.className   = 'status-message';

    buildKeyboard();
    updateUI();
}

// ── Guess logic ───────────────────────────────────────────────────────────────
function handleGuess(letter) {
    if (gameOver || guessedLetters.has(letter)) return;
    guessedLetters.add(letter);

    // Lock guess input after first letter — update label text
    if (guessedLetters.size === 1) {
        guessesInput.disabled      = true;
        guessesInput.style.opacity = '0.5';
        if (guessesLabel) guessesLabel.textContent = 'Guess Limit — locked mid-game (enable Always Win for more room):';
    }

    let hit = false;

    if (isAdversarial) {
        const groups = {};
        for (const word of possibleWords) {
            let pat = '';
            for (let i = 0; i < currentWordLength; i++) {
                pat += currentPattern[i] !== '_' ? currentPattern[i]
                     : word[i] === letter        ? letter
                     : '_';
            }
            (groups[pat] ??= []).push(word);
        }

        const alpha   = 1.5;
        const pats    = Object.keys(groups);
        const weights = pats.map(p => groups[p].length ** alpha);
        const total   = weights.reduce((a, v) => a + v, 0);

        console.log(`--- Adversarial (α=${alpha}) ---`);
        pats.forEach((p, i) => console.log(`${p} | n=${groups[p].length} | p=${(weights[i]/total*100).toFixed(1)}%`));

        let r = Math.random() * total, cum = 0, chosen = pats.at(-1);
        for (let i = 0; i < pats.length; i++) {
            cum += weights[i];
            if (r <= cum) { chosen = pats[i]; break; }
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

    const btn = document.getElementById(`key-${letter}`);
    if (btn) { btn.disabled = true; btn.classList.add(hit ? 'correct' : 'incorrect'); }
    if (!hit) wrongGuesses++;

    checkGameEnd();
    updateUI();
}

// ── End check ─────────────────────────────────────────────────────────────────
function checkGameEnd() {
    if (!currentPattern.includes('_') && !gameOver) {
        gameOver = true; gamesWon++; gamesPlayed++;
        statusMsg.textContent = 'You Win! 🎉';
        statusMsg.className   = 'status-message status-win';
        btnRestart.style.display = 'inline-block';
        btnRefresh.style.display = 'none';
    } else if (wrongGuesses >= maxErrors && !godMode && !gameOver) {
        gameOver = true; gamesPlayed++;
        const answer = isAdversarial
            ? possibleWords[Math.floor(Math.random() * possibleWords.length)]
            : regularWord;
        statusMsg.textContent = `Game Over. The word was: ${answer}`;
        statusMsg.className   = 'status-message status-lose';
        btnRestart.style.display = 'inline-block';
        btnRefresh.style.display = 'none';
        for (let i = 0; i < currentWordLength; i++) {
            if (currentPattern[i] === '_')
                currentPattern[i] = `<span style="color:var(--error-color)">${answer[i]}</span>`;
        }
    }
}

// ── UI ────────────────────────────────────────────────────────────────────────
function updateUI() {
    recordLabel.textContent = `Record: ${gamesWon}/${gamesPlayed}`;

    wordDisplay.innerHTML = '';
    for (let i = 0; i < currentWordLength; i++) {
        const box  = document.createElement('div');
        box.classList.add('letter-box');
        const char = currentPattern[i];
        if (char !== '_') {
            box.innerHTML = char;
            box.classList.add(char.includes('span') ? 'missed' : 'revealed');
        }
        wordDisplay.appendChild(box);
    }

    const godSaving  = wrongGuesses >= maxErrors && godMode;
    const partColor  = godSaving ? '#f59e0b' : 'var(--error-color)';

    for (let i = 0; i < TOTAL_PARTS; i++) {
        document.querySelectorAll(`.part-${i}`).forEach(el => {
            const show = i < wrongGuesses;
            el.classList.toggle('hidden', !show);
            el.style.stroke = show ? partColor : 'var(--error-color)';
        });
    }

    const halo = document.querySelector('.part-halo');
    if (halo) halo.classList.toggle('hidden', !godSaving);

    if (gameOver) document.querySelectorAll('.key').forEach(b => b.disabled = true);
}

updateToggleLabels();
loadDictionary();
