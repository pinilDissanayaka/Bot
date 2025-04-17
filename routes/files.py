import os
from fastapi import APIRouter, UploadFile, File
import markdown
from utils import Loader, File, VectorStore 
from typing import List, Optional
from database import session, Bot
from utils import run_sync
from fastapi.concurrency import run_in_threadpool


file_upload_router = APIRouter(
    prefix="/files",
    tags=['Create vector store'],
)

@file_upload_router.post("/upload-files/")
async def upload_files(
    name: str,
    files: Optional[List[UploadFile]]=None,
    text: Optional[str] = None,
    web_url: Optional[str] = None,
):
    """
    Upload files and create a vector store

    Args:
        name (str): Name of the vector store
        files (List[UploadFile], optional): List of files to upload. Defaults to None.
        text (str, optional): Text to process. Defaults to None.
        web_url (str, optional): URL to scrape. Defaults to None.

    Returns:
        dict: A dictionary containing the message, saved files and web name
    """

    file_object=File()
    
    
    # Save uploaded files (assumed to be sync)
    file_paths = await run_in_threadpool(file_object.save_uploaded_files, files=files)
    
    
    
    # Load content from files and/or URL/text (assumed to be async)
    loader = Loader(file_paths=file_paths, base_url=web_url, clean_text=text) 
    content = await loader.load()
    
    
    
    # Clean up temp files (assumed to be sync)
    await run_in_threadpool(file_object.cleanup_temp_files)
    
    # Save content as markdown (assumed to be sync)
    markdown_file_path=file_object.write_markdown_file(file_name=name, content=content)
     
    # Create vector store from content (blocking I/O + CPU-bound)
    web_name = await run_in_threadpool(VectorStore().create_vector_store, name, content)
    
    
    
    # Save bot metadata (assumed to be sync DB commit)
    new_bot=Bot(web_name=web_name, base_url=web_url)
    await run_sync(session.add, new_bot)
    await run_sync(session.commit)
    await run_sync(session.close)
    
    return {
        "message": "Vector store created successfully",
        "saved_files": content,
        "web_name": web_name
    }