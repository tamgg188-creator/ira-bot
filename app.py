import os
from flask import Flask, request
import requests
from groq import Groq

app = Flask(__name__)

# Render-এর Environment Variables থেকে ডেটা নেওয়া
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
WA_TOKEN = os.environ.get("WA_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = "ira123"

client = Groq(api_key=GROQ_API_KEY)

# মেটা যখন কানেকশন চেক করে (GET Request)
@app.route("/", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "WhatsApp Bot is Running"

# আসল কাজ এখানে - মেসেজ রিসিভ এবং রিপ্লাই (POST Request)
@app.route("/", methods=['POST'])
def webhook():
    data = request.json
    print(f"📥 Received Data: {data}") # লগে মেটার ডেটা দেখার জন্য
    try:
        # মেসেজ কি না তা চেক করা
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            sender_id = message['from']
            user_text = message['text']['body']

            # ১. Groq AI থেকে উত্তর নেওয়া
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": user_text}]
            )
            ai_response = completion.choices[0].message.content
            print(f"🤖 AI Response: {ai_response}") # এআই কী উত্তর দিলো তা দেখার জন্য

            # ২. হোয়াটসঅ্যাপে রিপ্লাই পাঠানো
            url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
            headers = {"Authorization": f"Bearer {WA_TOKEN}", "Content-Type": "application/json"}
            payload = {
                "messaging_product": "whatsapp",
                "to": sender_id,
                "type": "text",
                "text": {"body": ai_response}
            }
            resp = requests.post(url, json=payload, headers=headers)
            print(f"📤 WhatsApp Send Response: {resp.json()}") # হোয়াটসঅ্যাপ কী এরর দিচ্ছে তা দেখার জন্য
            
    except Exception as e:
        print(f"❌ Logic Error: {e}") # কোডে ভুল হলে এখানে দেখাবে
        
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
