import os
import sys
import json
import base64
import socket
import streamlit as st
import streamlit.components.v1 as components

# Add backend directory to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Monkey-patch SpeechBrain LazyModule to prevent crashes on missing optional integrations (nlp, numba, etc.)
try:
    import speechbrain.utils.importutils as _sb_importutils
    _orig_ensure = _sb_importutils.LazyModule.ensure_module
    def _safe_ensure_module(self, stacklevel=1):
        try:
            return _orig_ensure(self, stacklevel=stacklevel)
        except Exception:
            return None
    _sb_importutils.LazyModule.ensure_module = _safe_ensure_module
except Exception:
    pass

try:
    from app.ai.gemini_client import get_intent, parse_rule_based_intent, get_api_key
except ImportError:
    sys.path.append(os.path.join(BACKEND_DIR, "app"))
    from ai.gemini_client import get_intent, parse_rule_based_intent, get_api_key

def enroll_speaker(name: str, audio_path: str):
    try:
        try:
            from app.biometrics.speechbrain_model import enroll_speaker as _enroll
        except ImportError:
            from biometrics.speechbrain_model import enroll_speaker as _enroll
        return _enroll(name, audio_path)
    except Exception as e:
        print(f"Biometric enrollment unavailable: {e}")
        return False

def identify_speaker(audio_path: str):
    try:
        try:
            from app.biometrics.speechbrain_model import identify_speaker as _identify
        except ImportError:
            from biometrics.speechbrain_model import identify_speaker as _identify
        return _identify(audio_path)
    except Exception as e:
        print(f"Biometric identification unavailable: {e}")
        return "User", 100

