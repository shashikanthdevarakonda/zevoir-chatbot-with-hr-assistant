"""
ZEVOIR CHATBOT - ALL PAGES WORKING
"""

from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import pytz
import os

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Import RAG
try:
    from rag import rag_query
    print("✅ RAG loaded")
except Exception as e:
    print(f"❌ RAG Error: {e}")
    rag_query = None

# ---- HR Assistant add-on (RAG Chatbot for Email & WhatsApp Assistance) ----
# Self-contained Blueprint in hr_assistant/ — does not modify any existing
# route, template, or logic above/below this block.
try:
    from hr_assistant.hr_routes import hr_bp
    app.register_blueprint(hr_bp)
    print("✅ HR Assistant loaded (routes: /hr-assistant, /hr/ask, /hr/generate-email, /hr/generate-whatsapp, /hr/chat)")
except Exception as e:
    print(f"❌ HR Assistant Error: {e}")

# Import HR routing helpers so the SAME /chat endpoint (used by the floating
# Zevoir Assistant widget) can also answer HR questions / draft emails & WhatsApp
# messages, without touching the widget's HTML/CSS/JS at all.
try:
    from hr_assistant.hr_rag import hr_rag_query, is_hr_related
    print("✅ HR routing enabled for the main chat widget")
except Exception as e:
    print(f"❌ HR routing import error: {e}")
    hr_rag_query = None
    is_hr_related = None

def get_greeting():
    ist = pytz.timezone('Asia/Kolkata')
    hour = datetime.now(ist).hour
    if 5 <= hour < 12:
        return "Good Morning! ☀️ How can I help you today?"
    elif 12 <= hour < 17:
        return "Good Afternoon! 🌤️ What can I assist you with?"
    elif 17 <= hour < 21:
        return "Good Evening! 🌆 How can I help you?"
    else:
        return "Good Night! 🌙 Feel free to ask me anything!"

