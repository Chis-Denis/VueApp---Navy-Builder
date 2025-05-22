import os
import shutil
from fastapi import UploadFile, HTTPException
from typing import List
import aiofiles

# Configure upload directory
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save an uploaded file to the uploads directory
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
        
        # Use aiofiles for non-blocking file operations
        async with aiofiles.open(file_path, 'wb') as out_file:
            # Read and write in chunks to handle large files
            while content := await upload_file.read(1024 * 1024):  # 1MB chunks
                await out_file.write(content)
        
        return upload_file.filename
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_file_path(filename: str) -> str:
    """
    Get the full path for a file in the uploads directory
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return file_path

def list_files() -> List[str]:
    """
    List all files in the uploads directory
    """
    try:
        return [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def delete_file(filename: str) -> bool:
    """
    Delete a file from the uploads directory
    """
    try:
        file_path = get_file_path(filename)
        os.remove(file_path)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 