"""
Utility functions for PageIndex.

This module provides utility functions for:
- Token counting
- OpenAI API interaction
- JSON parsing and extraction
- PDF processing
- Tree structure manipulation
- Configuration management
- Logging
"""

import copy
import json
import logging
import os
import re
import time
import asyncio
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple, Union
from .constants import (
    EnvKeys,
    ApiPatterns,
    Defaults,
    Paths,
    JsonFields,
    ErrorMessages,
)

import openai
import pymupdf
import PyPDF2
import tiktoken
import yaml
from dotenv import load_dotenv
from types import SimpleNamespace as config

load_dotenv()


# =============================================================================
# Global Variables (with validation)
# =============================================================================
def _get_env_var(key: str, default: Optional[str] = None) -> str:
    """Get environment variable with optional default.

    Args:
        key: Environment variable name
        default: Default value if not set

    Returns:
        Environment variable value or default

    Raises:
        ValueError: If the variable is required and not set
    """
    value = os.getenv(key, default)
    if not value:
        if default is None:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return default
    return value


CHATGPT_API_KEY: str = _get_env_var(EnvKeys.CHATGPT_API_KEY)
OPENAI_BASE_URL: Optional[str] = _get_env_var(EnvKeys.OPENAI_BASE_URL, None)


# =============================================================================
# Rate Limiting
# =============================================================================
class RateLimiter:
    """Rate limiter for controlling concurrent API requests."""

    def __init__(self, max_concurrent: int = Defaults.MAX_CONCURRENT_REQUESTS, delay: float = Defaults.RATE_LIMIT_DELAY):
        """Initialize rate limiter.

        Args:
            max_concurrent: Maximum number of concurrent requests
            delay: Delay between requests in seconds
        """
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._delay = delay

    async def __aenter__(self):
        """Acquire semaphore."""
        await self._semaphore.acquire()
        # Add small delay to prevent overwhelming the API
        await asyncio.sleep(self._delay)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa: ARG002
        """Release semaphore.

        Args:
            exc_type: Exception type (unused)
            exc_val: Exception value (unused)
            exc_tb: Exception traceback (unused)
        """
        self._semaphore.release()


# Global rate limiter instance
_api_rate_limiter: Optional[RateLimiter] = None


def get_api_rate_limiter() -> RateLimiter:
    """Get or create the global API rate limiter.

    Returns:
        Global RateLimiter instance
    """
    global _api_rate_limiter
    if _api_rate_limiter is None:
        _api_rate_limiter = RateLimiter()
    return _api_rate_limiter


# =============================================================================
# Token Counting
# =============================================================================
def count_tokens(text: str, model: Optional[str] = None) -> int:
    """Count the number of tokens in a text string.

    Args:
        text: Input text to count tokens for
        model: Model name for encoding selection (uses cl100k_base if not recognized)

    Returns:
        Number of tokens in the text

    Examples:
        >>> count_tokens("Hello world")
        2
        >>> count_tokens("This is a longer text.", model="gpt-4")
        6
    """
    if not text or text.isspace():
        return 0

    try:
        # Try to get encoding for the model (works for OpenAI models)
        enc = tiktoken.encoding_for_model(model)
        tokens = enc.encode(text)
        return len(tokens)
    except (KeyError, AttributeError):
        # Fallback for non-OpenAI models (like GLM)
        # Use cl100k_base (GPT-4) encoding as a reasonable approximation
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            tokens = enc.encode(text)
            return len(tokens)
        except Exception as e:
            # Last resort: estimate (rough approximation)
            logging.warning(f"Token counting failed, using estimation: {e}")
            return len(text) // 4

