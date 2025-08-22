"""
File Downloaders Module
=======================

This module provides functions for downloading and saving files in various formats.
Automatically detects content type (JSON vs text) and handles both seamlessly.
Designed for reuse across multiple Jupyter notebooks.

Key Features:
- Auto-detection of JSON vs text content
- Smart download and save in one function
- Flexible content-type handling
- Comprehensive error handling
- File saving with timestamps
- GitHub file downloading

Primary Function: download_and_save_content() - Does everything automatically!

Author: Python Learning Notebook
Date: August 17, 2025
"""

import json
import requests
import os
from typing import Dict, Any, Union, Tuple
from datetime import datetime


# ==================== HELPER FUNCTIONS ====================

def _add_timestamp_to_path(file_path: str, add_timestamp: bool = True) -> str:
    """Helper: Add timestamp to filename if requested."""
    if not add_timestamp:
        return file_path
    
    timestamp = datetime.now().strftime("%y%m%d_%H:%M")
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
    if '.' in filename:
        name, extension = filename.rsplit('.', 1)
        timestamped_filename = f"{name}_{timestamp}.{extension}"
    else:
        timestamped_filename = f"{filename}_{timestamp}"
    
    result_path = os.path.join(directory, timestamped_filename)
    print(f"📅 Added timestamp to filename: {timestamped_filename}")
    return result_path


def _ensure_directory_exists(file_path: str, create_dirs: bool = True) -> None:
    """Helper: Create directory if it doesn't exist."""
    if not create_dirs:
        return
    
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created directory: {directory}")


# ==================== CORE FUNCTIONS ====================

