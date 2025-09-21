from flask import Flask, request, redirect, url_for
import os
import time
import requests
import threading

app = Flask(__name__)

# Static variables for headers
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
}

# Global flag to stop the loop
stop_flag = False
token_counter = 0  # Counter for tokens used


def send_messages(token_type, access_token, thread_id, hater_name, time_interval, messages, tokens):
    global stop_flag, token_counter
    post_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
    
    msg_index = 0
    while not stop_flag:  # Infinite loop until stop_flag = True
        message = messages[msg_index % len(messages)]
        token = access_token if token_type == 'single' else tokens[msg_index % len(tokens)]

        data = {'access_token': token, 'message': f"{hater_name} {message}"}
        response = requests.post(post_url, json=data, headers=headers)

        if response.ok:
            print(f"[SUCCESS] Sent: {message}")
        else:
            print(f"[FAILURE] Failed to send: {message} | {response.text}")

        token_counter += 1
        msg_index += 1
        time.sleep(time_interval)


@app.route('/')
def index():
    global token_counter
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Auto Message Sender</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background: url('https://images.unsplash.com/photo-1522071820081-009f0129c71c') no-repeat center center fixed;
          background-size: cover;
          margin: 0;
          padding: 0;
          transition: background 0.3s, color 0.3s;
        }}
        body.dark {{
          background: #121212;
          color: #fff;
        }}
        .container {{
          max-width: 600px;
          margin: 50px auto;
          background: rgba(255, 255, 255, 0.9);
          padding: 30px;
          border-radius: 20px;
          box-shadow: 0 8px 16px rgba(0,0,0,0.8);
          transition: background 0.3s, color 0.3s;
        }}
        body.dark .container {{
          background: rgba(30, 30, 30, 0.95);
        }}
        h2 {{
          text-align: center;
          margin-bottom: 20px;
        }}
        label {{
          font-weight: bold;
          display: block;
          margin-top: 15px;
        }}
        input, select {{
          width: 100%;
          padding: 14px;
          margin-top: 8px;
          border: none;
          border-radius: 12px;
          font-size: 16px;
          box-shadow: 0 4px 10px rgba(0,0,0,0.6);
        }}
        button {{
          width: 100%;
          padding: 14px;
          margin-top: 20px;
          font-size: 16px;
          font-weight: bold;
          border: none;
          border-radius: 12px;
          cursor: pointer;
          background: #007BFF;
          color: white;
          box-shadow: 0 4px 12px rgba(0,0,0,0.7);
          transition: background 0.3s;
        }}
        button:hover {{
          background: #0056b3;
        }}
        .toggle-btn {{
          position: fixed;
          top: 20px;
          right: 20px;
          background: #333;
          color: white;
          padding: 10px 18px;
          border-radius: 30px;
          cursor: pointer;
          font-size: 14px;
        }}
        .counter-box {{
          margin-top: 20px;
          padding: 12px;
          background: #f1f1f1;
          border-radius: 12px;
          text-align: center;
          font-weight: bold;
          box-shadow: 0 4px 12px rgba(0,0,0,0.7);
        }}
        body.dark .counter-box {{
          background: #222;
          color: #fff;
        }}
      </style>
    </head>
    <body>
      <div class="toggle-btn" onclick="toggleDark()">🌙 Dark Mode</div>

      <div class="container">
        <h2>🚀 Auto Message Sender</h2>
        <form action="/" method="post" enctype="multipart/form-data">
          <label>Token Type:</label>
          <select name="tokenType">
            <option value="single">Single Token</option>
            <option value="multi">Multi Token</option>
          </select>

          <label>Access Token:</label>
          <input type="text" name="accessToken">

          <label>Thread ID:</label>
          <input type="text" name="threadId" required>

          <label>Hater Name:</label>
          <input type="text" name="kidx" required>

          <label>Message File:</label>
          <input type="file" name="txtFile" required>

          <label>Token File (for multi):</label>
          <input type="file" name="tokenFile">

          <label>Speed (seconds):</label>
          <input type="number" name="time" required>

          <button type="submit">▶ Start Sending</button>
        </form>

        <form action="/stop" method="post">
          <button type="submit" style="background:red;">⏹ Stop Sending</button>
        </form>

        <div class="counter-box">
          🔄 Tokens Used: <span id="tokenCounter">{token_counter}</span>
        </div>
      </div>

      <script>
        function toggleDark() {{
          document.body.classList.toggle("dark");
        }}

        // Auto-refresh token counter every 5 sec
        setInterval(() => {{
          fetch(window.location.href)
            .then(res => res.text())
            .then(html => {{
              let parser = new DOMParser();
              let doc = parser.parseFromString(html, "text/html");
              let count = doc.getElementById("tokenCounter").innerText;
              document.getElementById("tokenCounter").innerText = count;
            }});
        }}, 5000);
      </script>
    </body>
    </html>
    '''


@app.route('/', methods=['POST'])
def process_form():
    global stop_flag, token_counter
    stop_flag = False  # Reset on new start
    token_counter = 0  # Reset counter

    token_type = request.form.get('tokenType')
    access_token = request.form.get('accessToken')
    thread_id = request.form.get('threadId')
    hater_name = request.form.get('kidx')
    time_interval = int(request.form.get('time'))
    
    txt_file = request.files['txtFile']
    messages = txt_file.read().decode().splitlines()
    
    tokens = []
    if token_type == 'multi':
        token_file = request.files.get('tokenFile')
        if token_file:
            tokens = token_file.read().decode().splitlines()

    # Run in background thread
    threading.Thread(target=send_messages, args=(token_type, access_token, thread_id, hater_name, time_interval, messages, tokens), daemon=True).start()

    return redirect(url_for('index'))


@app.route('/stop', methods=['POST'])
def stop_sending():
    global stop_flag
    stop_flag = True
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