# -----------------------------------------------
# CHATBOT HTML/CSS/JS WITH PERSISTENT HISTORY
# -----------------------------------------------
CHATBOT_CODE = '''
<style>
/* ── Chatbot container: sits above toggle button ── */
#zev-box {
  position: fixed;
  bottom: 95px;
  right: 25px;
  width: 380px;
  height: 580px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 60px rgba(13,71,161,0.25);
  z-index: 9999;
  display: none;
  flex-direction: column;
  font-family: Arial, sans-serif;
  overflow: hidden;
}
#zev-box.show { display: flex; }

/* ── Header ── */
#zev-top {
  background: linear-gradient(135deg, #1a73e8, #0d47a1);
  color: white;
  padding: 14px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}
#zev-top h3 { margin: 0; font-size: 17px; font-weight: bold; color: white; }
#zev-top-buttons { display: flex; gap: 6px; }
#zev-top button {
  background: rgba(255,255,255,0.15);
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
#zev-top button:hover { background: rgba(255,255,255,0.3); }

/* ── Chat messages area — blue-toned theme ── */
#zev-msgs {
  flex: 1;
  overflow-y: auto;
  padding: 16px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: #dce8fb;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(26,115,232,0.08) 0%, transparent 60%),
    radial-gradient(circle at 80% 70%, rgba(13,71,161,0.08) 0%, transparent 60%),
    url("data:image/svg+xml,%3Csvg width='52' height='52' viewBox='0 0 52 52' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%231a73e8' fill-opacity='0.06' fill-rule='evenodd'%3E%3Ccircle cx='6' cy='6' r='2'/%3E%3Ccircle cx='32' cy='6' r='2'/%3E%3Ccircle cx='6' cy='32' r='2'/%3E%3Ccircle cx='32' cy='32' r='2'/%3E%3Ccircle cx='19' cy='19' r='2'/%3E%3C/g%3E%3C/svg%3E");
}
#zev-msgs::-webkit-scrollbar { width: 5px; }
#zev-msgs::-webkit-scrollbar-track { background: #c8daf7; }
#zev-msgs::-webkit-scrollbar-thumb { background: #1a73e8; border-radius: 4px; }

/* ── Message bubbles ── */
.msg {
  max-width: 82%;
  padding: 9px 13px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
  position: relative;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12);
}
/* Bot bubble — white with blue left tail */
.bot {
  background: #ffffff;
  color: #1a1a2e;
  align-self: flex-start;
  border-top-left-radius: 3px;
}
.bot::before {
  content: '';
  position: absolute;
  top: 0; left: -7px;
  width: 0; height: 0;
  border-top: 7px solid #ffffff;
  border-left: 7px solid transparent;
}
/* User bubble — blue with right tail */
.user {
  background: linear-gradient(135deg, #1a73e8, #1565c0);
  color: #ffffff;
  align-self: flex-end;
  border-top-right-radius: 3px;
}
.user::after {
  content: '';
  position: absolute;
  top: 0; right: -7px;
  width: 0; height: 0;
  border-top: 7px solid #1a73e8;
  border-right: 7px solid transparent;
}
/* Typing indicator bubble */
.typing {
  background: #ffffff;
  color: #666;
  align-self: flex-start;
  border-top-left-radius: 3px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12);
}
.typing-dots { display: inline-block; }
.typing-dots span {
  display: inline-block;
  width: 6px; height: 6px;
  background: #1a73e8;
  border-radius: 50%;
  margin: 0 2px;
  animation: typing 1.4s infinite;
}
.typing-dots span:nth-child(1) { animation-delay: 0s; }
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing { 0%, 60%, 100% { opacity: 0.25; } 30% { opacity: 1; } }

/* ── Input area ── */
#zev-input-area {
  padding: 10px 12px;
  border-top: 1px solid #c5d9f7;
  display: flex;
  gap: 8px;
  background: #eef4ff;
  border-radius: 0 0 16px 16px;
  align-items: center;
  flex-shrink: 0;
}
#zev-input {
  flex: 1;
  padding: 10px 14px;
  border: 1.5px solid #c0d4f5;
  border-radius: 22px;
  outline: none;
  font-size: 14px;
  background: white;
  color: #1a1a2e;
  transition: border-color 0.2s, box-shadow 0.2s;
}
#zev-input:focus { border-color: #1a73e8; box-shadow: 0 0 0 3px rgba(26,115,232,0.15); }
#zev-input:disabled { background: #f0f4ff; }
#zev-send {
  background: linear-gradient(135deg, #1a73e8, #0d47a1);
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px; height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(26,115,232,0.4);
  transition: transform 0.15s, box-shadow 0.15s;
}
#zev-send:hover { transform: scale(1.08); box-shadow: 0 4px 14px rgba(26,115,232,0.5); }
#zev-send:disabled { background: #aaa; box-shadow: none; cursor: not-allowed; transform: none; }

/* ── Floating toggle button — placed BELOW the chat box ── */
#zev-toggle-btn {
  position: fixed;
  bottom: 25px;
  right: 25px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1a73e8, #0d47a1);
  color: white;
  border: none;
  cursor: pointer;
  z-index: 10000;
  box-shadow: 0 4px 18px rgba(26,115,232,0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
#zev-toggle-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 24px rgba(26,115,232,0.7);
}
/* Pulse ring — only when chat is closed */
#zev-toggle-btn:not(.active)::before {
  content: '';
  position: absolute;
  width: 100%; height: 100%;
  border-radius: 50%;
  background: rgba(26,115,232,0.3);
  animation: zev-pulse 2.2s ease-out infinite;
}
@keyframes zev-pulse {
  0%   { transform: scale(1);    opacity: 1; }
  70%  { transform: scale(1.6);  opacity: 0; }
  100% { transform: scale(1.6);  opacity: 0; }
}
</style>

<!-- Floating toggle button -->
<button id="zev-toggle-btn" onclick="toggleChat()" title="Chat with Zevoir Assistant">💬</button>

<div id="zev-box">
  <div id="zev-top">
    <h3>🤖 Zevoir Assistant</h3>
    <div id="zev-top-buttons">
      <button onclick="clearChat()" title="Clear history">🗑️</button>
      <button onclick="closeChat()" title="Close">✕</button>
    </div>
  </div>
  <div id="zev-msgs"></div>
  <div id="zev-input-area">
    <input type="text" id="zev-input" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
    <button id="zev-send" onclick="sendMsg()">➤</button>
  </div>
</div>

<script>
let chatBusy = false;
const STORAGE_KEY = 'zevoir_chat_history';

function toggleChat() {
  const box = document.getElementById('zev-box');
  const btn = document.getElementById('zev-toggle-btn');
  if (box.classList.contains('show')) {
    box.classList.remove('show');
    btn.classList.remove('active');
    btn.innerHTML = '💬';
  } else {
    openZevoirChat();
  }
}

window.openZevoorChat = function() {
  openZevoirChat();
}

function openZevoirChat() {
  const box = document.getElementById('zev-box');
  const btn = document.getElementById('zev-toggle-btn');
  box.classList.add('show');
  btn.classList.add('active');
  btn.innerHTML = '✕';

  const msgs = document.getElementById('zev-msgs');

  // Load history from localStorage
  const history = localStorage.getItem(STORAGE_KEY);
  if (history) {
    try {
      const messages = JSON.parse(history);
      msgs.innerHTML = '';
      messages.forEach(msg => {
        const div = document.createElement('div');
        div.className = `msg ${msg.type}`;
        div.innerText = msg.text;
        msgs.appendChild(div);
      });
      msgs.scrollTop = msgs.scrollHeight;
    } catch (e) {
      console.log('Failed to load history');
      addBotMsg('👋 Hi! Welcome to Zevoir Technologies. Ask me anything about our services!');
    }
  } else {
    // First time — only add greeting if chat is empty
    if (msgs.children.length === 0) {
      addBotMsg('👋 Hi! Welcome to Zevoir Technologies. Ask me anything about our services!');
    }
  }

  setTimeout(() => document.getElementById('zev-input').focus(), 100);
}

function closeChat() {
  const box = document.getElementById('zev-box');
  const btn = document.getElementById('zev-toggle-btn');
  box.classList.remove('show');
  btn.classList.remove('active');
  btn.innerHTML = '💬';
}

function clearChat() {
  if (confirm('Clear all chat history?')) {
    localStorage.removeItem(STORAGE_KEY);
    document.getElementById('zev-msgs').innerHTML = '';
    addBotMsg('👋 Hi! Welcome to Zevoir Technologies. Ask me anything about our services!');
  }
}

function saveHistory() {
  const msgs = document.getElementById('zev-msgs');
  const messages = [];

  msgs.querySelectorAll('.msg').forEach(msg => {
    if (!msg.id) { // Skip typing indicator
      messages.push({
        type: msg.classList.contains('bot') ? 'bot' : 'user',
        text: msg.innerText
      });
    }
  });

  localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
}

function addBotMsg(text) {
  const msgs = document.getElementById('zev-msgs');
  const div = document.createElement('div');
  div.className = 'msg bot';
  div.innerText = text;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  saveHistory();
}

function addUserMsg(text) {
  const msgs = document.getElementById('zev-msgs');
  const div = document.createElement('div');
  div.className = 'msg user';
  div.innerText = text;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  saveHistory();
}

function addTypingIndicator() {
  const msgs = document.getElementById('zev-msgs');
  const div = document.createElement('div');
  div.className = 'msg typing';
  div.id = 'typing-indicator';
  div.innerHTML = 'Zevoir Assistant is thinking<span class="typing-dots"><span></span><span></span><span></span></span>';
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function removeTypingIndicator() {
  const typing = document.getElementById('typing-indicator');
  if (typing) typing.remove();
}

async function sendMsg() {
  if (chatBusy) return;

  const input = document.getElementById('zev-input');
  const sendBtn = document.getElementById('zev-send');
  const text = input.value.trim();
  if (!text) return;

  chatBusy = true;
  input.value = '';
  input.disabled = true;
  sendBtn.disabled = true;

  addUserMsg(text);
  addTypingIndicator();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();

    removeTypingIndicator();
    addBotMsg(data.reply || 'No response');
  } catch (e) {
    removeTypingIndicator();
    addBotMsg('⚠️ Error! Server not running.');
  }

  input.disabled = false;
  sendBtn.disabled = false;
  input.focus();
  chatBusy = false;
}

// Hook into header AI Chat button
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    const allElements = document.querySelectorAll('*');
    for (let el of allElements) {
      if (el.innerText && el.innerText.trim() === 'AI Chat') {
        el.style.cursor = 'pointer';
        el.onclick = function(e) {
          e.preventDefault();
          e.stopPropagation();
          openZevoorChat();
          return false;
        };
        break;
      }
    }
  }, 500);
});
</script>
'''

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('images', filename)

