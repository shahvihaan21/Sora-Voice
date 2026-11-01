/**
 * Sora Voice — Interactive Web Preview Simulation Engine
 * Replicates PyQt AICore and AudioVisualizer rendering in HTML5 Canvas.
 */

class SoraPreviewController {
  constructor() {
    this.mode = 'IDLE';
    this.phase = 0;
    this.ringA = 0;
    this.ringB = 0;
    this.level = 0.12;
    this.targetLevel = 0.12;

    // DOM Elements
    this.statusBadge = document.getElementById('statusBadge');
    this.actionHint = document.getElementById('actionHint');
    this.stateLabel = document.getElementById('stateLabel');
    this.responseLabel = document.getElementById('responseLabel');
    this.chatDisplay = document.getElementById('chatDisplay');
    this.pillContainer = document.getElementById('pillContainer');
    this.cmdInput = document.getElementById('cmdInput');
    this.btnMic = document.getElementById('btnMic');
    this.btnSend = document.getElementById('btnSend');
    this.btnStop = document.getElementById('btnStop');
    this.btnError = document.getElementById('btnError');
    this.btnReset = document.getElementById('btnReset');

    // Canvas Contexts
    this.coreCtx = document.getElementById('coreCanvas').getContext('2d');
    this.waveCtx = document.getElementById('waveformCanvas').getContext('2d');

    // Random Particles for AI Core
    this.particles = Array.from({ length: 24 }, () => ({
      ang: Math.random() * Math.PI * 2,
      rad: 0.62 + Math.random() * 0.33,
      spd: 0.008 + Math.random() * 0.022,
      sz: 1.2 + Math.random() * 1.4
    }));

    this.initEvents();
    this.appendMessage('Sora', 'jarvis voice online - how may i assist you');
    this.animate();
  }

  setMode(mode, text) {
    this.mode = mode;
    const modeMap = {
      IDLE: { badge: 'ONLINE', hint: text || 'Ready', state: 'READY' },
      LISTENING: { badge: 'LISTENING', hint: text || 'Listening... speak now', state: 'LISTENING' },
      THINKING: { badge: 'THINKING', hint: text || 'Processing...', state: 'THINKING' },
      SPEAKING: { badge: 'SPEAKING', hint: text || 'Speaking...', state: 'SPEAKING' },
      ERROR: { badge: 'ERROR', hint: text || 'System error', state: 'SYSTEM ERROR' }
    };

    const config = modeMap[mode] || modeMap.IDLE;
    this.statusBadge.textContent = config.badge;
    this.statusBadge.setAttribute('data-mode', mode);
    this.actionHint.textContent = config.hint;
    this.stateLabel.textContent = config.state;
    this.pillContainer.setAttribute('data-mode', mode);

    if (mode === 'LISTENING') {
      this.btnMic.classList.add('active');
      this.btnMic.textContent = 'STOP';
    } else {
      this.btnMic.classList.remove('active');
      this.btnMic.textContent = 'MIC';
    }
  }

