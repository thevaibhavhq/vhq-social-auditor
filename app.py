"""
app.py — All-In-One AI Social Media Audit & Viral Engine
Single-file deployment. Contains all modules inline:
  [1] LLM Router      — OpenAI / Anthropic / Gemini / Groq
  [2] Input Models    — Platform metric dataclasses + validation
  [3] Prompt Engine   — 4-stage audit prompt builder
  [4] Streamlit UI    — Settings panel, forms, results renderer
"""

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional
import streamlit as st


# ═══════════════════════════════════════════════════════════════════════════════
# [1] LLM ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

class Provider(str, Enum):
    OPENAI    = "openai"
    ANTHROPIC = "anthropic"
    GEMINI    = "gemini"
    GROQ      = "groq"


PROVIDER_LABELS: dict[Provider, str] = {
    Provider.OPENAI:    "OpenAI · GPT-4o",
    Provider.ANTHROPIC: "Anthropic · Claude 3.5 Sonnet",
    Provider.GEMINI:    "Google AI · Gemini 1.5 Pro (Free tier)",
    Provider.GROQ:      "Groq Cloud · Llama-3 70B (Ultra-fast)",
}

_LLM_SYSTEM = (
    "You are an elite social media growth strategist and algorithm expert. "
    "You ALWAYS return your analysis as a single valid JSON object. "
    "Never include markdown fences, preamble, or trailing commentary."
)


def _call_openai(api_key: str, prompt: str, max_tokens: int) -> str:
    try:
        import openai as _openai
    except ImportError:
        raise ImportError("openai package not installed.")
    client = _openai.OpenAI(api_key=api_key)
    try:
        r = client.chat.completions.create(
            model="gpt-4o", max_tokens=max_tokens, temperature=0.75,
            messages=[{"role": "system", "content": _LLM_SYSTEM},
                      {"role": "user",   "content": prompt}],
        )
        return r.choices[0].message.content.strip()
    except _openai.AuthenticationError:
        raise ValueError("OpenAI: Invalid API key. Check your key and retry.")
    except _openai.RateLimitError:
        raise RuntimeError("OpenAI: Rate limit reached. Wait a moment and retry.")
    except _openai.APIError as e:
        raise RuntimeError(f"OpenAI API error: {e}")


