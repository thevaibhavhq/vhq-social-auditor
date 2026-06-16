"""
VHQ-SOCIAL-AUDITOR
Phase 1 — Premium UI Shell (glassmorphic, neon 3D header, animations)
Phase 2 — Supabase Auth (signup / login / profile onboarding with age-gate)
"""

import streamlit as st
from supabase import create_client, Client
from datetime import date, datetime, timedelta

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="VHQ · Social Auditor",
    page_icon="⬡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Orbitron:wght@700;900&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
  font-family: 'Space Grotesk', sans-serif;
  background: #050508;
  color: #E8E6F0;
  -webkit-font-smoothing: antialiased;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding: 0 1rem 5rem 1rem;
  max-width: 680px;
  margin: auto;
}

/* ══════════════════════════════════════════
   3D NEON HEADER
══════════════════════════════════════════ */
@keyframes neonPulse {
  0%, 100% {
    text-shadow:
      0 0 6px #fff,
      0 0 20px #a78bfa,
      0 0 40px #7c3aed,
      0 0 80px #7c3aed,
      0 2px 0 #4c1d95,
      0 4px 0 #3b0764,
      0 6px 10px rgba(0,0,0,0.6);
  }
  50% {
    text-shadow:
      0 0 10px #fff,
      0 0 30px #c4b5fd,
      0 0 60px #a78bfa,
      0 0 100px #7c3aed,
      0 2px 0 #4c1d95,
      0 4px 0 #3b0764,
      0 6px 14px rgba(0,0,0,0.7);
  }
}

@keyframes scanline {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
}

@keyframes fadeSlideDown {
  from { opacity: 0; transform: translateY(-18px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes glowBorder {
  0%, 100% { box-shadow: 0 0 8px rgba(124,58,237,0.4), inset 0 0 8px rgba(124,58,237,0.05); }
  50%       { box-shadow: 0 0 20px rgba(167,139,250,0.5), inset 0 0 12px rgba(124,58,237,0.08); }
}

@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position: 200% center; }
}

@keyframes badgePop {
  0%   { transform: scale(0.8); opacity: 0; }
  60%  { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}

/* ── Header wrapper ── */
.vhq-header {
  position: relative;
  text-align: center;
  padding: 3rem 1rem 2.2rem 1rem;
  overflow: hidden;
  animation: fadeSlideDown 0.7s ease both;
}

/* Scanline overlay */
.vhq-header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(167,139,250,0.6), transparent);
  animation: scanline 4s linear infinite;
  pointer-events: none;
}

/* Top rule */
.vhq-header::after {
  content: '';
  position: absolute;
  bottom: 0; left: 10%; right: 10%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(124,58,237,0.5), transparent);
}

.vhq-eyebrow {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgba(167,139,250,0.7);
  margin-bottom: 0.8rem;
  animation: fadeSlideDown 0.6s ease 0.1s both;
}

.vhq-logo {
  font-family: 'Orbitron', monospace;
  font-size: clamp(1.55rem, 6vw, 2.3rem);
  font-weight: 900;
  letter-spacing: 0.08em;
  color: #fff;
  animation: neonPulse 3s ease-in-out infinite, fadeSlideDown 0.7s ease 0.2s both;
  line-height: 1.1;
  user-select: none;
}

.vhq-tagline {
  font-size: 0.82rem;
  color: rgba(167,139,250,0.6);
  letter-spacing: 0.06em;
  margin-top: 0.7rem;
  font-family: 'IBM Plex Mono', monospace;
  animation: fadeSlideDown 0.7s ease 0.35s both;
}

.vhq-version {
  display: inline-block;
  background: rgba(124,58,237,0.15);
  border: 1px solid rgba(124,58,237,0.35);
  color: #a78bfa;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  padding: 0.2rem 0.7rem;
  border-radius: 20px;
  margin-top: 0.7rem;
  animation: badgePop 0.5s ease 0.5s both;
}