@app.route('/fonts/<path:filename>')
def serve_fonts(filename):
    return send_from_directory('fonts', filename)

# -----------------------------------------------
# SERVE HTML PAGES - ALL PAGES
# -----------------------------------------------

def inject_chatbot(html):
    """Add chatbot code to HTML"""
    return html.replace('</body>', CHATBOT_CODE + '</body>')

@app.route('/')
def home():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    return inject_chatbot(html)

@app.route('/index')
def index():
    return home()

@app.route('/about')
def about():
    try:
        with open('about.html', 'r', encoding='utf-8') as f:
            html = f.read()
        return inject_chatbot(html)
    except:
        return "Page not found", 404

@app.route('/services')
def services():
    try:
        with open('services.html', 'r', encoding='utf-8') as f:
            html = f.read()
        return inject_chatbot(html)
    except:
        return "Page not found", 404

@app.route('/contactus')
def contactus():
    try:
        with open('contactus.html', 'r', encoding='utf-8') as f:
            html = f.read()
        return inject_chatbot(html)
    except:
        return "Page not found", 404

@app.route('/<path:page>')
def serve_any_page(page):
    """Serve any HTML file"""
    # Remove .html if present
    if page.endswith('.html'):
        filename = page
    else:
        filename = f"{page}.html"

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            html = f.read()
        return inject_chatbot(html)
    except:
        return "Page not found", 404

