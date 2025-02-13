from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

FB_API_URL = "https://graph.facebook.com/v17.0"

# Function to fetch group chats
def get_group_chats(access_token):
    url = f"{FB_API_URL}/me/conversations?access_token={access_token}"
    response = requests.get(url)
    data = response.json()
    
    gc_list = []
    if "data" in data:
        for chat in data["data"]:
            gc_name = chat.get("name", f"Unnamed Chat ({chat['id']})")
            gc_list.append({"id": chat["id"], "name": gc_name})
    return gc_list

# Function to fetch messages from a GC
def get_chat_messages(gc_id, access_token):
    url = f"{FB_API_URL}/{gc_id}/messages?fields=message,from,created_time&access_token={access_token}"
    response = requests.get(url)
    data = response.json()
    
    messages = []
    if "data" in data:
        for msg in data["data"]:
            messages.append({
                "message": msg.get("message", "[Media]"),
                "from": msg["from"]["name"] if "from" in msg else "Unknown",
                "time": msg["created_time"]
            })
    return messages

@app.route("/", methods=["GET", "POST"])
def home():
    gc_list = []
    access_token = ""

    if request.method == "POST":
        access_token = request.form.get("access_token")
        gc_list = get_group_chats(access_token)

    return render_template("home.html", gc_list=gc_list, access_token=access_token)

@app.route("/chat/<gc_id>")
def chat(gc_id):
    access_token = request.args.get("access_token")
    messages = get_chat_messages(gc_id, access_token)
    return render_template("chat.html", messages=messages)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
