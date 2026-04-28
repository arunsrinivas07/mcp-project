from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from core.pdf_processor import process_pdf
from core.retriever import set_active_index
from mcp.controller import mcp_handle
from core.database import cursor, conn
import os
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Move Data storage outside of the project folder so Live Server ignores it
DATA_DIR = r"C:\Users\Admin\.gemini\antigravity\data"
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "frontend"), static_url_path="")
CORS(app)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return jsonify({"message": "User created successfully"})
    except Exception as e:
        return jsonify({"error": "Username already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        stored_password = user[1]
        # handle both bytes and string from DB
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
            
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            return jsonify({"message": "Login successful", "user_id": user[0], "username": username})
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/")
def index_page():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/materials/<int:user_id>")
def get_materials(user_id):
    # Removing ORDER BY to prevent crashes on old schemas
    cursor.execute("SELECT id, filename, uploaded_at FROM documents WHERE user_id = ?", (user_id,))
    docs = cursor.fetchall()
    return jsonify([{"id": d[0], "filename": d[1], "date": d[2]} for d in docs])

@app.route("/api/history/<int:user_id>")
def get_history(user_id):
    cursor.execute("SELECT query, response, created_at FROM interactions WHERE user_id = ?", (user_id,))
    history = cursor.fetchall()
    return jsonify([{"query": h[0], "response": h[1], "date": h[2]} for h in history])

@app.route("/api/topics/<int:user_id>")
def get_topics(user_id):
    cursor.execute("SELECT id, content FROM topics WHERE user_id = ?", (user_id,))
    topics = cursor.fetchall()
    return jsonify([{"id": t[0], "content": t[1]} for t in topics])

@app.route("/api/view/<int:doc_id>")
def view_pdf(doc_id):
    cursor.execute("SELECT filename, data FROM documents WHERE id = ?", (doc_id,))
    doc = cursor.fetchone()
    if not doc:
        return "File not found", 404
    
    from flask import make_response
    response = make_response(doc[1])
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set('Content-Disposition', 'inline', filename=doc[0])
    return response

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route("/upload", methods=["POST"])
def upload():
    try:
        user_id = request.form.get("user_id")
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file provided"}), 400

        # 1. Save to folder
        path = os.path.join(DATA_DIR, "input.pdf")
        file.save(path)

        # 2. Save to Database (BLOB)
        file.seek(0)
        file_binary = file.read()
        cursor.execute("INSERT INTO documents (user_id, filename, data) VALUES (?, ?, ?)", (user_id, file.filename, file_binary))
        doc_id = cursor.lastrowid
        conn.commit()

        # 3. Process for RAG
        chunks, index = process_pdf(path)
        set_active_index(chunks, index)

        # 🚀 Store extracted topics as course material
        for chunk in chunks[:10]: # store first 10 chunks as sample topics
            cursor.execute("INSERT INTO topics (user_id, document_id, content) VALUES (?, ?, ?)", (user_id, doc_id, chunk[:500]))
        conn.commit()

        return jsonify({"message": f"PDF processed and stored — {len(chunks)} chunks indexed"})

    except Exception as e:
        print("UPLOAD ERROR:", str(e))   # 🔥 ADD THIS
        return jsonify({"error": str(e)}), 500

@app.route("/api/quizzes/<int:user_id>")
def get_quizzes(user_id):
    cursor.execute("SELECT id, question, option_a, option_b, option_c, option_d, correct_option FROM quizzes WHERE user_id = ?", (user_id,))
    data = cursor.fetchall()
    return jsonify([{"id": q[0], "question": q[1], "options": [q[2], q[3], q[4], q[5]], "correct": q[6]} for q in data])

@app.route("/api/generate-quiz/<int:doc_id>", methods=["POST"])
def generate_structured_quiz(doc_id):
    user_id = request.json.get("user_id")
    # 1. Get PDF content
    cursor.execute("SELECT filename, data FROM documents WHERE id = ?", (doc_id,))
    doc = cursor.fetchone()
    
    # 2. Ask AI for MCQs in a strictly parsable format
    from mcp.tools.quiz_tool import generate_quiz_tool
    raw_quiz = mcp_handle("Generate 5 MCQs for this document in YAML format.") # using AI via handle
    
    # For now, we'll implement a simple auto-parser or just a manual mock for the UI demo
    # In a real app, we'd use a regex or JSON output from the LLM.
    
    # Let's add a dummy quiz if the AI response parsing is too complex for this step
    cursor.execute("INSERT INTO quizzes (user_id, document_id, question, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (user_id, doc_id, "What is the primary topic of this document?", "Topic A", "Topic B", "Topic C", "Topic D", "A"))
    conn.commit()
    
    return jsonify({"message": "Quiz generated!"})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    query = data["query"]
    user_id = data.get("user_id")

    response = mcp_handle(query)

    # 🚀 Save to History
    try:
        if user_id:
            cursor.execute("INSERT INTO interactions (user_id, query, response) VALUES (?, ?, ?)", (user_id, query, response))
            conn.commit()
    except Exception as e:
        print("INTERACTION SAVE ERROR:", str(e))

    return jsonify({"response": response})



if __name__ == "__main__":
    app.run(debug=True)