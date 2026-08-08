import google.generativeai as genai
import json
import re
import os

api_key = os.getenv("GEMINI_API_KEY", "")

# Load from local .env if not found in environment variables
if not api_key:
    env_path = os.path.join(os.path.dirname(__file__), "../../.env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break

if api_key:
    genai.configure(api_key=api_key)

CANDIDATE_MODELS = ["models/gemini-flash-latest", "models/gemini-2.0-flash", "models/gemini-pro-latest", "models/gemini-2.0-flash-lite"]

def parse_rule_based_intent(text: str):
    """Fast & reliable local keyword matching for locomotion commands."""
    text_lower = text.lower().strip()
    
    if any(w in text_lower for w in ["forward", "front", "ahead", "straight"]):
        return {"type": "locomotion", "action": "forward"}
    if any(w in text_lower for w in ["backward", "back", "reverse"]):
        return {"type": "locomotion", "action": "backward"}
    if "left" in text_lower:
        return {"type": "locomotion", "action": "left"}
    if "right" in text_lower:
        return {"type": "locomotion", "action": "right"}
    if any(w in text_lower for w in ["jump", "hop", "bounce"]):
        return {"type": "locomotion", "action": "jump"}
    if any(w in text_lower for w in ["spin", "dance", "twirl", "rotate"]):
        return {"type": "locomotion", "action": "spin"}
    if any(w in text_lower for w in ["reset", "center", "origin", "stop"]):
        return {"type": "locomotion", "action": "reset"}
        
    return None

def clean_extract_json(text_str: str):
    """Extract valid JSON dict even if model returns markdown or extra reasoning text."""
    if not text_str:
        return None
    # 1. Direct JSON parse
    try:
        data = json.loads(text_str.strip())
        if isinstance(data, dict): return data
    except Exception:
        pass

    # 2. Extract content from ```json ... ``` blocks
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text_str, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1).strip())
            if isinstance(data, dict): return data
        except Exception:
            pass

    # 3. Extract between outer braces '{' and '}'
    start = text_str.find('{')
    end = text_str.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            data = json.loads(text_str[start:end+1].strip())
            if isinstance(data, dict): return data
        except Exception:
            pass

    return None

def get_intent(transcribed_text: str, speaker_name: str):
    # 1. Rule-based fast path for locomotion commands
    rule_intent = parse_rule_based_intent(transcribed_text)
    if rule_intent:
        print(f"[INTENT PARSER] Rule matched: {rule_intent} from '{transcribed_text}'")
        return rule_intent

    # 2. AI Gemini / Gemma models for conversation or general questions (e.g. "who is president?", "tell me about gravity")
    prompt = f"""
    You are the brain of a 3D virtual robot. 
    The current speaker identified by biometrics is: {speaker_name}.
    The user's transcribed speech is: "{transcribed_text}"
    
    Determine if this is a locomotion command or a conversational query.
    Return ONLY a raw JSON object matching one of these schemas:
    
    If locomotion:
    {{"type": "locomotion", "action": "forward"}} (or backward, left, right)
    
    If conversation:
    {{"type": "conversation", "response": "Your textual answer here."}}
    """
    
    for model_name in CANDIDATE_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            
            # Try generation without mime_type first to maximize compatibility across models
            try:
                response = model.generate_content(prompt)
                parsed = clean_extract_json(response.text)
                if parsed and "type" in parsed:
                    return parsed
            except Exception:
                pass
                
            # Fallback try with application/json config
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(response_mime_type="application/json")
            )
            parsed = clean_extract_json(response.text)
            if parsed and "type" in parsed:
                return parsed

        except Exception as e:
            continue
            
    # Default conversation fallback if AI generation returns free-form text or rate-limited
    return {
        "type": "conversation", 
        "response": f"I am your virtual AI robot! Regarding '{transcribed_text}': It is fascinating to explore."
    }

