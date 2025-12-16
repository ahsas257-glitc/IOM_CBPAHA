import streamlit as st
import streamlit.components.v1 as components

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Welcome | IOM_CBPAHA", layout="wide")

# ---------------- CSS (OK in st.markdown) ----------------
st.markdown("""
<style>
@keyframes cosmicFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
@keyframes gradientFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes particleFloat {
    0% { transform: translate(0, 0) rotate(0deg); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translate(var(--tx), var(--ty)) rotate(360deg); opacity: 0; }
}

.stApp {
    background: linear-gradient(-45deg,
        #0a0a14 0%,
        #15152a 25%,
        #1a1a35 50%,
        #0f172a 75%,
        #0a0a14 100%);
    background-size: 400% 400%;
    animation: gradientFlow 25s ease infinite;
    min-height: 100vh;
    overflow-x: hidden;
}

.cosmic-particle {
    position: fixed;
    border-radius: 50%;
    background: radial-gradient(circle,
        rgba(100,200,255,0.4) 0%,
        rgba(100,200,255,0.2) 30%,
        transparent 70%);
    z-index: -1;
    pointer-events: none;
    animation: particleFloat linear infinite;
}

/* Hero Section */
.hero-section {
    background: linear-gradient(135deg,
        rgba(255,255,255,0.09) 0%,
        rgba(255,255,255,0.03) 100%);
    border-radius: 28px;
    padding: 40px 45px;
    margin: 0 0 35px 0;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow:
        0 25px 50px rgba(0,0,0,0.35),
        0 0 80px rgba(100,150,255,0.15),
        inset 0 1px 0 rgba(255,255,255,0.1),
        inset 0 -1px 0 rgba(0,0,0,0.3);
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    position: relative;
    overflow: hidden;
    animation: cosmicFloat 8s ease-in-out infinite;
}

@keyframes shine {
    0% { left: -100%; }
    20%, 100% { left: 100%; }
}
.hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg,
        transparent,
        rgba(255,255,255,0.06),
        transparent);
    animation: shine 5s infinite;
}

/* Mission Cards */
.mission-card {
    background: linear-gradient(145deg,
        rgba(255,255,255,0.07) 0%,
        rgba(255,255,255,0.03) 100%);
    border-radius: 20px;
    padding: 25px 28px;
    margin: 20px 0;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow:
        0 15px 35px rgba(0,0,0,0.25),
        0 5px 15px rgba(0,0,0,0.15),
        inset 0 1px 0 rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    transition: all 0.4s ease;
    position: relative;
    overflow: hidden;
}
.mission-card::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle,
        rgba(100,200,255,0.1) 0%,
        transparent 70%);
    opacity: 0;
    transition: opacity 0.6s ease;
}
.mission-card:hover {
    border-color: rgba(100,200,255,0.4);
    box-shadow:
        0 25px 50px rgba(0,0,0,0.3),
        0 10px 25px rgba(100,200,255,0.1),
        inset 0 1px 0 rgba(255,255,255,0.1);
    transform: translateY(-8px);
}
.mission-card:hover::after { opacity: 1; }

/* Feature Badges */
.feature-badge {
    display: inline-flex;
    align-items: center;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin: 0 8px 12px 0;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}
.badge-blue {
    background: linear-gradient(135deg, rgba(78, 205, 196, 0.2), rgba(69, 183, 209, 0.1));
    border: 1px solid rgba(78, 205, 196, 0.3);
    color: #a8edea;
}
.badge-green {
    background: linear-gradient(135deg, rgba(120, 220, 120, 0.2), rgba(80, 180, 80, 0.1));
    border: 1px solid rgba(120, 220, 120, 0.3);
    color: #aaffaa;
}
.badge-purple {
    background: linear-gradient(135deg, rgba(180, 120, 255, 0.2), rgba(150, 100, 220, 0.1));
    border: 1px solid rgba(180, 120, 255, 0.3);
    color: #d4aaff;
}
.badge-orange {
    background: linear-gradient(135deg, rgba(255, 180, 120, 0.2), rgba(220, 140, 80, 0.1));
    border: 1px solid rgba(255, 180, 120, 0.3);
    color: #ffccaa;
}
.feature-badge:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}

/* Divider */
.glow-divider {
    height: 2px;
    background: linear-gradient(90deg,
        transparent,
        rgba(255,255,255,0.1),
        rgba(100,200,255,0.4),
        rgba(255,255,255,0.1),
        transparent);
    margin: 35px 0;
    border: none;
    position: relative;
}
.glow-divider::after {
    content: '';
    position: absolute;
    top: 0;
    left: 25%;
    width: 50%;
    height: 100%;
    background: rgba(100,200,255,0.2);
    filter: blur(10px);
}

/* Callout */
.callout-box {
    background: linear-gradient(135deg, rgba(78, 205, 196, 0.1) 0%, rgba(69, 183, 209, 0.05) 100%);
    border-radius: 18px;
    padding: 25px;
    margin: 25px 0;
    border: 1px solid rgba(78, 205, 196, 0.2);
    border-left: 5px solid rgba(78, 205, 196, 0.5);
    backdrop-filter: blur(15px);
    transition: all 0.3s ease;
}
.callout-box:hover {
    border-color: rgba(78, 205, 196, 0.4);
    box-shadow: 0 15px 30px rgba(78, 205, 196, 0.1);
    transform: translateX(5px);
}

/* Text effects */
.gradient-text {
    background: linear-gradient(135deg, #4ecdc4 0%, #45b7d1 25%, #a8edea 50%, #45b7d1 75%, #4ecdc4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-size: 200% 200%;
    animation: gradientFlow 8s ease infinite;
}
.pulse-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #4ecdc4;
    margin: 0 10px;
    animation: pulse 2s infinite;
    box-shadow: 0 0 10px rgba(78, 205, 196, 0.5);
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.2); }
}

/* Lists */
.feature-list li {
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    position: relative;
    padding-left: 30px;
}
.feature-list li:before {
    content: '✦';
    position: absolute;
    left: 0;
    color: #4ecdc4;
    font-size: 16px;
}

/* Welcome */
.welcome-text { animation: fadeInUp 1s ease-out; }
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Nav prompt */
.nav-prompt {
    position: relative;
    padding: 20px;
    border-radius: 18px;
    background: rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.1);
    margin-top: 30px;
    overflow: hidden;
}
.nav-prompt::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(transparent, transparent, transparent, rgba(100,200,255,0.1));
    animation: rotate 4s linear infinite;
}
@keyframes rotate { 100% { transform: rotate(360deg); } }

.nav-prompt-content {
    position: relative;
    z-index: 1;
    background: rgba(10,10,20,0.8);
    padding: 15px;
    border-radius: 12px;
    backdrop-filter: blur(10px);
}
</style>
""", unsafe_allow_html=True)

