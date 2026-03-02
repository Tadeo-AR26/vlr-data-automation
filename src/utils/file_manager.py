import json
import os

def save_json(data, filename):
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

def load_json(filename):
    filepath = os.path.join('data', filename)
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}