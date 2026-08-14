import os
import sys
import json
import base64
import socket
import streamlit as st
import streamlit.components.v1 as components

# Add backend directory to sys.path so modules can be imported directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from app.ai.gemini_client import get_intent, parse_rule_based_intent, get_api_key
    from app.biometrics.speechbrain_model import identify_speaker, enroll_speaker
except ImportError:
    # Direct import fallback if needed
    sys.path.append(os.path.join(BACKEND_DIR, "app"))
    from ai.gemini_client import get_intent, parse_rule_based_intent, get_api_key
    from biometrics.speechbrain_model import identify_speaker, enroll_speaker

# Set Streamlit page configuration
st.set_page_config(
    page_title="Harry AI - 3D Voice Robot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cyberpunk / Futuristic Dark Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    /* Background and global styles */
    .stApp {
        background-color: #0a0a0a;
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1.5px;
    }
    
    .main-title {
        color: #00f3ff;
        text-shadow: 0 0 15px rgba(0, 243, 255, 0.6);
        font-size: 2.2rem;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 0px;
    }
    
    .sub-title {
        color: #888888;
        font-size: 0.95rem;
        margin-bottom: 20px;
        letter-spacing: 1px;
    }
    
    /* Glowing HUD Cards */
    .hud-card {
        background: linear-gradient(145deg, #141414, #0d0d0d);
        border: 1px solid #222222;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6);
    }
    
    .hud-card-accent {
        background: linear-gradient(145deg, #181c20, #0d1216);
        border: 1px solid #00f3ff44;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.15);
    }
    
    /* Status Badges */
    .badge-verified {
        display: inline-block;
        background: rgba(0, 243, 255, 0.12);
        color: #00f3ff;
        border: 1px solid #00f3ff;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    .badge-guest {
        display: inline-block;
        background: rgba(255, 152, 0, 0.12);
        color: #ff9800;
        border: 1px solid #ff9800;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    /* Terminal display */
    .terminal-box {
        background-color: #050505;
        border: 1px solid #2a2a2a;
        border-left: 3px solid #00f3ff;
        border-radius: 8px;
        padding: 12px 16px;
        font-family: 'Courier New', Courier, monospace;
        color: #00f3ff;
        font-size: 0.9rem;
        min-height: 80px;
        white-space: pre-wrap;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #161a1d, #1c2228);
        border: 1px solid #00f3ff88;
        color: #00f3ff;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 1px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: #00f3ff;
        color: #000000;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.7);
        border-color: #00f3ff;
    }
</style>
""", unsafe_allow_html=True)

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

# Initialize Session State
if "last_action" not in st.session_state:
    st.session_state.last_action = "reset"
if "action_seq" not in st.session_state:
    st.session_state.action_seq = 0
if "speaker_name" not in st.session_state:
    st.session_state.speaker_name = "Guest"
if "match_score" not in st.session_state:
    st.session_state.match_score = 0
if "terminal_msg" not in st.session_state:
    st.session_state.terminal_msg = "🤖 SYSTEM READY. Awaiting vocal or textual command..."
if "camera_view" not in st.session_state:
    st.session_state.camera_view = "isometric"
if "tts_text" not in st.session_state:
    st.session_state.tts_text = ""

# Sidebar Settings & Diagnostics
with st.sidebar:
    st.markdown("<h2 style='color:#00f3ff; font-size:1.3rem;'>⚡ CONTROL UPLINK</h2>", unsafe_allow_html=True)
    
    # Network status info
    local_ip = get_local_ip()
    st.markdown(f"""
    <div style='background:#111; padding:10px; border-radius:8px; border:1px solid #333; font-size:0.85rem; margin-bottom:15px;'>
        <div style='color:#888;'>🌐 Network Deployment:</div>
        <div style='color:#00f3ff; font-weight:bold;'>http://{local_ip}:8501</div>
        <div style='color:#666; font-size:0.75rem; margin-top:4px;'>Open to all LAN & public devices</div>
    </div>
    """, unsafe_allow_html=True)

    # Gemini API Key configuration
    st.markdown("### 🔑 AI Core Settings")
    current_key = get_api_key()
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=current_key,
        type="password",
        placeholder="Enter AI Studio API Key...",
        help="Obtain an API key from Google AI Studio (aistudio.google.com)"
    )
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input

    st.markdown("---")
    
    # Camera Presets
    st.markdown("### 🎥 3D Camera Presets")
    cam_col1, cam_col2, cam_col3 = st.columns(3)
    with cam_col1:
        if st.button("Isometric", key="cam_iso"):
            st.session_state.camera_view = "isometric"
            st.rerun()
    with cam_col2:
        if st.button("Top", key="cam_top"):
            st.session_state.camera_view = "top"
            st.rerun()
    with cam_col3:
        if st.button("Front", key="cam_front"):
            st.session_state.camera_view = "front"
            st.rerun()

    st.markdown("---")
    st.markdown("### 🛠️ Quick Movement Pad")
    
    col_up1, col_up2, col_up3 = st.columns([1, 2, 1])
    with col_up2:
        if st.button("⬆️ FORWARD", use_container_width=True):
            st.session_state.last_action = "forward"
            st.session_state.action_seq += 1
            st.session_state.terminal_msg = f"Executing: FORWARD movement (Seq #{st.session_state.action_seq})"
            st.session_state.tts_text = "Moving forward"
            st.rerun()

    col_mid1, col_mid2 = st.columns(2)
    with col_mid1:
        if st.button("⬅️ LEFT", use_container_width=True):
            st.session_state.last_action = "left"
            st.session_state.action_seq += 1
            st.session_state.terminal_msg = f"Executing: Turn LEFT (Seq #{st.session_state.action_seq})"
            st.session_state.tts_text = "Turning left"
            st.rerun()
    with col_mid2:
        if st.button("➡️ RIGHT", use_container_width=True):
            st.session_state.last_action = "right"
            st.session_state.action_seq += 1
            st.session_state.terminal_msg = f"Executing: Turn RIGHT (Seq #{st.session_state.action_seq})"
            st.session_state.tts_text = "Turning right"
            st.rerun()

    col_dn1, col_dn2, col_dn3 = st.columns([1, 2, 1])
    with col_dn2:
        if st.button("⬇️ BACKWARD", use_container_width=True):
            st.session_state.last_action = "backward"
            st.session_state.action_seq += 1
            st.session_state.terminal_msg = f"Executing: BACKWARD movement (Seq #{st.session_state.action_seq})"
            st.session_state.tts_text = "Moving backward"
            st.rerun()

    col_act1, col_act2, col_act3 = st.columns(3)
    with col_act1:
        if st.button("🦘 JUMP", use_container_width=True):
            st.session_state.last_action = "jump"
            st.session_state.action_seq += 1
            st.session_state.terminal_msg = f"Executing: Kinetic JUMP (Seq #{st.session_state.action_seq})"
            st.session_state.tts_text = "Jumping"
            st.rerun()
    with col_act2:
        if st.button("🔄 SPIN", use_container_width=True):
            st.session_state.last_action = "spin"
            st.session_state.action_seq += 1
            st.session_state.terminal_msg = f"Executing: 360 SPIN (Seq #{st.session_state.action_seq})"
            st.session_state.tts_text = "Spinning"
            st.rerun()
    with col_act3:
        if st.button("🎯 RESET", use_container_width=True):
            st.session_state.last_action = "reset"
            st.session_state.action_seq += 1
            st.session_state.terminal_msg = f"Position RESET to Origin (Seq #{st.session_state.action_seq})"
            st.session_state.tts_text = "Resetting position"
            st.rerun()

# Main App Header
st.markdown("<div class='main-title'>🤖 HARRY AI: 3D VOICE ROBOT</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Edge-to-Cloud Biometric Voice Control • Three.js Digital Twin • Gemini Intelligence</div>", unsafe_allow_html=True)

# Biometric & Status HUD Bar
status_col1, status_col2 = st.columns([1, 1])

with status_col1:
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:12px; background:#141414; padding:8px 16px; border-radius:30px; border:1px solid #2a2a2a;'>
        <span style='color:#888; font-size:0.85rem;'>SYSTEM STATUS:</span>
        <span style='color:#00f3ff; font-weight:bold; font-size:0.9rem;'>ONLINE (PORT 8501)</span>
        <span style='color:#444;'>|</span>
        <span style='color:#888; font-size:0.85rem;'>ACTIVE ACTION:</span>
        <span style='color:#4caf50; font-weight:bold; text-transform:uppercase;'>{st.session_state.last_action}</span>
    </div>
    """, unsafe_allow_html=True)

with status_col2:
    is_verified = st.session_state.match_score > 70 and st.session_state.speaker_name not in ["Guest", "Unknown"]
    badge_class = "badge-verified" if is_verified else "badge-guest"
    badge_text = f"VERIFIED: {st.session_state.speaker_name.upper()} ({st.session_state.match_score}% MATCH)" if is_verified else f"IDENTITY: {st.session_state.speaker_name.upper()} ({st.session_state.match_score}% MATCH)"
    st.markdown(f"""
    <div style='display:flex; align-items:center; justify-content:flex-end; gap:12px; padding:8px 0px;'>
        <span style='color:#888; font-size:0.85rem;'>BIOMETRIC UPLINK:</span>
        <span class='{badge_class}'>{badge_text}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

# Core Layout: Left column for Controls & AI, Right column for 3D Three.js Visualizer
col_left, col_right = st.columns([1, 1.3])

with col_left:
    tab_command, tab_enroll, tab_raw = st.tabs(["🎤 Voice & AI Commands", "👤 Biometric Enrollment", "📊 Terminal Logs"])
    
    with tab_command:
        st.markdown("<div class='hud-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#00f3ff; font-size:1.1rem; margin-top:0;'>Command Interface</h3>", unsafe_allow_html=True)
        
        # Audio File or Voice Input
        audio_file = st.file_uploader("Upload / Record Audio (.wav)", type=["wav", "mp3", "ogg"], key="cmd_audio")
        
        # Text prompt input
        text_prompt = st.text_input(
            "Natural Language Speech / Command Prompt",
            placeholder="e.g. 'move forward', 'turn left', 'jump', 'tell me about black holes'",
            key="cmd_text"
        )
        
        if st.button("🚀 Process Voice / Command", use_container_width=True, key="btn_process"):
            if not text_prompt and not audio_file:
                st.warning("Please provide either an audio file or a text command.")
            else:
                speaker_id = "User"
                match_val = 100

                # 1. Biometric speaker identification if audio is uploaded
                if audio_file:
                    temp_audio_path = os.path.join(CURRENT_DIR, "temp_command.wav")
                    with open(temp_audio_path, "wb") as f:
                        f.write(audio_file.getbuffer())
                    
                    speaker_id, match_val = identify_speaker(temp_audio_path)
                    try:
                        os.remove(temp_audio_path)
                    except Exception:
                        pass

                st.session_state.speaker_name = speaker_id
                st.session_state.match_score = match_val

                # 2. Intent parsing with Gemini & Rule-based engine
                query_text = text_prompt if text_prompt else "Process voice command"
                intent_res = get_intent(query_text, speaker_id)

                if intent_res:
                    intent_type = str(intent_res.get("type", "")).lower()
                    if intent_type == "locomotion" or "action" in intent_res:
                        act = intent_res.get("action", "forward")
                        st.session_state.last_action = act
                        st.session_state.action_seq += 1
                        st.session_state.terminal_msg = f"Speaker: {speaker_id} ({match_val}% match)\nIntent: LOCOMOTION -> [{act.upper()}]"
                        st.session_state.tts_text = f"Executing {act}"
                    else:
                        reply = intent_res.get("response", "Command processed.")
                        st.session_state.terminal_msg = f"Speaker: {speaker_id} ({match_val}% match)\nAI Response: {reply}"
                        st.session_state.tts_text = reply
                
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        
        # Real-time Terminal Output
        st.markdown("<div style='color:#888; font-size:0.85rem; margin-bottom:4px;'>ROBOT HUD TERMINAL</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='terminal-box'>{st.session_state.terminal_msg}</div>", unsafe_allow_html=True)

    with tab_enroll:
        st.markdown("<div class='hud-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#00f3ff; font-size:1.1rem; margin-top:0;'>Operator Biometric Enrollment</h3>", unsafe_allow_html=True)
        st.write("Enroll your voiceprint into the SpeechBrain neural biometric database for instant identity verification.")
        
        enroll_name = st.text_input("Operator Name", placeholder="e.g. Harshal", key="enroll_name")
        enroll_audio = st.file_uploader("Upload Voice Sample (.wav)", type=["wav"], key="enroll_audio")
        
        if st.button("💾 Enroll Voiceprint", use_container_width=True, key="btn_enroll"):
            if not enroll_name or not enroll_audio:
                st.warning("Please provide both an operator name and an audio file.")
            else:
                temp_enroll_path = os.path.join(CURRENT_DIR, f"temp_enroll_{enroll_name}.wav")
                with open(temp_enroll_path, "wb") as f:
                    f.write(enroll_audio.getbuffer())
                
                success = enroll_speaker(enroll_name, temp_enroll_path)
                try:
                    os.remove(temp_enroll_path)
                except Exception:
                    pass

                if success:
                    st.success(f"Voiceprint for '{enroll_name}' successfully enrolled!")
                    st.session_state.speaker_name = enroll_name
                    st.session_state.match_score = 100
                    st.session_state.terminal_msg = f"Biometric database updated: Profile created for {enroll_name}"
                    st.session_state.tts_text = f"Biometric enrollment complete for {enroll_name}"
                    st.rerun()
                else:
                    st.error("Failed to enroll voiceprint. Please ensure valid audio data.")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab_raw:
        st.markdown("<div class='hud-card'>", unsafe_allow_html=True)
        st.markdown("### System Telemetry")
        st.json({
            "active_action": st.session_state.last_action,
            "action_sequence": st.session_state.action_seq,
            "identified_speaker": st.session_state.speaker_name,
            "confidence_score": f"{st.session_state.match_score}%",
            "camera_preset": st.session_state.camera_view,
            "network_ip": local_ip
        })
        st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#00f3ff; font-size:1.1rem; margin:0;'>3D Digital Twin Visualizer</h3>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:#888; font-size:0.8rem;'>VIEW: {st.session_state.camera_view.upper()}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 3D Three.js Interactive WebGL Component
    threejs_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                overflow: hidden;
                background-color: #080808;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            #canvas-container {{
                width: 100%;
                height: 520px;
                position: relative;
                border-radius: 12px;
                border: 1px solid #2a2a2a;
                box-shadow: inset 0 0 30px rgba(0, 243, 255, 0.1);
            }}
            #speech-controls {{
                position: absolute;
                bottom: 12px;
                left: 12px;
                z-index: 10;
                display: flex;
                gap: 8px;
            }}
            .hud-btn {{
                background: rgba(10, 10, 10, 0.85);
                border: 1px solid #00f3ff;
                color: #00f3ff;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                cursor: pointer;
                backdrop-filter: blur(5px);
                transition: all 0.2s ease;
            }}
            .hud-btn:hover {{
                background: #00f3ff;
                color: #000;
                box-shadow: 0 0 10px #00f3ff;
            }}
            #hud-overlay {{
                position: absolute;
                top: 12px;
                left: 12px;
                z-index: 10;
                color: #00f3ff;
                font-size: 11px;
                font-family: monospace;
                background: rgba(0, 0, 0, 0.6);
                padding: 6px 10px;
                border-radius: 4px;
                border-left: 2px solid #00f3ff;
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    </head>
    <body>
        <div id="canvas-container">
            <div id="hud-overlay">
                POSE: [{st.session_state.last_action.upper()}] | SEQ: #{st.session_state.action_seq}
            </div>
            <div id="speech-controls">
                <button class="hud-btn" id="mic-btn" onclick="startSpeechRecognition()">🎤 In-Browser Speech Recognition</button>
            </div>
        </div>

        <script>
            // 1. Scene & Camera Setup
            const container = document.getElementById('canvas-container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0a);
            scene.fog = new THREE.FogExp2(0x0a0a0a, 0.035);

            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            
            // Set camera position based on preset
            const preset = "{st.session_state.camera_view}";
            if (preset === "top") {{
                camera.position.set(0, 12, 0.01);
            }} else if (preset === "front") {{
                camera.position.set(0, 2.5, 7.5);
            }} else {{
                camera.position.set(5.5, 5.5, 5.5);
            }}

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

            // 2. Cyberpunk Lighting & Grid
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0x00f3ff, 1.2);
            dirLight.position.set(5, 10, 5);
            dirLight.castShadow = true;
            scene.add(dirLight);

            const secondaryLight = new THREE.DirectionalLight(0xff0077, 0.8);
            secondaryLight.position.set(-5, 8, -5);
            scene.add(secondaryLight);

            // Sci-fi Grid Floor
            const gridHelper = new THREE.GridHelper(30, 30, 0x00f3ff, 0x222222);
            gridHelper.position.y = 0;
            scene.add(gridHelper);

            // Circular Cyber Platform
            const platformGeo = new THREE.CylinderGeometry(3.5, 3.7, 0.1, 32);
            const platformMat = new THREE.MeshStandardMaterial({{
                color: 0x111111,
                roughness: 0.2,
                metalness: 0.8
            }});
            const platform = new THREE.Mesh(platformGeo, platformMat);
            platform.position.y = -0.05;
            platform.receiveShadow = true;
            scene.add(platform);

            // Glowing ring around platform
            const ringGeo = new THREE.RingGeometry(3.6, 3.75, 32);
            const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f3ff, side: THREE.DoubleSide }});
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.x = -Math.PI / 2;
            ring.position.y = 0.01;
            scene.add(ring);

            // 3. Robot Digital Twin Model Creation (Procedural Futuristic Robot Avatar)
            const robotGroup = new THREE.Group();
            
            // Robot Base / Chassis
            const baseGeo = new THREE.CylinderGeometry(0.6, 0.7, 0.3, 16);
            const bodyMat = new THREE.MeshStandardMaterial({{ color: 0x1c232b, metalness: 0.9, roughness: 0.2 }});
            const base = new THREE.Mesh(baseGeo, bodyMat);
            base.position.y = 0.3;
            base.castShadow = true;
            robotGroup.add(base);

            // Torso
            const torsoGeo = new THREE.BoxGeometry(0.8, 0.9, 0.5);
            const torsoMat = new THREE.MeshStandardMaterial({{ color: 0x242d38, metalness: 0.8, roughness: 0.3 }});
            const torso = new THREE.Mesh(torsoGeo, torsoMat);
            torso.position.y = 0.9;
            torso.castShadow = true;
            robotGroup.add(torso);

            // Cyber Core Glow
            const coreGeo = new THREE.SphereGeometry(0.15, 16, 16);
            const coreMat = new THREE.MeshBasicMaterial({{ color: 0x00f3ff }});
            const core = new THREE.Mesh(coreGeo, coreMat);
            core.position.set(0, 0.9, 0.26);
            robotGroup.add(core);

            // Robot Head
            const headGeo = new THREE.BoxGeometry(0.5, 0.45, 0.45);
            const head = new THREE.Mesh(headGeo, bodyMat);
            head.position.y = 1.6;
            head.castShadow = true;
            robotGroup.add(head);

            // Glowing Visor
            const visorGeo = new THREE.BoxGeometry(0.4, 0.12, 0.1);
            const visorMat = new THREE.MeshBasicMaterial({{ color: 0x00f3ff }});
            const visor = new THREE.Mesh(visorGeo, visorMat);
            visor.position.set(0, 1.6, 0.24);
            robotGroup.add(visor);

            // Arms
            const armGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.7, 8);
            const leftArm = new THREE.Mesh(armGeo, bodyMat);
            leftArm.position.set(-0.55, 0.85, 0);
            leftArm.castShadow = true;
            robotGroup.add(leftArm);

            const rightArm = new THREE.Mesh(armGeo, bodyMat);
            rightArm.position.set(0.55, 0.85, 0);
            rightArm.castShadow = true;
            robotGroup.add(rightArm);

            scene.add(robotGroup);

            // 4. Locomotion Kinematics State
            const targetPos = new THREE.Vector3(0, 0, 0);
            let targetRot = Math.PI;
            let jumpHeight = 0;
            const action = "{st.session_state.last_action}".toLowerCase();
            const step = 2.0;
            const angleStep = Math.PI / 2;

            if (action.includes('forward') || action.includes('front')) {{
                targetPos.z -= step;
            }} else if (action.includes('backward') || action.includes('back')) {{
                targetPos.z += step;
            }} else if (action.includes('left')) {{
                targetRot += angleStep;
            }} else if (action.includes('right')) {{
                targetRot -= angleStep;
            }} else if (action.includes('jump')) {{
                jumpHeight = 1.8;
                setTimeout(() => {{ jumpHeight = 0; }}, 600);
            }} else if (action.includes('spin')) {{
                targetRot += Math.PI * 2;
            }} else if (action.includes('reset')) {{
                targetPos.set(0, 0, 0);
                targetRot = Math.PI;
                jumpHeight = 0;
            }}

            // 5. Speech Synthesis & Recognition in Browser
            const ttsMessage = "{st.session_state.tts_text}";
            if (ttsMessage && 'speechSynthesis' in window) {{
                try {{
                    window.speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance(ttsMessage);
                    utterance.rate = 1.05;
                    utterance.pitch = 1.1;
                    window.speechSynthesis.speak(utterance);
                }} catch (e) {{}}
            }}

            function startSpeechRecognition() {{
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRecognition) {{
                    alert("Speech recognition is not supported in this browser. Please use Chrome/Edge.");
                    return;
                }}
                const recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                const micBtn = document.getElementById('mic-btn');
                micBtn.innerText = "🔴 Listening...";

                recognition.onresult = (event) => {{
                    const transcript = event.results[0][0].transcript;
                    micBtn.innerText = "Heard: " + transcript;
                    alert("Speech Recognized: '" + transcript + "'\\nEnter this command in the left panel!");
                }};

                recognition.onerror = () => {{
                    micBtn.innerText = "🎤 In-Browser Speech Recognition";
                }};

                recognition.onend = () => {{
                    micBtn.innerText = "🎤 In-Browser Speech Recognition";
                }};

                recognition.start();
            }}

            // 6. Animation Render Loop
            let clock = new THREE.Clock();
            function animate() {{
                requestAnimationFrame(animate);
                const delta = clock.getDelta();
                const time = clock.getElapsedTime();

                // Smooth Position & Rotation Interpolation (Lerp)
                robotGroup.position.x = THREE.MathUtils.lerp(robotGroup.position.x, targetPos.x, 0.08);
                robotGroup.position.z = THREE.MathUtils.lerp(robotGroup.position.z, targetPos.z, 0.08);
                robotGroup.position.y = THREE.MathUtils.lerp(robotGroup.position.y, jumpHeight, 0.15);
                robotGroup.rotation.y = THREE.MathUtils.lerp(robotGroup.rotation.y, targetRot, 0.12);

                // Subtle idle hovering pulsation
                if (jumpHeight === 0) {{
                    torso.position.y = 0.9 + Math.sin(time * 3) * 0.03;
                    head.position.y = 1.6 + Math.sin(time * 3) * 0.03;
                }}

                controls.update();
                renderer.render(scene, camera);
            }}
            animate();

            // Responsive Resizing
            window.addEventListener('resize', () => {{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }});
        </script>
    </body>
    </html>
    """
    components.html(threejs_html, height=550)
