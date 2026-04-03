import os
from flask import Flask, request
import requests
from groq import Groq

app = Flask(__name__)

# এই ভ্যালুগুলো আমরা পরে রেন্ডারে (Render) সেট করবো
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
WA_TOKEN = os.environ.get("WA_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = "ira123" # এটি মেটা ড্যাশবোর্ডে লাগবে

client = Groq(api_key=GROQ_API_KEY)

@app.route("/", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "WhatsApp Bot is Running"

@app.route("/", methods=['POST'])
def webhook():
    data = request.json
    try:
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            sender_id = message['from']
            user_text = message['text']['body']

            # Groq AI থেকে উত্তর নেওয়া
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "তুমি 'ইরা', একজন স্মার্ট অ্যাসিস্ট্যান্ট।"},
                    {"role": "user", "content": user_text}
                ]
            )
            ai_response = completion.choices[0].message.content

            # হোয়াটসঅ্যাপে রিপ্লাই পাঠানো
            url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
            headers = {"Authorization": f"Bearer {WA_TOKEN}", "Content-Type": "application/json"}
            payload = {
                "messaging_product": "whatsapp",
                "to": sender_id,
                "type": "text",
                "text": {"body": ai_response}
            }
            requests.post(url, json=payload, headers=headers)
    except:
        pass
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
