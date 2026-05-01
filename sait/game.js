/* ================= CONFIG & CONSTANTS ================= */
const CONFIG = {
  canvasRatio: 4 / 3,
  colors: ['#f87171', '#fbbf24', '#34d399', '#60a5fa', '#a78bfa'],
  difficulties: {
    easy:   { ballSpeed: 240,  paddleScale: 1.4, blockHits: 1, bonusChance: 0.30, timerVisible: true },
    medium: { ballSpeed: 380,  paddleScale: 1.0, blockHits: 1, bonusChance: 0.15, timerVisible: true },
    hard:   { ballSpeed: 520,  paddleScale: 0.7, blockHits: 2, bonusChance: 0.08, timerVisible: false }
  },
  bonuses: ['wide', 'multi', 'slow'],
  namesRegex: /^[A-Za-zА-Яа-я0-9_ ]{2,15}$/,
  konamiCode: ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','KeyB','KeyA']
};

/* ================= STATE & UTILS ================= */
let state = {
  screen: 'MENU',
  diff: 'medium',
  score: 0,
  startTime: 0,
  elapsed: 0,
  level: 1,
  balls: [],
  paddle: { x: 0, y: 0, w: 0, h: 0, baseW: 0, targetW: 0 },
  blocks: [],
  fallingBonuses: [],
  particles: [],
  drag: { active: false, offsetX: 0 },
  keys: { left: false, right: false },
  tutorialSeen: false,
  slowEndTime: 0,
  konamiIndex: 0,
  easterEggActive: false
};

const $ = id => document.getElementById(id);
const formatTime = s => `${String(Math.floor(s/60)).padStart(2,'0')}:${String(Math.floor(s%60)).padStart(2,'0')}`;

/* ================= CANVAS SETUP ================= */
const canvas = $('gameCanvas');
const ctx = canvas.getContext('2d');
let W, H;

function resize() {
  const rect = canvas.parentElement.getBoundingClientRect();
  W = rect.width;
  H = rect.height;
  canvas.width = W;
  canvas.height = H;
  ctx.setTransform(1, 0, 0, 1, 0, 0);

  state.paddle.h = H * 0.02;
  state.paddle.y = H * 0.9;
  state.paddle.baseW = W * 0.15;
  applyDifficulty();
}
window.addEventListener('resize', resize);
resize();

/* ================= SOUND ================= */
const soundMap = {
  hitBlock:   'https://www.soundjay.com/misc/sounds/beep-07.mp3',
  hitPaddle:  'https://www.soundjay.com/misc/sounds/button-09.mp3',
  bonus:      'https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3',
  gameOver:   'https://www.soundjay.com/misc/sounds/fail-01.mp3',
  levelUp:    'https://www.soundjay.com/misc/sounds/success-01.mp3',
  bgMusic:    'https://www.soundjay.com/misc/sounds/ambient-01.mp3'
};

let sounds = {};
let bgMusic = null;

function initSounds() {
  for (let [key, url] of Object.entries(soundMap)) {
    if (key === 'bgMusic') {
      bgMusic = new Howl({ src: [url], loop: true, volume: 0.3 });
    } else {
      sounds[key] = new Howl({ src: [url], volume: 0.5 });
    }
  }
}

function playSound(name) {
  if (sounds[name] && state.screen === 'PLAYING') sounds[name].play();
}

/* ================= INPUT ================= */
function getPointerPos(e) {
  const rect = canvas.getBoundingClientRect();
  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  return Math.min(W, Math.max(0, (clientX - rect.left) * (W / rect.width)));
}

canvas.addEventListener('pointerdown', e => {
  if (state.screen !== 'PLAYING') return;
  const x = getPointerPos(e);
  if (x >= state.paddle.x && x <= state.paddle.x + state.paddle.w) {
    state.drag.active = true;
    state.drag.offsetX = x - state.paddle.x;
    canvas.setPointerCapture(e.pointerId);
  }
});

canvas.addEventListener('pointermove', e => {
  if (!state.drag.active) return;
  let x = getPointerPos(e) - state.drag.offsetX;
  state.paddle.x = Math.max(0, Math.min(W - state.paddle.w, x));
});

