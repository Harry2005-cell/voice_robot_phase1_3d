export const recordAudio = (durationMs = 5000) => {
  return new Promise(async (resolve, reject) => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks = [];

      mediaRecorder.addEventListener("dataavailable", event => {
        audioChunks.push(event.data);
      });

      mediaRecorder.addEventListener("stop", () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        stream.getTracks().forEach(track => track.stop()); // Release mic
        resolve(audioBlob);
      });

      mediaRecorder.start();
      setTimeout(() => mediaRecorder.stop(), durationMs);
    } catch (error) {
      reject("Microphone access denied or unavailable.");
    }
  });
};