def ChatGPT_API_with_finish_reason(
    model: str,
    prompt: str,
    api_key: str = CHATGPT_API_KEY,
    base_url: Optional[str] = OPENAI_BASE_URL,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> Tuple[str, str]:
    """Call OpenAI API and return response with finish reason.

    Args:
        model: Model name to use
        prompt: User prompt
        api_key: OpenAI API key
        base_url: Base URL for API (uses default if None)
        chat_history: Previous chat history for context

    Returns:
        Tuple of (response_content, finish_reason)
        finish_reason is "max_output_reached" or "finished"

    Raises:
        Exception: If max retries exceeded
    """
    max_retries = Defaults.MAX_RETRIES
    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    for i in range(max_retries):
        try:
            if chat_history:
                messages = chat_history.copy()
                messages.append({"role": "user", "content": prompt})
            else:
                messages = [{"role": "user", "content": prompt}]

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=Defaults.TEMPERATURE,
            )
            finish_reason = response.choices[0].finish_reason

            if finish_reason == "length":
                return response.choices[0].message.content, "max_output_reached"
            else:
                return response.choices[0].message.content, "finished"

        except openai.APIError as e:
            logging.error(f"OpenAI API error: {e}")
            if i < max_retries - 1:
                time.sleep(Defaults.RETRY_DELAY)
            else:
                logging.error(f"{ErrorMessages.MAX_RETRIES_REACHED} for prompt: {prompt[:100]}...")
                raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            if i < max_retries - 1:
                time.sleep(Defaults.RETRY_DELAY)
            else:
                logging.error(f"{ErrorMessages.MAX_RETRIES_REACHED} for prompt: {prompt[:100]}...")
                raise

    # This should never be reached, but satisfies type checker
    return "Error", "failed"