def download_content_from_url(url: str, headers: Dict[str, str] = None, timeout: int = 30) -> Union[Dict[str, Any], str]:
    """
    Download content from an HTTP URL and automatically detect if it's JSON or text.
    
    Args:
        url: The HTTP URL to download content from
        headers: HTTP headers to include in the request
        timeout: Request timeout in seconds (default: 30)
        
    Returns:
        JSON data as dictionary/list if valid JSON, otherwise text content as string
        
    Raises:
        requests.RequestException: If the HTTP request fails
    """
    if headers is None:
        headers = {
            'User-Agent': 'Python Content Downloader',
            'Accept': 'application/json, text/plain, text/*, */*'
        }
    
    print(f"📥 Downloading content from: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Check content type and try JSON first
        content_type = response.headers.get('content-type', '').lower()
        print(f"📋 Content-Type: {content_type}")
        
        # Try to parse as JSON
        if 'json' in content_type:
            try:
                json_data = response.json()
                print(f"✅ Successfully parsed as JSON data")
                print(f"📊 Data type: {type(json_data)}")
                
                if isinstance(json_data, dict):
                    keys = list(json_data.keys())[:5]
                    print(f"📋 Found {len(json_data)} top-level keys: {', '.join(keys)}{', ...' if len(json_data) > 5 else ''}")
                elif isinstance(json_data, list):
                    print(f"📋 Found {len(json_data)} items in array")
                
                return json_data
            except json.JSONDecodeError:
                print("⚠️ Content-Type indicates JSON but parsing failed, treating as text")
        
        # If not JSON content-type, still try parsing as JSON (some APIs are misconfigured)
        if 'json' not in content_type:
            try:
                json_data = response.json()
                print(f"✅ Successfully parsed as JSON data (despite content-type)")
                return json_data
            except json.JSONDecodeError:
                pass  # Continue to text handling
        
        # Handle as text content
        text_content = response.text
        print(f"✅ Successfully downloaded as text content")
        print(f"📊 Content length: {len(text_content):,} characters")
        
        if len(text_content) > 200:
            preview = text_content[:200] + "..."
            print(f"📋 Preview: {repr(preview)}")
        else:
            print(f"📋 Content: {repr(text_content)}")
        
        return text_content
        
    except requests.RequestException as e:
        print(f"❌ HTTP request failed: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error downloading content: {e}")
        raise


def download_and_save_content(url: str, file_path: str, headers: Dict[str, str] = None, 
                             timeout: int = 30, create_dirs: bool = True, 
                             indent: int = 4, add_timestamp: bool = True) -> Tuple[Union[Dict[str, Any], str], str]:
    """
    🚀 PRIMARY FUNCTION: Download content and save to appropriate format automatically.
    
    This is the main function you should use! It:
    - Downloads from any URL
    - Auto-detects JSON vs text content  
    - Saves in the appropriate format
    - Handles all the details for you
    
    Args:
        url: The HTTP URL to download content from
        file_path: Where to save the file (extension optional)
        headers: HTTP headers to include in the request
        timeout: Request timeout in seconds (default: 30)
        create_dirs: Whether to create directories if they don't exist (default: True)
        indent: JSON indentation for pretty formatting (default: 4)
        add_timestamp: Whether to add timestamp to filename (default: True)
        
    Returns:
        Tuple of (downloaded_content, actual_file_path_used)
        
    Raises:
        requests.RequestException: If the HTTP request fails
        OSError: If there's an error writing to the file
    """
    # Download the content (auto-detects JSON vs text)
    content_data = download_content_from_url(url, headers, timeout)
    
    # Prepare file path with timestamp
    actual_file_path = _add_timestamp_to_path(file_path, add_timestamp)
    _ensure_directory_exists(actual_file_path, create_dirs)
    
    # Save based on content type
    try:
        if isinstance(content_data, (dict, list)):
            # It's JSON data - save as JSON
            with open(actual_file_path, 'w', encoding='utf-8') as file:
                json.dump(content_data, file, indent=indent, ensure_ascii=False)
            print(f"� Successfully saved as JSON: {actual_file_path}")
            
        else:
            # It's text data - save as text
            with open(actual_file_path, 'w', encoding='utf-8') as file:
                file.write(content_data)
            print(f"� Successfully saved as text: {actual_file_path}")
        
        # Show file stats
        file_size = os.path.getsize(actual_file_path)
        print(f"📏 File size: {file_size:,} bytes")
        
        if isinstance(content_data, str):
            line_count = content_data.count('\n') + 1 if content_data else 0
            print(f"📄 Lines: {line_count:,}")
        
        return content_data, actual_file_path
        
    except OSError as e:
        print(f"❌ File operation failed: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error saving file: {e}")
        raise


# ==================== OPTIONAL WRAPPER FUNCTIONS ====================

def download_json_from_url(url: str, headers: Dict[str, str] = None, timeout: int = 30) -> Union[Dict[str, Any], list]:
    """
    Simple wrapper: Download JSON data only (raises error if not JSON).
    
    For most cases, use download_and_save_content() instead!
    """
    content = download_content_from_url(url, headers, timeout)
    if isinstance(content, (dict, list)):
        return content
    else:
        raise ValueError(f"URL returned text content, not JSON: {url}")


def download_text_from_url(url: str, headers: Dict[str, str] = None, timeout: int = 30) -> str:
    """
    Simple wrapper: Download text content only (converts JSON to text if needed).
    
    For most cases, use download_and_save_content() instead!
    """
    content = download_content_from_url(url, headers, timeout)
    if isinstance(content, str):
        return content
    else:
        return json.dumps(content, indent=2)


def download_and_save_json(url: str, file_path: str, headers: Dict[str, str] = None, 
                          timeout: int = 30, create_dirs: bool = True, indent: int = 4, 
                          add_timestamp: bool = True) -> Tuple[Union[Dict[str, Any], list], str]:
    """
    Simple wrapper: Download and save as JSON only (raises error if not JSON).
    
    For most cases, use download_and_save_content() instead!
    """
    # Use the smart function but validate it's JSON
    content_data, actual_file_path = download_and_save_content(
        url, file_path, headers, timeout, create_dirs, indent, add_timestamp
    )
    
    if not isinstance(content_data, (dict, list)):
        raise ValueError(f"URL returned text content, not JSON: {url}")
    
    return content_data, actual_file_path


def download_github_file(url: str, local_path: str, add_timestamp: bool = True) -> str:
    """
    Download any file from GitHub and save in its original format.
    Perfect for GitHub raw file URLs.
    
    Args:
        url: GitHub raw file URL
        local_path: Where to save (extension will be preserved)
        add_timestamp: Add timestamp to filename
        
    Returns:
        str: Actual file path used
    """
    try:
        print(f"📥 Downloading from GitHub: {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        
        # Add timestamp if requested
        actual_path = _add_timestamp_to_path(local_path, add_timestamp)
        _ensure_directory_exists(actual_path, True)
        
        # Save file (binary mode to preserve all file types)
        with open(actual_path, 'wb') as f:
            f.write(response.content)
        
        file_size = len(response.content)
        print(f"✅ Downloaded: {actual_path}")
        print(f"📏 File size: {file_size:,} bytes")
        
        return actual_path
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        raise


# ==================== MODULE TEST FUNCTION ====================

def test_module():
    """Quick test to verify the module is working correctly."""
    print("🧪 Testing file_downloaders module...")
    print("✅ Module imported successfully!")
    print("\n📋 Available functions:")
    print("  🚀 download_and_save_content() - PRIMARY FUNCTION (auto-detects everything!)")
    print("  📤 download_content_from_url() - Download only (no save)")
    print("  📥 download_github_file() - Download from GitHub")
    print("\n🔧 Optional wrappers (use main function instead):")
    print("  ⚙️  download_json_from_url() - JSON only")
    print("  ⚙️  download_text_from_url() - Text only")  
    print("  ⚙️  download_and_save_json() - JSON only with save")
    print("\n💡 Recommendation: Use download_and_save_content() for everything!")
    return True


if __name__ == "__main__":
    test_module()
