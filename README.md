# 🤖 Harry AI: Voice-Controlled 3D Robot Digital Twin

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B)
![React](https://img.shields.io/badge/React-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini-orange)

A full-stack, edge-to-cloud web application that allows users to control a 3D virtual robot using their voice. The system features biometric voice enrollment, real-time speech recognition, and uses Google's `gemini-2.5-flash` / `gemini-2.0-flash` AI to parse natural language into kinetic 3D commands.

---

## ✨ Features

* **Biometric Security:** Verifies speaker identity through audio voiceprint enrollment using SpeechBrain neural embeddings.
* **Real-Time Speech Recognition:** Captures and transcribes audio directly in the browser using the Web Speech API and audio streaming.
* **Smart Intent Parsing:** Leverages Google's Gemini AI to analyze natural language and determine whether a command is locomotion or conversational dialogue.
* **3D Digital Twin:** Renders a responsive, animated 3D robot in the browser using Three.js and React-Three-Fiber.
* **Multi-Network Ready:** Configured for open access across all local and remote network interfaces (`0.0.0.0:8501`).
* **Sci-Fi UI:** A sleek, dark-mode futuristic dashboard to monitor the system's status and terminal outputs.

---

## 🛠️ Prerequisites

Before you begin, ensure you have:
* **[Python](https://www.python.org/)** (v3.9 or higher)
* **[Node.js](https://nodejs.org/)** (v16 or higher, optional for React frontend)
* A valid **Google Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/))
* A working microphone

---

## 🚀 Quickstart: Streamlit Deployment (Open to All Networks)

### 1. Clone the Repository
```bash
git clone https://github.com/Harry2005-cell/voice_robot_phase1_3d.git
cd voice_robot_phase1_3d
```


### 2. Install Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Gemini API Key
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Launch Streamlit (Accessible on Local & LAN Network)
```bash
streamlit run app.py
```
> The application will bind to `0.0.0.0:8501`, allowing any device on your Wi-Fi/LAN or public IP to access `http://<YOUR_IP>:8501`.

### 5. Deploy to Streamlit Community Cloud
1. Fork or push this repository to GitHub: `https://github.com/Harry2005-cell/voice_robot_phase1_3d`
2. Go to [share.streamlit.io](https://share.streamlit.io/) and create a **New App**.
3. Select your repository, branch `main`, and main file `app.py`.
4. Under **Advanced settings > Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
5. Click **Deploy**!

---

## 🔧 Alternative: FastAPI Backend + React Frontend

### Backend Setup (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

---

## 📂 Project Structure
```text
├── app.py                    # Streamlit Application (3D Three.js + Gemini + Biometrics)
├── requirements.txt          # Python Dependencies for Streamlit Cloud & Hosting
├── .streamlit/
│   └── config.toml           # Network (0.0.0.0), CORS & Cyberpunk Theme Config
├── backend/                  # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py           # API routes & Gemini integration
│   │   ├── ai/
│   │   │   └── gemini_client.py # Gemini intent parser
│   │   └── biometrics/
│   │       └── speechbrain_model.py # SpeechBrain voice biometrics
│   └── requirements.txt      # Backend Python dependencies
│
└── frontend/                 # React + Three.js Frontend
    ├── public/
    │   └── robot.glb         # 3D Model Asset
    ├── src/
    │   ├── App.jsx           # React UI Dashboard
    │   ├── utils/
    │   │   └── audioStreamer.js # Audio recording utility
    │   └── three/
    │       └── Scene.jsx     # Three.js 3D Canvas
    └── package.json          # Node dependencies
```

---

## 📜 License
MIT License. Created for Harry AI Voice Robot Digital Twin.
