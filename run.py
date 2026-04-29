import sys
import os
from flask import send_from_directory

# Ensure mcp-learning-assistant/ is on the path so all imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.app import app

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
