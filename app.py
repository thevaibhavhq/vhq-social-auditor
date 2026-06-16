"""
VHQ-SOCIAL-AUDITOR — app.py
Phase 1: Premium UI Shell (neon 3D header, glassmorphic design, animations)
Phase 2: Supabase Auth (st.tabs login/signup, profile onboarding, 13+ age-gate)
"""

import streamlit as st
from supabase import create_client, Client
from datetime import date, datetime

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
# DESIGN SYSTEM & CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Orbitron:wght@700;900&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ── Base ── */
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
   ANIMATIONS
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
  0%   { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
}
@keyframes fadeSlideDown {
  from { opacity: 0; transform: translateY(-18px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes glowBorder {
  0%, 100% { box-shadow: 0 0 8px rgba(124,58,237,0.35), inset 0 0 8px rgba(124,58,237,0.04); }
  50%       { box-shadow: 0 0 22px rgba(167,139,250,0.45), inset 0 0 12px rgba(124,58,237,0.07); }
}
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position:  200% center; }
}
@keyframes badgePop {
  0%   { transform: scale(0.8); opacity: 0; }
  60%  { transform: scale(1.1); }
  100% { transform: scale(1);   opacity: 1; }
}

/* ══════════════════════════════════════════
   3D NEON HEADER
══════════════════════════════════════════ */
.vhq-header {
  position: relative;
  text-align: center;
  padding: 2.8rem 1rem 2rem 1rem;
  overflow: hidden;
  animation: fadeSlideDown 0.7s ease both;
}
.vhq-header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(167,139,250,0.6), transparent);
  animation: scanline 4s linear infinite;
  pointer-events: none;
}
.vhq-header::after {
  content: '';
  position: absolute;
  bottom: 0; left: 10%; right: 10%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(124,58,237,0.45), transparent);
}
.vhq-eyebrow {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.63rem;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: rgba(167,139,250,0.65);
  margin-bottom: 0.75rem;
  animation: fadeSlideDown 0.6s ease 0.1s both;
}
.vhq-logo {
  font-family: 'Orbitron', monospace;
  font-size: clamp(1.5rem, 5.5vw, 2.25rem);
  font-weight: 900;
  letter-spacing: 0.08em;
  color: #fff;
  line-height: 1.15;
  user-select: none;
  animation: neonPulse 3s ease-in-out infinite, fadeSlideDown 0.7s ease 0.15s both;
}
.vhq-tagline {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  color: rgba(167,139,250,0.55);
  letter-spacing: 0.06em;
  margin-top: 0.65rem;
  animation: fadeSlideDown 0.7s ease 0.3s both;
}
.vhq-version {
  display: inline-block;
  background: rgba(124,58,237,0.14);
  border: 1px solid rgba(124,58,237,0.33);
  color: #a78bfa;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.14em;
  padding: 0.2rem 0.75rem;
  border-radius: 20px;
  margin-top: 0.7rem;
  animation: badgePop 0.5s ease 0.5s both;
}

/* ══════════════════════════════════════════
   GLASSMORPHIC CARDS
══════════════════════════════════════════ */
.glass-card {
  background: rgba(255,255,255,0.028);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255,255,255,0.065);
  border-radius: 18px;
  padding: 1.8rem 1.6rem;
  margin-bottom: 1.1rem;
  position: relative;
  overflow: hidden;
  animation: glowBorder 4s ease-in-out infinite, fadeSlideUp 0.5s ease both;
}
.glass-card::before {
  content: '';
  position: absolute;
  top: 0; left: 15%; right: 15%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(167,139,250,0.35), transparent);
}
.glass-card-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(124,58,237,0.8);
  margin-bottom: 1rem;
}

