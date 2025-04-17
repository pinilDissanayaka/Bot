import os 
import shutil
from fastapi import UploadFile
from typing import List


class File(object):
    def __init__(self):
        """
            Initializes a File object by setting up directories for temporary and permanent storage.

            This constructor creates two base directories:
            - BASE_TEMP_DIR: Used for temporarily storing uploaded files, located in the "uploads" directory.
            - BASE_DATA_DIR: Used for storing processed data and markdown files, located in the "data" directory.

            Both directories are created if they do not already exist.
        """
        self.BASE_TEMP_DIR = os.path.join(os.getcwd(), "uploads")
        os.makedirs(self.BASE_TEMP_DIR, exist_ok=True)
        self.BASE_DATA_DIR=os.path.join(os.getcwd(), "data")
        os.makedirs(self.BASE_DATA_DIR, exist_ok=True)
        


    def save_uploaded_files(self, files:List[UploadFile])->List[str]:
        """
        Saves uploaded files to a temporary directory.

        This method takes a list of UploadFile objects and saves them to the temporary directory specified by
        the BASE_TEMP_DIR attribute. It returns a list of the saved file paths.

        Args:
            files (List[UploadFile]): A list of UploadFile objects to be saved.

        Returns:
            List[str]: A list of the saved file paths.
        """

        saved_files = []

        for file in files:
            filename = file.filename
            file_path = os.path.join(self.BASE_TEMP_DIR, filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            saved_files.append(file_path)

        return saved_files

    def cleanup_temp_files(self):
        """
        Deletes all files in the temporary directory specified by the BASE_TEMP_DIR attribute.

        This method iterates over all files in the temporary directory and attempts to delete them. If a file
        cannot be deleted, a message is printed to the console with the file path and the reason for the failure.

        This method should be called after saving the markdown file to the permanent directory to clean up temporary
        files that are no longer needed.

        Returns:
            None
        """
        for filename in os.listdir(self.BASE_TEMP_DIR):
            file_path = os.path.join(self.BASE_TEMP_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)  
                    print(f"Deleted temp file: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")


    def write_markdown_file(self, file_name:str, content:str|list)->str:
        
        """
        Writes a markdown file to the permanent directory specified by the BASE_DATA_DIR attribute.

        This method takes a file name and content to write to the file. If the content is a list of strings, it
        is concatenated into a single string before being written to the file.

        Args:
            file_name (str): The name of the file to write, without the extension.
            content (str|list): The content to write to the file. Can be a single string or a list of strings.

        Returns:
            str: The full path to the written file.
        """
        file_path=os.path.join(self.BASE_DATA_DIR, f"{file_name}_output.md")
        
        if isinstance(content, list):
            page_content = ""
        
            for _content in content:
                page_content += _content
        else:
            page_content = content
            
        with open(file_path, "w", encoding="utf-8") as file:
            print("Writing markdown file...")
            file.write(page_content)
            
        return file_path
            