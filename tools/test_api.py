import os, requests
from pathlib import Path

ENV = {}
if Path(".env").exists():
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                ENV[k.strip()] = v.strip().strip('"').strip("'")

print("=== TEST DES CLÉS API ===\n")

# 1. Test Groq
print("🤖 Test Groq...")
GROQ_KEY = ENV.get("GROQ_API_KEY") or ENV.get("GROK_API_KEY")
if GROQ_KEY:
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": "Dis OK"}], "max_tokens": 10}
        )
        if r.ok: print("✅ Groq (openai/gpt-oss-120b) fonctionne !")
        else: print(f"❌ Groq erreur {r.status_code} : {r.text[:100]}")
    except Exception as e: print(f"❌ Groq échec : {e}")
else: print("❌ Pas de clé Groq.")

# 2. Test Gemini
print("\n🤖 Test Gemini...")
GEMINI_KEY = ENV.get("GEMINI_API_KEY")
if GEMINI_KEY:
    try:
        r = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",
            headers={"x-goog-api-key": GEMINI_KEY, "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": "Dis OK"}]}]}
        )
        if r.ok: print("✅ Gemini (3.8-flash) fonctionne !")
        else: print(f"❌ Gemini erreur {r.status_code} : {r.text[:100]}")
    except Exception as e: print(f"❌ Gemini échec : {e}")
else: print("❌ Pas de clé Gemini.")
