from __future__ import annotations

import json
import time
from typing import Generator

import gradio as gr


TOPICS = [
    "AI should be open source",
    "Universal basic income is necessary",
    "Social media does more harm than good",
    "Nuclear energy is essential for climate goals",
    "Remote work should be the default",
    "Cryptocurrency is a net positive",
    "AI should be regulated like medicine",
    "Standardized testing should be abolished",
]

DEFAULT_TOPIC = "AI should be open source"


def _event(
    *,
    topic: str,
    mode: str,
    round_idx: int,
    rounds_total: int,
    pro_line: str,
    con_line: str,
    pro_score: int,
    con_score: int,
    momentum: int,
    speaker: str,
    timer_s: float,
    verdict: str | None = None,
) -> str:
    return json.dumps(
        {
            "topic": topic,
            "mode": mode,
            "round": round_idx,
            "roundsTotal": rounds_total,
            "proLine": pro_line,
            "conLine": con_line,
            "proScore": pro_score,
            "conScore": con_score,
            "momentum": momentum,
            "speaker": speaker,
            "timerS": timer_s,
            "verdict": verdict or "",
            "ts": time.time(),
        },
        ensure_ascii=False,
    )


def _debate_script(topic: str) -> tuple[list[str], list[str], list[int], list[int], str]:
    # Demo/showcase: always impressive, hardcoded arguments.
    # Default topic gets the "best" lines; others still map to the same script.
    pro = [
        "Open-source AI is the fastest path to safety: more eyes on the code means faster audits, faster patching, and fewer hidden failure modes.",
        "Innovation compounds when the baseline is shared. Open models become infrastructure—like Linux—unlocking startups, researchers, and local language communities.",
        "Closed models centralize power. Transparency disperses it, reducing single-point-of-failure governance and enabling independent verification of claims.",
        "Security through obscurity doesn’t scale. If adversaries can jailbreak closed systems anyway, openness lets defenders iterate faster and publish mitigations.",
        "The future is accountable AI: reproducible benchmarks, transparent weights, and open eval harnesses. Open source makes trust measurable—not marketing.",
    ]
    con = [
        "Open weights increase misuse: scalable disinformation, automated vulnerability discovery, and bio/chem assistance become cheaper and harder to contain.",
        "Safety work needs controlled deployment. With open models, you can’t recall a capability once it’s downloaded—mitigations arrive after the harm.",
        "The economics matter: training frontier models is expensive. If everything is open, fewer labs invest, slowing progress and concentrating compute access anyway.",
        "Verification isn’t guaranteed by openness. Most users can’t audit complex systems, while attackers only need one exploit path—risk increases asymmetrically.",
        "A middle path works better: open research + gated releases, with tiered access, monitoring, and liability—like handling dual‑use scientific tools.",
    ]

    # Hardcoded “impressive” scoring dynamics (PRO edges slightly).
    pro_delta = [2, 1, 2, 1, 2]
    con_delta = [1, 1, 1, 1, 1]

    verdict = (
        f"Verdict for topic: “{topic}”.\n\n"
        "Judge summary:\n"
        "- PRO wins on governance + verification: open evaluation and independent auditing make claims falsifiable.\n"
        "- CON wins on irreversibility: once a high-capability model is public, containment and recall are impossible.\n"
        "Final call: PRO by a narrow margin for emphasizing accountable deployment patterns (open tooling + transparent evals), "
        "while acknowledging CON’s strongest point on dual‑use risk."
    )
    return pro, con, pro_delta, con_delta, verdict