/* ══════════════════════════════════════════
   GLASS PANELS
══════════════════════════════════════════ */
.glass-card {
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 18px;
  padding: 1.8rem 1.6rem;
  margin-bottom: 1.1rem;
  animation: glowBorder 4s ease-in-out infinite, fadeSlideUp 0.5s ease both;
  position: relative;
  overflow: hidden;
}

/* inner top glow line */
.glass-card::before {
  content: '';
  position: absolute;
  top: 0; left: 15%; right: 15%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(167,139,250,0.4), transparent);
}

.glass-card-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #7c3aed;
  margin-bottom: 1rem;
}

/* ══════════════════════════════════════════
   INPUT OVERRIDES
══════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input,
.stSelectbox > div > div {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(124,58,237,0.3) !important;
  border-radius: 10px !important;
  color: #E8E6F0 !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 0.92rem !important;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: #7c3aed !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.18) !important;
  outline: none !important;
}
label, .stSelectbox label, .stTextInput label,
.stTextArea label, .stDateInput label {
  color: rgba(167,139,250,0.75) !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.03em !important;
}

/* ══════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════ */
/* Primary CTA */
.stButton > button[kind="primary"] {
  width: 100%;
  background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #7c3aed 100%) !important;
  background-size: 200% auto !important;
  color: #fff !important;
  border: none !important;
  border-radius: 12px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.95rem !important;
  padding: 0.75rem 1.2rem !important;
  letter-spacing: 0.04em;
  transition: background-position 0.4s ease, transform 0.15s ease, box-shadow 0.2s ease !important;
  box-shadow: 0 4px 20px rgba(124,58,237,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
  background-position: right center !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 28px rgba(124,58,237,0.5) !important;
}
.stButton > button[kind="primary"]:active {
  transform: translateY(0) !important;
}

/* Secondary */
.stButton > button[kind="secondary"] {
  width: 100%;
  background: rgba(255,255,255,0.04) !important;
  color: rgba(167,139,250,0.85) !important;
  border: 1px solid rgba(124,58,237,0.3) !important;
  border-radius: 12px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 0.88rem !important;
  transition: border-color 0.2s ease, background 0.2s ease !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: rgba(124,58,237,0.6) !important;
  background: rgba(124,58,237,0.08) !important;
}

/* ══════════════════════════════════════════
   SECTION LABEL
══════════════════════════════════════════ */
.section-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(124,58,237,0.8);
  margin: 1.8rem 0 0.7rem 0;
}

/* ══════════════════════════════════════════
   AUTH TAB TOGGLE
══════════════════════════════════════════ */
.auth-toggle {
  display: flex;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(124,58,237,0.2);
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 1.4rem;
  gap: 4px;
}
.auth-tab {
  flex: 1;
  text-align: center;
  padding: 0.5rem;
  border-radius: 9px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  color: rgba(167,139,250,0.5);
}
.auth-tab-active {
  background: linear-gradient(135deg, #7c3aed, #a855f7);
  color: #fff;
  box-shadow: 0 2px 12px rgba(124,58,237,0.4);
}

/* ══════════════════════════════════════════
   DASHBOARD NAV PILLS
══════════════════════════════════════════ */
.nav-bar {
  display: flex;
  gap: 0.5rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(124,58,237,0.15);
  border-radius: 14px;
  padding: 6px;
  margin-bottom: 1.4rem;
  flex-wrap: wrap;
}
.nav-pill {
  flex: 1;
  min-width: 80px;
  text-align: center;
  padding: 0.45rem 0.5rem;
  border-radius: 10px;
  font-size: 0.78rem;
  font-weight: 600;
  color: rgba(167,139,250,0.5);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}
.nav-pill-active {
  background: rgba(124,58,237,0.2);
  color: #c4b5fd;
  border: 1px solid rgba(124,58,237,0.4);
}

/* ══════════════════════════════════════════
   PROFILE AVATAR RING
══════════════════════════════════════════ */
.avatar-ring {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed, #a855f7, #ec4899);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 0.6rem auto;
  font-size: 1.8rem;
  box-shadow: 0 0 20px rgba(124,58,237,0.4);
  animation: glowBorder 3s ease-in-out infinite;
}

/* ══════════════════════════════════════════
   STAT CHIPS
══════════════════════════════════════════ */
.stat-row {
  display: flex;
  gap: 0.6rem;
  margin-top: 0.8rem;
}
.stat-chip {
  flex: 1;
  background: rgba(124,58,237,0.08);
  border: 1px solid rgba(124,58,237,0.2);
  border-radius: 10px;
  padding: 0.6rem 0.4rem;
  text-align: center;
}
.stat-chip-value {
  font-family: 'Orbitron', monospace;
  font-size: 1.1rem;
  font-weight: 700;
  color: #a78bfa;
}
.stat-chip-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(167,139,250,0.5);
  margin-top: 0.15rem;
}