canvas.addEventListener('pointerup', () => state.drag.active = false);
canvas.addEventListener('pointercancel', () => state.drag.active = false);

window.addEventListener('keydown', e => {
  if (e.code === 'ArrowLeft' || e.code === 'KeyA') state.keys.left = true;
  if (e.code === 'ArrowRight' || e.code === 'KeyD') state.keys.right = true;

  // Konami code пасхалка
  if (state.konamiIndex < CONFIG.konamiCode.length && e.code === CONFIG.konamiCode[state.konamiIndex]) {
    state.konamiIndex++;
    if (state.konamiIndex === CONFIG.konamiCode.length) {
      state.easterEggActive = true;
      playSound('bonus');
      alert('🎉 Режим "Флаппи-шар" активирован! Шары теперь падают медленнее. 🎉');
      state.konamiIndex = 0;
    }
  } else {
    if (e.code !== CONFIG.konamiCode[state.konamiIndex]) state.konamiIndex = 0;
  }
});
window.addEventListener('keyup', e => {
  if (e.code === 'ArrowLeft' || e.code === 'KeyA') state.keys.left = false;
  if (e.code === 'ArrowRight' || e.code === 'KeyD') state.keys.right = false;
});

/* ================= GAME LOGIC ================= */
function applyDifficulty() {
  const d = CONFIG.difficulties[state.diff];
  state.paddle.w = state.paddle.baseW * d.paddleScale;
  state.paddle.targetW = state.paddle.w;
  state.paddle.x = (W - state.paddle.w) / 2;
  $('timer').style.display = d.timerVisible ? 'block' : 'none';
}

function generateLevel() {
  state.blocks = [];
  const d = CONFIG.difficulties[state.diff];
  const cols = Math.max(5, Math.min(10, Math.floor(W / (W * 0.09))));
  const rows = Math.min(8, 4 + Math.floor(state.level / 2));
  const bw = W * 0.08;
  const bh = H * 0.04;
  const gap = 4;
  const offsetX = (W - (cols * (bw + gap) - gap)) / 2;
  const offsetY = H * 0.12;

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (Math.random() < 0.12) continue;
      let hits = d.blockHits;
      if (state.diff === 'hard' && Math.random() < 0.25) hits++;
      if (state.level > 5 && r === rows-1 && Math.random() < 0.3) hits = 2;
      state.blocks.push({
        x: offsetX + c * (bw + gap),
        y: offsetY + r * (bh + gap),
        w: bw, h: bh,
        hits: hits,
        color: CONFIG.colors[(r + c) % CONFIG.colors.length],
        active: true
      });
    }
  }
}

function spawnBall(x, y, vx = null, vy = null) {
  const speed = CONFIG.difficulties[state.diff].ballSpeed;
  let angle = (Math.random() * Math.PI / 1.8) + Math.PI/3.6; // 50°-130°
  if (vx === null) {
    vx = Math.cos(angle) * speed;
    vy = -Math.sin(angle) * speed;
  }
  state.balls.push({
    x, y, vx, vy,
    r: W * 0.015,
    lastPaddleY: 0
  });
}

