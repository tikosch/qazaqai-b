import os
import uvicorn
from app.main import app  # Ensure this path is correct based on your project structure

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Defaults to 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)
