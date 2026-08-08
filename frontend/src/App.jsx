import React, { useState } from 'react';
import RobotScene from './three/Scene';
import { recordAudio } from './utils/audioStreamer';

export default function App() {
  const [status, setStatus] = useState('Idle');
  const [responseMsg, setResponseMsg] = useState('');
  const [lastCommand, setLastCommand] = useState(null);
  const [enrollName, setEnrollName] = useState('');
  const [heardText, setHeardText] = useState('');
  const [manualText, setManualText] = useState('');

  const handleEnroll = async () => {
    if (!enrollName) return alert("Enter a name first");
    setStatus('Recording Enrollment (5s)... Keep speaking.');
    
    try {
      const audioBlob = await recordAudio(5000);
      setStatus('Sending to backend...');
      
      const formData = new FormData();
      formData.append('name', enrollName);
      formData.append('audio', audioBlob, 'enroll.wav');

      const response = await fetch('http://localhost:8000/api/enroll', { method: 'POST', body: formData });
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }
      
      setStatus('Enrollment Complete!');
    } catch (error) {
      console.error(error);
      setStatus(`Error: Could not record or send audio. Check console.`);
      alert("Microphone failed. Check if it is plugged in and allowed in your browser settings.");
    }
  };

  const processCommandToBackend = async (textToSend, audioBlob = null) => {
    try {
      setStatus('Processing Identity and Intent...');
      
      const formData = new FormData();
      formData.append('text', textToSend || "No text detected");
      if (audioBlob) {
        formData.append('audio', audioBlob, 'command.wav');
      } else {
        // Create an empty dummy blob if text command is sent
        const dummyBlob = new Blob([], { type: 'audio/wav' });
        formData.append('audio', dummyBlob, 'command.wav');
      }

      const res = await fetch('http://localhost:8000/api/command', { method: 'POST', body: formData });
      
      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }
      
      const data = await res.json();
      console.log("Backend API Response:", data);
      
      if (data.intent) {
        const intentType = String(data.intent.type || "").toLowerCase();
        
        if (intentType === 'locomotion' || data.intent.action) {
          const action = data.intent.action;
          setLastCommand({ 
            type: 'locomotion', 
            action: action, 
            timestamp: Date.now() 
          });
          setResponseMsg(`Speaker: ${data.speaker} | Action Executed: ${action.toUpperCase()}`);
        } else {
          setResponseMsg(`Speaker: ${data.speaker} | Reply: ${data.intent.response}`);
        }
      } else {
        setResponseMsg(`Speaker: ${data.speaker} | Error: Intent missing from backend`);
      }
    } catch (error) {
      console.error(error);
      setResponseMsg("Error: Command failed. Check console.");
    } finally {
      setStatus('Idle');
    }
  };

  const handleCommand = async () => {
    try {
      setStatus('Listening for command (5s)...');
      setResponseMsg('Listening...');
      setHeardText('');
      
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      let transcribedText = "";
      let recognition;

      if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        
        recognition.onresult = (event) => {
          let currentTranscript = "";
          for (let i = event.resultIndex; i < event.results.length; i++) {
            currentTranscript += event.results[i][0].transcript;
          }
          if (currentTranscript) {
            transcribedText = currentTranscript;
            setHeardText(currentTranscript);
            console.log("Browser heard:", currentTranscript);
          }
        };

        recognition.onerror = (err) => {
          console.warn("SpeechRecognition error:", err.error);
        };

        try {
          recognition.start();
        } catch (e) {
          console.warn("Recognition start issue:", e);
        }
      }

      // Record audio for exactly 5 seconds
      const audioBlob = await recordAudio(5000);
      
      if (recognition) {
        try { recognition.stop(); } catch (e) {}
      }

      const finalText = transcribedText || heardText || "No text detected";
      await processCommandToBackend(finalText, audioBlob);
      
    } catch (error) {
      console.error(error);
      setResponseMsg("Error: Microphone access denied or recording failed.");
      setStatus('Idle');
    }
  };

  const handleManualSend = (e) => {
    e.preventDefault();
    if (!manualText.trim()) return;
    setHeardText(manualText);
    processCommandToBackend(manualText);
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#0a0a0a',
      color: '#e0e0e0',
      fontFamily: '"Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      padding: '40px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>

      {/* Header */}
      <h1 style={{
        color: '#00f3ff',
        textTransform: 'uppercase',
        letterSpacing: '2px',
        textShadow: '0 0 10px rgba(0, 243, 255, 0.5)',
        marginBottom: '10px'
      }}>
        Harry AI Control Center
      </h1>

      <div style={{
        backgroundColor: '#1a1a1a',
        padding: '10px 30px',
        borderRadius: '20px',
        border: '1px solid #333',
        marginBottom: '40px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.3)'
      }}>
        <p style={{ margin: 0, fontSize: '14px' }}>
          System Status: <strong style={{ color: status === 'Idle' ? '#4caf50' : '#ff9800' }}>{status}</strong>
        </p>
      </div>

      {/* Main Dashboard Layout */}
      <div style={{
        display: 'flex',
        gap: '40px',
        width: '100%',
        maxWidth: '1200px',
        flexWrap: 'wrap' // Ensures it looks okay on smaller screens
      }}>

        {/* Left Column: Controls */}
        <div style={{ flex: '1', display: 'flex', flexDirection: 'column', gap: '30px', minWidth: '300px' }}>

          {/* Enrollment Card */}
          <div style={{
            background: 'linear-gradient(145deg, #1e1e1e, #121212)',
            padding: '25px',
            borderRadius: '16px',
            border: '1px solid #2a2a2a',
            boxShadow: '0 10px 30px rgba(0,0,0,0.5)'
          }}>
            <h3 style={{ marginTop: 0, color: '#aaa', fontSize: '16px', textTransform: 'uppercase' }}>1. Biometric Uplink</h3>
            <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
              <input
                type="text"
                placeholder="Operator Name"
                value={enrollName}
                onChange={e => setEnrollName(e.target.value)}
                style={{
                  flex: 1,
                  padding: '12px',
                  backgroundColor: '#000',
                  border: '1px solid #333',
                  color: '#fff',
                  borderRadius: '8px',
                  outline: 'none'
                }}
              />
              <button
                onClick={handleEnroll}
                style={{
                  padding: '12px 20px',
                  backgroundColor: 'transparent',
                  border: '1px solid #00f3ff',
                  color: '#00f3ff',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  transition: 'all 0.2s'
                }}
                onMouseOver={(e) => { e.target.style.backgroundColor = 'rgba(0, 243, 255, 0.1)' }}
                onMouseOut={(e) => { e.target.style.backgroundColor = 'transparent' }}
              >
                Enroll Voice
              </button>
            </div>
          </div>

          {/* Command Card */}
          <div style={{
            background: 'linear-gradient(145deg, #1e1e1e, #121212)',
            padding: '25px',
            borderRadius: '16px',
            border: '1px solid #2a2a2a',
            boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
            display: 'flex',
            flexDirection: 'column',
            gap: '15px'
          }}>
            <h3 style={{ marginTop: 0, color: '#aaa', fontSize: '16px', textTransform: 'uppercase' }}>2. Command Interface</h3>

            <button
              onClick={handleCommand}
              style={{
                background: 'linear-gradient(90deg, #00f3ff, #0073ff)',
                color: 'white',
                padding: '15px',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 'bold',
                boxShadow: '0 4px 15px rgba(0, 115, 255, 0.4)'
              }}
            >
              🎤 Initiate Voice Command (5s)
            </button>

            {/* Manual Text Command Input */}
            <form onSubmit={handleManualSend} style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                placeholder='Type query or command (e.g. "tell me about gravity")'
                value={manualText}
                onChange={e => setManualText(e.target.value)}
                style={{
                  flex: 1,
                  padding: '12px',
                  backgroundColor: '#000',
                  border: '1px solid #333',
                  color: '#fff',
                  borderRadius: '8px',
                  outline: 'none'
                }}
              />
              <button
                type="submit"
                style={{
                  padding: '12px 18px',
                  backgroundColor: '#00f3ff',
                  color: '#000',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                Send Text
              </button>
            </form>

            {/* Directional Quick Controls */}
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {['forward', 'backward', 'left', 'right'].map(dir => (
                <button
                  key={dir}
                  onClick={() => processCommandToBackend(dir)}
                  style={{
                    flex: 1,
                    padding: '8px',
                    backgroundColor: 'rgba(0, 243, 255, 0.05)',
                    border: '1px solid #00f3ff',
                    color: '#00f3ff',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    textTransform: 'uppercase'
                  }}
                >
                  {dir}
                </button>
              ))}
            </div>

            {/* Heard Speech Feedback */}
            {heardText && (
              <div style={{
                backgroundColor: 'rgba(0, 243, 255, 0.1)',
                borderLeft: '3px solid #00f3ff',
                padding: '10px 15px',
                borderRadius: '4px',
                fontSize: '13px'
              }}>
                <span style={{ color: '#00f3ff', fontWeight: 'bold' }}>HEARD SPEECH: </span>
                <span style={{ color: '#fff' }}>"{heardText}"</span>
              </div>
            )}

            {/* Terminal Output */}
            <div style={{
              backgroundColor: '#000',
              padding: '15px',
              borderRadius: '8px',
              border: '1px solid #333',
              minHeight: '60px'
            }}>
              <span style={{ color: '#666', fontSize: '12px', display: 'block', marginBottom: '5px' }}>TERMINAL OUTPUT</span>
              <span style={{ color: '#00f3ff', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>{responseMsg || "_ awaiting input..."}</span>
            </div>
          </div>

        </div>

        {/* Right Column: 3D Scene */}
        <div style={{
          flex: '2',
          border: '1px solid #2a2a2a',
          borderRadius: '16px',
          overflow: 'hidden',
          boxShadow: '0 10px 30px rgba(0,0,0,0.8)',
          minWidth: '300px'
        }}>
          <RobotScene lastCommand={lastCommand} />
        </div>

      </div>
    </div>
  );
}
