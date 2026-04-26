from __future__ import annotations

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


def _score_badge(score: int, accent: str) -> str:
    return (
        f"<div class='score' style='border-color:{accent}'>"
        f"<span class='score-label'>Score</span>"
        f"<span class='score-value'>{score}</span>"
        f"</div>"
    )


def _reward_svg(points: list[int]) -> str:
    w, h = 520, 120
    pad = 14
    if not points:
        points = [0]
    xs = []
    ys = []
    max_abs = max(1, max(abs(p) for p in points))
    for i, p in enumerate(points):
        x = pad + (w - 2 * pad) * (i / max(1, len(points) - 1))
        y = pad + (h - 2 * pad) * (1 - ((p + max_abs) / (2 * max_abs)))
        xs.append(x)
        ys.append(y)
    path = " ".join(
        f"{'M' if i == 0 else 'L'} {xs[i]:.2f},{ys[i]:.2f}" for i in range(len(points))
    )

    dots = "\n".join(
        f"<circle cx='{xs[i]:.2f}' cy='{ys[i]:.2f}' r='3.5' fill='#FFFFFF' opacity='0.9'/>"
        for i in range(len(points))
    )

    return f"""
    <div class="plot-wrap">
      <div class="plot-title">Reward trend</div>
      <svg viewBox="0 0 {w} {h}" class="plot" role="img" aria-label="Reward plot">
        <defs>
          <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#3B82F6" stop-opacity="0.95" />
            <stop offset="100%" stop-color="#EF4444" stop-opacity="0.95" />
          </linearGradient>
        </defs>
        <rect x="0" y="0" width="{w}" height="{h}" rx="12" fill="#0f0f10" />
        <path d="{path}" fill="none" stroke="url(#g)" stroke-width="3" />
        {dots}
      </svg>
      <div class="plot-caption">Round-by-round differential (PRO – CON)</div>
    </div>
    """


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


def start_debate(topic: str) -> Generator:
    topic = topic or DEFAULT_TOPIC
    pro_lines, con_lines, pro_delta, con_delta, verdict = _debate_script(topic)

    pro_text = ""
    con_text = ""
    pro_score = 0
    con_score = 0
    reward_points: list[int] = []

    # Initial UI reset
    yield (
        gr.update(value=topic),
        gr.update(interactive=False),
        gr.update(value="", lines=8),
        gr.update(value="", lines=8),
        gr.update(value=_score_badge(0, "#3B82F6")),
        gr.update(value=_score_badge(0, "#EF4444")),
        gr.update(value="Round 1 / 5"),
        gr.update(value=""),
        gr.update(value=_reward_svg([])),
    )

    for i in range(5):
        time.sleep(0.3)

        pro_text = (pro_text + f"• {pro_lines[i]}\n").strip() + "\n"
        con_text = (con_text + f"• {con_lines[i]}\n").strip() + "\n"

        pro_score += pro_delta[i]
        con_score += con_delta[i]

        reward_points.append(pro_delta[i] - con_delta[i])

        yield (
            gr.update(value=topic),
            gr.update(interactive=False),
            gr.update(value=pro_text, lines=8),
            gr.update(value=con_text, lines=8),
            gr.update(value=_score_badge(pro_score, "#3B82F6")),
            gr.update(value=_score_badge(con_score, "#EF4444")),
            gr.update(value=f"Round {i + 1} / 5"),
            gr.update(value=""),
            gr.update(value=_reward_svg(reward_points)),
        )

    time.sleep(0.3)
    yield (
        gr.update(value=topic),
        gr.update(interactive=True),
        gr.update(value=pro_text, lines=8),
        gr.update(value=con_text, lines=8),
        gr.update(value=_score_badge(pro_score, "#3B82F6")),
        gr.update(value=_score_badge(con_score, "#EF4444")),
        gr.update(value="Round 5 / 5"),
        gr.update(value=verdict),
        gr.update(value=_reward_svg(reward_points)),
    )