# ---------------- JS (MUST be components.html, not st.markdown) ----------------
components.html("""
<script>
(function () {
  const colors = [
    'rgba(78, 205, 196, 0.4)',
    'rgba(69, 183, 209, 0.4)',
    'rgba(168, 237, 234, 0.3)',
    'rgba(100, 200, 255, 0.3)'
  ];

  function addParticles() {
    const container = window.parent.document.querySelector('.stApp');
    if (!container) return;

    // جلوگیری از تکرار در rerun
    if (container.querySelector('.cosmic-particle')) return;

    for (let i = 0; i < 25; i++) {
      const particle = window.parent.document.createElement('div');
      particle.className = 'cosmic-particle';

      const size = Math.random() * 60 + 20;
      particle.style.width = size + 'px';
      particle.style.height = size + 'px';
      particle.style.left = Math.random() * 100 + '%';
      particle.style.top = Math.random() * 100 + '%';

      particle.style.background = `radial-gradient(circle, ${colors[Math.floor(Math.random() * colors.length)]} 0%, transparent 70%)`;

      const tx = (Math.random() - 0.5) * 200 + 'px';
      const ty = (Math.random() - 0.5) * 200 + 'px';
      particle.style.setProperty('--tx', tx);
      particle.style.setProperty('--ty', ty);

      particle.style.animationDuration = (Math.random() * 20 + 15) + 's';
      particle.style.animationDelay = Math.random() * 5 + 's';

      container.appendChild(particle);
    }
  }

  // کمی تاخیر برای اینکه DOM کامل لود شود
  setTimeout(addParticles, 300);
})();
</script>
""", height=0)

