import os
import groq
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Set your Groq API key (Replace with your actual API key)
GROQ_API_KEY = "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"
client = groq.Client(api_key=GROQ_API_KEY)

# WhatsApp Cloud API credentials (Update with your token & phone ID)
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0/623505390838035/messages"
WHATSAPP_ACCESS_TOKEN = "EAAIXCPTLBkwBO6cnX4lOBoxGK8vOAOExvzrZBZBKnnJuFSZBxGbNKejyZCx7jE2NbZBexf4YMTIfSP5l53yPhZBdZADoogsZCJV3hoZBNJwrb3zf81S7HZAV59PnCRc7dywBg2ZAkWnpHzgnIkjCcL1ip7bXdORiQguGtuKJisVkYwPX9LilbX1qxTq8Uk7oDTUmLmD4AuzkNDZA45rHZCUdxeGJ8U4nYb8EZD"

VERIFY_TOKEN = "my_secret_token"  # Must match Meta settings

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """Handle Meta webhook verification & incoming WhatsApp messages"""
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification token mismatch", 403

    elif request.method == "POST":
        data = request.get_json()
        if data and "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "messages" in change.get("value", {}):
                        for message in change["value"]["messages"]:
                            process_message(message)
        return jsonify({"status": "received"}), 200

def process_message(message):
    """Extract user message and send AI response"""
    user_text = message["text"]["body"]
    sender_number = message["from"]
    
    ai_response = chat_with_llama(user_text)  # Query Llama 2
    send_whatsapp_message(sender_number, ai_response)  # Send reply

def chat_with_llama(prompt):
    """Query Llama 2 via Groq API for AI-generated response"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Other option: "llama2-13b-chat"
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "Sorry, I'm having trouble responding now."

def send_whatsapp_message(to, text):
    """Send message via WhatsApp Cloud API"""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    print(f"WhatsApp Response: {response.json()}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
