from flask import Flask, request, jsonify, render_template_string, render_template
import requests

app = Flask(__name__)

FB_API_URL = "https://graph.facebook.com/v17.0"

# Function to get Group Chats (Names + UIDs)
def get_group_chats(access_token):
    url = f"{FB_API_URL}/me/conversations?access_token={access_token}"
    response = requests.get(url)
    data = response.json()
    
    gc_list = []
    if "data" in data:
        for chat in data["data"]:
            gc_name = chat.get("name", f"Unnamed Chat ({chat['id']})")  # Show GC ID if name is missing
            gc_list.append({"id": chat["id"], "name": gc_name})
    return gc_list

# Function to get messages from a GC
def get_chat_messages(gc_id, access_token):
    url = f"{FB_API_URL}/{gc_id}/messages?fields=message,from,created_time,from{id,picture}&access_token={access_token}"
    response = requests.get(url)
    data = response.json()
    
    messages = []
    if "data" in data:
        for msg in data["data"]:
            message_text = msg.get("message", "[Media: Image/Video/Sticker]")  # Default for media
            sender_name = msg["from"]["name"] if "from" in msg else "Unknown"
            sender_id = msg["from"]["id"] if "from" in msg else "0"
            timestamp = msg["created_time"]
            profile_pic = f"https://graph.facebook.com/{sender_id}/picture?type=small"  # Fetch sender profile pic
            
            messages.append({
                "message": message_text,
                "from": sender_name,
                "profile_pic": profile_pic,
                "time": timestamp
            })
    return messages

@app.route("/", methods=["GET", "POST"])
def home():
    access_token = ""
    gc_list = []
    
    if request.method == "POST":
        access_token = request.form.get("access_token")
        gc_list = get_group_chats(access_token)

    return render_template("home.html", gc_list=gc_list, access_token=access_token)

@app.route("/chat/<gc_id>")
def chat(gc_id):
    return render_template("chat.html", gc_id=gc_id)

@app.route("/get_messages", methods=["POST"])
def get_messages():
    gc_id = request.json.get("gc_id")
    access_token = request.json.get("access_token")
    messages = get_chat_messages(gc_id, access_token)
    return jsonify(messages)

if __name__ == "__main__":
    app.run(debug=True)