def ChatGPT_API(
    model: str,
    prompt: str,
    api_key: str = CHATGPT_API_KEY,
    base_url: Optional[str] = OPENAI_BASE_URL,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Call OpenAI API and return response content.

    Args:
        model: Model name to use
        prompt: User prompt
        api_key: OpenAI API key
        base_url: Base URL for API (uses default if None)
        chat_history: Previous chat history for context

    Returns:
        Response content as string

    Raises:
        Exception: If max retries exceeded
    """
    max_retries = Defaults.MAX_RETRIES
    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    for i in range(max_retries):
        try:
            if chat_history:
                messages = chat_history.copy()
                messages.append({"role": "user", "content": prompt})
            else:
                messages = [{"role": "user", "content": prompt}]

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=Defaults.TEMPERATURE,
            )

            return response.choices[0].message.content

        except openai.RateLimitError as e:
            # Use exponential backoff for rate limit errors
            delay = Defaults.RETRY_DELAY * (2 ** i)
            logging.warning(f"Rate limit hit, retrying in {delay}s... (attempt {i + 1}/{max_retries})")
            if i < max_retries - 1:
                time.sleep(min(delay, 10))  # Cap at 10 seconds
            else:
                logging.error(f"{ErrorMessages.MAX_RETRIES_REACHED} for prompt: {prompt[:100]}...")
                raise
        except openai.APIError as e:
            logging.error(f"OpenAI API error: {e}")
            if i < max_retries - 1:
                time.sleep(Defaults.RETRY_DELAY)
            else:
                logging.error(f"{ErrorMessages.MAX_RETRIES_REACHED} for prompt: {prompt[:100]}...")
                raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            if i < max_retries - 1:
                time.sleep(Defaults.RETRY_DELAY)
            else:
                logging.error(f"{ErrorMessages.MAX_RETRIES_REACHED} for prompt: {prompt[:100]}...")
                raise

    # This should never be reached, but satisfies type checker
    return "Error"
            

async def ChatGPT_API_async(
    model: str,
    prompt: str,
    api_key: str = CHATGPT_API_KEY,
    base_url: Optional[str] = OPENAI_BASE_URL,
) -> str:
    """Call OpenAI API asynchronously and return response content.

    Args:
        model: Model name to use
        prompt: User prompt
        api_key: OpenAI API key
        base_url: Base URL for API (uses default if None)

    Returns:
        Response content as string

    Raises:
        Exception: If max retries exceeded
    """
    max_retries = Defaults.MAX_RETRIES
    messages = [{"role": "user", "content": prompt}]
    rate_limiter = get_api_rate_limiter()

    for i in range(max_retries):
        try:
            # Use rate limiter to control concurrent requests
            async with rate_limiter:
                async with openai.AsyncOpenAI(api_key=api_key, base_url=base_url) as client:
                    response = await client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=Defaults.TEMPERATURE,
                    )
                    return response.choices[0].message.content

        except openai.RateLimitError as e:
            # Use exponential backoff for rate limit errors
            delay = Defaults.RETRY_DELAY * (2 ** i)
            logging.warning(f"Rate limit hit, retrying in {delay}s... (attempt {i + 1}/{max_retries})")
            if i < max_retries - 1:
                await asyncio.sleep(min(delay, 10))  # Cap at 10 seconds
            else:
                logging.error(f"{ErrorMessages.MAX_RETRIES_REACHED} for prompt: {prompt[:100]}...")
                raise
        except openai.APIError as e:
            logging.error(f"OpenAI API error: {e}")
            if i < max_retries - 1:
                await asyncio.sleep(Defaults.RETRY_DELAY)
            else:
                logging.error(f"{ErrorMessages.MAX_RETRIES_REACHED} for prompt: {prompt[:100]}...")
                raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            if i < max_retries - 1:
                await asyncio.sleep(Defaults.RETRY_DELAY)
            else:
                logging.error(f"{ErrorMessages.MAX_RETRIES_REACHED} for prompt: {prompt[:100]}...")
                raise

    # This should never be reached, but satisfies type checker
    return "Error"  
            
            
def get_json_content(response):
    start_idx = response.find("```json")
    if start_idx != -1:
        start_idx += 7
        response = response[start_idx:]
        
    end_idx = response.rfind("```")
    if end_idx != -1:
        response = response[:end_idx]
    
    json_content = response.strip()
    return json_content
         

def extract_json(content: str) -> Dict[str, Any]:
    """Extract JSON from LLM response content.

    Handles various formats including:
    - JSON code blocks (```json ... ```)
    - Plain JSON
    - Python None vs JSON null
    - Trailing commas
    - Whitespace normalization

    Args:
        content: Raw content from LLM response

    Returns:
        Parsed JSON as dictionary, or empty dict if parsing fails

    Examples:
        >>> extract_json('{"key": "value"}')
        {'key': 'value'}
        >>> extract_json('```json\\n{"key": "value"}\\n```')
        {'key': 'value'}
    """
    try:
        # First, try to extract JSON enclosed within ```json and ```
        start_idx = content.find(ApiPatterns.JSON_CODE_BLOCK_START)
        if start_idx != -1:
            start_idx += len(ApiPatterns.JSON_CODE_BLOCK_START)  # Skip ```json
            end_idx = content.rfind(ApiPatterns.JSON_CODE_BLOCK_END)
            json_content = content[start_idx:end_idx].strip()
        else:
            # If no delimiters, assume entire content could be JSON
            json_content = content.strip()

        # Clean up common issues that might cause parsing errors
        json_content = json_content.replace('None', 'null')  # Replace Python None with JSON null
        json_content = json_content.replace('\n', ' ').replace('\r', ' ')  # Remove newlines
        json_content = ' '.join(json_content.split())  # Normalize whitespace

        # Attempt to parse and return the JSON object
        return json.loads(json_content)

    except json.JSONDecodeError as e:
        logging.warning(f"Failed to extract JSON: {e}")
        # Try to clean up the content further if initial parsing fails
        try:
            # Remove any trailing commas before closing brackets/braces
            json_content = json_content.replace(',]', ']').replace(',}', '}')
            return json.loads(json_content)
        except json.JSONDecodeError as e2:
            logging.error(f"Failed to parse JSON even after cleanup: {e2}")
            return {}
    except Exception as e:
        logging.error(f"Unexpected error while extracting JSON: {e}")
        return {}

def write_node_id(data, node_id=0):
    if isinstance(data, dict):
        data['node_id'] = str(node_id).zfill(4)
        node_id += 1
        for key in list(data.keys()):
            if 'nodes' in key:
                node_id = write_node_id(data[key], node_id)
    elif isinstance(data, list):
        for index in range(len(data)):
            node_id = write_node_id(data[index], node_id)
    return node_id

def get_nodes(structure):
    if isinstance(structure, dict):
        structure_node = copy.deepcopy(structure)
        structure_node.pop('nodes', None)
        nodes = [structure_node]
        for key in list(structure.keys()):
            if 'nodes' in key:
                nodes.extend(get_nodes(structure[key]))
        return nodes
    elif isinstance(structure, list):
        nodes = []
        for item in structure:
            nodes.extend(get_nodes(item))
        return nodes
    
def structure_to_list(structure):
    if isinstance(structure, dict):
        nodes = []
        nodes.append(structure)
        if 'nodes' in structure:
            nodes.extend(structure_to_list(structure['nodes']))
        return nodes
    elif isinstance(structure, list):
        nodes = []
        for item in structure:
            nodes.extend(structure_to_list(item))
        return nodes

    
def get_leaf_nodes(structure):
    if isinstance(structure, dict):
        if not structure['nodes']:
            structure_node = copy.deepcopy(structure)
            structure_node.pop('nodes', None)
            return [structure_node]
        else:
            leaf_nodes = []
            for key in list(structure.keys()):
                if 'nodes' in key:
                    leaf_nodes.extend(get_leaf_nodes(structure[key]))
            return leaf_nodes
    elif isinstance(structure, list):
        leaf_nodes = []
        for item in structure:
            leaf_nodes.extend(get_leaf_nodes(item))
        return leaf_nodes

def is_leaf_node(data, node_id):
    # Helper function to find the node by its node_id
    def find_node(data, node_id):
        if isinstance(data, dict):
            if data.get('node_id') == node_id:
                return data
            for key in data.keys():
                if 'nodes' in key:
                    result = find_node(data[key], node_id)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = find_node(item, node_id)
                if result:
                    return result
        return None

    # Find the node with the given node_id
    node = find_node(data, node_id)

    # Check if the node is a leaf node
    if node and not node.get('nodes'):
        return True
    return False

def get_last_node(structure):
    return structure[-1]


def extract_text_from_pdf(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    ###return text not list 
    text=""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text+=page.extract_text()
    return text

def get_pdf_title(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    meta = pdf_reader.metadata
    title = meta.title if meta and meta.title else 'Untitled'
    return title

def get_text_of_pages(pdf_path, start_page, end_page, tag=True):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    for page_num in range(start_page-1, end_page):
        page = pdf_reader.pages[page_num]
        page_text = page.extract_text()
        if tag:
            text += f"<start_index_{page_num+1}>\n{page_text}\n<end_index_{page_num+1}>\n"
        else:
            text += page_text
    return text

def get_first_start_page_from_text(text):
    start_page = -1
    start_page_match = re.search(r'<start_index_(\d+)>', text)
    if start_page_match:
        start_page = int(start_page_match.group(1))
    return start_page

def get_last_start_page_from_text(text):
    start_page = -1
    # Find all matches of start_index tags
    start_page_matches = re.finditer(r'<start_index_(\d+)>', text)
    # Convert iterator to list and get the last match if any exist
    matches_list = list(start_page_matches)
    if matches_list:
        start_page = int(matches_list[-1].group(1))
    return start_page


def sanitize_filename(filename, replacement='-'):
    # In Linux, only '/' and '\0' (null) are invalid in filenames.
    # Null can't be represented in strings, so we only handle '/'.
    return filename.replace('/', replacement)

def get_pdf_name(pdf_path):
    # Extract PDF name
    if isinstance(pdf_path, str):
        pdf_name = os.path.basename(pdf_path)
    elif isinstance(pdf_path, BytesIO):
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        meta = pdf_reader.metadata
        pdf_name = meta.title if meta and meta.title else 'Untitled'
        pdf_name = sanitize_filename(pdf_name)
    return pdf_name


class JsonLogger:
    def __init__(self, file_path):
        # Extract PDF name for logger name
        pdf_name = get_pdf_name(file_path)
            
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"{pdf_name}_{current_time}.json"
        os.makedirs("./logs", exist_ok=True)
        # Initialize empty list to store all messages
        self.log_data = []

    def log(self, level, message, **kwargs):
        if isinstance(message, dict):
            self.log_data.append(message)
        else:
            self.log_data.append({'message': message})
        # Add new message to the log data
        
        # Write entire log data to file
        with open(self._filepath(), "w") as f:
            json.dump(self.log_data, f, indent=2)

    def info(self, message, **kwargs):
        self.log("INFO", message, **kwargs)

    def error(self, message, **kwargs):
        self.log("ERROR", message, **kwargs)

    def debug(self, message, **kwargs):
        self.log("DEBUG", message, **kwargs)

    def exception(self, message, **kwargs):
        kwargs["exception"] = True
        self.log("ERROR", message, **kwargs)

    def _filepath(self):
        return os.path.join("logs", self.filename)
    



def list_to_tree(data):
    def get_parent_structure(structure):
        """Helper function to get the parent structure code"""
        if not structure:
            return None
        parts = str(structure).split('.')
        return '.'.join(parts[:-1]) if len(parts) > 1 else None
    
    # First pass: Create nodes and track parent-child relationships
    nodes = {}
    root_nodes = []
    
    for item in data:
        structure = item.get('structure')
        node = {
            'title': item.get('title'),
            'start_index': item.get('start_index'),
            'end_index': item.get('end_index'),
            'nodes': []
        }
        
        nodes[structure] = node
        
        # Find parent
        parent_structure = get_parent_structure(structure)
        
        if parent_structure:
            # Add as child to parent if parent exists
            if parent_structure in nodes:
                nodes[parent_structure]['nodes'].append(node)
            else:
                root_nodes.append(node)
        else:
            # No parent, this is a root node
            root_nodes.append(node)
    
    # Helper function to clean empty children arrays
    def clean_node(node):
        if not node['nodes']:
            del node['nodes']
        else:
            for child in node['nodes']:
                clean_node(child)
        return node
    
    # Clean and return the tree
    return [clean_node(node) for node in root_nodes]

def add_preface_if_needed(data):
    if not isinstance(data, list) or not data:
        return data

    if data[0]['physical_index'] is not None and data[0]['physical_index'] > 1:
        preface_node = {
            "structure": "0",
            "title": "Preface",
            "physical_index": 1,
        }
        data.insert(0, preface_node)
    return data



def get_page_tokens(pdf_path, model="glm-5", pdf_parser="PyMuPDF"):
    # Get token encoding with fallback for non-OpenAI models
    try:
        enc = tiktoken.encoding_for_model(model)
    except (KeyError, AttributeError):
        # Fallback for non-OpenAI models (like GLM)
        # Use cl100k_base (GPT-4) encoding as a reasonable approximation
        enc = tiktoken.get_encoding("cl100k_base")

    if pdf_parser == "PyPDF2":
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        page_list = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            token_length = len(enc.encode(page_text))
            page_list.append((page_text, token_length))
        return page_list
    elif pdf_parser == "PyMuPDF":
        if isinstance(pdf_path, BytesIO):
            pdf_stream = pdf_path
            doc = pymupdf.open(stream=pdf_stream, filetype="pdf")
        elif isinstance(pdf_path, str) and os.path.isfile(pdf_path) and pdf_path.lower().endswith(".pdf"):
            doc = pymupdf.open(pdf_path)
        page_list = []
        for page in doc:
            page_text = page.get_text()
            token_length = len(enc.encode(page_text))
            page_list.append((page_text, token_length))
        return page_list
    else:
        raise ValueError(f"Unsupported PDF parser: {pdf_parser}")

        

def get_text_of_pdf_pages(pdf_pages, start_page, end_page):
    text = ""
    for page_num in range(start_page-1, end_page):
        text += pdf_pages[page_num][0]
    return text

def get_text_of_pdf_pages_with_labels(pdf_pages, start_page, end_page):
    text = ""
    for page_num in range(start_page-1, end_page):
        text += f"<physical_index_{page_num+1}>\n{pdf_pages[page_num][0]}\n<physical_index_{page_num+1}>\n"
    return text

def get_number_of_pages(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    num = len(pdf_reader.pages)
    return num



def post_processing(structure, end_physical_index):
    # First convert page_number to start_index in flat list
    for i, item in enumerate(structure):
        item['start_index'] = item.get('physical_index')
        if i < len(structure) - 1:
            if structure[i + 1].get('appear_start') == 'yes':
                item['end_index'] = structure[i + 1]['physical_index']-1
            else:
                item['end_index'] = structure[i + 1]['physical_index']
        else:
            item['end_index'] = end_physical_index
    tree = list_to_tree(structure)
    if len(tree)!=0:
        return tree
    else:
        ### remove appear_start 
        for node in structure:
            node.pop('appear_start', None)
            node.pop('physical_index', None)
        return structure

def clean_structure_post(data):
    if isinstance(data, dict):
        data.pop('page_number', None)
        data.pop('start_index', None)
        data.pop('end_index', None)
        if 'nodes' in data:
            clean_structure_post(data['nodes'])
    elif isinstance(data, list):
        for section in data:
            clean_structure_post(section)
    return data

def remove_fields(data, fields=['text']):
    if isinstance(data, dict):
        return {k: remove_fields(v, fields)
            for k, v in data.items() if k not in fields}
    elif isinstance(data, list):
        return [remove_fields(item, fields) for item in data]
    return data

def print_toc(tree, indent=0):
    for node in tree:
        print('  ' * indent + node['title'])
        if node.get('nodes'):
            print_toc(node['nodes'], indent + 1)

def print_json(data, max_len=40, indent=2):
    def simplify_data(obj):
        if isinstance(obj, dict):
            return {k: simplify_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [simplify_data(item) for item in obj]
        elif isinstance(obj, str) and len(obj) > max_len:
            return obj[:max_len] + '...'
        else:
            return obj
    
    simplified = simplify_data(data)
    print(json.dumps(simplified, indent=indent, ensure_ascii=False))


def remove_structure_text(data):
    if isinstance(data, dict):
        data.pop('text', None)
        if 'nodes' in data:
            remove_structure_text(data['nodes'])
    elif isinstance(data, list):
        for item in data:
            remove_structure_text(item)
    return data


def check_token_limit(structure, limit=110000):
    list = structure_to_list(structure)
    for node in list:
        num_tokens = count_tokens(node['text'], model='glm-5')
        if num_tokens > limit:
            print(f"Node ID: {node['node_id']} has {num_tokens} tokens")
            print("Start Index:", node['start_index'])
            print("End Index:", node['end_index'])
            print("Title:", node['title'])
            print("\n")


def convert_physical_index_to_int(data):
    if isinstance(data, list):
        for i in range(len(data)):
            # Check if item is a dictionary and has 'physical_index' key
            if isinstance(data[i], dict) and 'physical_index' in data[i]:
                if isinstance(data[i]['physical_index'], str):
                    if data[i]['physical_index'].startswith('<physical_index_'):
                        data[i]['physical_index'] = int(data[i]['physical_index'].split('_')[-1].rstrip('>').strip())
                    elif data[i]['physical_index'].startswith('physical_index_'):
                        data[i]['physical_index'] = int(data[i]['physical_index'].split('_')[-1].strip())
    elif isinstance(data, str):
        if data.startswith('<physical_index_'):
            data = int(data.split('_')[-1].rstrip('>').strip())
        elif data.startswith('physical_index_'):
            data = int(data.split('_')[-1].strip())
        # Check data is int
        if isinstance(data, int):
            return data
        else:
            return None
    return data


def convert_page_to_int(data):
    for item in data:
        if 'page' in item and isinstance(item['page'], str):
            try:
                item['page'] = int(item['page'])
            except ValueError:
                # Keep original value if conversion fails
                pass
    return data


def add_node_text(node, pdf_pages):
    if isinstance(node, dict):
        start_page = node.get('start_index')
        end_page = node.get('end_index')
        node['text'] = get_text_of_pdf_pages(pdf_pages, start_page, end_page)
        if 'nodes' in node:
            add_node_text(node['nodes'], pdf_pages)
    elif isinstance(node, list):
        for index in range(len(node)):
            add_node_text(node[index], pdf_pages)
    return


def add_node_text_with_labels(node, pdf_pages):
    if isinstance(node, dict):
        start_page = node.get('start_index')
        end_page = node.get('end_index')
        node['text'] = get_text_of_pdf_pages_with_labels(pdf_pages, start_page, end_page)
        if 'nodes' in node:
            add_node_text_with_labels(node['nodes'], pdf_pages)
    elif isinstance(node, list):
        for index in range(len(node)):
            add_node_text_with_labels(node[index], pdf_pages)
    return


async def generate_node_summary(node, model=None):
    prompt = f"""You are given a part of a document, your task is to generate a description of the partial document about what are main points covered in the partial document.

    Partial Document Text: {node['text']}
    
    Directly return the description, do not include any other text.
    """
    response = await ChatGPT_API_async(model, prompt)
    return response


async def generate_summaries_for_structure(structure, model=None):
    nodes = structure_to_list(structure)
    tasks = [generate_node_summary(node, model=model) for node in nodes]
    summaries = await asyncio.gather(*tasks)
    
    for node, summary in zip(nodes, summaries):
        node['summary'] = summary
    return structure


def create_clean_structure_for_description(structure):
    """
    Create a clean structure for document description generation,
    excluding unnecessary fields like 'text'.
    """
    if isinstance(structure, dict):
        clean_node = {}
        # Only include essential fields for description
        for key in ['title', 'node_id', 'summary', 'prefix_summary']:
            if key in structure:
                clean_node[key] = structure[key]
        
        # Recursively process child nodes
        if 'nodes' in structure and structure['nodes']:
            clean_node['nodes'] = create_clean_structure_for_description(structure['nodes'])
        
        return clean_node
    elif isinstance(structure, list):
        return [create_clean_structure_for_description(item) for item in structure]
    else:
        return structure


def generate_doc_description(structure, model=None):
    prompt = f"""Your are an expert in generating descriptions for a document.
    You are given a structure of a document. Your task is to generate a one-sentence description for the document, which makes it easy to distinguish the document from other documents.
        
    Document Structure: {structure}
    
    Directly return the description, do not include any other text.
    """
    response = ChatGPT_API(model, prompt)
    return response


def reorder_dict(data, key_order):
    if not key_order:
        return data
    return {key: data[key] for key in key_order if key in data}


def format_structure(structure, order=None):
    if not order:
        return structure
    if isinstance(structure, dict):
        if 'nodes' in structure:
            structure['nodes'] = format_structure(structure['nodes'], order)
        if not structure.get('nodes'):
            structure.pop('nodes', None)
        structure = reorder_dict(structure, order)
    elif isinstance(structure, list):
        structure = [format_structure(item, order) for item in structure]
    return structure


class ConfigLoader:
    """Load and manage PageIndex configuration from YAML files.

    This class loads default configuration from config.yaml and merges
    it with user-provided options.

    Attributes:
        _default_dict: Default configuration values from YAML file

    Examples:
        >>> loader = ConfigLoader()
        >>> config = loader.load({'model': 'gpt-4'})
        >>> config.model
        'gpt-4'
    """

    def __init__(self, default_path: Optional[Union[str, Path]] = None):
        """Initialize ConfigLoader with default configuration file.

        Args:
            default_path: Path to config.yaml file (uses default if None)
        """
        if default_path is None:
            default_path = Path(__file__).parent / "config.yaml"
        self._default_dict: Dict[str, Any] = self._load_yaml(default_path)

    @staticmethod
    def _load_yaml(path: Union[str, Path]) -> Dict[str, Any]:
        """Load YAML file and return as dictionary.

        Args:
            path: Path to YAML file

        Returns:
            Parsed YAML content as dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        path = Path(path)
        if not path.exists():
            logging.warning(f"Config file not found: {path}, using empty defaults")
            return {}

        with open(path, "r", encoding="utf-8") as f:
            try:
                return yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                logging.error(f"Failed to parse config file {path}: {e}")
                return {}

    def _validate_keys(self, user_dict: Dict[str, Any]) -> None:
        """Validate that user config keys exist in default config.

        Args:
            user_dict: User-provided configuration dictionary

        Raises:
            ValueError: If unknown keys are provided
        """
        unknown_keys = set(user_dict) - set(self._default_dict)
        if unknown_keys:
            raise ValueError(ErrorMessages.CONFIG_UNKNOWN_KEYS.format(unknown_keys))

    def load(self, user_opt: Optional[Union[Dict[str, Any], config]] = None) -> config:
        """Load configuration, merging user options with defaults.

        Args:
            user_opt: User configuration options (dict, config, or None)

        Returns:
            SimpleNamespace object with merged configuration

        Raises:
            TypeError: If user_opt has invalid type
            ValueError: If unknown config keys provided
        """
        if user_opt is None:
            user_dict = {}
        elif isinstance(user_opt, config):
            user_dict = vars(user_opt)
        elif isinstance(user_opt, dict):
            user_dict = user_opt
        else:
            raise TypeError("user_opt must be dict, config(SimpleNamespace) or None")

        self._validate_keys(user_dict)
        merged = {**self._default_dict, **user_dict}
        return config(**merged)