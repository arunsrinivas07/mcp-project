import sys
import os

# Ensure mcp-learning-assistant/ is on the path so all imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.app import app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