function update(dt) {
  if (state.screen !== 'PLAYING') return;
  if (dt > 0.03) dt = 0.03; // ограничим

  // ---- управление платформой ----
  const paddleSpeed = W * 6 * dt;
  if (state.keys.left) state.paddle.x = Math.max(0, state.paddle.x - paddleSpeed);
  if (state.keys.right) state.paddle.x = Math.min(W - state.paddle.w, state.paddle.x + paddleSpeed);
  state.paddle.w += (state.paddle.targetW - state.paddle.w) * 0.1 * (dt*60);
  state.paddle.x = Math.min(state.paddle.x, W - state.paddle.w);

  // ---- бонус slow ----
  if (state.slowEndTime && Date.now() > state.slowEndTime) {
    state.slowEndTime = 0;
    for (let b of state.balls) {
      b.vx *= 2;
      b.vy *= 2;
    }
  }

  // ---- таймер и очки ----
  state.elapsed = (Date.now() - state.startTime) / 1000;
  $('timer').textContent = formatTime(state.elapsed);
  $('score').textContent = state.score;
  $('level').textContent = state.level;

  // ---- обновление шаров ----
  for (let i = state.balls.length-1; i >= 0; i--) {
    const b = state.balls[i];
    b.x += b.vx * dt;
    b.y += b.vy * dt;

    // стены
    if (b.x - b.r < 0) { b.vx = Math.abs(b.vx); b.x = b.r; playSound('hitPaddle'); }
    if (b.x + b.r > W) { b.vx = -Math.abs(b.vx); b.x = W - b.r; playSound('hitPaddle'); }
    if (b.y - b.r < 0) { b.vy = Math.abs(b.vy); b.y = b.r; playSound('hitPaddle'); }

    if (b.y + b.r > H + 100) {
      state.balls.splice(i,1);
      if (state.balls.length === 0) gameOver();
      continue;
    }

    // платформа
    if (b.vy > 0 && b.y + b.r > state.paddle.y && b.y - b.r < state.paddle.y + state.paddle.h &&
        b.x + b.r > state.paddle.x && b.x - b.r < state.paddle.x + state.paddle.w) {
      const hitPos = (b.x - state.paddle.x) / state.paddle.w;
      const angle = Math.PI * (hitPos - 0.5) * 0.65;
      const speed = Math.hypot(b.vx, b.vy);
      b.vx = speed * Math.sin(angle);
      b.vy = -speed * Math.cos(angle);
      b.y = state.paddle.y - b.r;
      playSound('hitPaddle');
    }

    // блоки
    for (let j=0; j<state.blocks.length; j++) {
      const blk = state.blocks[j];
      if (!blk.active) continue;
      if (b.x + b.r > blk.x && b.x - b.r < blk.x + blk.w &&
          b.y + b.r > blk.y && b.y - b.r < blk.y + blk.h) {
        blk.hits--;
        if (blk.hits <= 0) {
          blk.active = false;
          state.score += 10;
          spawnParticles(blk.x + blk.w/2, blk.y + blk.h/2, blk.color);
          if (Math.random() < CONFIG.difficulties[state.diff].bonusChance)
            spawnFallingBonus(blk.x + blk.w/2, blk.y + blk.h);
          playSound('hitBlock');
        } else {
          state.score += 5;
          playSound('hitBlock');
        }
        const overlapX = (b.r + blk.w/2) - Math.abs(b.x - (blk.x + blk.w/2));
        const overlapY = (b.r + blk.h/2) - Math.abs(b.y - (blk.y + blk.h/2));
        if (overlapX < overlapY) b.vx *= -1;
        else b.vy *= -1;

        if (state.blocks.every(b => !b.active)) nextLevel();
        break;
      }
    }
  }

  // бонусы
  for (let i=0; i<state.fallingBonuses.length; i++) {
    const bn = state.fallingBonuses[i];
    bn.y += bn.vy * dt;
    if (bn.y + bn.h > state.paddle.y && bn.y < state.paddle.y + state.paddle.h &&
        bn.x + bn.w > state.paddle.x && bn.x < state.paddle.x + state.paddle.w) {
      applyBonus(bn.type);
      state.fallingBonuses.splice(i,1);
      i--;
    } else if (bn.y > H) {
      state.fallingBonuses.splice(i,1);
      i--;
    }
  }

  // частицы
  state.particles = state.particles.filter(p => p.life > 0);
  state.particles.forEach(p => { p.x += p.vx*dt; p.y += p.vy*dt; p.life -= p.decay*dt; });
}

function applyBonus(type) {
  playSound('bonus');
  if (type === 'wide') state.paddle.targetW = Math.min(W*0.45, state.paddle.targetW + W*0.05);
  if (type === 'slow') {
    if (!state.slowEndTime) {
      for (let b of state.balls) { b.vx *= 0.5; b.vy *= 0.5; }
      state.slowEndTime = Date.now() + 7000;
    }
  }
  if (type === 'multi') {
    if (state.balls.length > 0) {
      const b = state.balls[0];
      spawnBall(b.x, b.y, b.vx*0.9, b.vy*0.9);
      spawnBall(b.x, b.y, -b.vx*0.9, b.vy*0.9);
    }
  }
}

