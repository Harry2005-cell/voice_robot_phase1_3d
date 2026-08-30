# NEXUS — AI Voice-Controlled Robotic Assistant

> **"Speak. Command. Watch Intelligence Move."**

NEXUS is a futuristic, professional, interactive AI voice-controlled 3D robot assistant web application. Built with **React 18**, **TypeScript**, **Tailwind CSS**, **Three.js**, **React Three Fiber (R3F)**, **Web Speech API**, and **Web Audio API**.

---

## 🌟 Key Features

1. **Futuristic Glassmorphic UI Dashboard**
   - Modern dark theme inspired by Tesla robotics & professional AI dashboards.
   - Micro-interactions, glowing status rings, responsive mobile/desktop layout.

2. **Articulated 3D Humanoid Robot Simulation**
   - High-precision 3D WebGL model built with Three.js / React Three Fiber.
   - Articulated joints (Head, Visor, Torso Arc Reactor, Shoulders, Elbows, Hands, Hips, Knees, Feet).
   - Raycast body part hover highlighting & interactive joint override selection.
   - Orbit controls, zoom, pan, and smooth camera position presets (`Front`, `Side`, `Back`, `Top`, `Reset`).

3. **Natural Voice Control Pipeline**
   - **User Voice → STT → Intent Extraction → Safety Check → Motion Kinematics → 3D Action → Response → TTS Audio**.
   - Circular animated microphone button with real-time Web Audio API frequency waveform visualizer.
   - Graceful fallback for microphone permissions, silence, or unsupported browsers via text input.

4. **Dual-Mode AI Intent Engine**
   - **Client-Side Semantic NLP**: Converts natural speech into validated JSON schemas (`MOVE`, `ROTATE`, `GESTURE`, `INTERACTION`, `SEQUENCE`).
   - Supports complex composite commands (e.g., *"Move forward 2 steps, turn right 90 degrees, and wave"*).
   - Optional **OpenAI API Integration**: Enable via `VITE_OPENAI_API_KEY` in `.env`.

5. **Smooth Kinematic Motion Planner**
   - Cubic easing interpolation (`easeInOutCubic`) for natural joint acceleration/deceleration without visual snapping.
   - Multi-state Animation Controller (`IDLE`, `LISTENING`, `THINKING`, `WALKING`, `TURNING`, `WAVING`, `POINTING`, `NODDING`, `SPEAKING`, `SUCCESS`, `ERROR`, `STOPPED`).

6. **Safety & Emergency Controls**
   - Ambiguity validation modal for unclear instructions (e.g. *"Go over there"*).
   - Prominent **STOP ROBOT** button & instant `ESC` key hotkey override.

7. **Autonomous Demo & Telemetry Analytics**
   - Dedicated **AI ROBOT DEMO** presentation routine showcasing full capabilities.
   - Real-time Telemetry Panel (Battery, Mode, Speed, X/Y/Z Coordinates, Heading Angle, Health).
   - System Activity Monitor Terminal Log & Session Analytics modal.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher

### Installation

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Open your browser at `http://localhost:3000`.

---

## ⚙️ Environment Configuration (.env)

NEXUS includes a built-in zero-latency NLP intent engine that works 100% offline out-of-the-box. To optionally connect an OpenAI API key:

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Set your API key:
```env
VITE_OPENAI_API_KEY=your_openai_api_key_here
```

---

## 🗣️ Supported Commands

- **Movement**:
  - *"Move forward two steps"*
  - *"Step backward"*
  - *"Move 3 steps to the left"*
- **Rotation**:
  - *"Turn left"*
  - *"Turn right 90 degrees"*
  - *"Turn around"*
- **Gestures**:
  - *"Wave your right hand"*
  - *"Raise both hands"*
  - *"Dance routine"*
  - *"Bow polite"*
- **Interaction**:
  - *"Say hello"*
  - *"Introduce yourself"*
  - *"What is your status?"*
  - *"Start demonstration"*
  - *"Stop robot"*
- **Composite Sequences**:
  - *"Move forward, turn right, and wave"*

---

## 🛠️ Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Framer Motion, Lucide Icons
- **3D Graphics**: Three.js, React Three Fiber (`@react-three/fiber`), Drei (`@react-three/drei`)
- **State Management**: Zustand
- **Speech & Audio**: Web Speech API (`SpeechRecognition`), SpeechSynthesis TTS, Web Audio API Synthesizer
- **Build Tool**: Vite

---

## 📄 License

MIT License. Designed for engineering project demonstrations, hackathons, portfolios, and research showcase.
