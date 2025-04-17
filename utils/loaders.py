import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    JSONLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader,
    Docx2txtLoader

)
from typing import List


class Loader(object):
    def __init__(self, file_paths: List[str] = None, base_url: str = None, clean_text: str = None):
        """
        Initialize a Loader object.

        Args:
            file_paths (List[str], optional): List of files to load. Defaults to None.
            base_url (str, optional): URL to scrape. Defaults to None.
            clean_text (str, optional): Text to process. Defaults to None.
        """
        self.file_paths = file_paths
        self.base_url = base_url
        self.clean_text = clean_text

    async def __pdf_loader(self, file_path: str) -> list:
        """
        Load a PDF file.

        Args:
            file_path (str): The path to the PDF file to load.

        Returns:
            list: A list of text chunks from the PDF file.
        """
        loop = asyncio.get_event_loop()
        loader = PyPDFLoader(file_path)
        return await loop.run_in_executor(None, loader.load)

    async def __pptx_loader(self, file_path: str) -> list:
        """
        Load a PowerPoint file.

        Args:
            file_path (str): The path to the PowerPoint file to load.

        Returns:
            list: A list of text chunks from the PowerPoint file.
        """
        loop = asyncio.get_event_loop()
        loader = UnstructuredPowerPointLoader(file_path)
        return await loop.run_in_executor(None, loader.load)

    async def __text_loader(self, file_path: str) -> list:
        
        """
        Load a text file.

        Args:
            file_path (str): The path to the text file to load.

        Returns:
            list: A list of text chunks from the text file.
        """
        loop = asyncio.get_event_loop()
        loader = TextLoader(file_path)
        return await loop.run_in_executor(None, loader.load)

    async def __csv_loader(self, file_path: str) -> list:
        """
        Load a CSV file asynchronously.

        Args:
            file_path (str): The path to the CSV file to load.

        Returns:
            list: A list of text chunks from the CSV file.
        """
        loop=asyncio.get_event_loop()
        loader = CSVLoader(file_path)
        return await loop.run_in_executor(None, loader.load)
    
    async def __json_loader(self, file_path: str) -> list:
        """
        Load a JSON file asynchronously.

        Args:
            file_path (str): The path to the JSON file to load.

        Returns:
            list: A list of text chunks from the JSON file.
        """
        loop = asyncio.get_event_loop()
        loader = JSONLoader(file_path)
        return await loop.run_in_executor(None, loader.load)

    async def __markdown_loader(self, file_path: str) -> list:
        """
        Load a Markdown file asynchronously.

        Args:
            file_path (str): The path to the Markdown file to load.

        Returns:
            list: A list of text chunks from the Markdown file.
        """
        loop = asyncio.get_event_loop()
        loader = UnstructuredMarkdownLoader(file_path)
        return await loop.run_in_executor(None, loader.load)
    
    async def __docx_loader(self, file_path: str) -> list:
        """
        Load a DOCX file asynchronously.

        Args:
            file_path (str): The path to the DOCX file to load.

        Returns:
            list: A list of text chunks from the DOCX file.
        """
        loop = asyncio.get_event_loop()
        loader = Docx2txtLoader(file_path)
        return await loop.run_in_executor(None, loader.load)

    async def __load_file(self) -> List[list]:
        """
        Load content from files asynchronously.

        This method will load content from each file in self.file_paths asynchronously
        using the appropriate loader. It will return a list of lists, where each inner list
        contains the content from a single file.

        Args:
            None

        Returns:
            List[list]: A list of lists, where each inner list contains the content from a single file.
        """
        tasks = []
        for file_path in self.file_paths:
            file_path_lower = file_path.lower()
            if file_path_lower.endswith(".pdf"):
                tasks.append(self.__pdf_loader(file_path))
            elif file_path_lower.endswith(".pptx"):
                tasks.append(self.__pptx_loader(file_path))
            elif file_path_lower.endswith(".txt"):
                tasks.append(self.__text_loader(file_path))
            elif file_path_lower.endswith(".csv"):
                tasks.append(self.__csv_loader(file_path))
            elif file_path_lower.endswith(".json"):
                tasks.append(self.__json_loader(file_path))
            elif file_path_lower.endswith(".md"):
                tasks.append(self.__markdown_loader(file_path))
            elif file_path_lower.endswith(".docx"):
                tasks.append(self.__docx_loader(file_path))
            else:
                raise ValueError(f"Unsupported file type: {file_path}")

        return await asyncio.gather(*tasks)

    async def __scrape_page(self, url: str) -> list:
        """
        Scrape content from a given URL and its linked pages asynchronously.

        This method will scrape the content from a given URL and all linked pages
        asynchronously. It will return a list of text content from all scraped pages.

        Args:
            url (str): The URL to scrape.

        Returns:
            list: A list of text content from all scraped pages.
        """
        visited_urls = set()
        scraped_content = []

        async def __recursive_scrape(session, url):
            if url in visited_urls:
                return
            print(f"Scraping: {url}")
            visited_urls.add(url)

            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        print(f"Failed to retrieve {url}")
                        return
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    page_content = soup.get_text(separator='\n', strip=True)
                    scraped_content.append(page_content)

                    for link in soup.find_all('a', href=True):
                        next_url = urljoin(url, link['href'])
                        if next_url.startswith(url):
                            await __recursive_scrape(session, next_url)

            except Exception as e:
                print(f"Error scraping {url}: {e}")
        async with aiohttp.ClientSession() as session:
            await __recursive_scrape(session, url)

        return scraped_content

    async def web_loader(self) -> str:
        """
        Load content from a web URL asynchronously.

        This method scrapes the content from the specified base URL if it exists and returns the
        concatenated text content from all scraped pages.

        Returns:
            str: The concatenated text content from the web pages, or an empty string if no base URL is provided.
        """
        if self.base_url:
            web_contents = await self.__scrape_page(self.base_url)
            return ''.join(web_contents)
        return ""

    async def load(self) -> str:
        """
        Load content from files and/or web URL asynchronously.

        This method will load content from files if file_paths is provided and load content from a web URL if base_url is provided.
        It will return the concatenated text content from all loaded files and/or web pages.

        Returns:
            str: The concatenated text content from the loaded files and/or web pages, or an empty string if no files or base URL is provided.
        """
        text_content = ""

        if self.file_paths:
            loaded_documents = await self.__load_file()
            for doc_group in loaded_documents:
                for doc in doc_group:
                    text_content += doc.page_content

        if self.base_url:
            text_content += await self.web_loader()

        if self.clean_text:
            text_content += self.clean_text

        return text_content.replace("\n", "")
        
        

                
        
    