def start_debate(topic: str, mode: str) -> Generator:
    topic = topic or DEFAULT_TOPIC
    mode = mode or "AI vs AI"
    pro_lines, con_lines, pro_delta, con_delta, verdict = _debate_script(topic)

    pro_score = 0
    con_score = 0
    reward_points: list[int] = []

    rounds_total = 5

    # Initial UI reset (canvas drives visuals; Python streams events)
    yield (
        gr.update(value=topic),
        gr.update(interactive=False),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(interactive=False),
        gr.update(value=_event(
            topic=topic,
            mode=mode,
            round_idx=1,
            rounds_total=rounds_total,
            pro_line="",
            con_line="",
            pro_score=0,
            con_score=0,
            momentum=0,
            speaker="none",
            timer_s=0.0,
            verdict="",
        )),
    )

    for i in range(rounds_total):
        # PRO speaks
        time.sleep(0.3)
        pro_score += pro_delta[i]
        con_score += 0
        reward_points.append(pro_delta[i] - 0)
        momentum = sum(reward_points)
        yield (
            gr.update(value=topic),
            gr.update(interactive=False),
            gr.update(value=""),
            gr.update(value=""),
            gr.update(
                value=_event(
                    topic=topic,
                    mode=mode,
                    round_idx=i + 1,
                    rounds_total=rounds_total,
                    pro_line=pro_lines[i],
                    con_line="",
                    pro_score=pro_score,
                    con_score=con_score,
                    momentum=momentum,
                    speaker="pro",
                    timer_s=0.3,
                )
            ),
        )

        # CON speaks
        time.sleep(0.3)
        con_score += con_delta[i]
        reward_points.append(0 - con_delta[i])
        momentum = sum(reward_points)
        yield (
            gr.update(value=topic),
            gr.update(interactive=False),
            gr.update(value=""),
            gr.update(value=""),
            gr.update(
                value=_event(
                    topic=topic,
                    mode=mode,
                    round_idx=i + 1,
                    rounds_total=rounds_total,
                    pro_line="",
                    con_line=con_lines[i],
                    pro_score=pro_score,
                    con_score=con_score,
                    momentum=momentum,
                    speaker="con",
                    timer_s=0.3,
                )
            ),
        )

    time.sleep(0.3)
    yield (
        gr.update(value=topic),
        gr.update(interactive=True),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(
            value=_event(
                topic=topic,
                mode=mode,
                round_idx=rounds_total,
                rounds_total=rounds_total,
                pro_line="",
                con_line="",
                pro_score=pro_score,
                con_score=con_score,
                momentum=sum(reward_points),
                speaker="none",
                timer_s=0.0,
                verdict=verdict,
            )
        ),
    )


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

:root { color-scheme: dark; }

.gradio-container{
  background:#0a0a0a !important;
  color:#fff !important;
  font-family: 'Press Start 2P', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace !important;
}

.pixel-hero{
  padding: 10px 6px 6px 6px;
}
.pixel-title{
  font-size: 34px;
  line-height: 1.25;
  margin: 0 0 6px 0;
  letter-spacing: 1px;
}
.pixel-sub{
  margin: 0;
  opacity: 0.85;
  font-size: 12px;
}

.hud-row{
  display:flex;
  gap: 12px;
  align-items:flex-end;
}

.pixel-panel{
  background: rgba(255,255,255,0.03);
  border: 2px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 12px;
}

.arena-wrap{
  border-radius: 16px;
  overflow: hidden;
  border: 2px solid rgba(255,255,255,0.1);
  background: #0f0f10;
}

