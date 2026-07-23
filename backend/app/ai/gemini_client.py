import google.generativeai as genai
import json
import os

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

def get_intent(transcribed_text: str, speaker_name: str):
    prompt = f"""
    You are the brain of a 3D virtual robot. 
    The current speaker identified by biometrics is: {speaker_name}.
    The user's transcribed speech is: "{transcribed_text}"
    
    Determine if this is a locomotion command or a conversational query.
    Return ONLY a raw JSON object matching one of these schemas:
    
    If locomotion (e.g., move forward, turn left):
    {{"type": "locomotion", "action": "forward/backward/left/right"}}
    
    If conversation (e.g., who am I, what is your name):
    {{"type": "conversation", "response": "Your textual answer here, addressing the speaker by name if relevant."}}
    """
    
    try:
        response = model.generate_content(prompt)
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {"type": "conversation", "response": f"Hello {speaker_name}, I heard you say: {transcribed_text}"}