# -----------------------------------------------
# CHAT API
# -----------------------------------------------

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '').strip()
        message_lower = message.lower()

        if not message:
            return jsonify({'reply': '😊 Please type a question!'})

        # GREETINGS
        if message_lower in ['hi', 'hello', 'hey', 'hii', 'hiii']:
            return jsonify({'reply': get_greeting()})

        elif 'good morning' in message_lower:
            return jsonify({'reply': '☀️ Good Morning! How can I help you with Zevoir Technologies?'})

        elif 'good afternoon' in message_lower:
            return jsonify({'reply': '🌤️ Good Afternoon! What would you like to know about our services?'})

        elif 'good evening' in message_lower:
            return jsonify({'reply': '🌆 Good Evening! How can I assist you?'})

        elif 'good night' in message_lower:
            return jsonify({'reply': '🌙 Good Night! Feel free to ask me anything about Zevoir before you go!'})

        elif message_lower in ['bye', 'goodbye', 'see you', 'see you later', 'take care']:
            return jsonify({'reply': '👋 Goodbye! Have a great day! Feel free to reach out anytime.'})

        elif 'thanks' in message_lower or 'thank you' in message_lower:
            return jsonify({'reply': '😊 You\'re welcome! Feel free to ask if you need anything else about Zevoir!'})

        # ---- HR ASSISTANT ROUTING ----
        # Leave / WFH / holiday questions, or email/WhatsApp drafting requests,
        # get answered from the HR knowledge base instead of the website RAG.
        if is_hr_related is not None and hr_rag_query is not None and is_hr_related(message):
            hr_result = hr_rag_query(message)
            return jsonify({'reply': hr_result.get('reply', 'No response')})

        # RAG FOR EVERYTHING ELSE
        if rag_query is None:
            return jsonify({'reply': '⚠️ RAG not loaded.'})

        result = rag_query(message)
        return jsonify({'reply': result.get('reply', 'No response')})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'reply': f'⚠️ Error: {str(e)}'})

if __name__ == '__main__':
    print('🚀 Zevoir Chatbot Starting...')
    print('📍 Pages: /, /about, /services, /contactus')
    print('📍 HR Assistant: /hr-assistant')
    app.run(debug=False, port=5000)