 import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)
application = app

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

MODEL_NAMES = [
    "gemini-2.5-flash",
    "gemini-3.7-flash",
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EcoNexus AI - General Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        .glass {
            background: rgba(6, 78, 59, 0.25);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        .typing-dot { animation: typing 1.4s infinite ease-in-out both; }
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        pre {
            background: #022c22;
            padding: 1rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            border: 1px solid #065f46;
            margin: 0.5rem 0;
        }
        code {
            font-family: 'JetBrains Mono', monospace;
            color: #6ee7b7;
        }
    </style>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen flex flex-col">

    <!-- Header -->
    <header class="glass sticky top-0 z-50 border-b border-emerald-900/50">
        <div class="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-emerald-600/20 rounded-lg flex items-center justify-center border border-emerald-500/40">
                    <i class="fas fa-leaf text-emerald-400 text-lg"></i>
                </div>
                <div>
                    <h1 class="font-bold text-lg tracking-tight text-emerald-100">EcoNexus AI</h1>
                    <p class="text-xs text-emerald-400/80">Personal Assistant</p>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="flex-1 max-w-4xl mx-auto w-full px-4 py-6 flex flex-col">
        
        <!-- Welcome Screen -->
        <div id="welcome" class="text-center py-12">
            <div class="w-16 h-16 bg-emerald-950/60 rounded-2xl mx-auto flex items-center justify-center mb-4 border border-emerald-800/60 shadow-lg">
                <i class="fas fa-seedling text-2xl text-emerald-400"></i>
            </div>
            <h2 class="text-2xl font-bold mb-2">Halo! Ada yang bisa EcoNexus bantu hari ini?</h2>
            <p class="text-gray-400 max-w-md mx-auto mb-6 text-sm">
                Tanyakan apa saja, mulai dari membuat teks, belajar, menerjemahkan bahasa, hingga menganalisis gambar.
            </p>
        </div>

        <!-- Chat History -->
        <div id="chat-messages" class="flex-1 space-y-4 mb-4"></div>

        <!-- Typing Indicator -->
        <div id="typing" class="hidden py-2">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-emerald-600/20 rounded-full flex items-center justify-center border border-emerald-500/40">
                    <i class="fas fa-leaf text-emerald-400 text-xs"></i>
                </div>
                <div class="glass px-4 py-3 rounded-2xl rounded-tl-md">
                    <div class="flex gap-1">
                        <div class="w-2 h-2 bg-emerald-400 rounded-full typing-dot"></div>
                        <div class="w-2 h-2 bg-emerald-400 rounded-full typing-dot"></div>
                        <div class="w-2 h-2 bg-emerald-400 rounded-full typing-dot"></div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Input Bar -->
    <div class="glass border-t border-emerald-900/50 sticky bottom-0">
        <div class="max-w-4xl mx-auto px-4 py-4">
            <!-- File Preview Area -->
            <div id="file-preview" class="hidden mb-2 flex items-center gap-2 bg-gray-900 p-2 rounded-lg border border-emerald-800/60 w-fit text-xs">
                <span id="file-name" class="text-emerald-400"></span>
                <button type="button" onclick="removeFile()" class="text-gray-400 hover:text-red-400"><i class="fas fa-times"></i></button>
            </div>
            
            <form id="chat-form" class="flex gap-3 items-center">
                <label for="image-input" class="cursor-pointer bg-gray-900 hover:bg-gray-800 border border-emerald-800/60 text-gray-300 px-3 py-3 rounded-xl transition-all flex items-center justify-center text-sm" title="Upload Gambar">
                    <i class="fas fa-image text-emerald-400"></i>
                </label>
                <input type="file" id="image-input" accept="image/*" class="hidden" onchange="handleFileSelect(event)">
                
                <input type="text" id="user-input" 
                    class="flex-1 bg-gray-900 border border-emerald-800/60 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 text-gray-100 placeholder-gray-500"
                    placeholder="Ketik pesan atau pertanyaanmu di sini..." autocomplete="off">
                <button type="submit" 
                    class="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-3 rounded-xl transition-all flex items-center gap-2 font-medium text-sm shadow-lg shadow-emerald-900/40">
                    <span>Kirim</span>
                    <i class="fas fa-paper-plane text-xs"></i>
                </button>
            </form>
        </div>
    </div>

    <script>
        let selectedFileBase64 = null;
        let selectedFileType = null;

        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(e) {
                const base64String = e.target.result.split(',')[1];
                selectedFileBase64 = base64String;
                selectedFileType = file.type;

                document.getElementById('file-name').innerText = file.name;
                document.getElementById('file-preview').classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }

        function removeFile() {
            selectedFileBase64 = null;
            selectedFileType = null;
            document.getElementById('image-input').value = '';
            document.getElementById('file-preview').classList.add('hidden');
        }

        const chatForm = document.getElementById('chat-form');
        const userInput = document.getElementById('user-input');
        const chatMessages = document.getElementById('chat-messages');
        const typingIndicator = document.getElementById('typing');
        const welcomeScreen = document.getElementById('welcome');

        function cleanText(text) {
            return text.replace(/\\*+/g, '');
        }

        function appendMessage(sender, text, imgBase64 = null) {
            welcomeScreen.style.display = 'none';
            const isUser = sender === 'user';
            const div = document.createElement('div');
            div.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;
            
            let imgHtml = '';
            if (imgBase64) {
                imgHtml = `<div class="mb-2"><img src="data:image/jpeg;base64,${imgBase64}" class="max-h-48 rounded-lg border border-emerald-800/50"></div>`;
            }

            const processedText = isUser ? text : cleanText(text);

            div.innerHTML = `
                <div class="max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${isUser ? 'bg-emerald-600 text-white rounded-tr-sm' : 'glass text-gray-200 rounded-tl-sm border border-emerald-800/40'}">
                    <div class="font-bold text-xs opacity-75 mb-1">${isUser ? 'Anda' : 'EcoNexus AI'}</div>
                    ${imgHtml}
                    <div class="whitespace-pre-wrap">${escapeHtml(processedText)}</div>
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
            if (!prompt && !selectedFileBase64) return;

            const currentImg = selectedFileBase64;
            appendMessage('user', prompt || '[Mengirim Gambar]', currentImg);
            
            userInput.value = '';
            const payloadData = {
                prompt: prompt || 'Tolong jelaskan gambar ini.',
                image: selectedFileBase64,
                image_type: selectedFileType
            };

            removeFile();
            typingIndicator.classList.remove('hidden');
            window.scrollTo(0, document.body.scrollHeight);

            try {
                const res = await fetch('/ask-ai', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payloadData)
                });
                const data = await res.json();
                typingIndicator.classList.add('hidden');

                if (data.error) {
                    appendMessage('ai', 'Error: ' + data.error);
                } else {
                    appendMessage('ai', data.response);
                }
            } catch (err) {
                typingIndicator.classList.add('hidden');
                appendMessage('ai', 'Gagal terhubung ke server backend.');
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
    image_base64 = data.get("image")
    image_type = data.get("image_type", "image/jpeg")

    if not user_prompt and not image_base64:
        return jsonify({"error": "Prompt atau gambar tidak boleh kosong!"}), 400

    system_instruction = (
        "Kamu adalah EcoNexus AI, asisten virtual umum yang cerdas, ramah, dan membantu. "
        "Berikan jawaban yang jelas, informatif, dan akurat untuk berbagai macam pertanyaan. "
        "JANGAN PERNAH gunakan tanda bintang atau format markdown apapun di dalam teks jawabanmu agar hasilnya bersih."
    )

    parts_list = [
        {"text": f"{system_instruction}\n\nPertanyaan: {user_prompt}"}
    ]

    if image_base64:
        parts_list.append({
            "inline_data": {
                "mime_type": image_type,
                "data": image_base64
            }
        })

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": parts_list
            }
        ]
    }

    last_error = None
    
    for model_name in MODEL_NAMES:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=45)
            
            try:
                res_data = response.json()
            except Exception:
                last_error = f"HTTP {response.status_code}: {response.text[:100]}"
                continue
            
            if response.status_code == 200 and "candidates" in res_data:
                ai_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return jsonify({"response": ai_reply})
            else:
                last_error = res_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                continue    
                
        except Exception as e:
            last_error = str(e)
            continue    

    return jsonify({
        "error": f"Semua model gagal. Error terakhir: {last_error}."
    }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