# Streamlit Page Config
st.set_page_config(
    page_title="Harry AI - 3D Voice Controlled Robot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to get local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

local_ip = get_local_ip()
api_key = get_api_key()

# Custom Sci-Fi Dark Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp {
        background-color: #07090c;
        color: #e0e6ed;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .main-title {
        color: #00f3ff;
        text-shadow: 0 0 15px rgba(0, 243, 255, 0.6);
        font-family: 'Orbitron', sans-serif !important;
        font-size: 2.1rem;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 0px;
        letter-spacing: 2px;
    }
    
    .sub-title {
        color: #8fa0b3;
        font-size: 0.95rem;
        margin-bottom: 15px;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("<h2 style='color:#00f3ff; font-family:Orbitron; font-size:1.2rem; letter-spacing:1px;'>⚡ CONTROL CENTER</h2>", unsafe_allow_html=True)
    
    # Network status info
    st.markdown(f"""
    <div style='background:rgba(0, 243, 255, 0.05); padding:12px; border-radius:10px; border:1px solid rgba(0, 243, 255, 0.2); font-size:0.85rem; margin-bottom:15px;'>
        <div style='color:#8fa0b3; font-weight:600;'>🌐 Multi-Network Uplink:</div>
        <div style='color:#00f3ff; font-weight:bold; font-size:1rem; margin-top:2px;'>http://{local_ip}:8501</div>
        <div style='color:#6a7c92; font-size:0.75rem; margin-top:4px;'>Accessible from any phone, PC, or tablet on LAN</div>
    </div>
    """, unsafe_allow_html=True)

    # Gemini API Key setup
    st.markdown("### 🔑 Gemini AI Core")
    gemini_key_input = st.text_input(
        "Google Gemini API Key",
        value=api_key,
        type="password",
        placeholder="AI Studio API Key...",
        help="Enables conversational AI intelligence and answers."
    )
    if gemini_key_input:
        os.environ["GEMINI_API_KEY"] = gemini_key_input
        api_key = gemini_key_input

    st.markdown("---")
    st.markdown("### 🎙️ Voice Control Guide")
    st.markdown("""
    **Supported Voice Commands:**
    - `Move Forward` / `Front` / `Ahead`
    - `Move Backward` / `Back` / `Reverse`
    - `Turn Left` / `Go Left`
    - `Turn Right` / `Go Right`
    - `Jump` / `Hop` / `Bounce`
    - `Spin` / `Dance` / `Rotate`
    - `Reset` / `Center` / `Stop`
    - *Any Conversational Question* (e.g. *"Who are you?"*, *"Tell me about Mars"*)
    """)

    st.markdown("---")
    st.markdown("### 👤 Biometric Profiles")
    profile_dir = os.path.join(CURRENT_DIR, "backend", "app", "biometrics", "profiles")
    if os.path.exists(profile_dir):
        profiles = [f.replace(".npy", "") for f in os.listdir(profile_dir) if f.endswith(".npy")]
        if profiles:
            st.write(f"Enrolled Operators ({len(profiles)}):")
            for p in profiles:
                st.markdown(f"- 🔒 **{p}** (Active Voiceprint)")
        else:
            st.info("No operator voiceprints registered yet. Enroll below.")
    else:
        st.info("No biometric profiles yet.")

# Main Dashboard Header
st.markdown("<div class='main-title'>🤖 HARRY AI: REAL-TIME VOICE-CONTROLLED ROBOT</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Direct In-Browser Voice Recognition • 3D Cybernetic Digital Twin • Gemini Intelligence • Neural Biometrics</div>", unsafe_allow_html=True)

# Build Comprehensive In-Browser Real-Time Voice Robot Application Component
robot_console_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

        * {{
            box-sizing: border-box;
            user-select: none;
        }}

        body {{
            margin: 0;
            padding: 10px;
            background-color: #07090c;
            color: #e0e6ed;
            font-family: 'Rajdhani', sans-serif;
            overflow-x: hidden;
        }}

        .hud-grid {{
            display: grid;
            grid-template-columns: 1fr 1.4fr;
            gap: 20px;
            max-width: 1300px;
            margin: 0 auto;
        }}

        @media (max-width: 900px) {{
            .hud-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .panel {{
            background: linear-gradient(160deg, #10141a, #0b0e12);
            border: 1px solid rgba(0, 243, 255, 0.2);
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
            position: relative;
        }}

        .panel-header {{
            font-family: 'Orbitron', sans-serif;
            color: #00f3ff;
            font-size: 1.1rem;
            margin-top: 0;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 243, 255, 0.15);
            padding-bottom: 8px;
            letter-spacing: 1px;
        }}

        /* Big Voice Control Button */
        .voice-master-btn {{
            width: 100%;
            background: linear-gradient(135deg, #00f3ff, #0077ff);
            color: #000;
            border: none;
            border-radius: 14px;
            padding: 18px 20px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            font-size: 1.15rem;
            letter-spacing: 2px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            box-shadow: 0 0 25px rgba(0, 243, 255, 0.4);
            transition: all 0.25s ease;
            margin-bottom: 15px;
        }}

        .voice-master-btn:hover {{
            box-shadow: 0 0 35px rgba(0, 243, 255, 0.75);
            transform: scale(1.02);
        }}

        .voice-master-btn.listening {{
            background: linear-gradient(135deg, #ff0055, #ff5500);
            color: #fff;
            box-shadow: 0 0 35px rgba(255, 0, 85, 0.7);
            animation: pulse-border 1.2s infinite alternate;
        }}

        @keyframes pulse-border {{
            0% {{ box-shadow: 0 0 20px rgba(255, 0, 85, 0.4); }}
            100% {{ box-shadow: 0 0 45px rgba(255, 0, 85, 0.9); }}
        }}

        /* Live Waveform */
        .audio-wave {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
            height: 32px;
            margin-bottom: 15px;
        }}

        .audio-bar {{
            width: 5px;
            height: 8px;
            background: #00f3ff;
            border-radius: 3px;
            transition: height 0.1s ease;
        }}

        .audio-bar.active {{
            animation: wave 0.5s infinite alternate;
        }}

        @keyframes wave {{
            0% {{ height: 6px; background: #00f3ff; }}
            100% {{ height: 30px; background: #ff0055; }}
        }}

        /* Speech Recognition Status Box */
        .speech-transcript-box {{
            background: #05070a;
            border: 1px solid rgba(0, 243, 255, 0.3);
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 15px;
            min-height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .speech-label {{
            font-size: 0.75rem;
            color: #8fa0b3;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 2px;
        }}

        .speech-text {{
            font-size: 1.1rem;
            font-weight: 700;
            color: #00f3ff;
            word-break: break-word;
        }}

        /* Directional Pad Grid */
        .dpad-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 15px;
        }}

        .hud-btn {{
            background: rgba(16, 25, 35, 0.9);
            border: 1px solid rgba(0, 243, 255, 0.3);
            color: #00f3ff;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            font-size: 0.95rem;
            padding: 10px;
            border-radius: 8px;
            cursor: pointer;
            letter-spacing: 1px;
            transition: all 0.2s ease;
            text-align: center;
        }}

        .hud-btn:hover {{
            background: #00f3ff;
            color: #000;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.6);
        }}

        .hud-btn.accent {{
            border-color: rgba(255, 152, 0, 0.4);
            color: #ff9800;
        }}

        .hud-btn.accent:hover {{
            background: #ff9800;
            color: #000;
            box-shadow: 0 0 15px rgba(255, 152, 0, 0.6);
        }}

        /* Terminal Logs */
        .terminal-display {{
            background: #030406;
            border: 1px solid #1a222d;
            border-left: 3px solid #00f3ff;
            border-radius: 8px;
            padding: 12px;
            font-family: 'Courier New', Courier, monospace;
            color: #00f3ff;
            font-size: 0.85rem;
            min-height: 80px;
            max-height: 120px;
            overflow-y: auto;
            white-space: pre-wrap;
        }}

        /* 3D Canvas Viewport */
        #canvas-wrap {{
            width: 100%;
            height: 520px;
            position: relative;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(0, 243, 255, 0.25);
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.9);
        }}

        #overlay-status {{
            position: absolute;
            top: 14px;
            left: 14px;
            z-index: 10;
            background: rgba(5, 10, 16, 0.8);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(0, 243, 255, 0.3);
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 0.8rem;
            color: #00f3ff;
            font-family: monospace;
            pointer-events: none;
        }}

        #camera-controls {{
            position: absolute;
            top: 14px;
            right: 14px;
            z-index: 10;
            display: flex;
            gap: 6px;
        }}

        .cam-btn {{
            background: rgba(10, 15, 22, 0.85);
            border: 1px solid rgba(0, 243, 255, 0.4);
            color: #8fa0b3;
            font-family: 'Rajdhani', sans-serif;
            font-weight: bold;
            font-size: 0.75rem;
            padding: 5px 10px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .cam-btn.active, .cam-btn:hover {{
            background: #00f3ff;
            color: #000;
        }}

        .switch-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            font-size: 0.85rem;
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>

<div class="hud-grid">

    <!-- LEFT CONTROL PANEL -->
    <div class="panel">
        <div class="panel-header">
            <span>🎙️ VOICE COMMAND HUB</span>
            <span id="speaker-badge" style="font-size:0.75rem; color:#4caf50; background:rgba(76,175,80,0.1); padding:3px 8px; border-radius:12px; border:1px solid #4caf50;">
                BIOMETRICS: READY
            </span>
        </div>

        <!-- Master Voice Trigger Button -->
        <button id="voice-btn" class="voice-master-btn" onclick="toggleVoiceListening()">
            <span id="voice-icon">🎤</span>
            <span id="voice-label">CLICK TO TALK (VOICE CONTROL)</span>
        </button>

        <!-- Dynamic Audio Wave Visualizer -->
        <div class="audio-wave" id="wave-container">
            <div class="audio-bar"></div>
            <div class="audio-bar"></div>
            <div class="audio-bar"></div>
            <div class="audio-bar"></div>
            <div class="audio-bar"></div>
            <div class="audio-bar"></div>
            <div class="audio-bar"></div>
            <div class="audio-bar"></div>
            <div class="audio-bar"></div>
        </div>

        <!-- Live Recognized Speech Box -->
        <div class="speech-transcript-box">
            <div class="speech-label">Real-Time Speech Recognized</div>
            <div class="speech-text" id="live-speech">"Ready. Click the microphone and say 'Move forward', 'Jump', or 'Spin'!"</div>
        </div>

        <!-- Hands-free & Audio Settings -->
        <div class="switch-row">
            <span>🔊 Robot Voice Talkback (TTS):</span>
            <label style="cursor:pointer; color:#00f3ff;">
                <input type="checkbox" id="tts-toggle" checked> Enabled
            </label>
        </div>

        <div class="switch-row">
            <span>🔄 Continuous Voice Listening:</span>
            <label style="cursor:pointer; color:#00f3ff;">
                <input type="checkbox" id="continuous-toggle" onchange="toggleContinuousMode(this.checked)"> Hands-Free
            </label>
        </div>

        <!-- Quick Directional & Action Buttons -->
        <div class="panel-header" style="font-size:0.9rem; margin-top:10px;">
            <span>🕹️ QUICK MOTION CONTROLS</span>
        </div>

        <div class="dpad-grid">
            <div></div>
            <button class="hud-btn" onclick="executeLocomotion('forward')">⬆️ FORWARD</button>
            <div></div>
            <button class="hud-btn" onclick="executeLocomotion('left')">⬅️ LEFT</button>
            <button class="hud-btn accent" onclick="executeLocomotion('reset')">🎯 RESET</button>
            <button class="hud-btn" onclick="executeLocomotion('right')">➡️ RIGHT</button>
            <div></div>
            <button class="hud-btn" onclick="executeLocomotion('backward')">⬇️ BACK</button>
            <div></div>
        </div>

        <div style="display:flex; gap:8px; margin-bottom:12px;">
            <button class="hud-btn accent" style="flex:1;" onclick="executeLocomotion('jump')">🦘 JUMP</button>
            <button class="hud-btn accent" style="flex:1;" onclick="executeLocomotion('spin')">🔄 360 SPIN</button>
        </div>

        <!-- Text command manual fallback -->
        <div style="display:flex; gap:8px; margin-bottom:12px;">
            <input type="text" id="manual-text-input" placeholder="Type prompt (e.g. 'tell me about galaxies', 'forward')..." 
                style="flex:1; background:#05070a; border:1px solid rgba(0,243,255,0.3); color:#fff; padding:8px 12px; border-radius:6px; font-family:'Rajdhani'; outline:none;"
                onkeydown="if(event.key === 'Enter') sendManualText();"
            />
            <button class="hud-btn" style="padding:8px 14px;" onclick="sendManualText()">Send</button>
        </div>

        <!-- Terminal Output -->
        <div class="terminal-display" id="terminal-log">> HARRY AI Voice Digital Twin ready.
> Microphone speech recognition engine initialized.
> Say 'Forward', 'Backward', 'Left', 'Right', 'Jump', or 'Spin'.</div>
    </div>

    <!-- RIGHT 3D DIGITAL TWIN CANVAS -->
    <div class="panel" style="padding:10px;">
        <div id="canvas-wrap">
            <div id="overlay-status">
                ROBOT: <span id="robot-action-label" style="color:#4caf50; font-weight:bold;">IDLE</span> | 
                POS: <span id="pos-label">X:0.0 Y:0.0 Z:0.0</span> | 
                ROT: <span id="rot-label">180°</span>
            </div>

            <div id="camera-controls">
                <button class="cam-btn active" id="btn-iso" onclick="setCameraPreset('iso')">Isometric</button>
                <button class="cam-btn" id="btn-top" onclick="setCameraPreset('top')">Top</button>
                <button class="cam-btn" id="btn-front" onclick="setCameraPreset('front')">Front</button>
            </div>
        </div>
    </div>

</div>

<script>
    // ----------------------------------------------------
    // 1. THREE.JS 3D SCENE & ROBOT MODEL SETUP
    // ----------------------------------------------------
    const container = document.getElementById('canvas-wrap');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x06080b);
    scene.fog = new THREE.FogExp2(0x06080b, 0.03);

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(5.5, 5.0, 6.0);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 0.8, 0);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x00f3ff, 1.3);
    dirLight.position.set(6, 12, 6);
    dirLight.castShadow = true;
    scene.add(dirLight);

    const pinkLight = new THREE.DirectionalLight(0xff0066, 0.8);
    pinkLight.position.set(-6, 8, -6);
    scene.add(pinkLight);

    // Cyber Grid Floor
    const gridHelper = new THREE.GridHelper(30, 30, 0x00f3ff, 0x16202c);
    gridHelper.position.y = 0;
    scene.add(gridHelper);

    // Glowing Cybernetic Platform
    const platGeo = new THREE.CylinderGeometry(3.6, 3.8, 0.1, 32);
    const platMat = new THREE.MeshStandardMaterial({{ color: 0x0c1117, roughness: 0.2, metalness: 0.8 }});
    const platform = new THREE.Mesh(platGeo, platMat);
    platform.position.y = -0.05;
    platform.receiveShadow = true;
    scene.add(platform);

    const ringGeo = new THREE.RingGeometry(3.65, 3.8, 32);
    const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f3ff, side: THREE.DoubleSide }});
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.01;
    scene.add(ring);

    // Robot 3D Mesh Construction
    const robotGroup = new THREE.Group();

    const chassisGeo = new THREE.CylinderGeometry(0.65, 0.75, 0.35, 16);
    const darkMetal = new THREE.MeshStandardMaterial({{ color: 0x182028, metalness: 0.85, roughness: 0.25 }});
    const chassis = new THREE.Mesh(chassisGeo, darkMetal);
    chassis.position.y = 0.35;
    chassis.castShadow = true;
    robotGroup.add(chassis);

    const torsoGeo = new THREE.BoxGeometry(0.85, 0.95, 0.55);
    const armorMat = new THREE.MeshStandardMaterial({{ color: 0x222e3b, metalness: 0.8, roughness: 0.3 }});
    const torso = new THREE.Mesh(torsoGeo, armorMat);
    torso.position.y = 1.0;
    torso.castShadow = true;
    robotGroup.add(torso);

    // Arc Core
    const arcGeo = new THREE.SphereGeometry(0.16, 16, 16);
    const arcMat = new THREE.MeshBasicMaterial({{ color: 0x00f3ff }});
    const arc = new THREE.Mesh(arcGeo, arcMat);
    arc.position.set(0, 1.0, 0.29);
    robotGroup.add(arc);

    // Head
    const headGeo = new THREE.BoxGeometry(0.55, 0.5, 0.5);
    const head = new THREE.Mesh(headGeo, darkMetal);
    head.position.y = 1.75;
    head.castShadow = true;
    robotGroup.add(head);

    // Glowing Cyan Visor
    const visorGeo = new THREE.BoxGeometry(0.45, 0.14, 0.12);
    const visorMat = new THREE.MeshBasicMaterial({{ color: 0x00f3ff }});
    const visor = new THREE.Mesh(visorGeo, visorMat);
    visor.position.set(0, 1.75, 0.26);
    robotGroup.add(visor);

    // Arms
    const armGeo = new THREE.CylinderGeometry(0.09, 0.09, 0.75, 8);
    const leftArm = new THREE.Mesh(armGeo, darkMetal);
    leftArm.position.set(-0.6, 0.95, 0);
    leftArm.castShadow = true;
    robotGroup.add(leftArm);

    const rightArm = new THREE.Mesh(armGeo, darkMetal);
    rightArm.position.set(0.6, 0.95, 0);
    rightArm.castShadow = true;
    robotGroup.add(rightArm);

    scene.add(robotGroup);

    // Robot Motion Kinematics State
    const targetPos = new THREE.Vector3(0, 0, 0);
    let targetRot = Math.PI;
    let jumpY = 0;
    let currentAction = 'idle';

    // Camera presets
    function setCameraPreset(preset) {{
        document.querySelectorAll('.cam-btn').forEach(b => b.classList.remove('active'));
        if (preset === 'top') {{
            document.getElementById('btn-top').classList.add('active');
            camera.position.set(0, 11, 0.01);
        }} else if (preset === 'front') {{
            document.getElementById('btn-front').classList.add('active');
            camera.position.set(0, 2.2, 7.0);
        }} else {{
            document.getElementById('btn-iso').classList.add('active');
            camera.position.set(5.5, 5.0, 6.0);
        }}
    }}

    // ----------------------------------------------------
    // 2. KINETIC LOCOMOTION & AI EXECUTION ENGINE
    // ----------------------------------------------------
    function executeLocomotion(actionName) {{
        const step = 2.0;
        const angleStep = Math.PI / 2;
        currentAction = actionName;

        document.getElementById('robot-action-label').innerText = actionName.toUpperCase();

        if (actionName === 'forward') {{
            targetPos.z -= step;
            speakRobotVoice("Moving forward");
            appendLog(`[ACTION] Locomotion: FORWARD`);
        }} else if (actionName === 'backward') {{
            targetPos.z += step;
            speakRobotVoice("Moving backward");
            appendLog(`[ACTION] Locomotion: BACKWARD`);
        }} else if (actionName === 'left') {{
            targetRot += angleStep;
            speakRobotVoice("Turning left");
            appendLog(`[ACTION] Locomotion: TURN LEFT`);
        }} else if (actionName === 'right') {{
            targetRot -= angleStep;
            speakRobotVoice("Turning right");
            appendLog(`[ACTION] Locomotion: TURN RIGHT`);
        }} else if (actionName === 'jump') {{
            jumpY = 1.8;
            speakRobotVoice("Jumping");
            appendLog(`[ACTION] Locomotion: JUMP`);
            setTimeout(() => {{ jumpY = 0; }}, 600);
        }} else if (actionName === 'spin') {{
            targetRot += Math.PI * 2;
            speakRobotVoice("Spinning");
            appendLog(`[ACTION] Locomotion: 360 SPIN`);
        }} else if (actionName === 'reset') {{
            targetPos.set(0, 0, 0);
            targetRot = Math.PI;
            jumpY = 0;
            speakRobotVoice("Resetting to origin");
            appendLog(`[ACTION] Locomotion: RESET ORIGIN`);
        }}
    }}

    function appendLog(msg) {{
        const term = document.getElementById('terminal-log');
        term.innerText += '\\n> ' + msg;
        term.scrollTop = term.scrollHeight;
    }}

    // ----------------------------------------------------
    // 3. TEXT-TO-SPEECH (TTS) ROBOT VOICE SYNTHESIZER
    // ----------------------------------------------------
    function speakRobotVoice(text) {{
        const enabled = document.getElementById('tts-toggle').checked;
        if (!enabled || !('speechSynthesis' in window)) return;
        try {{
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.05;
            utterance.pitch = 1.15; // Robotic tone
            window.speechSynthesis.speak(utterance);
        }} catch (e) {{
            console.warn("TTS Error:", e);
        }}
    }}

    // ----------------------------------------------------
    // 4. REAL-TIME SPEECH RECOGNITION (WEB SPEECH API)
    // ----------------------------------------------------
    let recognition = null;
    let isListening = false;
    let continuousMode = false;

    function initSpeechRecognition() {{
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {{
            appendLog("Speech recognition not supported in this browser. Please use Chrome/Edge.");
            return null;
        }}

        const rec = new SpeechRec();
        rec.continuous = true;
        rec.interimResults = true;
        rec.lang = 'en-US';

        rec.onstart = () => {{
            isListening = true;
            updateVoiceButtonUI(true);
            setAudioWaveActive(true);
        }};

        rec.onresult = (event) => {{
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {{
                if (event.results[i].isFinal) {{
                    finalTranscript += event.results[i][0].transcript;
                }} else {{
                    interimTranscript += event.results[i][0].transcript;
                }}
            }}

            const heard = (finalTranscript || interimTranscript).trim();
            if (heard) {{
                document.getElementById('live-speech').innerText = `"${{heard}}"`;
            }}

            if (finalTranscript) {{
                processVoiceCommand(finalTranscript.trim());
            }}
        }};

        rec.onerror = (event) => {{
            console.warn("Speech recognition error:", event.error);
            if (event.error === 'not-allowed') {{
                alert("Microphone access denied. Please click allow in browser address bar.");
            }}
        }};

        rec.onend = () => {{
            isListening = false;
            setAudioWaveActive(false);
            if (continuousMode) {{
                // Auto-restart for hands-free continuous voice control
                try {{ rec.start(); }} catch(e) {{}}
            }} else {{
                updateVoiceButtonUI(false);
            }}
        }};

        return rec;
    }}

    function toggleVoiceListening() {{
        if (!recognition) {{
            recognition = initSpeechRecognition();
        }}
        if (!recognition) return;

        if (isListening) {{
            continuousMode = false;
            document.getElementById('continuous-toggle').checked = false;
            recognition.stop();
        }} else {{
            try {{
                recognition.start();
            }} catch (e) {{
                console.warn(e);
            }}
        }}
    }}

    function toggleContinuousMode(enabled) {{
        continuousMode = enabled;
        if (enabled && !isListening) {{
            toggleVoiceListening();
        }}
    }}

    function updateVoiceButtonUI(listening) {{
        const btn = document.getElementById('voice-btn');
        const label = document.getElementById('voice-label');
        const icon = document.getElementById('voice-icon');

        if (listening) {{
            btn.classList.add('listening');
            label.innerText = "🔴 LISTENING... SPEAK NOW!";
            icon.innerText = "🎙️";
        }} else {{
            btn.classList.remove('listening');
            label.innerText = "CLICK TO TALK (VOICE CONTROL)";
            icon.innerText = "🎤";
        }}
    }}

    function setAudioWaveActive(active) {{
        document.querySelectorAll('.audio-bar').forEach(bar => {{
            if (active) bar.classList.add('active');
            else bar.classList.remove('active');
        }});
    }}

    // ----------------------------------------------------
    // 5. INTENT PARSING & COMMAND DISPATCHER
    // ----------------------------------------------------
    const API_KEY = "{api_key}";

    function parseRuleBasedLocomotion(text) {{
        const lower = text.toLowerCase();
        if (lower.includes('forward') || lower.includes('front') || lower.includes('ahead') || lower.includes('straight')) return 'forward';
        if (lower.includes('backward') || lower.includes('back') || lower.includes('reverse')) return 'backward';
        if (lower.includes('left')) return 'left';
        if (lower.includes('right')) return 'right';
        if (lower.includes('jump') || lower.includes('hop')) return 'jump';
        if (lower.includes('spin') || lower.includes('dance') || lower.includes('rotate')) return 'spin';
        if (lower.includes('reset') || lower.includes('center') || lower.includes('stop')) return 'reset';
        return null;
    }}

    async function processVoiceCommand(spokenText) {{
        appendLog(`Heard Voice: "${{spokenText}}"`);

        // 1. Instant rule-based check for zero latency locomotion
        const matchedAction = parseRuleBasedLocomotion(spokenText);
        if (matchedAction) {{
            executeLocomotion(matchedAction);
            return;
        }}

        // 2. Gemini AI query if conversational or complex
        if (API_KEY) {{
            appendLog(`Querying Gemini AI brain...`);
            try {{
                const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${{API_KEY}}`;
                const payload = {{
                    contents: [{{
                        parts: [{{
                            text: `You are Harry, a friendly voice-controlled 3D robot companion. The user spoke: "${{spokenText}}". Respond in 1-2 concise, witty sentences suitable for spoken robot dialogue.`
                        }}]
                    }}]
                }};

                const res = await fetch(url, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});

                const data = await res.json();
                
                if (data.error) {{
                    const errMsg = `Gemini API Error: ${{data.error.message || 'Unable to process query'}}`;
                    appendLog(errMsg);
                    speakRobotVoice("Sorry, I encountered an issue accessing my AI brain. Please check your Gemini API key.");
                    return;
                }}

                const reply = data.candidates?.[0]?.content?.parts?.[0]?.text;
                if (reply) {{
                    appendLog(`AI Response: "${{reply}}"`);
                    speakRobotVoice(reply);
                }} else {{
                    const fallback = `I hear you, operator: "${{spokenText}}"`;
                    appendLog(fallback);
                    speakRobotVoice(fallback);
                }}
            }} catch (e) {{
                const fallback = `I hear you, operator: "${{spokenText}}"`;
                appendLog(fallback);
                speakRobotVoice(fallback);
            }}
        }} else {{
            const fallback = `Understood: "${{spokenText}}". To enable full conversational answers, set your Gemini API key in the sidebar.`;
            appendLog(fallback);
            speakRobotVoice(fallback);
        }}
    }}

    function sendManualText() {{
        const inp = document.getElementById('manual-text-input');
        const val = inp.value.trim();
        if (!val) return;
        document.getElementById('live-speech').innerText = `"${{val}}"`;
        processVoiceCommand(val);
        inp.value = '';
    }}

    // ----------------------------------------------------
    // 6. ANIMATION & RENDER LOOP
    // ----------------------------------------------------
    let clock = new THREE.Clock();

    function animate() {{
        requestAnimationFrame(animate);
        const time = clock.getElapsedTime();

        // Smooth Lerp Position & Rotation
        robotGroup.position.x = THREE.MathUtils.lerp(robotGroup.position.x, targetPos.x, 0.08);
        robotGroup.position.z = THREE.MathUtils.lerp(robotGroup.position.z, targetPos.z, 0.08);
        robotGroup.position.y = THREE.MathUtils.lerp(robotGroup.position.y, jumpY, 0.15);
        robotGroup.rotation.y = THREE.MathUtils.lerp(robotGroup.rotation.y, targetRot, 0.12);

        // Idle hovering float
        if (jumpY === 0) {{
            torso.position.y = 1.0 + Math.sin(time * 3) * 0.03;
            head.position.y = 1.75 + Math.sin(time * 3) * 0.03;
        }}

        // Update telemetry HUD
        document.getElementById('pos-label').innerText = 
            `X:${{robotGroup.position.x.toFixed(1)}} Y:${{robotGroup.position.y.toFixed(1)}} Z:${{robotGroup.position.z.toFixed(1)}}`;
        const deg = Math.round((robotGroup.rotation.y * 180 / Math.PI) % 360);
        document.getElementById('rot-label').innerText = `${{deg < 0 ? deg + 360 : deg}}°`;

        controls.update();
        renderer.render(scene, camera);
    }}
    animate();

    window.addEventListener('resize', () => {{
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }});
</script>

</body>
</html>
"""

components.html(robot_console_html, height=750, scrolling=False)