/* ══════════════════════════════════════════
   AGE GATE BANNER
══════════════════════════════════════════ */
.age-gate-banner {
  background: rgba(239,68,68,0.08);
  border: 1px solid rgba(239,68,68,0.35);
  border-radius: 12px;
  padding: 0.85rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.7rem;
  font-size: 0.85rem;
  color: #fca5a5;
  margin-bottom: 1rem;
  animation: fadeSlideUp 0.3s ease both;
}

/* ══════════════════════════════════════════
   SUCCESS BANNER
══════════════════════════════════════════ */
.success-banner {
  background: rgba(34,197,94,0.08);
  border: 1px solid rgba(34,197,94,0.3);
  border-radius: 12px;
  padding: 0.85rem 1rem;
  font-size: 0.85rem;
  color: #86efac;
  margin-bottom: 1rem;
  animation: fadeSlideUp 0.3s ease both;
}

/* ══════════════════════════════════════════
   SHIMMER DIVIDER
══════════════════════════════════════════ */
.shimmer-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(167,139,250,0.4) 50%, transparent);
  margin: 1.4rem 0;
  background-size: 200% auto;
  animation: shimmer 3s linear infinite;
}

/* ══════════════════════════════════════════
   FOOTER
══════════════════════════════════════════ */
.vhq-footer {
  text-align: center;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  color: rgba(124,58,237,0.35);
  margin-top: 3rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(124,58,237,0.1);
}

/* Misc */
.stAlert { border-radius: 10px !important; }
hr { border-color: rgba(124,58,237,0.12); }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SUPABASE CLIENT
# ═══════════════════════════════════════════════════════════════
@st.cache_resource
def init_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_ANON_KEY"],
    )

supabase = init_supabase()


# ═══════════════════════════════════════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════════════════════════════════════
def auth_signup(email: str, password: str):
    return supabase.auth.sign_up({"email": email, "password": password})

def auth_login(email: str, password: str):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def auth_logout():
    supabase.auth.sign_out()

def get_profile(user_id: str) -> dict | None:
    res = supabase.table("profiles").select("*").eq("id", user_id).execute()
    return res.data[0] if res.data else None

def save_profile(user_id: str, full_name: str, bio: str, dob: str) -> dict:
    """Upsert the profile row after successful onboarding."""
    return supabase.table("profiles").upsert({
        "id": user_id,
        "full_name": full_name,
        "bio": bio,
        "dob": dob,
        "onboarded": True,
        "tier": "free",
        "updated_at": datetime.utcnow().isoformat(),
    }).execute()

