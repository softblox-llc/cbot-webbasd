from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Set your Google Gemini API key
key = "AIzaSyAZCzlm89j-8fkN4gBHGvrDUOjp1FDpbQA"
genai.configure(api_key=key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Conversation log
conversation_log = []

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 50px;
        }
        #conversation {
            margin-top: 20px;
            text-align: left;
            max-width: 400px;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
</head>
<body>
    <h1>Voice Assistant</h1>
    <button id="start-button">Start Listening</button>
    <p id="output"></p><br>
    <div id="conversation"></div><br>

    <script>
        const startButton = document.getElementById('start-button');
        const output = document.getElementById('output');
        const conversation = document.getElementById('conversation');

        startButton.addEventListener('click', () => {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = () => {
                output.textContent = 'Listening...';
            };

            recognition.onresult = async (event) => {
                const transcript = event.results[0][0].transcript;
                output.textContent = `You said: ${transcript}`;
                
                const response = await fetch('/api/respond', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: transcript }),
                });

                const data = await response.json();
                speak(data.response);
                updateConversation(transcript, data.response);
            };

            recognition.onerror = (event) => {
                output.textContent = 'Error occurred in recognition: ' + event.error;
            };

            recognition.start();
        });

        function speak(text) {
            const utterance = new SpeechSynthesisUtterance(text);
            speechSynthesis.speak(utterance);
        }

        function updateConversation(userText, aiText) {
            const userDiv = document.createElement('div');
            userDiv.textContent = 'User: ' + userText;
            const aiDiv = document.createElement('div');
            aiDiv.textContent = 'AI: ' + aiText;
            conversation.appendChild(userDiv);
            conversation.appendChild(aiDiv);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/respond', methods=['POST'])
def respond():
    data = request.json
    text = data['text']
    response = model.generate_content(f"Please make short human-like responses. Don't use emojis or markdown. The user says: {text}")
    
    # Store the conversation in the log
    conversation_log.append({'user': text, 'ai': response.text})
    
    return jsonify({'response': response.text})

if __name__ == '__main__':
    app.run(debug=True)
