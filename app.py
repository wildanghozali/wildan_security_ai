import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Mengambil API key secara aman dari environment variable server
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# List model yang akan dicoba secara berurutan
# List model terbaru yang aktif
MODEL_NAMES = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecuAI - Cyber Security Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        .glass {
            background: rgba(17, 24, 39, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(75, 85, 99, 0.3);
        }
        .typing-dot { animation: typing 1.4s infinite ease-in-out both; }
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        pre {
            background: #0f172a;
            padding: 1rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            border: 1px solid #334155;
            margin: 0.5rem 0;
        }
        code {
            font-family: 'JetBrains Mono', monospace;
            color: #34d399;
        }
        .mode-btn.active {
            background: rgba(16, 185, 129, 0.2);
            border-color: rgba(16, 185, 129, 0.6);
            color: #34d399;
        }
    </style>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen flex flex-col">

    <!-- Header -->
    <header class="glass sticky top-0 z-50 border-b border-gray-800">
        <div class="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center border border-emerald-500/30">
                    <i class="fas fa-shield-halved text-emerald-400 text-lg"></i>
                </div>
                <div>
                    <h1 class="font-bold text-lg tracking-tight">SecuAI Asisten</h1>
                    <p class="text-xs text-gray-400">Bug Hunter & Pentest Edition</p>
                </div>
            </div>
            <span class="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 text-xs rounded border border-emerald-500/20 font-mono">Linux Mint Ready</span>
        </div>
    </header>

    <!-- Main Container -->
    <main class="flex-1 max-w-4xl mx-auto w-full px-4 py-6 flex flex-col">
        
        <!-- Welcome Screen -->
        <div id="welcome" class="text-center py-8">
            <div class="w-16 h-16 bg-gray-900 rounded-2xl mx-auto flex items-center justify-center mb-4 border border-gray-800 shadow-lg">
                <i class="fas fa-terminal text-2xl text-emerald-400"></i>
            </div>
            <h2 class="text-2xl font-bold mb-2">Halo Wildan, Siap Berburu Bug Hari Ini?</h2>
            <p class="text-gray-400 max-w-md mx-auto mb-6 text-sm">
                Pilih mode kerja di bawah atau langsung ketik pertanyaan teknis keamanan siber, analisis payload, dan draf laporanmu.
            </p>

            <!-- Mode Selector -->
            <div class="flex justify-center gap-2 mb-6 flex-wrap">
                <button onclick="setMode('general')" id="btn-general" class="mode-btn active px-4 py-2 rounded-lg border border-gray-700 bg-gray-900 text-sm transition-all">
                    <i class="fas fa-comments mr-1"></i> General
                </button>
                <button onclick="setMode('exploit')" id="btn-exploit" class="mode-btn px-4 py-2 rounded-lg border border-gray-700 bg-gray-900 text-sm transition-all">
                    <i class="fas fa-bug mr-1"></i> Exploit / PoC
                </button>
                <button onclick="setMode('report')" id="btn-report" class="mode-btn px-4 py-2 rounded-lg border border-gray-700 bg-gray-900 text-sm transition-all">
                    <i class="fas fa-file-shield mr-1"></i> Vulnerability Report
                </button>
            </div>
        </div>

        <!-- Chat History -->
        <div id="chat-messages" class="flex-1 space-y-4 mb-4"></div>

        <!-- Typing Indicator -->
        <div id="typing" class="hidden py-2">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-emerald-500/20 rounded-full flex items-center justify-center border border-emerald-500/30">
                    <i class="fas fa-shield-halved text-emerald-400 text-xs"></i>
                </div>
                <div class="glass px-4 py-3 rounded-2xl rounded-tl-md">
                    <div class="flex gap-1">
                        <div class="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                        <div class="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                        <div class="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Input Bar -->
    <div class="glass border-t border-gray-800 sticky bottom-0">
        <div class="max-w-4xl mx-auto px-4 py-4">
            <form id="chat-form" class="flex gap-3">
                <input type="text" id="user-input" 
                    class="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 text-gray-100 placeholder-gray-500"
                    placeholder="Ketik perintah atau analisis target..." autocomplete="off">
                <button type="submit" 
                    class="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-3 rounded-xl transition-all flex items-center gap-2 font-medium text-sm shadow-lg shadow-emerald-600/20">
                    <span>Kirim</span>
                    <i class="fas fa-paper-plane text-xs"></i>
                </button>
            </form>
        </div>
    </div>

    <script>
        let currentMode = 'general';

        function setMode(mode) {
            currentMode = mode;
            document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('btn-' + mode).classList.add('active');
        }

        const chatForm = document.getElementById('chat-form');
        const userInput = document.getElementById('user-input');
        const chatMessages = document.getElementById('chat-messages');
        const typingIndicator = document.getElementById('typing');
        const welcomeScreen = document.getElementById('welcome');

        function appendMessage(sender, text) {
            welcomeScreen.style.display = 'none';
            const isUser = sender === 'user';
            const div = document.createElement('div');
            div.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;
            
            div.innerHTML = `
                <div class="max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${isUser ? 'bg-emerald-600 text-white rounded-tr-sm' : 'glass text-gray-200 rounded-tl-sm border border-gray-700/50'}">
                    <div class="font-bold text-xs opacity-75 mb-1">${isUser ? 'Wildan' : 'SecuAI Cyber Assistant'}</div>
                    <div class="whitespace-pre-wrap">${escapeHtml(text)}</div>
                </div>
            `;
            chatMessages.appendChild(div);
            window.scrollTo(0, document.body.scrollHeight);
        }

        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const prompt = userInput.value.trim();
            if (!prompt) return;

            appendMessage('user', prompt);
            userInput.value = '';
            typingIndicator.classList.remove('hidden');
            window.scrollTo(0, document.body.scrollHeight);

            try {
                const res = await fetch('/ask-ai', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt, mode: currentMode })
                });
                const data = await res.json();
                typingIndicator.classList.add('hidden');

                if (data.error) {
                    appendMessage('ai', 'Error: ' + data.error);
                } else {
                    appendMessage('ai', data.response + (data.model_used ? `\\n\\n[Model: ${data.model_used}]` : ''));
                }
            } catch (err) {
                typingIndicator.classList.add('hidden');
                appendMessage('ai', 'Gagal terhubung ke server backend Flask.');
            }
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/ask-ai", methods=["POST"])
def ask_ai():
    data = request.json
    user_prompt = data.get("prompt", "")
    mode = data.get("mode", "general")

    if not user_prompt:
        return jsonify({"error": "Prompt tidak boleh kosong!"}), 400

    system_instruction = (
        "Kamu adalah asisten AI expert di bidang Cyber Security, Penetration Testing, "
        "dan Bug Bounty. Berikan analisis teknis yang tajam, solusi mitigasi, "
        "serta panduan keamanan yang profesional."
    )

    if mode == "exploit":
        system_instruction += (
            " Pengguna meminta analisis eksploitasi. Berikan langkah-langkah teknis, "
            "payload contoh (untuk tujuan edukasi/authorized testing), dan teknik mitigasi. "
            "Selalu tekankan bahwa eksploitasi hanya boleh dilakukan pada sistem yang "
            "memiliki izin tertulis (authorized penetration testing)."
        )
    elif mode == "report":
        system_instruction += (
            " Pengguna meminta draf laporan kerentanan (vulnerability report). "
            "Buat laporan formal lengkap dengan: Judul Temuan, Severity (CVSS), Deskripsi, "
            "Langkah Reproduksi (PoC), Dampak, Remediasi, dan WAJIB sertakan format "
            "permintaan sertifikat apresiasi (Hall of Fame / Certificate of Appreciation) "
            "kepada pihak pengelola target."
        )

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_instruction}\\n\\nPertanyaan/Data Target: {user_prompt}"}
                ]
            }
        ]
    }

    last_error = None
    
    # Coba setiap model sampai ada yang berhasil
    for model_name in MODEL_NAMES:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            res_data = response.json()
            
            if response.status_code == 200 and "candidates" in res_data:
                ai_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return jsonify({"response": ai_reply, "model_used": model_name})
            else:
                last_error = res_data.get("error", {}).get("message", f"Unknown error with {model_name}")
                print(f"Model {model_name} failed: {last_error}")
                continue  
                
        except Exception as e:
            last_error = str(e)
            print(f"Model {model_name} error: {last_error}")
            continue  

    # Kalau semua model gagal
    return jsonify({
        "error": f"Semua model gagal. Error terakhir: {last_error}."
    }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)