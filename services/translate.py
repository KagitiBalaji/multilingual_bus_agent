from langdetect import detect
from deep_translator import GoogleTranslator

# Map language codes to names and TTS codes
LANG_MAP = {
    'te': {'name': 'telugu', 'tts': 'te'},  # Telugu
    'hi': {'name': 'hindi', 'tts': 'hi'},    # Hindi
    'ur': {'name': 'urdu', 'tts': 'ur'},     # Urdu
    'ta': {'name': 'tamil', 'tts': 'ta'},    # Tamil
    'kn': {'name': 'kannada', 'tts': 'kn'},  # Kannada
    'ml': {'name': 'malayalam', 'tts': 'ml'},# Malayalam
    'en': {'name': 'english', 'tts': 'en'}   # English
}

def detect_language(text):
    try:
        lang_code = detect(text)
        return LANG_MAP.get(lang_code, LANG_MAP['en'])
    except:
        return LANG_MAP['en']

def translate_to_english(text, source_lang):
    try:
        if source_lang['tts'] == 'en':
            return text
        return GoogleTranslator(source=source_lang['tts'], target='en').translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def translate_from_english(text, target_lang):
    try:
        if target_lang['tts'] == 'en':
            return text
        return GoogleTranslator(source='en', target=target_lang['tts']).translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text