CSS = """
:root { color-scheme: dark; }

.gradio-container{
  background:#0a0a0a !important;
  color:#fff !important;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica, Arial;
}

.hero{
  padding: 8px 2px 0px 2px;
}
.hero h1{
  margin: 0;
  font-size: 42px;
  font-weight: 800;
  letter-spacing: 0.6px;
}
.hero p{
  margin: 6px 0 0 0;
  opacity: 0.85;
  font-size: 16px;
}

.card{
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 14px;
}
.card.pro{ border-color: rgba(59,130,246,0.65); box-shadow: 0 0 0 1px rgba(59,130,246,0.25) inset; }
.card.con{ border-color: rgba(239,68,68,0.65); box-shadow: 0 0 0 1px rgba(239,68,68,0.22) inset; }
.agent-title{
  font-weight: 800;
  letter-spacing: 0.35px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin-bottom: 10px;
}
.pill{
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.12);
  opacity: 0.85;
}

.score{
  margin-top: 10px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(0,0,0,0.28);
}
.score-label{ opacity:0.75; font-size: 12px; letter-spacing:0.2px; }
.score-value{ font-size: 20px; font-weight: 900; }

.center-stack{
  height: 100%;
  min-height: 260px;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  gap: 10px;
}
.round{
  font-weight: 800;
  font-size: 16px;
  opacity: 0.95;
}
.vs{
  font-weight: 900;
  font-size: 34px;
  letter-spacing: 2px;
  opacity: 0.9;
}

.plot-wrap{
  width: 100%;
}
.plot-title{
  font-weight: 800;
  margin-bottom: 8px;
  opacity: 0.95;
}
.plot{
  width: 100%;
  height: auto;
  border-radius: 14px;
}
.plot-caption{
  margin-top: 6px;
  opacity: 0.7;
  font-size: 12px;
}
"""


with gr.Blocks(title="DIALECTICA", css=CSS, theme=gr.themes.Base()) as demo:
    gr.HTML(
        """
        <div class="hero">
          <h1>DIALECTICA ⚔️</h1>
          <p>Self-play LLM Debate Arena</p>
        </div>
        """
    )

    with gr.Row():
        topic = gr.Dropdown(
            TOPICS,
            value=DEFAULT_TOPIC,
            label="Topic",
            interactive=True,
        )
        start = gr.Button("⚡ Start Debate", variant="primary")

    with gr.Row(equal_height=True):
        with gr.Column(scale=5):
            with gr.Group(elem_classes=["card", "pro"]):
                gr.HTML(
                    "<div class='agent-title'>PRO <span class='pill'>#3B82F6</span></div>"
                )
                pro_box = gr.Textbox(
                    value="",
                    label=None,
                    lines=8,
                    show_label=False,
                )
                pro_score_html = gr.HTML(_score_badge(0, "#3B82F6"))

        with gr.Column(scale=2, min_width=180):
            with gr.Group(elem_classes=["card"]):
                round_label = gr.Markdown("Round 1 / 5", elem_classes=["round"])
                gr.Markdown("<div class='vs'>VS</div>", elem_classes=["center-stack"])

        with gr.Column(scale=5):
            with gr.Group(elem_classes=["card", "con"]):
                gr.HTML(
                    "<div class='agent-title'>CON <span class='pill'>#EF4444</span></div>"
                )
                con_box = gr.Textbox(
                    value="",
                    label=None,
                    lines=8,
                    show_label=False,
                )
                con_score_html = gr.HTML(_score_badge(0, "#EF4444"))

    with gr.Row():
        judge = gr.Textbox(
            label="Judge verdict",
            lines=6,
            placeholder="Verdict will appear here after 5 rounds...",
        )

    reward_plot = gr.HTML(_reward_svg([]))

    start.click(
        fn=start_debate,
        inputs=[topic],
        outputs=[
            topic,
            start,
            pro_box,
            con_box,
            pro_score_html,
            con_score_html,
            round_label,
            judge,
            reward_plot,
        ],
    )


if __name__ == "__main__":
    demo.launch()