.hud{
  display:flex;
  justify-content:space-between;
  gap: 10px;
  padding: 10px 12px;
  border-top: 2px solid rgba(255,255,255,0.08);
  background: rgba(0,0,0,0.25);
}
.hud .meter{
  flex: 1;
  height: 12px;
  border-radius: 999px;
  border: 2px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
  overflow: hidden;
}
.hud .fill{
  height: 100%;
  width: 50%;
  background: linear-gradient(90deg, #3B82F6, #EF4444);
}
.hud .stat{
  min-width: 220px;
  text-align:right;
  font-size: 11px;
  opacity: 0.9;
}

.verdict{
  font-size: 12px !important;
}
"""


ARENA_HTML = r"""
<div class="pixel-hero">
  <div class="pixel-title">DIALECTICA ⚔️</div>
  <p class="pixel-sub">Self-play LLM Debate Arena</p>
</div>

<div class="arena-wrap">
  <canvas id="arena" width="980" height="420" style="width:100%; height:auto; image-rendering: pixelated;"></canvas>
  <div class="hud">
    <div class="meter"><div id="momentumFill" class="fill"></div></div>
    <div id="hudStat" class="stat">Round 1/5 · Momentum 0</div>
  </div>
</div>

<script>
(() => {
  const canvas = document.getElementById('arena');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const PRO = { accent: '#3B82F6', name: 'PRO' };
  const CON = { accent: '#EF4444', name: 'CON' };

  const state = {
    topic: 'AI should be open source',
    round: 1,
    roundsTotal: 5,
    proScore: 0,
    conScore: 0,
    momentum: 0,
    speaker: 'none',
    proLine: '',
    conLine: '',
    verdict: '',
    animT: 0,
  };

  const fx = {
    bubbleT: 0,
    proMood: 'idle',
    conMood: 'idle',
    pop: 0
  };

  function clamp(v, a, b){ return Math.max(a, Math.min(b, v)); }

  function drawPixelRect(x,y,w,h,fill,stroke){
    ctx.fillStyle = fill;
    ctx.fillRect(x,y,w,h);
    if (stroke){
      ctx.strokeStyle = stroke;
      ctx.lineWidth = 2;
      ctx.strokeRect(x+1,y+1,w-2,h-2);
    }
  }

  function drawHall(){
    // background
    ctx.fillStyle = '#0b0b0c';
    ctx.fillRect(0,0,canvas.width,canvas.height);

    // audience silhouettes
    ctx.fillStyle = '#0f0f12';
    for (let i=0;i<70;i++){
      const x = (i*15) % canvas.width;
      const y = 240 + Math.floor(i/70*0);
      const h = 22 + (i%7);
      ctx.fillRect(x, 250 + (i%3)*3, 10, h);
    }

    // stage platform
    drawPixelRect(0, 300, canvas.width, 120, '#0f0f10', null);
    drawPixelRect(40, 285, canvas.width-80, 85, '#121216', 'rgba(255,255,255,0.08)');

    // lights
    ctx.fillStyle = 'rgba(255,255,255,0.04)';
    ctx.beginPath();
    ctx.ellipse(260, 120, 220, 150, 0, 0, Math.PI*2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(720, 120, 220, 150, 0, 0, Math.PI*2);
    ctx.fill();
  }

  function drawPodium(x, accent){
    drawPixelRect(x-70, 250, 140, 110, '#15151b', 'rgba(255,255,255,0.10)');
    drawPixelRect(x-70, 250, 140, 6, accent, null);
    // mic
    ctx.fillStyle = 'rgba(255,255,255,0.7)';
    ctx.fillRect(x+28, 238, 4, 18);
    ctx.fillRect(x+20, 235, 18, 4);
  }

  function drawDebater(x, baseY, side, mood){
    // simple generated pixel-sprite style (no external assets)
    const accent = side.accent;
    const bob = Math.sin(state.animT*2 + (side===PRO?0:1.2)) * 2;
    const speak = (mood === 'speaking') ? (Math.sin(state.animT*14) * 2) : 0;
    const think = (mood === 'thinking') ? (Math.sin(state.animT*6) * 1) : 0;
    const react = (mood === 'react') ? (Math.sin(state.animT*10) * 3) : 0;

    const y = baseY + bob + speak + think + react;

    // body
    drawPixelRect(x-26, y-56, 52, 56, '#1a1a22', 'rgba(255,255,255,0.10)');
    drawPixelRect(x-26, y-56, 52, 4, accent, null);
    // head
    drawPixelRect(x-18, y-84, 36, 28, '#1f1f2a', 'rgba(255,255,255,0.10)');
    // eyes
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.fillRect(x-10, y-72, 4, 4);
    ctx.fillRect(x+6, y-72, 4, 4);
    // mouth
    ctx.fillStyle = (mood==='speaking') ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.35)';
    ctx.fillRect(x-4, y-64, 8, 3);
  }

  function drawSpeechBubble(side, text){
    if (!text) return;
    const left = (side===PRO);
    const bx = left ? 90 : canvas.width - 430;
    const by = 70;
    const bw = 340;
    const bh = 120;
    drawPixelRect(bx, by, bw, bh, 'rgba(0,0,0,0.50)', 'rgba(255,255,255,0.14)');
    // tail
    ctx.fillStyle = 'rgba(0,0,0,0.50)';
    ctx.fillRect(left ? bx+38 : bx+bw-58, by+bh-10, 20, 20);
    ctx.strokeStyle = 'rgba(255,255,255,0.14)';
    ctx.lineWidth = 2;
    ctx.strokeRect(left ? bx+39 : bx+bw-57, by+bh-9, 18, 18);

    // pixel text (drawn on canvas)
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    ctx.font = '12px "Press Start 2P", monospace';
    ctx.textBaseline = 'top';
    const words = text.split(' ');
    let line = '';
    let y = by + 14;
    const maxW = bw - 18;
    for (const w of words){
      const test = line ? (line + ' ' + w) : w;
      if (ctx.measureText(test).width > maxW){
        ctx.fillText(line, bx+10, y);
        y += 18;
        line = w;
        if (y > by + bh - 26) break;
      } else {
        line = test;
      }
    }
    if (line && y <= by + bh - 18) ctx.fillText(line, bx+10, y);
  }

  function drawHUD(){
    // top banner
    ctx.fillStyle = 'rgba(255,255,255,0.06)';
    ctx.fillRect(0, 0, canvas.width, 44);
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    ctx.font = '14px "Press Start 2P", monospace';
    ctx.textBaseline = 'middle';
    ctx.fillText(state.topic.toUpperCase(), 18, 22);

    // scores
    ctx.font = '12px "Press Start 2P", monospace';
    ctx.fillStyle = PRO.accent;
    ctx.fillText(`PRO ${state.proScore}`, 18, 66);
    ctx.fillStyle = CON.accent;
    ctx.fillText(`CON ${state.conScore}`, canvas.width-180, 66);

    // round center
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.fillText(`ROUND ${state.round}/${state.roundsTotal}`, canvas.width/2 - 120, 66);

    // turn indicator
    const turn = state.speaker === 'pro' ? 'PRO TURN' : (state.speaker === 'con' ? 'CON TURN' : 'READY');
    ctx.fillStyle = state.speaker === 'pro' ? PRO.accent : (state.speaker === 'con' ? CON.accent : 'rgba(255,255,255,0.7)');
    ctx.fillText(turn, canvas.width/2 - 78, 92);
  }

  function tick(){
    state.animT += 1/60;
    drawHall();

    // podiums + debaters
    drawPodium(250, PRO.accent);
    drawPodium(730, CON.accent);

    const proMood = state.speaker === 'pro' ? 'speaking' : (state.speaker === 'con' ? 'react' : 'idle');
    const conMood = state.speaker === 'con' ? 'speaking' : (state.speaker === 'pro' ? 'react' : 'idle');

    drawDebater(250, 278, PRO, proMood);
    drawDebater(730, 278, CON, conMood);

    // speech bubble
    if (state.speaker === 'pro') drawSpeechBubble(true, state.proLine);
    if (state.speaker === 'con') drawSpeechBubble(false, state.conLine);

    drawHUD();

    requestAnimationFrame(tick);
  }

  function setMomentum(v){
    const el = document.getElementById('momentumFill');
    const stat = document.getElementById('hudStat');
    if (!el || !stat) return;
    const pct = clamp(50 + v*6, 8, 92);
    el.style.width = pct + '%';
    stat.textContent = `Round ${state.round}/${state.roundsTotal} · Momentum ${v}`;
  }

  // Listen to Gradio updates: a hidden textbox (JSON event) changes over time.
  function hookEventStream(){
    const candidates = Array.from(document.querySelectorAll('textarea, input')).filter(el => {
      const aria = (el.getAttribute('aria-label') || '').toLowerCase();
      return aria.includes('arena_event_stream');
    });
    const el = candidates[0];
    if (!el) { setTimeout(hookEventStream, 500); return; }

    const apply = (raw) => {
      if (!raw) return;
      try{
        const e = JSON.parse(raw);
        state.topic = e.topic || state.topic;
        state.round = e.round || state.round;
        state.roundsTotal = e.roundsTotal || state.roundsTotal;
        state.proScore = e.proScore ?? state.proScore;
        state.conScore = e.conScore ?? state.conScore;
        state.momentum = e.momentum ?? state.momentum;
        state.speaker = e.speaker || 'none';
        state.proLine = e.proLine || '';
        state.conLine = e.conLine || '';
        state.verdict = e.verdict || '';
        setMomentum(state.momentum);
      }catch(err){}
    };

    apply(el.value);
    const obs = new MutationObserver(() => apply(el.value));
    obs.observe(el, { attributes: true, childList: true, subtree: true });
    el.addEventListener('input', () => apply(el.value));
  }

  hookEventStream();
  tick();
})();
</script>
"""


with gr.Blocks(title="DIALECTICA", css=CSS, theme=gr.themes.Base()) as demo:
    gr.HTML(ARENA_HTML)

    with gr.Row():
        topic = gr.Dropdown(TOPICS, value=DEFAULT_TOPIC, label="Topic", interactive=True)
        mode = gr.Dropdown(
            ["AI vs AI", "Human vs AI"],
            value="AI vs AI",
            label="Mode",
            interactive=True,
        )
        start = gr.Button("⚡ Start Debate", variant="primary")

    verdict = gr.Textbox(label="Judge verdict", lines=6, elem_classes=["verdict"])

    # Hidden event stream: JS listens to this field and animates canvas.
    arena_event_stream = gr.Textbox(
        label="arena_event_stream",
        value="",
        interactive=False,
        visible=False,
    )

    start.click(
        fn=start_debate,
        inputs=[topic, mode],
        outputs=[topic, start, verdict, arena_event_stream],
    )


if __name__ == "__main__":
    demo.launch()

