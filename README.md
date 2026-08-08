# 🤖 Nexus AI: Voice-Controlled 3D Robot

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![React](https://img.shields.io/badge/React-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini-orange)

A full-stack, edge-to-cloud web application that allows users to control a 3D virtual robot using their voice. The system features biometric voice enrollment, real-time speech-to-text, and uses Google's `gemini-2.5-flash` AI to parse natural language into kinetic 3D commands.

## ✨ Features

* **Biometric Security:** Verifies the user's identity through audio voiceprint enrollment.
* **Real-Time Speech Recognition:** Captures and transcribes audio directly in the browser using the Web Speech API.
* **Smart Intent Parsing:** Leverages Google's Gemini AI to analyze natural language and determine if a user wants to chat or move the robot.
* **3D Digital Twin:** Renders a responsive, animated 3D robot in the browser using React-Three-Fiber.
* **Sci-Fi UI:** A sleek, dark-mode futuristic dashboard to monitor the system's status and terminal outputs.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your machine:
* **[Node.js](https://nodejs.org/)** (v16 or higher)
* **[Python](https://www.python.org/)** (v3.8 or higher)
* A valid **Google Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/))
* A working microphone

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME


2. Backend Setup (Python / FastAPI)

# Navigate to the backend directory
cd backend

# Create a virtual environment (Recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt

Start the Backend Server:
uvicorn app.main:app --host 127.0.0.1 --port 8000

3. Frontend Setup (React / Vite)
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

Start the Frontend Server:
npm run dev


📂 Project Structure
├── backend/                  # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py           # API routes & Gemini integration
│   │   └── biometrics.py     # Voice processing logic
│   └── requirements.txt      # Python dependencies
│
└── frontend/                 # React + Three.js Frontend
    ├── public/
    │   └── robot.glb         # 3D model asset (Add this yourself!)
    ├── src/
    │   ├── App.jsx           # Main Dashboard UI & Logic
    │   ├── utils/
    │   │   └── audioStreamer.js # Audio recording utility
    │   └── three/
    │       └── Scene.jsx     # React-Three-Fiber 3D Canvas
    └── package.json          # Node dependencies