/* ══════════════════════════════════════════
   ST.TABS OVERRIDE — premium pill style
══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.025) !important;
  border: 1px solid rgba(124,58,237,0.2) !important;
  border-radius: 13px !important;
  padding: 5px !important;
  gap: 4px !important;
  margin-bottom: 1.2rem !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: 9px !important;
  color: rgba(167,139,250,0.55) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  padding: 0.5rem 1.2rem !important;
  border: none !important;
  transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
  color: #fff !important;
  box-shadow: 0 2px 14px rgba(124,58,237,0.4) !important;
}
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 0.2rem !important; }

/* ══════════════════════════════════════════
   INPUTS
══════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input,
.stSelectbox > div > div {
  background: rgba(255,255,255,0.038) !important;
  border: 1px solid rgba(124,58,237,0.28) !important;
  border-radius: 10px !important;
  color: #E8E6F0 !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 0.92rem !important;
  transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: #7c3aed !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.17) !important;
}
label,
.stSelectbox label,
.stTextInput label,
.stTextArea label,
.stDateInput label {
  color: rgba(167,139,250,0.75) !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.03em !important;
}

/* ══════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════ */
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
  letter-spacing: 0.04em !important;
  box-shadow: 0 4px 20px rgba(124,58,237,0.35) !important;
  transition: background-position 0.4s ease, transform 0.15s ease, box-shadow 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
  background-position: right center !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 28px rgba(124,58,237,0.5) !important;
}
.stButton > button[kind="secondary"] {
  width: 100%;
  background: rgba(255,255,255,0.035) !important;
  color: rgba(167,139,250,0.85) !important;
  border: 1px solid rgba(124,58,237,0.28) !important;
  border-radius: 12px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 0.88rem !important;
  transition: border-color 0.2s ease, background 0.2s ease !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: rgba(124,58,237,0.55) !important;
  background: rgba(124,58,237,0.08) !important;
}

/* ══════════════════════════════════════════
   SECTION LABEL
══════════════════════════════════════════ */
.section-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(124,58,237,0.75);
  margin: 1.8rem 0 0.7rem 0;
}

/* ══════════════════════════════════════════
   DASHBOARD NAV PILLS
══════════════════════════════════════════ */
.nav-bar {
  display: flex;
  gap: 0.4rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(124,58,237,0.14);
  border-radius: 14px;
  padding: 5px;
  margin-bottom: 1.4rem;
}

/* ══════════════════════════════════════════
   PROFILE AVATAR
══════════════════════════════════════════ */
.avatar-ring {
  width: 70px; height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed, #a855f7, #ec4899);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 0.6rem auto;
  font-size: 1.75rem; font-weight: 700;
  box-shadow: 0 0 22px rgba(124,58,237,0.4);
  animation: glowBorder 3s ease-in-out infinite;
}

/* ══════════════════════════════════════════
   STAT CHIPS
══════════════════════════════════════════ */
.stat-row { display:flex; gap:0.55rem; margin-top:0.85rem; }
.stat-chip {
  flex:1;
  background: rgba(124,58,237,0.07);
  border: 1px solid rgba(124,58,237,0.18);
  border-radius: 10px;
  padding: 0.6rem 0.4rem;
  text-align: center;
}
.stat-chip-value {
  font-family: 'Orbitron', monospace;
  font-size: 1.05rem; font-weight: 700; color: #a78bfa;
}
.stat-chip-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.58rem; letter-spacing: 0.1em;
  text-transform: uppercase; color: rgba(167,139,250,0.45);
  margin-top: 0.15rem;
}

/* ══════════════════════════════════════════
   ALERT BANNERS
══════════════════════════════════════════ */
.banner-error {
  background: rgba(239,68,68,0.08);
  border: 1px solid rgba(239,68,68,0.32);
  border-radius: 11px;
  padding: 0.8rem 1rem;
  font-size: 0.84rem;
  color: #fca5a5;
  margin: 0.6rem 0;
  animation: fadeSlideUp 0.25s ease both;
}
.banner-success {
  background: rgba(34,197,94,0.07);
  border: 1px solid rgba(34,197,94,0.28);
  border-radius: 11px;
  padding: 0.8rem 1rem;
  font-size: 0.84rem;
  color: #86efac;
  margin: 0.6rem 0;
  animation: fadeSlideUp 0.25s ease both;
}

/* ══════════════════════════════════════════
   SHIMMER DIVIDER
══════════════════════════════════════════ */
.shimmer-div {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(167,139,250,0.38) 50%, transparent);
  background-size: 200% auto;
  animation: shimmer 3s linear infinite;
  margin: 1.4rem 0;
}

