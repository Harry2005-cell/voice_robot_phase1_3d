import React, { useState } from 'react';
import RobotScene from './three/Scene';
import { recordAudio } from './utils/audioStreamer';

export default function App() {
  const [status, setStatus] = useState('Idle');
  const [responseMsg, setResponseMsg] = useState('');
  const [lastCommand, setLastCommand] = useState(null);
  const [enrollName, setEnrollName] = useState('');

  const handleEnroll = async () => {
    if (!enrollName) return alert("Enter a name first");
    setStatus('Recording Enrollment (5s)... Keep speaking.');
    
    const audioBlob = await recordAudio(5000);
    setStatus('Sending to backend...');
    
    const formData = new FormData();
    formData.append('name', enrollName);
    formData.append('audio', audioBlob, 'enroll.wav');

    await fetch('http://localhost:8000/api/enroll', { method: 'POST', body: formData });
    setStatus('Enrollment Complete!');
  };

  const handleCommand = async () => {
    setStatus('Listening for command (5s)...');
    
    // Web Speech API for client-side transcription
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    let transcribedText = "";
    
    recognition.onresult = (event) => {
      transcribedText = event.results[0][0].transcript;
    };
    recognition.start();

    // Simultaneously record audio for Biometrics
    const audioBlob = await recordAudio(5000);
    recognition.stop();
    
    setStatus('Processing Identity and Intent...');
    
    const formData = new FormData();
    formData.append('text', transcribedText || "No text detected");
    formData.append('audio', audioBlob, 'command.wav');

    const res = await fetch('http://localhost:8000/api/command', { method: 'POST', body: formData });
    const data = await res.json();
    
    if (data.intent.type === 'locomotion') {
      setLastCommand(data.intent);
      setResponseMsg(`Speaker: ${data.speaker} | Action: ${data.intent.action}`);
    } else {
      setResponseMsg(`Speaker: ${data.speaker} | Reply: ${data.intent.response}`);
    }
    
    setStatus('Idle');
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Virtual AI Robot Control Center</h1>
      <p>Status: <strong>{status}</strong></p>
      
      <div style={{ marginBottom: '20px', padding: '10px', background: '#eee' }}>
        <h3>1. Enroll Voiceprint</h3>
        <input 
          type="text" 
          placeholder="Enter your name" 
          value={enrollName} 
          onChange={e => setEnrollName(e.target.value)} 
        />
        <button onClick={handleEnroll}>Start Enrollment</button>
      </div>

      <div style={{ marginBottom: '20px', padding: '10px', background: '#eee' }}>
        <h3>2. Send Command</h3>
        <button onClick={handleCommand} style={{ background: 'blue', color: 'white' }}>
          Speak Command
        </button>
        <p><strong>Robot Response:</strong> {responseMsg}</p>
      </div>

      <RobotScene lastCommand={lastCommand} />
    </div>
  );
}