# ---------------- HERO SECTION ----------------
st.markdown("""
<div class="hero-section welcome-text">
  <div style="text-align: center; margin-bottom: 30px;">
    <h1 style="margin: 0; font-size: 3.5rem;" class="gradient-text">🌍 IOM — CBPAHA Dashboard</h1>
    <div style="display: flex; justify-content: center; align-items: center; margin-top: 15px;">
      <span class="pulse-dot"></span>
      <span style="color: rgba(255,255,255,0.7); font-size: 1.2rem; letter-spacing: 2px;">
        HUMANITARIAN DATA INTELLIGENCE PLATFORM
      </span>
      <span class="pulse-dot"></span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- ABOUT IOM ----------------
st.markdown("""
<div class="mission-card">
  <div style="display:flex; align-items:center; margin-bottom:20px;">
    <div style="font-size:2.5rem; margin-right:20px;">📌</div>
    <div>
      <h2 style="margin:0; color:#a8edea;">About IOM</h2>
      <p style="margin:5px 0 0 0; color:rgba(255,255,255,0.6); font-size:0.95rem;">United Nations Migration Agency</p>
    </div>
  </div>

  <div style="color:rgba(255,255,255,0.85); line-height:1.8; font-size:1.05rem;">
    The <strong>International Organization for Migration (IOM)</strong> is a UN migration agency dedicated to
    ensuring the <span style="color:#4ecdc4;">orderly and humane management of migration</span>.
    We work to promote international cooperation on migration issues, assist in finding
    practical solutions to migration challenges, and provide
    <span style="color:#a8edea;">humanitarian assistance to migrants in need</span>, including refugees and internally displaced persons.
  </div>

  <div style="margin-top:25px; display:flex; flex-wrap:wrap;">
    <span class="feature-badge badge-blue">Migration Management</span>
    <span class="feature-badge badge-green">Humanitarian Assistance</span>
    <span class="feature-badge badge-purple">International Cooperation</span>
    <span class="feature-badge badge-orange">Refugee Support</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- CBPAHA PROJECT ----------------
st.markdown("""
<div class="mission-card">
  <div style="display:flex; align-items:center; margin-bottom:20px;">
    <div style="font-size:2.5rem; margin-right:20px;">🚀</div>
    <div>
      <h2 style="margin:0; color:#a8edea;">CBPAHA Project</h2>
      <p style="margin:5px 0 0 0; color:rgba(255,255,255,0.6); font-size:0.95rem;">
        Community-Based Protection & Assistance to Host & Affected Populations
      </p>
    </div>
  </div>

  <div style="color:rgba(255,255,255,0.85); line-height:1.8; font-size:1.05rem; margin-bottom:25px;">
    The <strong>CBPAHA Project</strong> implements IOM's mandate at the community level, focusing on
    <span style="color:#4ecdc4;">protection, assistance, and resilience-building</span> for vulnerable populations
    affected by migration and displacement.
  </div>

  <div style="background:rgba(0,0,0,0.2); border-radius:15px; padding:20px;">
    <h4 style="color:#a8edea; margin-top:0; margin-bottom:15px;">Core Activities:</h4>
    <ul class="feature-list" style="color:rgba(255,255,255,0.8); padding-left:20px;">
      <li><strong>Strengthening local community protection mechanisms</strong> and response systems</li>
      <li><strong>Supporting internally displaced persons (IDPs)</strong> and host communities</li>
      <li><strong>Improving access</strong> to essential humanitarian services and resources</li>
      <li><strong>Ensuring safety, dignity, and community-level resilience</strong> in crisis situations</li>
      <li><strong>Managing physical data collection</strong> and remote follow-up coordination</li>
      <li><strong>Monitoring protection cases</strong> with structured trackers and real-time dashboards</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

# ---------------- DASHBOARD PURPOSE ----------------
st.markdown("""
<div class="callout-box">
  <h2 style="color:#a8edea; margin-top:0;">🎯 Dashboard Purpose</h2>
  <div style="color:rgba(255,255,255,0.85); font-size:1.05rem; margin-bottom:20px;">
    This <span style="color:#4ecdc4; font-weight:bold;">Liquid Glass Intelligence Platform</span> was engineered to empower the IOM-CBPAHA team with advanced data capabilities for field operations and project monitoring.
  </div>
</div>
""", unsafe_allow_html=True)

# Features Grid
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="mission-card" style="height:100%;">
      <h3 style="color:#a8edea; margin-top:0;">📊 Data Management</h3>
      <ul class="feature-list" style="color:rgba(255,255,255,0.8);">
        <li><strong>Tracking IOM case data</strong> with precision analytics</li>
        <li><strong>Detecting language patterns</strong> (Dari/Pashto) automatically</li>
        <li><strong>Monitoring submission duration</strong> and delay analytics</li>
        <li><strong>Applying correction workflows</strong> with validation locks</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="mission-card" style="height:100%;">
      <h3 style="color:#a8edea; margin-top:0;">🔍 Quality Assurance</h3>
      <ul class="feature-list" style="color:rgba(255,255,255,0.8);">
        <li><strong>Identifying duplicate references</strong> (IOM numbers)</li>
        <li><strong>Removing invalid records</strong> from field datasets</li>
        <li><strong>Ensuring data integrity</strong> across all operations</li>
        <li><strong>Real-time validation</strong> and error detection</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

# ---------------- VALUE PROPOSITION ----------------
st.markdown("""
<div class="callout-box">
  <div style="text-align:center; padding:20px;">
    <div style="font-size:2.5rem; margin-bottom:15px;">💡</div>
    <h3 style="color:#a8edea; margin-top:0;">Intelligent Humanitarian Platform</h3>
    <p style="color:rgba(255,255,255,0.85); font-size:1.1rem; line-height:1.6;">
      This platform transforms raw field data into <span style="color:#4ecdc4;">actionable humanitarian intelligence</span>,
      enabling faster decision-making, clearer insights, and more reliable monitoring for effective field coordination and project management.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

# ---------------- NAVIGATION PROMPT ----------------
st.markdown("""
<div class="nav-prompt">
  <div class="nav-prompt-content">
    <div style="text-align:center;">
      <h3 style="color:#a8edea; margin-top:0; margin-bottom:15px;">✅ Dashboard Ready — Begin Your Mission</h3>
      <p style="color:rgba(255,255,255,0.8); margin-bottom:20px;">
        Select a module from the navigation sidebar to access specialized tools and analytics.
      </p>
      <div style="display:flex; justify-content:center; gap:15px; flex-wrap:wrap;">
        <span class="feature-badge badge-blue">Data Cleaning</span>
        <span class="feature-badge badge-green">Visualization</span>
        <span class="feature-badge badge-purple">Case Tracking</span>
        <span class="feature-badge badge-orange">Analytics</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- FINAL CTA ----------------
st.markdown("""
<div style="text-align:center; margin-top:40px; padding:30px; border-radius:20px;
            background: linear-gradient(135deg, rgba(78,205,196,0.05), rgba(69,183,209,0.02));
            border: 1px solid rgba(78,205,196,0.1);">
  <div style="font-size:3rem; margin-bottom:20px; animation: cosmicFloat 4s ease-in-out infinite;">🌟</div>
  <h3 style="color:#a8edea; margin-bottom:15px;">Empowering Humanitarian Action Through Data</h3>
  <p style="color:rgba(255,255,255,0.7); max-width:700px; margin:0 auto; font-size:1.05rem;">
    Every data point represents a life, a story, a need. This dashboard helps ensure no one is left behind.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
