import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WORKERS", "1"))
    reload = os.getenv("ENVIRONMENT") != "production"
    
    # Configure uvicorn
    uvicorn.run(
        "Backend.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level="info"
    )