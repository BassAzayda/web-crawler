import streamlit as st
import asyncio
import json
import random
import nest_asyncio
import aiohttp
import xml.etree.ElementTree as ET
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import base64
from datetime import datetime
import os
import sys
from pathlib import Path
import time
import re
import subprocess
import tempfile
from urllib.parse import urlparse
import logging

# Add Crawl4AI imports
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, DefaultMarkdownGenerator
from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
from crawl4ai.async_configs import HTTPCrawlerConfig
from crawl4ai.content_filter_strategy import PruningContentFilter

# Apply nest_asyncio for compatibility
nest_asyncio.apply()

# Configure Streamlit page
st.set_page_config(
    page_title="Web Crawler App",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        margin-top: 0.5rem;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: rgba(76, 175, 80, 0.2);
        color: #8affa2;
        margin: 1rem 0;
        border: 1px solid rgba(76, 175, 80, 0.4);
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: rgba(240, 70, 70, 0.2);
        color: #ff9090;
        margin: 1rem 0;
        border: 1px solid rgba(240, 70, 70, 0.4);
    }
    .download-button {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #4CAF50;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .download-button:hover {
        background-color: #45a049;
    }
    .stExpander {
        border: 1px solid #2d3035;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .url-card {
        background-color: #1e1e1e;
        border: 1px solid #2d3035;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
        color: #e0e0e0;
    }
    .url-active {
        background-color: #2c3e50;
        border-left: 3px solid #3498db;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    .results-container {
        max-height: 600px;
        overflow-y: auto;
        padding-right: 1rem;
    }
    .markdown-nav {
        border-left: 3px solid #4CAF50;
        padding-left: 1rem;
        margin: 1rem 0;
        color: #a0a0a0;
    }
    .markdown-content img {
        max-width: 100%;
        height: auto;
    }
    .st-emotion-cache-16txtl3 h1 {
        margin-bottom: 0.5rem;
    }
    .settings-card {
        background-color: #1e1e1e;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #2d3035;
    }
    .progress-card {
        background-color: #1e1e1e;
        border-radius: 0.8rem;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    .progress-card h3 {
        margin-top: 0;
        color: #8affa2;
    }
    .float-container {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
        background-color: rgba(30, 30, 30, 0.95);
        padding: 15px 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid #4CAF50;
        max-width: 300px;
        animation: pulse 2s infinite;
        color: #e0e0e0;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
        100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
    }
    .current-url {
        background-color: #2c3e50;
        border-left: 3px solid #3498db;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
    }
    .progress-heading {
        color: #8affa2;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .url-processing {
        animation: processing-pulse 1.5s infinite alternate;
        background-color: rgba(52, 152, 219, 0.2);
        border-left: 4px solid #3498db;
    }
    @keyframes processing-pulse {
        0% { background-color: rgba(52, 152, 219, 0.2); }
        100% { background-color: rgba(52, 152, 219, 0.4); }
    }
    .url-success {
        background-color: rgba(76, 175, 80, 0.2);
        border-left: 4px solid #4CAF50;
    }
    .url-error {
        background-color: rgba(231, 76, 60, 0.2);
        border-left: 4px solid #e74c3c;
    }
    .url-count {
        background-color: #4CAF50;
        color: white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 8px;
        font-size: 12px;
    }
    .url-status-icon {
        margin-right: 8px;
        font-weight: bold;
    }
    code {
        background-color: #2d3035;
        color: #e0e0e0;
        padding: 2px 5px;
        border-radius: 3px;
    }
    .stAlert {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    /* Additional dark theme improvements */
    .stApp {
        background-color: #121212;
    }
    .css-10trblm {
        color: #ffffff;
    }
    .css-16idsys p {
        color: #e0e0e0;
    }
    .css-5rimss {
        color: #e0e0e0;
    }
    .stTextInput > div > div > input {
        background-color: #2d3035;
        color: #e0e0e0;
    }
    .stTextArea > div > div > textarea {
        background-color: #2d3035;
        color: #e0e0e0;
    }
    .stSlider > div > div {
        background-color: #4e4e4e;
    }
    .stTabs [data-baseweb="tab"] {
        color: #e0e0e0;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #4CAF50;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e1e1e;
        border-radius: 8px;
    }
    .stMarkdown a {
        color: #4CAF50;
    }
    .stSelectbox > div > div {
        background-color: #2d3035;
        color: #e0e0e0;
    }
    .stRadio label {
        color: #e0e0e0;
    }
    .stCheckbox label {
        color: #e0e0e0;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #e0e0e0;
    }
    p {
        color: #c0c0c0;
    }
    .content-area {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #2d3035;
    }
    .st-ae {
        color: #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# List of realistic user agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
]

# Ensure the environment is set up correctly


def check_environment():
    try:
        import requests
        import bs4

        # Check if Crawl4AI is installed
        try:
            from crawl4ai import AsyncWebCrawler
            st.sidebar.success("✅ Crawl4AI is installed")
        except ImportError:
            st.error(f"""
            ⚠️ Crawl4AI not found

            Please install Crawl4AI:
            ```bash
            pip install crawl4ai
            ```
            """)
            st.stop()

    except ImportError as e:
        st.error(f"""
        ⚠️ Required dependencies not found: {e}

        Please run the setup script:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\\Scripts\\activate
        pip install -r requirements.txt
        ```
        """)
        st.stop()


def get_urls_from_google(query, num_results=10):
    """Get URLs from Google search results."""
    return [result for result in search(query, num_results=num_results, advanced=False)]


def is_valid_url(url):
    """Check if URL starts with a valid scheme."""
    return url.startswith(("http://", "https://", "file://", "raw:"))


def extract_metadata(soup):
    """Extract metadata from HTML soup."""
    metadata = {}

    # Extract title
    title_tag = soup.find('title')
    if title_tag:
        metadata['title'] = title_tag.text.strip()
    else:
        metadata['title'] = "No title"

    # Extract description
    description_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find(
        'meta', attrs={'property': 'og:description'})
    if description_tag and description_tag.get('content'):
        metadata['description'] = description_tag.get('content').strip()
    else:
        metadata['description'] = "No description available"

    return metadata


def extract_code_from_pre(code_html):
    """Extract formatted code from HTML pre/code tags with language detection."""
    soup = BeautifulSoup(code_html, 'html.parser')

    # Try to find the language from class attributes
    language = ""
    code_tag = soup.find('code')
    pre_tag = soup.find('pre')

    # Check code tag classes first
    if code_tag and code_tag.has_attr('class'):
        for cls in code_tag.get('class', []):
            if cls.startswith(('language-', 'lang-', 'brush:', 'syntax-')):
                parts = cls.split('-') if '-' in cls else cls.split(':')
                if len(parts) > 1:
                    language = parts[1].strip()
                    break

    # If no language found, check pre tag
    if not language and pre_tag and pre_tag.has_attr('class'):
        for cls in pre_tag.get('class', []):
            if cls.startswith(('language-', 'lang-', 'brush:', 'syntax-')):
                parts = cls.split('-') if '-' in cls else cls.split(':')
                if len(parts) > 1:
                    language = parts[1].strip()
                    break

    # Extract the code text, preferring the code tag if it exists
    if code_tag:
        code_text = code_tag.get_text()
    elif pre_tag:
        code_text = pre_tag.get_text()
    else:
        code_text = soup.get_text()

    # Clean up the code text
    code_text = code_text.strip()

    return language, code_text


def clean_html(html_content):
    """Clean HTML content using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove unwanted elements but preserve code blocks
    unwanted_elements = [
        'script', 'style', 'nav', 'footer', 'iframe', 'noscript',
        'header', 'aside', 'sidebar', 'menu', 'advertisement', 'ad',
        'banner', 'cookie', 'popup', 'modal', 'social-media'
    ]

    # Remove elements by tag name
    for tag in ['script', 'style', 'nav', 'footer', 'iframe', 'noscript', 'header', 'aside']:
        for element in soup.find_all(tag):
            if not element.find(['pre', 'code']):  # Don't remove if contains code
                element.decompose()

    # Remove elements by class or id containing specific terms
    for term in ['nav', 'menu', 'sidebar', 'footer', 'header', 'banner', 'ad', 'cookie', 'popup', 'social']:
        # Check for classes containing the term
        for element in soup.find_all(class_=lambda x: x and term in x.lower()):
            if not element.find(['pre', 'code']):
                element.decompose()

        # Check for ids containing the term
        for element in soup.find_all(id=lambda x: x and term in x.lower()):
            if not element.find(['pre', 'code']):
                element.decompose()

    return str(soup)


async def process_with_crawl4ai(html_content, url, extraction_config=None):
    """Process HTML content using Crawl4AI's markdown generator."""
    if extraction_config is None:
        extraction_config = {
            "prioritize_code_blocks": True,
            "content_type": "Technical Documentation",
            "extract_full_page": True,
            "custom_selectors": []
        }

    try:
        # Configure markdown generator with the same settings as Google Colab
        markdown_generator = DefaultMarkdownGenerator(
            # Use PruningContentFilter with threshold=0.2 to match Google Colab
            content_filter=PruningContentFilter(
                threshold=0.2,  # Same threshold as Google Colab
                threshold_type="fixed"
            ),
            options={
                "ignore_links": False,      # Keep links for better context
                "body_width": 0,            # No line wrapping
                "skip_internal_links": True,  # Skip navigation links
                "include_sup_sub": True,    # Better handling of superscript/subscript
                "escape_html": False,       # Don't escape HTML entities
                "mark_code": True           # Better code block handling
            }
        )

        # Generate markdown directly from raw HTML
        markdown_result = markdown_generator.generate_markdown(
            cleaned_html=html_content,  # Pass the raw HTML directly
            html=html_content,          # Pass the raw HTML directly
            url=url
        )

        # Try to use fit_markdown if it's available, otherwise use raw_markdown
        if hasattr(markdown_result, 'fit_markdown') and markdown_result.fit_markdown:
            markdown_content = markdown_result.fit_markdown
        else:
            markdown_content = markdown_result.raw_markdown

        # Clean up line number markers from the markdown
        cleaned_markdown = re.sub(
            r'\[\]\(#__codelineno-\d+-\d+\)', '', markdown_content)

        # Only remove null bytes which could break file writing
        cleaned_markdown = cleaned_markdown.replace('\x00', '')

        return cleaned_markdown

    except Exception as e:
        return f"Error generating markdown with Crawl4AI: {str(e)}"


async def fetch_url(url, timeout=30, use_crawl4ai=True, use_requests=True, extraction_config=None):
    """
    Fetch URL content using the best method for the situation.

    This hybrid approach:
    1. First tries to fetch content with requests (bypasses proxy auth)
    2. Processes the content with Crawl4AI for high-quality markdown extraction
    3. Falls back to aiohttp if requests fails
    """
    try:
        html_content = None
        status_code = None
        headers = {}

        # First attempt: Use requests to bypass proxy auth
        if use_requests:
            try:
                html_content, content_type = fetch_with_requests(url, timeout)
                status_code = 200  # Assume 200 as we don't get actual status code
                headers = {'Content-Type': content_type}
            except Exception as e:
                logging.warning(f"Requests fetch failed: {str(e)}")
                html_content = None

        # Second attempt: Use aiohttp if requests fails
        if not html_content:
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    html_content = await response.text()
                    status_code = response.status
                    headers = dict(response.headers)

        # Process the HTML content to extract markdown
        if html_content:
            # Process with Crawl4AI
            markdown_content = await process_with_crawl4ai(html_content, url, extraction_config)

            return {
                'success': True,
                'status_code': status_code,
                'url': url,
                'html': html_content,
                'markdown': markdown_content,
                'headers': headers
            }
        else:
            return {
                'success': False,
                'url': url,
                'error_message': "Failed to fetch HTML content"
            }
    except Exception as e:
        return {
            'success': False,
            'url': url,
            'error_message': str(e)
        }


# NEW FUNCTION: Process a crawl result with both the original and Crawl4AI approaches
def process_result(result, extraction_config=None, crawl_method="unknown"):
    """Process a crawl result and return formatted output for Streamlit."""
    # Set default extraction config if not provided
    if extraction_config is None:
        extraction_config = {
            "prioritize_code_blocks": True,
            "content_type": "Technical Documentation",
            "extract_full_page": True,
            "custom_selectors": []
        }

    output = []
    # Add crawler metadata as comments
    output.append(f"<!-- URL: {result.get('url', 'unknown')} -->\n")
    output.append(f"<!-- Crawl Method: {crawl_method} -->\n")
    output.append(
        f"<!-- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->\n")

    # Also add metadata as visible text
    output.append(f"# {result.get('url', 'unknown')}\n")
    output.append(f"*Crawled using: {crawl_method}*\n")
    output.append(f"*Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

    if 'status_code' in result:
        output.append(f"Status Code: {result.get('status_code', 'N/A')}\n")

    if not result.get('success', False):
        display_output = "\n".join(
            output) + f"\n❌ Error: {result.get('error_message', 'Unknown error')}"
        file_output = "\n".join(
            output) + f"\n❌ Error: {result.get('error_message', 'Unknown error')}\n\n---\n"
        return display_output, file_output

    # Process HTML content
    soup = BeautifulSoup(result.get('html', ''), 'html.parser')
    metadata = extract_metadata(soup)

    # Add metadata to output
    output.append(f"## {metadata['title']}\n")
    description = metadata.get('description')
    if description:
        preview_desc = description if len(
            description) <= 150 else description[:150] + "..."
        output.append(f"_{preview_desc}_\n")

    # Get the markdown content that was already processed by Crawl4AI
    markdown_content = result.get("markdown", "")

    # Only remove null bytes which could break file writing
    if markdown_content:
        markdown_content = markdown_content.replace('\x00', '')

    # Truncate markdown for display
    display_markdown = markdown_content[:2000] + \
        "..." if len(markdown_content) > 2000 else markdown_content

    display_output = "\n".join(
        output) + f"\n### Content Preview\n{display_markdown}"
    file_output = "\n".join(output) + f"\n{markdown_content}\n\n---\n"

    return display_output, file_output


def get_download_link(content, filename):
    """Generate a download link for the content"""
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:text/markdown;base64,{b64}" download="{filename}" class="download-button">Download Markdown File</a>'


async def fetch_sitemap(url):
    """Fetch and parse sitemap XML to extract all URLs."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            xml_text = await response.text()
            root = ET.fromstring(xml_text)
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            return [elem.text for elem in root.findall("ns:url/ns:loc", ns)]


# Helper function to process a single URL
async def process_single_url(url, index, total_urls, progress_data, semaphore, wait_time, extraction_config, crawl_method="hybrid"):
    """Process a single URL with progress tracking and status updates."""
    async with semaphore:
        # Update status to "processing"
        progress_data["current_urls"].append(url)
        progress_data["url_statuses"][index] = "processing"

        # Add delay between requests if this isn't the first concurrent batch
        if index >= progress_data["concurrency"]:
            await asyncio.sleep(wait_time)

        try:
            # Process the URL based on the selected crawl method
            if crawl_method == "hybrid":
                # Use requests + Crawl4AI approach (best for bypassing auth)
                result = await fetch_url(
                    url,
                    timeout=progress_data.get("timeout", 30),
                    use_crawl4ai=True,
                    use_requests=True,
                    extraction_config=extraction_config
                )
            elif crawl_method == "requests_only":
                # Use only requests (no Crawl4AI processing)
                try:
                    html_content, content_type = fetch_with_requests(
                        url, timeout=progress_data.get("timeout", 30))
                    # Convert HTML to Markdown using Crawl4AI's processor
                    markdown_content = await process_with_crawl4ai(html_content, url, extraction_config)

                    result = {
                        'success': True,
                        'status_code': 200,  # Assume 200 as we don't get the actual status code
                        'url': url,
                        'html': html_content,
                        'markdown': markdown_content,
                        'error_message': ''
                    }
                except Exception as e:
                    result = {
                        'success': False,
                        'url': url,
                        'error_message': str(e)
                    }
            elif crawl_method == "crawl4ai_http":
                # Use Crawl4AI's HTTP strategy (similar to requests)
                http_config = HTTPCrawlerConfig(
                    method="GET",
                    verify_ssl=True,
                    follow_redirects=True,
                    headers={
                        "User-Agent": random.choice(USER_AGENTS)
                    }
                )
                http_strategy = AsyncHTTPCrawlerStrategy(
                    browser_config=http_config
                )

                async with AsyncWebCrawler(crawler_strategy=http_strategy) as crawler:
                    # Create configuration that matches the successful Google Colab settings
                    crawl_result = await crawler.arun(
                        url=url,
                        config=CrawlerRunConfig(
                            # Core settings
                            cache_mode=CacheMode.BYPASS,
                            # Performance optimizations
                            stream=False,
                            simulate_user=True,
                            override_navigator=True,
                            remove_overlay_elements=True,
                            magic=True,
                            # Timing
                            delay_before_return_html=random.uniform(1.0, 3.0),
                            wait_until="networkidle",
                            page_timeout=60000,
                            # Markdown generator with the same settings as Google Colab
                            markdown_generator=DefaultMarkdownGenerator(
                                content_filter=PruningContentFilter(
                                    threshold=0.2,  # Same threshold as Google Colab
                                    threshold_type="fixed"
                                ),
                                options={
                                    "ignore_links": False,
                                    "body_width": 0,
                                    "skip_internal_links": True,
                                    "include_sup_sub": True,
                                    "escape_html": False,
                                    "mark_code": True
                                }
                            )
                        )
                    )

                    result = {
                        'success': crawl_result.success,
                        'status_code': crawl_result.status_code,
                        'url': crawl_result.url,
                        'html': crawl_result.html,
                        'markdown': crawl_result.markdown.fit_markdown if crawl_result.success and hasattr(crawl_result.markdown, 'fit_markdown') and crawl_result.markdown.fit_markdown else crawl_result.markdown.raw_markdown if crawl_result.success else "",
                        'error_message': crawl_result.error_message
                    }
            elif crawl_method == "crawl4ai_raw_html":
                # Use Crawl4AI's raw HTML processing (fetch with requests, process with Crawl4AI)
                try:
                    html_content, content_type = fetch_with_requests(
                        url, timeout=progress_data.get("timeout", 30))
                    # Process with the unmodified HTML directly via Crawl4AI
                    markdown_content = await process_with_crawl4ai(html_content, url, extraction_config)

                    result = {
                        'success': True,
                        'status_code': 200,  # We don't have the actual status code, so assume 200
                        'url': url,
                        'html': html_content,
                        'markdown': markdown_content,
                        'error_message': ''
                    }
                except Exception as e:
                    result = {
                        'success': False,
                        'url': url,
                        'error_message': str(e)
                    }
            else:
                # Default to hybrid approach
                result = await fetch_url(
                    url,
                    timeout=progress_data.get("timeout", 30),
                    extraction_config=extraction_config
                )

            if result["success"]:
                progress_data["successful_crawls"] += 1
                display_output, file_output = process_result(
                    result, extraction_config, crawl_method)
                progress_data["results"].append(file_output)
                progress_data["current_content"] = display_output
                progress_data["url_statuses"][index] = "success"
            else:
                progress_data["failed_crawls"] += 1
                error_message = result.get("error_message", "Unknown error")
                progress_data["url_statuses"][index] = "error"
                progress_data["results"].append(
                    f"\n## Error processing {url}\n\n{error_message}\n")
                progress_data["current_content"] = f"❌ Error processing {url}: {error_message}"

        except Exception as e:
            progress_data["failed_crawls"] += 1
            progress_data["url_statuses"][index] = "error"
            error_message = str(e)
            progress_data["results"].append(
                f"\n## Error processing {url}\n\n{error_message}\n")
            progress_data["current_content"] = f"❌ Error processing {url}: {error_message}"

        # Remove from current URLs being processed
        if url in progress_data["current_urls"]:
            progress_data["current_urls"].remove(url)

        # Update progress
        progress_data["processed_count"] += 1
        progress_data["progress"] = progress_data["processed_count"] / total_urls


async def crawl_list_of_urls(urls, combined_markdown_output="", wait_time=3, extraction_config=None, concurrency_limit=5, crawl_method="hybrid"):
    """Crawl a list of URLs concurrently using asyncio and semaphores."""
    # Set default extraction config if not provided
    if extraction_config is None:
        extraction_config = {
            "prioritize_code_blocks": True,
            "content_type": "Technical Documentation",
            "extract_full_page": True,
            "custom_selectors": []
        }

    if not urls:
        return []

    # Create progress tracking area at top of results
    st.markdown("<h2 class='progress-heading'>Crawling Progress</h2>",
                unsafe_allow_html=True)

    # Initialize download area at top (will be populated later)
    download_placeholder = st.empty()

    # Create a layout for the progress information
    progress_area = st.container()

    # Floating status indicator
    float_container = st.empty()

    # Main results
    results_container = st.container()

    total_urls = len(urls)

    # Initialize progress tracking data structure
    progress_data = {
        "progress": 0.0,
        "processed_count": 0,
        "successful_crawls": 0,
        "failed_crawls": 0,
        "current_urls": [],  # URLs currently being processed
        # Status for each URL: pending, processing, success, error
        "url_statuses": ["pending"] * total_urls,
        "results": [],  # Store results for all URLs
        "current_content": "",  # Content currently being displayed
        "concurrency": concurrency_limit,  # Concurrency limit
        "timeout": 30  # Request timeout
    }

    # Initialize the progress bar
    progress_bar = progress_area.progress(0.0)
    status_text = progress_area.empty()
    status_text.markdown(
        "<div class='progress-card'><h3>Starting crawler...</h3><p>Preparing to process URLs</p></div>", unsafe_allow_html=True)

    with results_container:
        st.write("### Results")
        col1, col2 = st.columns([1, 2])

        with col1:
            st.write("#### URLs processed")
            url_status_area = st.empty()

        with col2:
            st.write("#### Content extracted")
            content_area = st.empty()
            # Content area wrapper for styling - don't replace the content_area variable
            st.markdown(
                '<div class="content-area" id="content-display-area"></div>', unsafe_allow_html=True)

    # Initialize URL list display
    url_list_html = "<div style='max-height: 400px; overflow-y: auto; background-color: #1e1e1e; border-radius: 8px; padding: 10px;'>"
    for i, url in enumerate(urls):
        url_list_html += f"""<div id='url-{i}' class='url-card'>
            <span class='url-count'>{i+1}</span>
            <span class='url-status-icon' style="color: #a0a0a0;">⏳</span>
            <span style="word-break: break-all;">{url}</span>
        </div>"""
    url_list_html += "</div>"
    url_status_area.markdown(url_list_html, unsafe_allow_html=True)

    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency_limit)

    # Create task list
    tasks = []
    for i, url in enumerate(urls):
        task = asyncio.create_task(process_single_url(
            url, i, total_urls, progress_data, semaphore, wait_time, extraction_config, crawl_method))
        tasks.append(task)

    # Update UI loop
    async def update_ui():
        while progress_data["progress"] < 1.0:
            # Update progress bar
            progress_bar.progress(progress_data["progress"])

            # Update status text
            current_urls_html = ""
            if progress_data["current_urls"]:
                for cur_url in progress_data["current_urls"]:
                    current_urls_html += f"<div class='current-url'>{cur_url}</div>"

            status_html = f"""
            <div class='progress-card'>
                <h3>Processing URLs: {progress_data["processed_count"]} of {total_urls} ({progress_data["progress"]*100:.1f}%)</h3>
                <p>Currently processing {len(progress_data["current_urls"])} URLs (max: {concurrency_limit})</p>
                {current_urls_html}
                <div style='display: flex; gap: 20px; margin-top: 10px;'>
                    <div style="color: #8affa2;">✅ Success: {progress_data["successful_crawls"]}</div>
                    <div style="color: #ff9090;">❌ Failed: {progress_data["failed_crawls"]}</div>
                </div>
            </div>
            """
            status_text.markdown(status_html, unsafe_allow_html=True)

            # Update floating status
            float_html = f"""
            <div class='float-container'>
                <div><b>Processing URLs: {progress_data["processed_count"]}/{total_urls}</b></div>
                <div>Running {len(progress_data["current_urls"])}/{concurrency_limit} concurrent tasks</div>
                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <div style="color: #8affa2;">✅ Success: {progress_data["successful_crawls"]}</div>
                    <div style="color: #ff9090;">❌ Failed: {progress_data["failed_crawls"]}</div>
                </div>
            </div>
            """
            float_container.markdown(float_html, unsafe_allow_html=True)

            # Update URL statuses
            url_list_html = "<div style='max-height: 400px; overflow-y: auto; background-color: #1e1e1e; border-radius: 8px; padding: 10px;'>"
            for i, url in enumerate(urls):
                status = progress_data["url_statuses"][i]

                if status == "pending":
                    status_icon = f'<span class="url-status-icon" style="color: #a0a0a0;">⏳</span>'
                    class_name = "url-card"
                elif status == "processing":
                    status_icon = f'<span class="url-status-icon" style="color: #3498db;">🔄</span>'
                    class_name = "url-card url-processing"
                elif status == "success":
                    status_icon = f'<span class="url-status-icon" style="color: #8affa2;">✅</span>'
                    class_name = "url-card url-success"
                else:  # error
                    status_icon = f'<span class="url-status-icon" style="color: #ff9090;">❌</span>'
                    class_name = "url-card url-error"

                url_list_html += f"""<div id='url-{i}' class='{class_name}'>
                    <span class='url-count'>{i+1}</span>
                    {status_icon}
                    <span style="word-break: break-all;">{url}</span>
                </div>"""
            url_list_html += "</div>"
            url_status_area.markdown(url_list_html, unsafe_allow_html=True)

            # Update content area
            if progress_data["current_content"]:
                content_area.markdown(
                    progress_data["current_content"], unsafe_allow_html=True)

            await asyncio.sleep(0.5)  # Update UI every 0.5 seconds

    # Run UI updater in parallel with tasks
    ui_task = asyncio.create_task(update_ui())

    # Wait for all URL processing tasks to complete
    await asyncio.gather(*tasks)

    # Set progress to 100%
    progress_data["progress"] = 1.0
    progress_bar.progress(1.0)

    # Cancel the UI updater
    ui_task.cancel()

    # Final UI update
    status_html = f"""
    <div class='progress-card'>
        <h3>✅ Crawling Complete!</h3>
        <p>Processed {total_urls} URLs</p>
        <div style='display: flex; gap: 20px; margin-top: 10px;'>
            <div style="color: #8affa2;">✅ Success: {progress_data["successful_crawls"]}</div>
            <div style="color: #ff9090;">❌ Failed: {progress_data["failed_crawls"]}</div>
        </div>
    </div>
    """
    status_text.markdown(status_html, unsafe_allow_html=True)

    # Remove floating status
    float_container.empty()

    # Combine all content with proper formatting
    combined_content = "\n".join(progress_data["results"])

    # Add metadata at the top of the file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metadata = f"""# Web Crawler Results
Generated on: {timestamp}
Crawl method: {crawl_method}

Total URLs processed: {total_urls}
- ✅ Successful: {progress_data["successful_crawls"]}
- ❌ Failed: {progress_data["failed_crawls"]}

---

"""
    final_content = metadata + combined_content

    # Add download button at the top via placeholder
    filename = f"crawl_results_{crawl_method}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    download_html = f'''
    <div style="background-color: #1e1e1e; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #4CAF50;">
        <h3 style="color: #8affa2; margin-top: 0;">📥 Download Results</h3>
        <p style="color: #e0e0e0; margin-bottom: 10px;">
            Crawling completed at: {timestamp}<br>
            Method: {crawl_method}<br>
            Total URLs: {total_urls}, <span style="color: #8affa2;">Successful: {progress_data["successful_crawls"]}</span>, <span style="color: #ff9090;">Failed: {progress_data["failed_crawls"]}</span>
        </p>
    </div>
    '''
    download_placeholder.markdown(download_html, unsafe_allow_html=True)

    download_placeholder.download_button(
        label="📥 Download as Markdown",
        data=final_content,
        file_name=filename,
        mime="text/markdown",
        help="Download the complete crawl results as a Markdown file"
    )

    return final_content


async def crawl_sitemap(sitemap_url, extraction_config=None, concurrency_limit=5, crawl_method="hybrid"):
    """Crawl all URLs found in the sitemap and write full markdown content to a file."""
    with st.spinner('🔍 Fetching sitemap...'):
        urls = await fetch_sitemap(sitemap_url)
        st.success(f"📋 Found {len(urls)} URLs in sitemap")
    await crawl_list_of_urls(urls, extraction_config=extraction_config, concurrency_limit=concurrency_limit, crawl_method=crawl_method)


async def crawl_using_query(query, extraction_config=None, concurrency_limit=5, num_results=10, crawl_method="hybrid"):
    """Perform a Google search using the provided query and crawl the resulting URLs."""
    with st.spinner('🔍 Searching Google...'):
        urls = get_urls_from_google(query, num_results=num_results)
        if urls:
            st.success(f"🎯 Found {len(urls)} search results")
        else:
            st.warning("No search results found")
    await crawl_list_of_urls(urls, extraction_config=extraction_config, concurrency_limit=concurrency_limit, crawl_method=crawl_method)


def markdown_to_html(markdown_content):
    """Convert markdown to HTML using Python-Markdown or a fallback method."""
    try:
        # Try to import markdown module
        try:
            import markdown
            html = markdown.markdown(markdown_content, extensions=[
                'fenced_code', 'tables', 'codehilite'])
        except ImportError:
            # Fallback to a simple conversion if markdown module is not available
            html = "<pre>" + \
                markdown_content.replace("<", "&lt;").replace(
                    ">", "&gt;") + "</pre>"
            st.warning(
                "📝 Python-Markdown module not installed. Using simple HTML conversion.")

        # Add some basic styling
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Web Crawler Results</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                pre {{
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                code {{ font-family: Consolas, Monaco, "Andale Mono", monospace; }}
                h1, h2, h3, h4, h5, h6 {{ margin-top: 1.5em; margin-bottom: 0.5em; }}
                h1 {{ font-size: 2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
                h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
                a {{ color: #0366d6; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                img {{ max-width: 100%; }}
                blockquote {{
                    margin-left: 0;
                    padding-left: 1em;
                    border-left: 4px solid #ddd;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
    except Exception as e:
        return f"<html><body>Error converting to HTML: {str(e)}</body></html>"


def fetch_with_requests(url, timeout=30):
    """Fetch URL using the requests library."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Handle encoding issues
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            # If encoding is not detected or set to ISO-8859-1 (requests' default fallback),
            # use apparent_encoding which is more reliable
            response.encoding = response.apparent_encoding

        # Clean HTML content before returning
        html_content = response.text

        # Remove null bytes and other problematic characters
        html_content = html_content.replace('\x00', '')

        # Return cleaned HTML
        return html_content, response.headers.get('Content-Type', '')
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        raise


def main():
    check_environment()

    # App header with logo
    st.title("🕷️ Web Crawler App")

    # Create a tab-based interface for different crawling modes
    tabs = st.tabs(["Crawl URL", "Settings", "About"])

    with tabs[0]:
        # Main input area
        st.markdown("### Enter URL or Search Query")

        # Input form
        with st.form(key="crawl_form"):
            input_text = st.text_input(
                "URL or search query:",
                placeholder="Enter website URL, sitemap URL (.xml), or search query",
                help="For sitemaps, make sure the URL ends with .xml"
            )

            # Input type selection with radio buttons
            input_type = st.radio(
                "Input type:",
                ["🌐 Webpage URL", "📑 Sitemap URL", "🔍 Search Query"],
                horizontal=True,
                help="Select the type of input you're providing"
            )

            # Crawl method selection - NEW
            crawl_method = st.radio(
                "Crawl method:",
                ["🔄 Hybrid (Best for Work Proxy)", "🌐 Requests Only",
                 "🔍 Crawl4AI HTTP", "⚡ Crawl4AI Raw HTML"],
                horizontal=True,
                help="Select how to fetch and process the content"
            )

            # Basic settings right in the form
            col1, col2, col3 = st.columns(3)
            with col1:
                concurrency_limit = st.slider(
                    "Concurrent requests",
                    1, 20, 5,
                    help="How many URLs to process simultaneously"
                )
            with col2:
                wait_time = st.slider(
                    "Wait time (seconds)",
                    0, 10, 3,
                    help="Add delay between requests to avoid rate limiting"
                )
            with col3:
                max_results = st.slider(
                    "Max search results",
                    5, 30, 10,
                    help="Maximum number of results to fetch from search"
                )

            # Submit button
            submit_button = st.form_submit_button(
                label="🚀 Start Crawling",
                type="primary",
                use_container_width=True
            )

    with tabs[1]:
        # Settings tab
        st.markdown("### Content Extraction Settings")

        # Core settings card
        with st.container():
            st.markdown("#### Core Settings")

            # First row of settings
            col1, col2 = st.columns(2)
            with col1:
                prioritize_code_blocks = st.checkbox("Prioritize code blocks", value=True,
                                                     help="Ensures code blocks are properly preserved in markdown output")
            with col2:
                respect_robots = st.checkbox("Respect robots.txt", value=True,
                                             help="Follow robots.txt rules when crawling")

            # Content type radio selector
            prioritize_content_type = st.radio(
                "Content optimization:",
                ["Technical Documentation", "Article/Blog", "General"],
                horizontal=True,
                help="Optimizes extraction for different types of content"
            )

            # Performance settings
            st.markdown("#### Performance Settings")
            col1, col2 = st.columns(2)
            with col1:
                concurrency_setting = st.slider(
                    "Concurrent URL limit",
                    1, 20, 5,
                    help="Number of URLs to process simultaneously (higher values may increase speed but risk rate limiting)"
                )
            with col2:
                timeout_setting = st.slider(
                    "Request timeout (seconds)",
                    5, 60, 30,
                    help="Maximum time to wait for a response"
                )

            # Advanced settings
            with st.expander("Advanced Settings", expanded=False):
                # First row
                col1, col2 = st.columns(2)
                with col1:
                    retry_count = st.slider("Retry count", 0, 5, 2,
                                            help="Number of times to retry failed requests")
                with col2:
                    extract_full_page = st.checkbox("Extract full page", value=True,
                                                    help="Include all page content, not just main section")

                # User agent selection
                user_agent_option = st.radio(
                    "User Agent:",
                    ["Random (recommended)", "Custom"],
                    horizontal=True
                )

                if user_agent_option == "Custom":
                    selected_agent = st.selectbox(
                        "Select User Agent", USER_AGENTS)

                # Custom CSS selectors for advanced users
                # Custom CSS selectors for advanced users
                custom_selectors = st.text_area(
                    "Additional CSS selectors to extract (comma-separated)",
                    placeholder=".article-content, .code-block, .my-custom-class",
                    help="For advanced users: target specific page elements"
                )

                # Proxy settings
                use_proxy = st.checkbox("Use proxy", value=False,
                                        help="Use a proxy server (useful for bypassing rate limits)")
                if use_proxy:
                    proxy_url = st.text_input(
                        "Proxy URL",
                        placeholder="http://proxy.example.com:8080",
                        help="Format: http://hostname:port or http://username:password@hostname:port"
                    )

    with tabs[2]:
        # About tab
        st.markdown("""
        # 🕷️ Web Crawler

        A powerful web crawler that can handle corporate proxies and generate high-quality markdown from web pages.

        ## Features
        - **Proxy-friendly** using requests library
        - **High-fidelity conversion** using Crawl4AI
        - **Concurrent crawling** for faster processing
        - **Multiple crawling methods** to handle different scenarios
        - **Progress tracking** with real-time updates
        - **Error handling** with detailed feedback
        - **Markdown output** with clean formatting

        ## How to Use
        1. Enter URLs (one per line)
        2. Choose crawling method:
           - **Hybrid (Recommended)**: Uses requests + Crawl4AI for best results
           - **Requests Only**: Basic HTML to markdown conversion
           - **Crawl4AI HTTP**: Uses Crawl4AI's HTTP strategy
           - **Crawl4AI Raw HTML**: Uses requests to fetch, then Crawl4AI to process
        3. Configure extraction settings
        4. Click "Start Crawling"

        Built with Streamlit, Beautiful Soup, and Crawl4AI for high-quality content extraction.
        """, unsafe_allow_html=True)

    # Get settings for crawling
    extraction_config = {
        "prioritize_code_blocks": prioritize_code_blocks if 'prioritize_code_blocks' in locals() else True,
        "content_type": prioritize_content_type if 'prioritize_content_type' in locals() else "Technical Documentation",
        "extract_full_page": extract_full_page if 'extract_full_page' in locals() else True,
        "custom_selectors": [s.strip() for s in custom_selectors.split(',')] if 'custom_selectors' in locals() and custom_selectors else []
    }

    # Use concurrency setting from either the form or the settings tab
    actual_concurrency = concurrency_limit if 'submit_button' in locals(
    ) and submit_button else concurrency_setting if 'concurrency_setting' in locals() else 5

    # Map the crawl method selection to the proper method string
    method_mapping = {
        "🔄 Hybrid (Best for Work Proxy)": "hybrid",
        "🌐 Requests Only": "requests_only",
        "🔍 Crawl4AI HTTP": "crawl4ai_http",
        "⚡ Crawl4AI Raw HTML": "crawl4ai_raw_html"
    }

    actual_method = method_mapping.get(
        crawl_method, "hybrid") if 'crawl_method' in locals() else "hybrid"

    # Process the input if form is submitted
    if 'submit_button' in locals() and submit_button:
        if input_text:
            if input_type == "📑 Sitemap URL" or input_text.lower().endswith(".xml"):
                st.info("🔄 Processing sitemap...")
                asyncio.run(crawl_sitemap(
                    input_text, extraction_config=extraction_config, concurrency_limit=actual_concurrency, crawl_method=actual_method))
            elif input_type == "🌐 Webpage URL" or is_valid_url(input_text):
                st.info("🔄 Processing URL...")
                asyncio.run(crawl_list_of_urls(
                    [input_text], wait_time=wait_time, extraction_config=extraction_config, concurrency_limit=actual_concurrency, crawl_method=actual_method))
            else:
                st.info("🔄 Processing search query...")
                asyncio.run(crawl_using_query(
                    input_text, extraction_config=extraction_config, concurrency_limit=actual_concurrency, num_results=max_results, crawl_method=actual_method))
        else:
            st.warning("⚠️ Please enter a URL or search query.")


if __name__ == "__main__":
    main()