function spawnFallingBonus(x, y) {
  const type = CONFIG.bonuses[Math.floor(Math.random() * CONFIG.bonuses.length)];
  const colors = { wide: '#3b82f6', multi: '#f59e0b', slow: '#10b981' };
  state.fallingBonuses.push({ x: x-10, y, w: 20, h: 20, type, vy: 100, color: colors[type] });
}

function spawnParticles(x, y, color) {
  for (let i=0; i<10; i++) {
    state.particles.push({
      x, y, vx: (Math.random()-0.5)*120, vy: (Math.random()-0.5)*120,
      life: 0.8, decay: 2, color
    });
  }
}

/* ================= RENDER ================= */
function draw() {
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0,0,W,H);

  // блоки
  for (let blk of state.blocks) {
    if (!blk.active) continue;
    ctx.fillStyle = blk.color;
    ctx.fillRect(blk.x, blk.y, blk.w, blk.h);
    ctx.strokeStyle = 'rgba(0,0,0,0.3)';
    ctx.strokeRect(blk.x, blk.y, blk.w, blk.h);
    if (blk.hits > 1) {
      ctx.fillStyle = '#fff';
      ctx.font = `${blk.h*0.6}px monospace`;
      ctx.fillText(blk.hits, blk.x+blk.w/2-4, blk.y+blk.h/2+4);
    }
  }

  // бонусы
  for (let bn of state.fallingBonuses) {
    ctx.fillStyle = bn.color;
    ctx.fillRect(bn.x, bn.y, bn.w, bn.h);
    ctx.fillStyle = '#fff';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(bn.type==='wide'?'↔':bn.type==='multi'?'●●':'🐢', bn.x+bn.w/2, bn.y+14);
  }

  // платформа
  ctx.fillStyle = '#e2e8f0';
  ctx.fillRect(state.paddle.x, state.paddle.y, state.paddle.w, state.paddle.h);
  ctx.fillStyle = '#94a3b8';
  ctx.fillRect(state.paddle.x, state.paddle.y, state.paddle.w, 4);

  // шары
  for (let b of state.balls) {
    ctx.beginPath();
    ctx.arc(b.x, b.y, b.r, 0, Math.PI*2);
    ctx.fillStyle = state.easterEggActive ? '#ffd966' : '#f8fafc';
    ctx.fill();
    ctx.closePath();
  }

  // частицы
  for (let p of state.particles) {
    ctx.globalAlpha = p.life;
    ctx.fillStyle = p.color;
    ctx.fillRect(p.x-2, p.y-2, 4, 4);
  }
  ctx.globalAlpha = 1;
}

/* ================= GAME FLOW & LEADERBOARD ================= */
function loadLeaderboard() {
  const raw = localStorage.getItem('arkLeaderboard');
  if (!raw) return [];
  try {
    return JSON.parse(raw).slice(0,8);
  } catch(e) { return []; }
}

function saveScore(name, score) {
  let board = loadLeaderboard();
  board.push({ name, score, date: Date.now() });
  board.sort((a,b) => b.score - a.score);
  board = board.slice(0,8);
  localStorage.setItem('arkLeaderboard', JSON.stringify(board));
  renderLeaderboard();
}

function renderLeaderboard() {
  const container = $('leaderboardList');
  if (!container) return;
  const board = loadLeaderboard();
  container.innerHTML = board.map(entry => `<li>${escapeHtml(entry.name)} — ${entry.score} очков</li>`).join('');
  if (board.length === 0) container.innerHTML = '<li>— пока пусто —</li>';
}

function escapeHtml(str) {
  return str.replace(/[&<>]/g, function(m) {
    if (m === '&') return '&amp;';
    if (m === '<') return '&lt;';
    if (m === '>') return '&gt;';
    return m;
  });
}

function saveProgress() {
  if (state.screen === 'PLAYING') {
    localStorage.setItem('arkProgress', JSON.stringify({
      level: state.level,
      score: state.score,
      diff: state.diff,
      elapsed: state.elapsed
    }));
  }
}