  initEvents() {
    this.btnMic.addEventListener('click', () => {
      if (this.mode === 'LISTENING') {
        this.setMode('IDLE', 'Stopped listening');
      } else {
        this.startSimulatedListening();
      }
    });

    this.btnSend.addEventListener('click', () => this.handleUserSubmit());
    this.cmdInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.handleUserSubmit();
    });

    this.btnStop.addEventListener('click', () => {
      this.setMode('IDLE', 'Stopped simulation');
    });

    this.btnError.addEventListener('click', () => {
      this.setMode('ERROR', 'Simulated connection failure');
      this.responseLabel.textContent = 'Error: Ollama server offline. Showing local fallback UI.';
    });

    this.btnReset.addEventListener('click', () => {
      this.chatDisplay.innerHTML = '';
      this.setMode('IDLE', 'Ready');
      this.responseLabel.textContent = 'How can I help?';
      this.appendMessage('Sora', 'jarvis voice online - conversation reset');
    });
  }

  startSimulatedListening() {
    this.setMode('LISTENING', 'Listening... speak now');
    setTimeout(() => {
      if (this.mode === 'LISTENING') {
        const sampleCommands = [
          'What time is it?',
          'Calculate 50 * 2',
          'What is the status of Jarvis?',
          'Who are you?'
        ];
        const cmd = sampleCommands[Math.floor(Math.random() * sampleCommands.length)];
        this.processCommand(cmd);
      }
    }, 2800);
  }

  handleUserSubmit() {
    const text = this.cmdInput.value.trim();
    if (!text) return;
    this.cmdInput.value = '';
    this.processCommand(text);
  }

  processCommand(cmd) {
    this.appendMessage('You', cmd);
    this.setMode('THINKING', 'Processing...');
    this.responseLabel.textContent = 'Thinking...';

    setTimeout(() => {
      if (this.mode !== 'THINKING') return;

      let reply = `I heard: '${cmd}'. Local browser preview mode is functional.`;
      const lower = cmd.toLowerCase();
      if (lower.includes('time')) {
        reply = `It is currently ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}.`;
      } else if (lower.includes('calculate') || lower.includes('*') || lower.includes('+')) {
        reply = 'The calculation result is 100.';
      } else if (lower.includes('who are you') || lower.includes('status')) {
        reply = 'I am Jarvis, your next-generation desktop AI assistant.';
      }

      this.setMode('SPEAKING', 'Speaking...');
      this.responseLabel.textContent = reply;
      this.appendMessage('Sora', reply);

      setTimeout(() => {
        if (this.mode === 'SPEAKING') {
          this.setMode('IDLE', 'Ready');
        }
      }, 3000);
    }, 1200);
  }

  appendMessage(sender, text) {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const isUser = sender.toLowerCase() === 'you';
    const div = document.createElement('div');
    div.className = `chat-msg ${isUser ? 'user' : 'sora'}`;
    div.innerHTML = `<span class="sender">[${sender}]</span><span class="time">${time}</span><br><span>${this.escapeHtml(text)}</span>`;
    this.chatDisplay.appendChild(div);
    this.chatDisplay.scrollTop = this.chatDisplay.scrollHeight;
  }

  escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  getColors() {
    const pal = {
      IDLE: ['#38bdf8', '#818cf8'],
      LISTENING: ['#22d3ee', '#38bdf8'],
      THINKING: ['#60a5fa', '#a78bfa'],
      SPEAKING: ['#a78bfa', '#22d3ee'],
      ERROR: ['#f87171', '#f87171']
    };
    return pal[this.mode] || pal.IDLE;
  }

  animate() {
    this.updateState();
    this.drawCore();
    this.drawWaveform();
    requestAnimationFrame(() => this.animate());
  }

  updateState() {
    const speeds = { IDLE: 0.02, LISTENING: 0.055, THINKING: 0.075, SPEAKING: 0.065, ERROR: 0.015 };
    const spd = speeds[this.mode] || 0.025;
    this.phase += spd;
    this.ringA += 0.012 + (this.mode === 'THINKING' ? 0.03 : 0);
    this.ringB -= 0.009 + (this.mode === 'THINKING' ? 0.02 : 0);

    const baseLevels = { IDLE: 0.12, LISTENING: 0.55, THINKING: 0.35, SPEAKING: 0.60, ERROR: 0.10 };
    const base = baseLevels[this.mode] || 0.15;
    this.targetLevel = base + 0.06 * Math.sin(this.phase * 1.7);
    this.level += (this.targetLevel - this.level) * 0.15;
  }

  drawCore() {
    const ctx = this.coreCtx;
    const w = 240, h = 240;
    ctx.clearRect(0, 0, w, h);

    const cx = w / 2, cy = h / 2, R = 100;
    const [c1, c2] = this.getColors();
    const br = 1.0 + 0.025 * Math.sin(this.phase * 1.6);
    const en = 1.0 + this.level * 0.14;

    // Background Glow
    const halo = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 1.05);
    halo.addColorStop(0, 'rgba(0,0,0,0)');
    halo.addColorStop(0.7, `${c1}11`);
    halo.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(cx, cy, R * 1.05, 0, Math.PI * 2);
    ctx.fill();

    // Layered Concentric Rings
    const rings = [
      { ang: this.ringA, fr: 0.98, alpha: '44', width: 1.2 },
      { ang: this.ringB, fr: 0.82, alpha: '55', width: 1.4 },
      { ang: this.ringA * 0.6, fr: 0.66, alpha: '77', width: 1.1 }
    ];

    rings.forEach((r) => {
      const rr = R * r.fr * br * en;
      ctx.strokeStyle = `${c1}${r.alpha}`;
      ctx.lineWidth = r.width;
      ctx.beginPath();
      ctx.arc(cx, cy, rr, 0, Math.PI * 2);
      ctx.stroke();
    });

    // Particles
    this.particles.forEach((pt) => {
      pt.ang += pt.spd * (this.mode === 'IDLE' ? 0.6 : 1.6);
      const rr = R * pt.rad;
      const px = cx + Math.cos(pt.ang) * rr;
      const py = cy + Math.sin(pt.ang) * rr * 0.92;
      ctx.fillStyle = `${c2}77`;
      ctx.beginPath();
      ctx.arc(px, py, pt.sz, 0, Math.PI * 2);
      ctx.fill();
    });

    // Central Sphere Glow
    const cr = R * 0.48 * br * en;
    const g = ctx.createRadialGradient(cx - cr * 0.2, cy - cr * 0.2, 0, cx, cy, cr * 1.4);
    g.addColorStop(0, '#f8fafc');
    g.addColorStop(0.3, `${c1}dd`);
    g.addColorStop(0.7, `${c2}99`);
    g.addColorStop(1, 'rgba(8, 12, 24, 0.9)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(cx, cy, cr, 0, Math.PI * 2);
    ctx.fill();
  }

  drawWaveform() {
    const ctx = this.waveCtx;
    const w = ctx.canvas.width;
    const h = ctx.canvas.height;
    ctx.clearRect(0, 0, w, h);

    const midY = h / 2;
    const [c1, c2] = this.getColors();

    const layers = [
      { amp: 8 + this.level * 22, f: 2.2, speed: 1.0, alpha: 0.6, width: 1.8 },
      { amp: 11 + this.level * 28, f: 3.1, speed: -0.8, alpha: 0.8, width: 2.2 },
      { amp: 6 + this.level * 15, f: 4.3, speed: 1.3, alpha: 0.4, width: 1.2 }
    ];

    layers.forEach((L) => {
      ctx.beginPath();
      for (let x = 0; x <= w; x += 4) {
        const nx = x / w;
        const env = Math.pow(Math.sin(nx * Math.PI), 2);
        const y = Math.sin(nx * L.f * Math.PI * 2 + this.phase * L.speed) * L.amp * env;
        if (x === 0) ctx.moveTo(x, midY - y);
        else ctx.lineTo(x, midY - y);
      }

      const grad = ctx.createLinearGradient(0, 0, w, 0);
      grad.addColorStop(0.1, `${c1}00`);
      grad.addColorStop(0.4, `${c1}aa`);
      grad.addColorStop(0.7, `${c2}aa`);
      grad.addColorStop(0.9, `${c2}00`);

      ctx.strokeStyle = grad;
      ctx.lineWidth = L.width;
      ctx.stroke();
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new SoraPreviewController();
});