def _call_anthropic(api_key: str, prompt: str, max_tokens: int) -> str:
    try:
        import anthropic as _anthropic
    except ImportError:
        raise ImportError("anthropic package not installed.")
    client = _anthropic.Anthropic(api_key=api_key)
    try:
        msg = client.messages.create(
            model="claude-3-5-sonnet-20241022", max_tokens=max_tokens,
            system=_LLM_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except _anthropic.AuthenticationError:
        raise ValueError("Anthropic: Invalid API key. Check your key and retry.")
    except _anthropic.RateLimitError:
        raise RuntimeError("Anthropic: Rate limit reached. Wait a moment and retry.")
    except _anthropic.APIError as e:
        raise RuntimeError(f"Anthropic API error: {e}")


def _call_gemini(api_key: str, prompt: str, max_tokens: int) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("google-generativeai package not installed.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=genai.GenerationConfig(max_output_tokens=max_tokens, temperature=0.75),
    )
    try:
        r = model.generate_content(_LLM_SYSTEM + "\n\n" + prompt)
        return r.text.strip()
    except Exception as e:
        err = str(e).lower()
        if "api_key" in err or "invalid" in err or "authentication" in err:
            raise ValueError("Gemini: Invalid API key. Check your key and retry.")
        elif "quota" in err or "rate" in err:
            raise RuntimeError("Gemini: Quota exceeded. Wait or upgrade your plan.")
        raise RuntimeError(f"Gemini API error: {e}")


def _call_groq(api_key: str, prompt: str, max_tokens: int) -> str:
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("groq package not installed.")
    client = Groq(api_key=api_key)
    try:
        r = client.chat.completions.create(
            model="llama3-70b-8192", max_tokens=max_tokens, temperature=0.75,
            messages=[{"role": "system", "content": _LLM_SYSTEM},
                      {"role": "user",   "content": prompt}],
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        err = str(e).lower()
        if "invalid api key" in err or "authentication" in err:
            raise ValueError("Groq: Invalid API key. Check your key and retry.")
        elif "rate limit" in err:
            raise RuntimeError("Groq: Rate limit hit. Wait a moment and retry.")
        raise RuntimeError(f"Groq API error: {e}")


def _safe_parse_json(raw: str) -> dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Model returned malformed JSON: {e}\n\nRaw:\n{raw[:500]}")


def run_prompt(provider: Provider, api_key: str, prompt: str, max_tokens: int = 2000) -> dict[str, Any]:
    if not api_key or not api_key.strip():
        raise ValueError(f"No API key provided for {PROVIDER_LABELS[provider]}.")
    callers = {
        Provider.OPENAI:    _call_openai,
        Provider.ANTHROPIC: _call_anthropic,
        Provider.GEMINI:    _call_gemini,
        Provider.GROQ:      _call_groq,
    }
    raw = callers[provider](api_key.strip(), prompt, max_tokens)
    return _safe_parse_json(raw)


# ═══════════════════════════════════════════════════════════════════════════════
# [2] INPUT MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class Platform(str, Enum):
    YOUTUBE_LONG   = "youtube_long"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM      = "instagram"
    THREADS        = "threads"
    WHATSAPP       = "whatsapp"
    MESSENGER      = "messenger"


PLATFORM_LABELS: dict[Platform, str] = {
    Platform.YOUTUBE_LONG:   "YouTube · Long-form Video",
    Platform.YOUTUBE_SHORTS: "YouTube · Shorts",
    Platform.INSTAGRAM:      "Instagram · Reels & Posts",
    Platform.THREADS:        "Threads · Posts",
    Platform.WHATSAPP:       "WhatsApp Business · Broadcast",
    Platform.MESSENGER:      "Facebook Messenger · Broadcast",
}

PLATFORM_ICONS: dict[Platform, str] = {
    Platform.YOUTUBE_LONG:   "▶",
    Platform.YOUTUBE_SHORTS: "⚡",
    Platform.INSTAGRAM:      "◈",
    Platform.THREADS:        "◎",
    Platform.WHATSAPP:       "◉",
    Platform.MESSENGER:      "◈",
}


def _pct(v: float, name: str) -> float:
    if not (0.0 <= v <= 100.0):
        raise ValueError(f"{name} must be 0–100%. Got: {v}")
    return v

def _pos(v: float, name: str) -> float:
    if v < 0:
        raise ValueError(f"{name} cannot be negative. Got: {v}")
    return v


@dataclass
class YouTubeLongMetrics:
    niche: str; content_description: str
    impressions: int; views: int; ctr_percent: float
    avd_percent: float; avd_minutes: float
    likes: int = 0; comments: int = 0; subscribers_gained: int = 0

    def __post_init__(self):
        _pct(self.ctr_percent, "CTR %"); _pct(self.avd_percent, "AVD %")
        _pos(self.avd_minutes, "AVD Minutes")

    def to_prompt_context(self) -> str:
        return f"""PLATFORM: YouTube Long-form Video
NICHE: {self.niche}
CONTENT: {self.content_description}
Impressions: {self.impressions:,} | Views: {self.views:,} | CTR: {self.ctr_percent:.2f}%
AVD: {self.avd_percent:.1f}% ({self.avd_minutes:.1f} min) | Likes: {self.likes:,} | Comments: {self.comments:,} | Subs gained: {self.subscribers_gained:,}
BENCHMARKS: Strong CTR ≥ 6% | Acceptable 3–6% | Weak < 3%. Strong AVD ≥ 50% | Weak < 35%."""


@dataclass
class YouTubeShortsMetrics:
    niche: str; content_description: str
    views: int; likes: int; comments: int; shares: int
    avd_percent: float; subscribers_gained: int = 0

    def __post_init__(self):
        _pct(self.avd_percent, "AVD %")

    def to_prompt_context(self) -> str:
        eng = ((self.likes + self.comments + self.shares) / self.views * 100) if self.views > 0 else 0
        return f"""PLATFORM: YouTube Shorts
NICHE: {self.niche}
CONTENT: {self.content_description}
Views: {self.views:,} | Likes: {self.likes:,} | Comments: {self.comments:,} | Shares: {self.shares:,}
Engagement: {eng:.2f}% | AVD: {self.avd_percent:.1f}% | Subs gained: {self.subscribers_gained:,}
BENCHMARKS: Shorts AVD ≥ 80% excellent | < 60% = drop-off. Engagement ≥ 5% healthy | < 2% suppression risk."""


@dataclass
class InstagramMetrics:
    platform: Platform; niche: str; content_description: str; content_type: str
    plays_or_reach: int; likes: int; comments: int; saves: int; shares: int
    follows_gained: int = 0; profile_visits: int = 0

    def to_prompt_context(self) -> str:
        eng = ((self.likes + self.comments + self.saves + self.shares) / self.plays_or_reach * 100) if self.plays_or_reach > 0 else 0
        label = PLATFORM_LABELS[self.platform]
        return f"""PLATFORM: {label} · {self.content_type}
NICHE: {self.niche}
CONTENT: {self.content_description}
Plays/Reach: {self.plays_or_reach:,} | Likes: {self.likes:,} | Comments: {self.comments:,}
Saves: {self.saves:,} | Shares: {self.shares:,} | Engagement: {eng:.2f}%
Follows gained: {self.follows_gained:,} | Profile visits: {self.profile_visits:,}
BENCHMARKS: Engagement ≥ 5% strong | < 2% suppressed. Saves are highest-weight signal. Low saves (< 0.5% reach) = weak value perception."""


@dataclass
class MessagingMetrics:
    platform: Platform; niche: str; campaign_goal: str
    messages_sent: int; messages_opened: int; open_rate: float
    replies: int; reply_rate: float
    link_clicks: int = 0; opt_outs: int = 0

    def __post_init__(self):
        _pct(self.open_rate, "Open Rate %"); _pct(self.reply_rate, "Reply Rate %")

    def to_prompt_context(self) -> str:
        click_rate = (self.link_clicks / self.messages_sent * 100) if self.messages_sent > 0 else 0
        label = PLATFORM_LABELS[self.platform]
        return f"""PLATFORM: {label}
NICHE: {self.niche} | GOAL: {self.campaign_goal}
Sent: {self.messages_sent:,} | Opened: {self.messages_opened:,} | Open rate: {self.open_rate:.2f}%
Replies: {self.replies:,} | Reply rate: {self.reply_rate:.2f}% | Clicks: {self.link_clicks:,} | Click rate: {click_rate:.2f}% | Opt-outs: {self.opt_outs:,}
BENCHMARKS: WhatsApp open rate avg 85–98% | Below 70% = list health issue. Reply rate > 10% strong | < 3% = message failure. Opt-out > 2% = content mismatch."""


# ═══════════════════════════════════════════════════════════════════════════════
# [3] PROMPT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

_OUTPUT_SCHEMA = """
Return ONLY a JSON object matching this schema. No markdown. No text outside the JSON.

{
  "diagnostics": {
    "overall_health_score": <integer 0-100>,
    "health_label": "<Struggling | Below Average | Average | Good | Excellent>",
    "flags": [
      {
        "metric": "<metric name>",
        "value": "<observed value>",
        "benchmark": "<target value>",
        "severity": "<Critical | Warning | Info>",
        "fault": "<one-sentence plain-English fault>"
      }
    ],
    "primary_bottleneck": "<the single most important thing hurting performance>"
  },
  "behavioral_analysis": {
    "algorithm_status": "<Suppressed | Neutral | Favoured | Viral>",
    "suppression_reasons": ["<reason 1>", "<reason 2>", "<reason 3>"],
    "audience_signal_quality": "<Poor | Fair | Good | Excellent>",
    "content_signal_quality": "<Poor | Fair | Good | Excellent>",
    "verdict": "<2-3 sentence expert paragraph explaining WHY the algorithm is responding this way>"
  },
  "action_plan": {
    "priority": "<Immediate | This Week | This Month>",
    "steps": [
      {
        "step_number": <integer>,
        "action": "<concise action title>",
        "detail": "<specific tactical instruction — not generic advice>",
        "expected_impact": "<what metric this improves and by how much>"
      }
    ]
  },
  "viral_assets": {
    "niche": "<user niche>",
    "title_variations": ["<title 1>", "<title 2>", "<title 3>"],
    "hook_scripts": [
      {"hook_type": "<Pattern Interrupt | Curiosity | Pain-Point | Bold Claim>", "script": "<15-30 word verbatim hook>"},
      {"hook_type": "<Pattern Interrupt | Curiosity | Pain-Point | Bold Claim>", "script": "<15-30 word verbatim hook>"}
    ]
  }
}""".strip()


def build_prompt(metrics: object) -> str:
    ctx = metrics.to_prompt_context()

    if isinstance(metrics, YouTubeLongMetrics):
        persona = "You are a senior YouTube growth consultant who has helped creators go from 0 to 500K subscribers. Be brutally honest and hyper-specific to the numbers — never say 'CTR is low', say exactly how far below benchmark it is and what thumbnail/title issue causes it."
    elif isinstance(metrics, YouTubeShortsMetrics):
        persona = "You are a YouTube Shorts algorithm expert who reverse-engineers virality. Shorts are judged by loop rate and AVD%. Focus the action plan on hook (0-2 sec), loop triggers, vertical pacing, and comment-bait techniques."
    elif isinstance(metrics, InstagramMetrics):
        pname = "Instagram" if metrics.platform == Platform.INSTAGRAM else "Threads"
        persona = f"You are an Instagram and Meta algorithm specialist. Saves and shares are the highest-weight signals for {pname} distribution — calibrate severity flags accordingly. Viral assets should be formatted as Reel concepts or post hooks for {pname}."
    elif isinstance(metrics, MessagingMetrics):
        pname = "WhatsApp Business" if metrics.platform == Platform.WHATSAPP else "Facebook Messenger"
        persona = f"You are a conversational marketing expert specialising in {pname} broadcast campaigns. Key signals: open rate (list health + timing), reply rate (message relevance + CTA), opt-out rate (content-audience fit). For viral_assets, replace title_variations with 3 high-converting message opening lines, and hook_scripts with 2 full broadcast message openers (first 2-3 sentences) that maximise open-to-reply conversion."
    else:
        raise TypeError(f"Unknown metrics type: {type(metrics).__name__}")

    return f"{persona}\n\n{ctx}\n\nAUDIT TASK: Perform a deep algorithmic audit of the above metrics.\n\n{_OUTPUT_SCHEMA}"


# ═══════════════════════════════════════════════════════════════════════════════
# [4] STREAMLIT UI
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Viral Engine · AI Audit Suite",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #080808; color: #EDECE8; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 1rem 4rem 1rem; max-width: 720px; margin: auto; }

[data-testid="stSidebar"] { background: #0F0F0F; border-right: 1px solid #1F1F1F; }
[data-testid="stSidebar"] label { color: #999 !important; font-size: 0.8rem !important; }
[data-testid="stSidebar"] .stSelectbox > div > div { background: #1A1A1A !important; border: 1px solid #2A2A2A !important; border-radius: 8px !important; color: #EDECE8 !important; }
[data-testid="stSidebar"] .stTextInput > div > div > input { background: #1A1A1A !important; border: 1px solid #2A2A2A !important; border-radius: 8px !important; color: #EDECE8 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.8rem !important; }

.hero { padding: 3rem 0 2rem 0; text-align: center; border-bottom: 1px solid #1A1A1A; margin-bottom: 2rem; }
.hero-eyebrow { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: #F97316; margin-bottom: 0.8rem; }
.hero-title { font-family: 'Syne', sans-serif; font-size: clamp(1.9rem, 6vw, 2.8rem); font-weight: 800; line-height: 1.05; letter-spacing: -0.03em; margin: 0 0 0.7rem 0; color: #FFF; }
.hero-title span { color: #F97316; }
.hero-sub { font-size: 0.92rem; color: #666; margin: 0; line-height: 1.5; }

.section-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; letter-spacing: 0.15em; text-transform: uppercase; color: #F97316; margin: 1.6rem 0 0.6rem 0; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div { background-color: #161616 !important; border: 1px solid #252525 !important; border-radius: 8px !important; color: #EDECE8 !important; font-size: 0.92rem !important; }
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus { border-color: #F97316 !important; box-shadow: 0 0 0 2px rgba(249,115,22,0.15) !important; }
label { color: #999 !important; font-size: 0.82rem !important; font-weight: 500 !important; }

.stButton > button[kind="primary"] { width: 100%; background: #F97316 !important; color: #000 !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 0.95rem !important; padding: 0.75rem 1rem !important; letter-spacing: 0.03em; font-family: 'IBM Plex Mono', monospace !important; }
.stButton > button[kind="primary"]:hover { background: #ea6a0d !important; }

.score-ring { display: flex; align-items: center; gap: 1.2rem; background: #0D0D0D; border: 1px solid #1E1E1E; border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 1rem; }
.score-number { font-family: 'Syne', sans-serif; font-size: 3rem; font-weight: 800; line-height: 1; min-width: 80px; }
.score-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; color: #666; margin-bottom: 0.2rem; }
.score-health { font-size: 1.1rem; font-weight: 700; }

.flag-chip { display: inline-flex; align-items: flex-start; gap: 0.4rem; background: #161616; border-radius: 6px; padding: 0.5rem 0.85rem; margin: 0.3rem 0.3rem 0 0; font-size: 0.82rem; border-left: 3px solid transparent; width: 100%; box-sizing: border-box; }
.flag-critical { border-left-color: #EF4444; }
.flag-warning  { border-left-color: #F97316; }
.flag-info     { border-left-color: #3B82F6; }
.flag-metric   { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #888; }
.flag-fault    { color: #EDECE8; margin-top: 0.2rem; }

.verdict-block { background: #0D0D0D; border-left: 3px solid #F97316; border-radius: 0 8px 8px 0; padding: 1rem 1.1rem; font-size: 0.92rem; line-height: 1.65; color: #CCC; margin: 0.8rem 0; }

.badge { display: inline-block; font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase; padding: 0.25rem 0.7rem; border-radius: 4px; font-weight: 600; }
.badge-suppressed { background: #2D1111; color: #EF4444; }
.badge-neutral    { background: #1A1A1A; color: #888; }
.badge-favoured   { background: #102010; color: #22C55E; }
.badge-viral      { background: #1A1000; color: #F97316; }
.badge-poor       { background: #2D1111; color: #EF4444; }
.badge-fair       { background: #1A1500; color: #EAB308; }
.badge-good       { background: #102010; color: #22C55E; }
.badge-excellent  { background: #0D1A10; color: #4ADE80; }

.step-card { display: flex; gap: 1rem; background: #111; border: 1px solid #1E1E1E; border-radius: 10px; padding: 1rem 1.1rem; margin-bottom: 0.6rem; }
.step-num { font-family: 'IBM Plex Mono', monospace; font-size: 1.2rem; font-weight: 600; color: #F97316; min-width: 2rem; padding-top: 0.05rem; }
.step-action { font-weight: 600; color: #EDECE8; font-size: 0.92rem; margin-bottom: 0.3rem; }
.step-detail { color: #888; font-size: 0.85rem; line-height: 1.55; }
.step-impact { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #22C55E; margin-top: 0.4rem; }

.title-chip { background: #0D0D0D; border: 1px solid #252525; border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.92rem; color: #EDECE8; margin-bottom: 0.5rem; line-height: 1.4; }
.hook-card { background: #0D0D0D; border: 1px solid #252525; border-radius: 10px; padding: 1rem 1.1rem; margin-bottom: 0.6rem; }
.hook-type { font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase; color: #F97316; margin-bottom: 0.5rem; }
.hook-script { font-size: 0.92rem; color: #EDECE8; line-height: 1.55; }

.provider-pill { display: inline-block; background: #1A0F00; color: #F97316; border: 1px solid #3A2000; border-radius: 4px; font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; letter-spacing: 0.06em; padding: 0.2rem 0.6rem; }

hr { border-color: #1A1A1A; margin: 1.5rem 0; }
.stAlert { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "audit_result" not in st.session_state:
    st.session_state.audit_result = None

# ── Sidebar — Settings ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")

    st.markdown("**AI Engine**")
    provider_display = {PROVIDER_LABELS[p]: p for p in Provider}
    selected_label = st.selectbox("Active provider", list(provider_display.keys()), label_visibility="collapsed")
    active_provider: Provider = provider_display[selected_label]

    st.markdown(f"**API Key · {selected_label.split('·')[0].strip()}**")
    api_key_input = st.text_input("API key", type="password", placeholder="Paste your API key here…", label_visibility="collapsed")

    if api_key_input:
        st.markdown('<div class="provider-pill">✓ KEY LOADED</div>', unsafe_allow_html=True)
    else:
        st.caption("No key entered.")

    st.markdown("---")
    st.caption("Keys are stored in your session only. Never logged or transmitted.")
    st.markdown("**Get API Keys**")
    st.markdown(
        "- [OpenAI](https://platform.openai.com/api-keys)\n"
        "- [Anthropic](https://console.anthropic.com/)\n"
        "- [Google AI Studio](https://aistudio.google.com/app/apikey) *(Free)*\n"
        "- [Groq Cloud](https://console.groq.com/keys) *(Free)*"
    )

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">⚡ AI-Powered Growth Intelligence</div>
  <h1 class="hero-title">Social Media<br><span>Audit & Viral Engine</span></h1>
  <p class="hero-sub">Feed your metrics. Get an algorithmic autopsy, suppression diagnosis,<br>a step-by-step action plan, and viral assets — in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ── Platform selector ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label">01 · Select Platform</div>', unsafe_allow_html=True)
platform_display = {f"{PLATFORM_ICONS[p]}  {PLATFORM_LABELS[p]}": p for p in Platform}
active_platform: Platform = platform_display[st.selectbox("Platform", list(platform_display.keys()), label_visibility="collapsed")]

# ── Dynamic metric forms ──────────────────────────────────────────────────────
st.markdown('<div class="section-label">02 · Enter Your Metrics</div>', unsafe_allow_html=True)

metrics_obj = None
input_error = None

if active_platform == Platform.YOUTUBE_LONG:
    niche = st.text_input("Your niche / content topic", placeholder="e.g. Personal Finance for Gen Z")
    description = st.text_area("What is this video about?", placeholder="e.g. How I saved ₹1 Lakh in 6 months on a ₹25K salary", height=80)
    c1, c2, c3 = st.columns(3)
    impressions = c1.number_input("Impressions", min_value=0, value=10000)
    views       = c2.number_input("Views", min_value=0, value=500)
    ctr         = c3.number_input("CTR %", min_value=0.0, max_value=100.0, value=5.0, step=0.1, format="%.2f")
    c4, c5 = st.columns(2)
    avd_pct = c4.number_input("AVD %", min_value=0.0, max_value=100.0, value=42.0, step=0.1, format="%.1f")
    avd_min = c5.number_input("AVD (minutes)", min_value=0.0, value=3.5, step=0.1, format="%.1f")
    c6, c7, c8 = st.columns(3)
    likes    = c6.number_input("Likes", min_value=0, value=40)
    comments = c7.number_input("Comments", min_value=0, value=8)
    subs     = c8.number_input("Subs Gained", min_value=0, value=5)
    try:
        metrics_obj = YouTubeLongMetrics(niche=niche, content_description=description, impressions=impressions, views=views, ctr_percent=ctr, avd_percent=avd_pct, avd_minutes=avd_min, likes=likes, comments=comments, subscribers_gained=subs)
    except ValueError as e:
        input_error = str(e)

elif active_platform == Platform.YOUTUBE_SHORTS:
    niche = st.text_input("Your niche / content topic", placeholder="e.g. Gym Motivation & Fitness Tips")
    description = st.text_area("What is this Short about?", placeholder="e.g. 5 foods that destroy your testosterone", height=80)
    c1, c2 = st.columns(2)
    views   = c1.number_input("Views", min_value=0, value=15000)
    avd_pct = c2.number_input("AVD %", min_value=0.0, max_value=100.0, value=68.0, step=0.1)
    c3, c4, c5 = st.columns(3)
    likes    = c3.number_input("Likes", min_value=0, value=320)
    comments = c4.number_input("Comments", min_value=0, value=45)
    shares   = c5.number_input("Shares", min_value=0, value=18)
    subs     = st.number_input("Subscribers Gained", min_value=0, value=60)
    try:
        metrics_obj = YouTubeShortsMetrics(niche=niche, content_description=description, views=views, likes=likes, comments=comments, shares=shares, avd_percent=avd_pct, subscribers_gained=subs)
    except ValueError as e:
        input_error = str(e)

elif active_platform in (Platform.INSTAGRAM, Platform.THREADS):
    niche = st.text_input("Your niche / content topic", placeholder="e.g. Productivity & Study Tips")
    description = st.text_area("What is this post / Reel about?", placeholder="e.g. Morning routine of a CA student", height=80)
    content_type = st.selectbox("Content type", ["Reel", "Carousel", "Static Post"])
    c1, c2 = st.columns(2)
    plays    = c1.number_input("Plays / Reach", min_value=0, value=8000)
    likes    = c2.number_input("Likes", min_value=0, value=210)
    c3, c4, c5 = st.columns(3)
    comments = c3.number_input("Comments", min_value=0, value=28)
    saves    = c4.number_input("Saves", min_value=0, value=95)
    shares   = c5.number_input("Shares", min_value=0, value=40)
    c6, c7 = st.columns(2)
    follows = c6.number_input("Follows Gained", min_value=0, value=35)
    visits  = c7.number_input("Profile Visits", min_value=0, value=180)
    try:
        metrics_obj = InstagramMetrics(platform=active_platform, niche=niche, content_description=description, content_type=content_type, plays_or_reach=plays, likes=likes, comments=comments, saves=saves, shares=shares, follows_gained=follows, profile_visits=visits)
    except ValueError as e:
        input_error = str(e)

elif active_platform in (Platform.WHATSAPP, Platform.MESSENGER):
    niche = st.text_input("Your niche / business type", placeholder="e.g. EdTech – Online Coaching for UPSC")
    goal  = st.text_input("Campaign goal", placeholder="e.g. Flash sale announcement, Re-engagement, New batch launch")
    c1, c2 = st.columns(2)
    sent   = c1.number_input("Messages Sent", min_value=0, value=2400)
    opened = c2.number_input("Opened / Read", min_value=0, value=1800)
    c3, c4 = st.columns(2)
    open_rt  = c3.number_input("Open Rate %", min_value=0.0, max_value=100.0, value=75.0, step=0.1)
    replies  = c4.number_input("Replies", min_value=0, value=90)
    c5, c6, c7 = st.columns(3)
    reply_rt = c5.number_input("Reply Rate %", min_value=0.0, max_value=100.0, value=3.75, step=0.1)
    clicks   = c6.number_input("Link Clicks", min_value=0, value=120)
    opt_outs = c7.number_input("Opt-Outs", min_value=0, value=14)
    try:
        metrics_obj = MessagingMetrics(platform=active_platform, niche=niche, campaign_goal=goal, messages_sent=sent, messages_opened=opened, open_rate=open_rt, replies=replies, reply_rate=reply_rt, link_clicks=clicks, opt_outs=opt_outs)
    except ValueError as e:
        input_error = str(e)

if input_error:
    st.error(f"⚠️ Input error: {input_error}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Generate ──────────────────────────────────────────────────────────────────
run_audit = st.button("⚡ Run Full AI Audit", type="primary", use_container_width=True)

if run_audit:
    if not api_key_input or not api_key_input.strip():
        st.error(f"⚠️ No API key for **{PROVIDER_LABELS[active_provider]}**. Add it in the Settings panel.")
        st.stop()
    if input_error or metrics_obj is None:
        st.error("⚠️ Fix the input errors above before running the audit.")
        st.stop()
    with st.spinner("Running algorithmic audit… 10–25 seconds"):
        try:
            result = run_prompt(
                provider=active_provider,
                api_key=api_key_input.strip(),
                prompt=build_prompt(metrics_obj),
                max_tokens=2000,
            )
            st.session_state.audit_result = result
        except ValueError as e:
            st.error(f"⚠️ {e}"); st.stop()
        except RuntimeError as e:
            st.error(f"⚠️ {e}"); st.stop()
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {e}"); st.stop()

# ── Results renderer ──────────────────────────────────────────────────────────
def _score_color(s: int) -> str:
    return "#22C55E" if s >= 75 else ("#F97316" if s >= 50 else "#EF4444")

def render_results(data: dict):
    diag  = data.get("diagnostics", {})
    behav = data.get("behavioral_analysis", {})
    plan  = data.get("action_plan", {})
    viral = data.get("viral_assets", {})

    # 1. Diagnostics
    st.markdown('<div class="section-label">Diagnostics</div>', unsafe_allow_html=True)
    score = diag.get("overall_health_score", 0)
    sc = _score_color(score)
    st.markdown(f"""<div class="score-ring">
      <div class="score-number" style="color:{sc}">{score}</div>
      <div>
        <div class="score-label">Overall Health Score</div>
        <div class="score-health" style="color:{sc}">{diag.get("health_label","—")}</div>
        <div style="font-size:0.82rem;color:#666;margin-top:0.3rem;">Primary bottleneck: {diag.get("primary_bottleneck","—")}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    for flag in diag.get("flags", []):
        sev = flag.get("severity", "Info").lower()
        cls = {"critical": "flag-critical", "warning": "flag-warning", "info": "flag-info"}.get(sev, "flag-info")
        icon = {"critical": "🔴", "warning": "🟠", "info": "🔵"}.get(sev, "○")
        st.markdown(f"""<div class="flag-chip {cls}"><div>
          <div class="flag-metric">{icon} {flag.get("metric","—")} · observed: {flag.get("value","—")} · target: {flag.get("benchmark","—")}</div>
          <div class="flag-fault">{flag.get("fault","—")}</div>
        </div></div>""", unsafe_allow_html=True)

    # 2. Behavioral analysis
    st.markdown('<div class="section-label">Behavioral Analysis</div>', unsafe_allow_html=True)
    algo = behav.get("algorithm_status", "Neutral")
    aud  = behav.get("audience_signal_quality", "Fair")
    con  = behav.get("content_signal_quality", "Fair")
    ALGO = {"suppressed":"badge-suppressed","neutral":"badge-neutral","favoured":"badge-favoured","viral":"badge-viral"}
    SIG  = {"poor":"badge-poor","fair":"badge-fair","good":"badge-good","excellent":"badge-excellent"}

    c1, c2, c3 = st.columns(3)
    for col, lbl, val, mapping in [
        (c1, "Algorithm Status", algo, ALGO),
        (c2, "Audience Signal",  aud,  SIG),
        (c3, "Content Signal",   con,  SIG),
    ]:
        col.markdown(f"""<div style="text-align:center">
          <div class="score-label" style="text-align:center">{lbl}</div>
          <div style="margin-top:0.4rem"><span class="badge {mapping.get(val.lower(),'badge-neutral')}">{val}</span></div>
        </div>""", unsafe_allow_html=True)

    reasons = behav.get("suppression_reasons", [])
    if reasons:
        st.markdown("<br>**Suppression Factors**", unsafe_allow_html=True)
        for r in reasons:
            st.markdown(f"- {r}")

    if behav.get("verdict"):
        st.markdown(f'<div class="verdict-block">{behav["verdict"]}</div>', unsafe_allow_html=True)

    # 3. Action plan
    st.markdown('<div class="section-label">Custom Action Plan</div>', unsafe_allow_html=True)
    if plan.get("priority"):
        st.markdown(f"**Priority level:** `{plan['priority']}`")
    for step in plan.get("steps", []):
        st.markdown(f"""<div class="step-card">
          <div class="step-num">#{step.get("step_number","")}</div>
          <div>
            <div class="step-action">{step.get("action","")}</div>
            <div class="step-detail">{step.get("detail","")}</div>
            <div class="step-impact">↑ {step.get("expected_impact","")}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # 4. Viral assets
    st.markdown('<div class="section-label">Instant Viral Assets</div>', unsafe_allow_html=True)
    if viral.get("niche"):
        st.markdown(f"**Niche:** {viral['niche']}")
    if viral.get("title_variations"):
        st.markdown("**High-Converting Titles / Subject Lines**")
        for i, t in enumerate(viral["title_variations"], 1):
            st.markdown(f"""<div class="title-chip"><span style="color:#F97316;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;margin-right:0.6rem;">T{i}</span>{t}</div>""", unsafe_allow_html=True)
    if viral.get("hook_scripts"):
        st.markdown("<br>**Hook Scripts**", unsafe_allow_html=True)
        for hook in viral["hook_scripts"]:
            st.markdown(f"""<div class="hook-card">
              <div class="hook-type">{hook.get("hook_type","")}</div>
              <div class="hook-script">"{hook.get("script","")}"</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""<hr><p style='text-align:center;color:#333;font-size:0.75rem;font-family:"IBM Plex Mono",monospace;'>VIRAL ENGINE · AUDIT COMPLETE</p>""", unsafe_allow_html=True)


if st.session_state.audit_result:
    st.markdown("---")
    st.markdown('<div class="section-label">Audit Results</div>', unsafe_allow_html=True)
    render_results(st.session_state.audit_result)