function loadProgress() {
  const saved = localStorage.getItem('arkProgress');
  if (saved) {
    try {
      const p = JSON.parse(saved);
      if (confirm(`Найден сохранённый прогресс: уровень ${p.level}, очки ${p.score}. Загрузить?`)) {
        state.level = p.level;
        state.score = p.score;
        state.diff = p.diff;
        state.elapsed = p.elapsed;
        document.querySelector(`input[name="diff"][value="${p.diff}"]`).checked = true;
        $('playerName').value = localStorage.getItem('arkLastPlayer') || '';
        startGame(false); // false = не сбрасывать уровень/очки
        return true;
      }
    } catch(e) {}
  }
  return false;
}

function startGame(resetProgress = true) {
  state.diff = document.querySelector('input[name="diff"]:checked').value;
  const name = $('playerName').value.trim();
  if (!CONFIG.namesRegex.test(name)) {
    $('nameError').classList.remove('hidden');
    return false;
  }
  $('nameError').classList.add('hidden');
  localStorage.setItem('arkLastPlayer', name);

  if (resetProgress) {
    state.score = 0;
    state.level = 1;
    state.elapsed = 0;
  } else {
    // уже загружено из сохранения, только синхронизировать таймер
    state.startTime = Date.now() - state.elapsed * 1000;
  }
  state.startTime = Date.now() - state.elapsed * 1000;
  state.screen = 'PLAYING';
  state.balls = [];
  state.fallingBonuses = [];
  state.particles = [];
  state.slowEndTime = 0;
  state.easterEggActive = false;
  applyDifficulty();
  generateLevel();
  spawnBall(W/2, H*0.8);

  $('startScreen').classList.add('hidden');
  $('hud').classList.remove('hidden');
  $('endScreen').classList.add('hidden');
  if (bgMusic && !bgMusic.playing()) bgMusic.play();
  return true;
}

function nextLevel() {
  playSound('levelUp');
  state.level++;
  state.balls = [];
  generateLevel();
  spawnBall(W/2, H*0.8);
  saveProgress();
}

function gameOver() {
  playSound('gameOver');
  state.screen = 'END';
  $('endTitle').textContent = 'Игра окончена';
  $('finalScore').textContent = state.score;

  const playerName = $('playerName').value.trim();
  if (playerName && state.score > 0) {
    saveScore(playerName, state.score);
  }
  if (bgMusic) bgMusic.stop();

  $('hud').classList.add('hidden');
  $('endScreen').classList.remove('hidden');
  saveProgress(); // удалить прогресс или оставить? лучше удалить после завершения
  localStorage.removeItem('arkProgress');
}

/* ================= INIT & LOOP ================= */
// --- элементы UI ---
$('btnPlay').addEventListener('click', () => startGame(true));
$('btnTutorial').addEventListener('click', () => $('tutorialModal').classList.remove('hidden'));
$('btnCloseTutorial').addEventListener('click', () => $('tutorialModal').classList.add('hidden'));
$('btnRestart').addEventListener('click', () => {
  state.screen = 'MENU';
  $('endScreen').classList.add('hidden');
  $('startScreen').classList.remove('hidden');
  if (bgMusic) bgMusic.stop();
  renderLeaderboard();
});
document.querySelectorAll('input[name="diff"]').forEach(radio => {
  radio.addEventListener('change', () => applyDifficulty());
});

// добавим пасхалку на 1000 очков
setInterval(() => {
  if (state.screen === 'PLAYING' && state.score >= 1000 && !state.easterEggActive && !window._1000triggered) {
    window._1000triggered = true;
    state.easterEggActive = true;
    playSound('bonus');
    alert('✨ Пасхалка: 1000 очков! Все шары стали золотыми. ✨');
  }
}, 100);

let lastTime = 0;
function loop(now) {
  let dt = Math.min(0.033, (now - lastTime) / 1000);
  if (dt > 0) update(dt);
  draw();
  lastTime = now;
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

window.addEventListener('load', () => {
  resize();
  initSounds();
  renderLeaderboard();
  loadProgress(); // предложит загрузить сохранение
});
setInterval(saveProgress, 5000); // автосохранение каждые 5 секунд