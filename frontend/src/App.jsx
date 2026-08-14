import React, { useState, useEffect } from 'react';
import RobotScene from './three/Scene';
import { recordAudio } from './utils/audioStreamer';

export default function App() {
  const [status, setStatus] = useState('Idle');
  const [responseMsg, setResponseMsg] = useState('');
  const [lastCommand, setLastCommand] = useState(null);
  const [enrollName, setEnrollName] = useState('');
  const [heardText, setHeardText] = useState('');
  const [manualText, setManualText] = useState('');
  const [isMuted, setIsMuted] = useState(false);
  const [cameraView, setCameraView] = useState('isometric');
  const [biometricBadge, setBiometricBadge] = useState({ name: 'Guest', score: 0 });

  // Text-To-Speech Synthesizer Function
  const speakText = (textToSpeak) => {
    if (isMuted || !('speechSynthesis' in window)) return;
    try {
      window.speechSynthesis.cancel(); // Stop prior speech
      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      utterance.rate = 1.0;
      utterance.pitch = 1.1; // Robotic pitch accent
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn("SpeechSynthesis error:", e);
    }
  };

  const getApiUrl = () => {
    const host = window.location.hostname || 'localhost';
    return `http://${host}:8000`;
  };

  const handleEnroll = async () => {
    if (!enrollName) return alert("Enter a name first");
    setStatus('Recording Enrollment (5s)... Keep speaking.');
    
    try {
      const audioBlob = await recordAudio(5000);
      setStatus('Sending to backend...');
      
      const formData = new FormData();
      formData.append('name', enrollName);
      formData.append('audio', audioBlob, 'enroll.wav');

      const response = await fetch(`${getApiUrl()}/api/enroll`, { method: 'POST', body: formData });
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }
      
      setStatus('Enrollment Complete!');
      speakText(`Enrollment complete for ${enrollName}`);
    } catch (error) {
      console.error(error);
      setStatus(`Error: Could not record or send audio.`);
      alert("Microphone failed. Check browser audio permissions.");
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
        const dummyBlob = new Blob([], { type: 'audio/wav' });
        formData.append('audio', dummyBlob, 'command.wav');
      }

      const res = await fetch(`${getApiUrl()}/api/command`, { method: 'POST', body: formData });
      
      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }
      
      const data = await res.json();
      console.log("Backend API Response:", data);

      const speakerName = data.speaker || "Unknown";
      const matchScore = data.match_score || 0;
      setBiometricBadge({ name: speakerName, score: matchScore });
      
      if (data.intent) {
        const intentType = String(data.intent.type || "").toLowerCase();
        
        if (intentType === 'locomotion' || data.intent.action) {
          const action = data.intent.action;
          setLastCommand({ 
            type: 'locomotion', 
            action: action, 
            timestamp: Date.now() 
          });
          const msg = `Speaker: ${speakerName} (${matchScore}% match) | Action: ${action.toUpperCase()}`;
          setResponseMsg(msg);
          speakText(`Executing ${action}`);
        } else {
          const aiReply = data.intent.response;
          const msg = `Speaker: ${speakerName} (${matchScore}% match) | Reply: ${aiReply}`;
          setResponseMsg(msg);
          speakText(aiReply);
        }
      } else {
        setResponseMsg(`Speaker: ${speakerName} | Error: Intent missing`);
      }
    } catch (error) {
      console.error(error);
      setResponseMsg("Error: Command failed. Check backend.");
    } finally {
      setStatus('Idle');
    }
  };

  const handleCommand = async () => {
    try {
      setStatus('Listening...');
      setResponseMsg('Listening to your voice...');
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
          }
        };

        try { recognition.start(); } catch (e) {}
      }

      const audioBlob = await recordAudio(5000);
      
      if (recognition) {
        try { recognition.stop(); } catch (e) {}
      }

      const finalText = transcribedText || heardText || "No text detected";
      await processCommandToBackend(finalText, audioBlob);
      
    } catch (error) {
      console.error(error);
      setResponseMsg("Error: Microphone access denied.");
      setStatus('Idle');
    }
  };

  const handleManualSend = (e) => {
    e.preventDefault();
    if (!manualText.trim()) return;
    setHeardText(manualText);
    processCommandToBackend(manualText);
    setManualText('');
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#0a0a0a',
      color: '#e0e0e0',
      fontFamily: '"Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      padding: '30px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>

      {/* Header & Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', maxWidth: '1200px', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{
          color: '#00f3ff',
          textTransform: 'uppercase',
          letterSpacing: '2px',
          textShadow: '0 0 12px rgba(0, 243, 255, 0.6)',
          margin: 0,
          fontSize: '28px'
        }}>
          Harry AI Control Center
        </h1>

        <button
          onClick={() => {
            setIsMuted(!isMuted);
            if (!isMuted) window.speechSynthesis.cancel();
          }}
          style={{
            backgroundColor: isMuted ? '#333' : 'rgba(0, 243, 255, 0.1)',
            border: '1px solid #00f3ff',
            color: isMuted ? '#aaa' : '#00f3ff',
            padding: '8px 16px',
            borderRadius: '20px',
            cursor: 'pointer',
            fontWeight: 'bold',
            fontSize: '13px'
          }}
        >
          {isMuted ? '🔇 Audio Muted' : '🔊 Robot Voice ON'}
        </button>
      </div>

      {/* Biometric Security Badge */}
      <div style={{
        display: 'flex',
        gap: '20px',
        alignItems: 'center',
        backgroundColor: '#161616',
        padding: '12px 25px',
        borderRadius: '30px',
        border: '1px solid #2a2a2a',
        marginBottom: '30px',
        boxShadow: '0 4px 15px rgba(0,0,0,0.5)'
      }}>
        <span style={{ fontSize: '13px', color: '#888' }}>SYSTEM STATUS:</span>
        <span style={{ color: status === 'Idle' ? '#4caf50' : '#ff9800', fontWeight: 'bold', fontSize: '14px' }}>
          {status}
        </span>
        <span style={{ color: '#333' }}>|</span>
        <span style={{ fontSize: '13px', color: '#888' }}>BIOMETRIC UPLINK:</span>
        <span style={{
          backgroundColor: biometricBadge.score > 70 ? 'rgba(76, 175, 80, 0.15)' : 'rgba(255, 152, 0, 0.15)',
          border: `1px solid ${biometricBadge.score > 70 ? '#4caf50' : '#ff9800'}`,
          color: biometricBadge.score > 70 ? '#4caf50' : '#ff9800',
          padding: '4px 12px',
          borderRadius: '12px',
          fontSize: '12px',
          fontWeight: 'bold'
        }}>
          {biometricBadge.name !== 'Guest' && biometricBadge.name !== 'Unknown'
            ? `VERIFIED: ${biometricBadge.name.toUpperCase()} (${biometricBadge.score}% MATCH)`
            : `UNVERIFIED / GUEST (${biometricBadge.score}% MATCH)`}
        </span>
      </div>

      {/* Main Dashboard Layout */}
      <div style={{
        display: 'flex',
        gap: '30px',
        width: '100%',
        maxWidth: '1200px',
        flexWrap: 'wrap'
      }}>

        {/* Left Column: Controls */}
        <div style={{ flex: '1', display: 'flex', flexDirection: 'column', gap: '25px', minWidth: '320px' }}>

          {/* 1. Biometric Enrollment */}
          <div style={{
            background: 'linear-gradient(145deg, #1c1c1c, #111)',
            padding: '20px',
            borderRadius: '16px',
            border: '1px solid #2a2a2a'
          }}>
            <h3 style={{ marginTop: 0, color: '#aaa', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px' }}>
              1. Voice Enrollment
            </h3>
            <div style={{ display: 'flex', gap: '10px', marginTop: '12px' }}>
              <input
                type="text"
                placeholder="Operator Name (e.g. Harshal)"
                value={enrollName}
                onChange={e => setEnrollName(e.target.value)}
                style={{
                  flex: 1,
                  padding: '10px',
                  backgroundColor: '#000',
                  border: '1px solid #333',
                  color: '#fff',
                  borderRadius: '8px',
                  outline: 'none',
                  fontSize: '13px'
                }}
              />
              <button
                onClick={handleEnroll}
                style={{
                  padding: '10px 16px',
                  backgroundColor: 'transparent',
                  border: '1px solid #00f3ff',
                  color: '#00f3ff',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '13px'
                }}
              >
                Enroll Voice (5s)
              </button>
            </div>
          </div>

          {/* 2. Command Interface */}
          <div style={{
            background: 'linear-gradient(145deg, #1c1c1c, #111)',
            padding: '20px',
            borderRadius: '16px',
            border: '1px solid #2a2a2a',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            <h3 style={{ marginTop: 0, color: '#aaa', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px' }}>
              2. Command & Question Interface
            </h3>

            <button
              onClick={handleCommand}
              style={{
                background: 'linear-gradient(90deg, #00f3ff, #0073ff)',
                color: 'white',
                padding: '14px',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '15px',
                fontWeight: 'bold',
                boxShadow: '0 4px 15px rgba(0, 115, 255, 0.4)'
              }}
            >
              🎤 Speak Command / Ask AI (5s)
            </button>

            {/* Audio Wave Visualizer Animation */}
            {status.includes('Listening') && (
              <div style={{ display: 'flex', gap: '4px', justifyContent: 'center', height: '24px', alignItems: 'center' }}>
                {[12, 22, 16, 26, 14, 20, 10].map((h, i) => (
                  <div
                    key={i}
                    style={{
                      width: '4px',
                      height: `${h}px`,
                      backgroundColor: '#00f3ff',
                      borderRadius: '2px',
                      animation: `pulse 0.6s infinite alternate ${i * 0.1}s`
                    }}
                  />
                ))}
              </div>
            )}

            {/* Manual Text Command Input */}
            <form onSubmit={handleManualSend} style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                placeholder='Type command (e.g. "tell me about gravity", "jump", "spin")'
                value={manualText}
                onChange={e => setManualText(e.target.value)}
                style={{
                  flex: 1,
                  padding: '10px',
                  backgroundColor: '#000',
                  border: '1px solid #333',
                  color: '#fff',
                  borderRadius: '8px',
                  outline: 'none',
                  fontSize: '13px'
                }}
              />
              <button
                type="submit"
                style={{
                  padding: '10px 16px',
                  backgroundColor: '#00f3ff',
                  color: '#000',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '13px'
                }}
              >
                Send
              </button>
            </form>

            {/* Direction & Action Controls */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '5px' }}>
              <span style={{ fontSize: '11px', color: '#666', textTransform: 'uppercase' }}>Quick Locomotion & Actions:</span>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {['forward', 'backward', 'left', 'right'].map(dir => (
                  <button
                    key={dir}
                    onClick={() => processCommandToBackend(dir)}
                    style={{
                      flex: 1,
                      padding: '6px',
                      backgroundColor: 'rgba(0, 243, 255, 0.05)',
                      border: '1px solid #00f3ff',
                      color: '#00f3ff',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '11px',
                      fontWeight: 'bold',
                      textTransform: 'uppercase'
                    }}
                  >
                    {dir}
                  </button>
                ))}
              </div>

              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {['jump', 'spin', 'reset'].map(act => (
                  <button
                    key={act}
                    onClick={() => processCommandToBackend(act)}
                    style={{
                      flex: 1,
                      padding: '6px',
                      backgroundColor: 'rgba(255, 152, 0, 0.05)',
                      border: '1px solid #ff9800',
                      color: '#ff9800',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '11px',
                      fontWeight: 'bold',
                      textTransform: 'uppercase'
                    }}
                  >
                    {act}
                  </button>
                ))}
              </div>
            </div>

            {/* Heard Speech Feedback */}
            {heardText && (
              <div style={{
                backgroundColor: 'rgba(0, 243, 255, 0.1)',
                borderLeft: '3px solid #00f3ff',
                padding: '8px 12px',
                borderRadius: '4px',
                fontSize: '12px'
              }}>
                <span style={{ color: '#00f3ff', fontWeight: 'bold' }}>SPEECH RECOGNIZED: </span>
                <span style={{ color: '#fff' }}>"{heardText}"</span>
              </div>
            )}

            {/* Terminal Output */}
            <div style={{
              backgroundColor: '#000',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #333',
              minHeight: '60px'
            }}>
              <span style={{ color: '#666', fontSize: '11px', display: 'block', marginBottom: '4px' }}>ROBOT OUTPUT TERMINAL</span>
              <span style={{ color: '#00f3ff', fontFamily: 'monospace', fontSize: '13px', whiteSpace: 'pre-wrap' }}>
                {responseMsg || "_ awaiting command input..."}
              </span>
            </div>
          </div>

        </div>

        {/* Right Column: 3D Scene */}
        <div style={{
          flex: '2',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          minWidth: '320px'
        }}>
          {/* Camera Selector Bar */}
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', color: '#888' }}>CAMERA PRESET:</span>
            {[
              { id: 'isometric', label: 'Isometric' },
              { id: 'top', label: 'Top View' },
              { id: 'front', label: 'Front View' }
            ].map(cam => (
              <button
                key={cam.id}
                onClick={() => setCameraView(cam.id)}
                style={{
                  padding: '5px 12px',
                  backgroundColor: cameraView === cam.id ? '#00f3ff' : '#1e1e1e',
                  color: cameraView === cam.id ? '#000' : '#aaa',
                  border: '1px solid #333',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '11px',
                  fontWeight: 'bold'
                }}
              >
                {cam.label}
              </button>
            ))}
          </div>

          <div style={{
            border: '1px solid #2a2a2a',
            borderRadius: '16px',
            overflow: 'hidden',
            boxShadow: '0 10px 30px rgba(0,0,0,0.8)'
          }}>
            <RobotScene lastCommand={lastCommand} cameraView={cameraView} />
          </div>
        </div>

      </div>
    </div>
  );
}