def age_from_dob(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


# ═══════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════
defaults = {
    "authenticated": False,
    "user_id": None,
    "user_email": None,
    "onboarded": False,
    "profile": None,
    "auth_mode": "login",     # "login" | "signup"
    "active_tab": "Audit",   # dashboard tab
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════
# VHQ HEADER (always visible)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="vhq-header">
  <div class="vhq-eyebrow">⬡ Powered by Multi-LLM Intelligence</div>
  <div class="vhq-logo">VHQ · SOCIAL<br>AUDITOR</div>
  <div class="vhq-tagline">Algorithmic Diagnostics · Viral Growth Engine · AI Analytics</div>
  <div class="vhq-version">v2.0 · PHASE 1 + 2 LIVE</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# ── PAGE: AUTH ──────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════
if not st.session_state.authenticated:

    is_login = st.session_state.auth_mode == "login"

    # Toggle tabs
    st.markdown(f"""
    <div class="auth-toggle">
      <div class="auth-tab {'auth-tab-active' if is_login else ''}">Sign In</div>
      <div class="auth-tab {'auth-tab-active' if not is_login else ''}">Create Account</div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    if col_a.button("Sign In", type="primary" if is_login else "secondary", use_container_width=True):
        st.session_state.auth_mode = "login"
        st.rerun()
    if col_b.button("Create Account", type="primary" if not is_login else "secondary", use_container_width=True):
        st.session_state.auth_mode = "signup"
        st.rerun()

    st.markdown('<div class="shimmer-divider"></div>', unsafe_allow_html=True)

    # Auth form
    st.markdown(f'<div class="glass-card"><div class="glass-card-label">{"— Sign In —" if is_login else "— New Account —"}</div>', unsafe_allow_html=True)

    email    = st.text_input("Email address", placeholder="you@email.com", key="auth_email")
    password = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="auth_pw")

    if is_login:
        submit = st.button("⬡  Sign In to VHQ", type="primary", use_container_width=True)
    else:
        submit = st.button("⬡  Create My Account", type="primary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if submit:
        if not email.strip() or not password.strip():
            st.markdown('<div class="age-gate-banner">⚠ Please fill in both email and password.</div>', unsafe_allow_html=True)
        elif len(password) < 6:
            st.markdown('<div class="age-gate-banner">⚠ Password must be at least 6 characters.</div>', unsafe_allow_html=True)
        else:
            try:
                if is_login:
                    res  = auth_login(email.strip().lower(), password)
                    user = res.user
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id       = user.id
                        st.session_state.user_email    = user.email
                        profile = get_profile(user.id)
                        st.session_state.profile    = profile
                        st.session_state.onboarded  = bool(profile and profile.get("onboarded"))
                        st.rerun()
                    else:
                        st.markdown('<div class="age-gate-banner">⚠ Invalid email or password.</div>', unsafe_allow_html=True)
                else:
                    res  = auth_signup(email.strip().lower(), password)
                    user = res.user
                    if user:
                        st.markdown('<div class="success-banner">✓ Account created! Check your email to confirm, then sign in.</div>', unsafe_allow_html=True)
                        st.session_state.auth_mode = "login"
                    else:
                        st.markdown('<div class="age-gate-banner">⚠ Could not create account. Try a different email.</div>', unsafe_allow_html=True)
            except Exception as e:
                msg = str(e).lower()
                if "already registered" in msg or "already exists" in msg:
                    st.markdown('<div class="age-gate-banner">⚠ Email already registered. Sign in instead.</div>', unsafe_allow_html=True)
                elif "invalid login" in msg or "invalid credentials" in msg:
                    st.markdown('<div class="age-gate-banner">⚠ Wrong email or password.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="age-gate-banner">⚠ Auth error: {str(e)[:120]}</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="vhq-footer">
      VHQ · SOCIAL AUDITOR &nbsp;·&nbsp; PHASE 1 + 2 &nbsp;·&nbsp; BUILD 2025
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════
# ── PAGE: PROFILE ONBOARDING ───────────────────────────────────
# ═══════════════════════════════════════════════════════════════
if not st.session_state.onboarded:

    st.markdown('<div class="section-label">⬡ &nbsp; Complete Your Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="glass-card-label">— Profile Setup —</div>', unsafe_allow_html=True)

    full_name = st.text_input("Full Name", placeholder="e.g. Vaibhav Sharma", key="ob_name")
    bio       = st.text_area("Bio", placeholder="Tell us what you create or build…", height=90, key="ob_bio")
    dob       = st.date_input(
        "Date of Birth",
        value=date(2000, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date.today(),
        key="ob_dob",
    )

    # Live age-gate feedback
    if dob:
        age = age_from_dob(dob)
        if age < 13:
            st.markdown(f'<div class="age-gate-banner">🔒 You must be 13 or older to use VHQ. Detected age: {age}.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-banner">✓ Age verified &nbsp;({age} years old)</div>', unsafe_allow_html=True)

    save = st.button("⬡  Save Profile & Enter VHQ", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if save:
        if not full_name.strip():
            st.markdown('<div class="age-gate-banner">⚠ Full name is required.</div>', unsafe_allow_html=True)
        elif not dob:
            st.markdown('<div class="age-gate-banner">⚠ Date of birth is required.</div>', unsafe_allow_html=True)
        elif age_from_dob(dob) < 13:
            st.markdown('<div class="age-gate-banner">🔒 You must be 13 or older to continue.</div>', unsafe_allow_html=True)
        else:
            try:
                save_profile(
                    user_id=st.session_state.user_id,
                    full_name=full_name.strip(),
                    bio=bio.strip(),
                    dob=str(dob),
                )
                st.session_state.onboarded = True
                st.session_state.profile   = get_profile(st.session_state.user_id)
                st.markdown('<div class="success-banner">✓ Profile saved! Loading your dashboard…</div>', unsafe_allow_html=True)
                st.rerun()
            except Exception as e:
                st.markdown(f'<div class="age-gate-banner">⚠ Could not save profile: {str(e)[:120]}</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="vhq-footer">VHQ · SOCIAL AUDITOR &nbsp;·&nbsp; SETUP</div>
    """, unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════
# ── PAGE: DASHBOARD (authenticated + onboarded) ────────────────
# ═══════════════════════════════════════════════════════════════
profile    = st.session_state.profile or {}
full_name  = profile.get("full_name", "Creator")
tier       = profile.get("tier", "free").upper()
initials   = "".join(w[0] for w in full_name.split()[:2]).upper() or "VH"
tier_color = "#f59e0b" if tier == "FREE" else "#a78bfa"

# ── Profile card ──────────────────────────────────────────────
st.markdown(f"""
<div class="glass-card" style="text-align:center; animation-delay:0.05s">
  <div class="avatar-ring">{initials}</div>
  <div style="font-size:1.05rem; font-weight:700; letter-spacing:0.02em;">{full_name}</div>
  <div style="font-size:0.78rem; color:rgba(167,139,250,0.6); margin:0.2rem 0 0.5rem;">
    {st.session_state.user_email}
  </div>
  <span style="
    display:inline-block;
    background:rgba(124,58,237,0.15);
    border:1px solid {tier_color}55;
    color:{tier_color};
    font-family:'IBM Plex Mono',monospace;
    font-size:0.62rem;
    letter-spacing:0.14em;
    padding:0.2rem 0.8rem;
    border-radius:20px;
  ">{tier} PLAN</span>
  <div class="stat-row">
    <div class="stat-chip">
      <div class="stat-chip-value">0</div>
      <div class="stat-chip-label">Audits</div>
    </div>
    <div class="stat-chip">
      <div class="stat-chip-value">—</div>
      <div class="stat-chip-label">Reports</div>
    </div>
    <div class="stat-chip">
      <div class="stat-chip-value">∞</div>
      <div class="stat-chip-label">Potential</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Nav tabs ──────────────────────────────────────────────────
tabs = ["⬡ Audit", "◈ Reports", "◉ Profile", "⚙ Settings"]
tab_keys = ["Audit", "Reports", "Profile", "Settings"]

active_tab = st.session_state.active_tab

st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
cols = st.columns(len(tabs))
for i, (col, label, key) in enumerate(zip(cols, tabs, tab_keys)):
    is_active = (active_tab == key)
    if col.button(label, key=f"tab_{key}", type="secondary", use_container_width=True):
        st.session_state.active_tab = key
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="shimmer-divider"></div>', unsafe_allow_html=True)


# ── TAB: AUDIT ────────────────────────────────────────────────
if active_tab == "Audit":
    st.markdown('<div class="section-label">⬡ &nbsp; Platform Audit Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="glass-card-label">— Audit Module —</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding: 2rem 1rem; color: rgba(167,139,250,0.5);">
      <div style="font-size:2rem; margin-bottom:0.7rem;">⬡</div>
      <div style="font-family:'IBM Plex Mono',monospace; font-size:0.78rem; letter-spacing:0.1em;">
        AUDIT ENGINE · PHASE 3 COMING NEXT
      </div>
      <div style="font-size:0.82rem; margin-top:0.5rem; color:rgba(167,139,250,0.35);">
        Platform selector, metric inputs, and AI diagnostics will live here.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── TAB: REPORTS ─────────────────────────────────────────────
elif active_tab == "Reports":
    st.markdown('<div class="section-label">◈ &nbsp; Audit Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="glass-card-label">— Reports —</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding:2rem 1rem; color:rgba(167,139,250,0.4);">
      <div style="font-size:0.82rem; font-family:'IBM Plex Mono',monospace; letter-spacing:0.1em;">
        NO REPORTS YET · RUN YOUR FIRST AUDIT
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── TAB: PROFILE ─────────────────────────────────────────────
elif active_tab == "Profile":
    st.markdown('<div class="section-label">◉ &nbsp; Your Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="glass-card-label">— Account Details —</div>', unsafe_allow_html=True)

    st.markdown(f"**Full Name** &nbsp; `{profile.get('full_name','—')}`")
    st.markdown(f"**Bio** &nbsp; {profile.get('bio','—') or '—'}")
    st.markdown(f"**Date of Birth** &nbsp; `{profile.get('dob','—')}`")
    st.markdown(f"**Email** &nbsp; `{st.session_state.user_email}`")
    st.markdown(f"**Tier** &nbsp; `{tier}`")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.7rem;
      color:rgba(124,58,237,0.5); text-align:center; margin-top:0.5rem; letter-spacing:0.08em;">
      ⚠ Name/username edits limited to 2× per 10 days (Phase 3 enforcement)
    </div>
    """, unsafe_allow_html=True)

# ── TAB: SETTINGS ────────────────────────────────────────────
elif active_tab == "Settings":
    st.markdown('<div class="section-label">⚙ &nbsp; Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="glass-card-label">— Preferences —</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem;
      color:rgba(167,139,250,0.45); letter-spacing:0.06em; line-height:1.8;">
      ◉ &nbsp; AI Engine &nbsp;&nbsp;&nbsp; Backend-managed (Phase 3)<br>
      ◉ &nbsp; Notifications &nbsp; Phase 3<br>
      ◉ &nbsp; Upgrade to Pro &nbsp; Phase 4 (Razorpay)<br>
      ◉ &nbsp; Ad preferences &nbsp; Phase 4
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="shimmer-divider"></div>', unsafe_allow_html=True)

    if st.button("⬡  Sign Out", type="secondary", use_container_width=True):
        auth_logout()
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ── Footer ────────────────────────────────────────────────────
st.markdown("""
<div class="vhq-footer">
  VHQ · SOCIAL AUDITOR &nbsp;·&nbsp; PHASE 1 + 2 COMPLETE
  &nbsp;·&nbsp; PHASE 3 NEXT &nbsp;·&nbsp; BUILD 2025
</div>
""", unsafe_allow_html=True)