/* ══════════════════════════════════════════
   FOOTER
══════════════════════════════════════════ */
.vhq-footer {
  text-align: center;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.12em;
  color: rgba(124,58,237,0.3);
  margin-top: 3rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(124,58,237,0.08);
}

.stAlert { border-radius: 10px !important; }
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
# AUTH & PROFILE HELPERS
# ═══════════════════════════════════════════════════════════════
def auth_signup(email: str, password: str):
    return supabase.auth.sign_up({
        "email": email,
        "password": password,
        "options": {"data": {"onboarded": False}},
    })

def auth_login(email: str, password: str):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def auth_logout():
    supabase.auth.sign_out()

def get_profile(user_id: str) -> dict | None:
    res = supabase.table("profiles").select("*").eq("id", user_id).execute()
    return res.data[0] if res.data else None

def save_profile(user_id: str, full_name: str, bio: str, dob: str):
    supabase.table("profiles").upsert({
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
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
_defaults = {
    "authenticated": False,
    "user_id":       None,
    "user_email":    None,
    "onboarded":     False,
    "profile":       None,
    "active_tab":    "Audit",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ═══════════════════════════════════════════════════════════════
# VHQ HEADER — always visible
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="vhq-header">
  <div class="vhq-eyebrow">⬡ Powered by Multi-LLM Intelligence</div>
  <div class="vhq-logo">VHQ · SOCIAL<br>AUDITOR</div>
  <div class="vhq-tagline">Algorithmic Diagnostics · Viral Growth Engine · AI Analytics</div>
  <div class="vhq-version">v2.0 · PHASE 1 + 2</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: AUTH
# ═══════════════════════════════════════════════════════════════
if not st.session_state.authenticated:

    tab_login, tab_signup = st.tabs(["🔐  Sign In", "🚀  Create Account"])

    # ── Sign In tab ───────────────────────────────────────────
    with tab_login:
        st.markdown('<div class="glass-card"><div class="glass-card-label">— Sign In to VHQ —</div>', unsafe_allow_html=True)

        li_email = st.text_input("Email address", placeholder="you@email.com", key="li_email")
        li_pw    = st.text_input("Password", type="password", placeholder="Your password", key="li_pw")
        li_btn   = st.button("⬡  Sign In", type="primary", use_container_width=True, key="li_btn")

        st.markdown('</div>', unsafe_allow_html=True)

        if li_btn:
            if not li_email.strip() or not li_pw.strip():
                st.markdown('<div class="banner-error">⚠ Please enter your email and password.</div>', unsafe_allow_html=True)
            else:
                try:
                    res  = auth_login(li_email.strip().lower(), li_pw)
                    user = res.user
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id       = user.id
                        st.session_state.user_email    = user.email
                        profile = get_profile(user.id)
                        st.session_state.profile   = profile
                        st.session_state.onboarded = bool(profile and profile.get("onboarded"))
                        st.rerun()
                    else:
                        st.markdown('<div class="banner-error">⚠ Invalid email or password.</div>', unsafe_allow_html=True)
                except Exception as e:
                    msg = str(e).lower()
                    if "invalid login" in msg or "invalid credentials" in msg or "invalid" in msg:
                        st.markdown('<div class="banner-error">⚠ Wrong email or password. Please try again.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="banner-error">⚠ Sign-in error: {str(e)[:120]}</div>', unsafe_allow_html=True)

    # ── Create Account tab ────────────────────────────────────
    with tab_signup:
        st.markdown('<div class="glass-card"><div class="glass-card-label">— New Account —</div>', unsafe_allow_html=True)

        su_email = st.text_input("Email address", placeholder="you@email.com", key="su_email")
        su_pw    = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="su_pw")
        su_pw2   = st.text_input("Confirm password", type="password", placeholder="Repeat password", key="su_pw2")
        su_btn   = st.button("⬡  Create My Account", type="primary", use_container_width=True, key="su_btn")

        st.markdown('</div>', unsafe_allow_html=True)

        if su_btn:
            if not su_email.strip() or not su_pw.strip():
                st.markdown('<div class="banner-error">⚠ Email and password are required.</div>', unsafe_allow_html=True)
            elif len(su_pw) < 6:
                st.markdown('<div class="banner-error">⚠ Password must be at least 6 characters.</div>', unsafe_allow_html=True)
            elif su_pw != su_pw2:
                st.markdown('<div class="banner-error">⚠ Passwords do not match.</div>', unsafe_allow_html=True)
            else:
                try:
                    res  = auth_signup(su_email.strip().lower(), su_pw)
                    user = res.user
                    if user:
                        # Auto sign-in immediately after signup (email confirm disabled in Supabase)
                        login_res = auth_login(su_email.strip().lower(), su_pw)
                        if login_res.user:
                            st.session_state.authenticated = True
                            st.session_state.user_id       = login_res.user.id
                            st.session_state.user_email    = login_res.user.email
                            st.session_state.profile       = None
                            st.session_state.onboarded     = False
                            st.rerun()
                        else:
                            st.markdown('<div class="banner-success">✓ Account created! Switch to Sign In to continue.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="banner-error">⚠ Could not create account. Try a different email.</div>', unsafe_allow_html=True)
                except Exception as e:
                    msg = str(e).lower()
                    if "already registered" in msg or "already exists" in msg or "duplicate" in msg:
                        st.markdown('<div class="banner-error">⚠ This email is already registered. Use Sign In.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="banner-error">⚠ Signup error: {str(e)[:120]}</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="vhq-footer">VHQ · SOCIAL AUDITOR &nbsp;·&nbsp; PHASE 1 + 2 &nbsp;·&nbsp; 2025</div>
    """, unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════
# PAGE: PROFILE ONBOARDING
# ═══════════════════════════════════════════════════════════════
if not st.session_state.onboarded:

    st.markdown('<div class="section-label">⬡ &nbsp; Complete Your Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="glass-card-label">— Setup: Step 1 of 1 —</div>', unsafe_allow_html=True)

    ob_name = st.text_input("Full Name *", placeholder="e.g. Vaibhav Sharma", key="ob_name")
    ob_bio  = st.text_area("Bio", placeholder="Tell the world what you create or build…", height=85, key="ob_bio")
    ob_dob  = st.date_input(
        "Date of Birth *",
        value=date(2000, 1, 1),
        min_value=date(1910, 1, 1),
        max_value=date.today(),
        key="ob_dob",
    )

    # Live age feedback
    if ob_dob:
        _age = age_from_dob(ob_dob)
        if _age < 13:
            st.markdown(f'<div class="banner-error">🔒 You must be 13 or older to use VHQ. Detected age: {_age}.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="banner-success">✓ Age verified — {_age} years old.</div>', unsafe_allow_html=True)

    ob_save = st.button("⬡  Save & Enter Dashboard", type="primary", use_container_width=True, key="ob_save")
    st.markdown('</div>', unsafe_allow_html=True)

    if ob_save:
        if not ob_name.strip():
            st.markdown('<div class="banner-error">⚠ Full name is required.</div>', unsafe_allow_html=True)
        elif age_from_dob(ob_dob) < 13:
            st.markdown('<div class="banner-error">🔒 Must be 13+ to use VHQ. Access denied.</div>', unsafe_allow_html=True)
        else:
            try:
                save_profile(
                    user_id=st.session_state.user_id,
                    full_name=ob_name.strip(),
                    bio=ob_bio.strip(),
                    dob=str(ob_dob),
                )
                st.session_state.onboarded = True
                st.session_state.profile   = get_profile(st.session_state.user_id)
                st.rerun()
            except Exception as e:
                st.markdown(f'<div class="banner-error">⚠ Could not save profile: {str(e)[:120]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="vhq-footer">VHQ · PROFILE SETUP</div>', unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════
# PAGE: MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════════
profile   = st.session_state.profile or {}
full_name = profile.get("full_name", "Creator")
tier      = profile.get("tier", "free").upper()
initials  = "".join(w[0] for w in full_name.split()[:2]).upper() or "VH"
tier_col  = "#f59e0b" if tier == "FREE" else "#a78bfa"

# ── Profile summary card ───────────────────────────────────────
st.markdown(f"""
<div class="glass-card" style="text-align:center; animation-delay:0.05s">
  <div class="avatar-ring">{initials}</div>
  <div style="font-size:1.05rem;font-weight:700;letter-spacing:0.02em">{full_name}</div>
  <div style="font-size:0.78rem;color:rgba(167,139,250,0.55);margin:0.2rem 0 0.5rem">
    {st.session_state.user_email}
  </div>
  <span style="
    display:inline-block;
    background:rgba(124,58,237,0.13);
    border:1px solid {tier_col}44;
    color:{tier_col};
    font-family:'IBM Plex Mono',monospace;
    font-size:0.6rem; letter-spacing:0.14em;
    padding:0.2rem 0.85rem; border-radius:20px;
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

st.markdown('<div class="shimmer-div"></div>', unsafe_allow_html=True)

# ── Dashboard tabs ─────────────────────────────────────────────
dash_tabs = st.tabs(["⬡  Audit", "◈  Reports", "◉  Profile", "⚙  Settings"])

# ── TAB 1: AUDIT ──────────────────────────────────────────────
with dash_tabs[0]:
    st.markdown('<div class="section-label">⬡ &nbsp; Platform Audit Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="glass-card-label">— Audit Module —</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;padding:2.2rem 1rem;color:rgba(167,139,250,0.4)">
      <div style="font-size:2rem;margin-bottom:0.6rem">⬡</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;letter-spacing:0.1em">
        AUDIT ENGINE · PHASE 3 COMING NEXT
      </div>
      <div style="font-size:0.8rem;margin-top:0.45rem;color:rgba(167,139,250,0.28)">
        Platform selector, metric inputs &amp; AI diagnostics will live here.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 2: REPORTS ────────────────────────────────────────────
with dash_tabs[1]:
    st.markdown('<div class="section-label">◈ &nbsp; Audit Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="glass-card-label">— Reports —</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;padding:2rem 1rem;color:rgba(167,139,250,0.35)">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;letter-spacing:0.1em">
        NO REPORTS YET · RUN YOUR FIRST AUDIT
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 3: PROFILE ────────────────────────────────────────────
with dash_tabs[2]:
    st.markdown('<div class="section-label">◉ &nbsp; Your Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="glass-card-label">— Account Details —</div>', unsafe_allow_html=True)

    fields = {
        "Full Name":  profile.get("full_name", "—"),
        "Bio":        profile.get("bio", "—") or "—",
        "Date of Birth": profile.get("dob", "—"),
        "Email":      st.session_state.user_email,
        "Plan":       tier,
    }
    for label, val in fields.items():
        st.markdown(
            f'<div style="margin-bottom:0.6rem">'
            f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
            f'letter-spacing:0.12em;text-transform:uppercase;color:rgba(124,58,237,0.65)">'
            f'{label}</span><br>'
            f'<span style="font-size:0.92rem;color:#E8E6F0">{val}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
      color:rgba(124,58,237,0.4);text-align:center;letter-spacing:0.07em;margin-top:0.3rem">
      ⚠ Name / username edits: max 2× per 10 days (enforced in Phase 3)
    </div>
    """, unsafe_allow_html=True)

# ── TAB 4: SETTINGS ───────────────────────────────────────────
with dash_tabs[3]:
    st.markdown('<div class="section-label">⚙ &nbsp; Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="glass-card-label">— Preferences —</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.73rem;
      color:rgba(167,139,250,0.4);letter-spacing:0.06em;line-height:2">
      ◉ &nbsp; AI Engine &nbsp;&nbsp;&nbsp;&nbsp; Backend-managed (Phase 3)<br>
      ◉ &nbsp; Notifications &nbsp; Phase 3<br>
      ◉ &nbsp; Upgrade to Pro &nbsp; Phase 4 · Razorpay<br>
      ◉ &nbsp; Ad preferences &nbsp; Phase 4
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="shimmer-div"></div>', unsafe_allow_html=True)

    if st.button("⬡  Sign Out of VHQ", type="secondary", use_container_width=True, key="signout"):
        auth_logout()
        for _k in list(st.session_state.keys()):
            del st.session_state[_k]
        st.rerun()

# ── Footer ─────────────────────────────────────────────────────
st.markdown("""
<div class="vhq-footer">
  VHQ · SOCIAL AUDITOR &nbsp;·&nbsp; PHASE 1 + 2 COMPLETE
  &nbsp;·&nbsp; PHASE 3 NEXT &nbsp;·&nbsp; 2025
</div>
""", unsafe_allow_html=True)
