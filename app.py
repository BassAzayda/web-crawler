import streamlit as st
import asyncio
import json
import random
import nest_asyncio
import aiohttp
import xml.etree.ElementTree as ET
from googlesearch import search
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# Apply nest_asyncio for compatibility
nest_asyncio.apply()

# List of realistic user agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
]

def get_urls_from_google(query, num_results=10):
    """Get URLs from Google search results."""
    return [result for result in search(query, num_results=num_results, advanced=False)]

def is_valid_url(url):
    """Check if URL starts with a valid scheme."""
    return url.startswith(("http://", "https://", "file://", "raw:"))

async def process_result(result):
    """
    Process a crawl result:
      - Format the result for display in Streamlit
      - Return the full markdown content (LLM-friendly if available)
    """
    result_info = {
        "url": result.url,
        "status_code": getattr(result, 'status_code', 'N/A'),
        "title": "No title",
        "description": "",
        "content": "",
        "content_length": 0,
        "content_type": "None"
    }
    
    if hasattr(result, 'metadata') and result.metadata:
        result_info["title"] = result.metadata.get('title', 'No title')
        result_info["description"] = result.metadata.get('description', '')
    
    # Prefer LLM-friendly markdown if available
    if hasattr(result, 'markdown') and result.markdown:
        if hasattr(result.markdown, 'fit_markdown') and result.markdown.fit_markdown:
            result_info["content"] = result.markdown.fit_markdown
            result_info["content_type"] = "LLM-friendly Markdown"
        elif isinstance(result.markdown, str):
            result_info["content"] = result.markdown
            result_info["content_type"] = "Markdown"
    elif hasattr(result, 'html') and result.html:
        result_info["content"] = result.html
        result_info["content_type"] = "HTML"
    
    result_info["content_length"] = len(result_info["content"])
    return result_info

async def fetch_sitemap(url):
    """Fetch and parse sitemap XML to extract all URLs."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            xml_text = await response.text()
            root = ET.fromstring(xml_text)
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            return [elem.text for elem in root.findall("ns:url/ns:loc", ns)]

async def crawl_list_of_urls(urls, progress_bar=None):
    """Crawl a list of URLs using common settings and return list of results."""
    browser_config = BrowserConfig(
        headless=True,
        user_agent=random.choice(USER_AGENTS),
        viewport_width=random.randint(1200, 1920),
        viewport_height=random.randint(800, 1080),
        ignore_https_errors=True,
        java_script_enabled=True,
        extra_args=["--disable-blink-features=AutomationControlled"]
    )
    
    md_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.2, threshold_type="fixed")
    )
    
    # Allow up to 10 concurrent crawls
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False,
        simulate_user=True,
        override_navigator=True,
        remove_overlay_elements=True,
        magic=True,
        delay_before_return_html=random.uniform(1.0, 3.0),
        wait_until="networkidle",
        page_timeout=90000,
        mean_delay=1.0,
        max_range=1.0,
        semaphore_count=10,
        markdown_generator=md_generator
    )
    
    processed_results = []
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(urls, config=run_conf)
        
        for i, result in enumerate(results):
            if progress_bar:
                progress_bar.progress((i + 1) / len(results))
                
            if result.success:
                processed_result = await process_result(result)
                processed_results.append(processed_result)
                st.session_state.crawl_results.append(processed_result)
            else:
                st.error(f"Failed to crawl {result.url}: {result.error_message}")
    
    return processed_results

def save_results_to_file(results, filename):
    """Save the crawl results to a markdown file."""
    with open(filename, "w", encoding="utf-8") as f:
        for result in results:
            f.write(f"\n\n## {result['title']}\n\n")
            f.write(f"**URL:** {result['url']}\n\n")
            if result['description']:
                f.write(f"**Description:** {result['description']}\n\n")
            f.write(f"**Content Type:** {result['content_type']}\n\n")
            f.write(result['content'])
            f.write("\n\n---\n\n")
    return filename

# Setup the Streamlit app
st.set_page_config(
    page_title="Web Crawler App",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing results
if 'crawl_results' not in st.session_state:
    st.session_state.crawl_results = []

# App title and description
st.title("🕸️ Web Crawler App")
st.markdown("""
This application helps you crawl websites and extract content in a markdown format.
You can enter a sitemap URL, a single webpage URL, or perform a Google search and crawl the results.
""")

# Sidebar for inputs and controls
with st.sidebar:
    st.header("Crawler Settings")
    
    input_type = st.radio(
        "Select input type:",
        ["Single URL", "Sitemap URL", "Google Search Query"]
    )
    
    if input_type == "Single URL":
        user_input = st.text_input("Enter a URL to crawl:", "https://example.com")
    elif input_type == "Sitemap URL":
        user_input = st.text_input("Enter a sitemap URL:", "https://example.com/sitemap.xml")
    else:  # Google Search Query
        user_input = st.text_input("Enter a search query:", "web crawler python")
    
    num_results = st.slider("Number of results to crawl:", 1, 20, 5)
    
    crawl_button = st.button("Start Crawling")
    
    st.divider()
    
    # Export options
    st.header("Export Options")
    export_filename = st.text_input("Export filename:", "crawl_results.md")
    export_button = st.button("Export Results")
    
    if export_button and st.session_state.crawl_results:
        filename = save_results_to_file(st.session_state.crawl_results, export_filename)
        st.success(f"Results saved to {filename}")
        
    clear_button = st.button("Clear Results")
    if clear_button:
        st.session_state.crawl_results = []
        st.success("Results cleared!")

# Main content area
if crawl_button:
    st.subheader("Crawling in progress...")
    
    # Prepare URLs to crawl based on input type
    urls_to_crawl = []
    
    if input_type == "Single URL" and is_valid_url(user_input):
        urls_to_crawl = [user_input]
        st.info(f"Crawling single URL: {user_input}")
    
    elif input_type == "Sitemap URL" and user_input.lower().endswith(".xml"):
        st.info(f"Fetching URLs from sitemap: {user_input}")
        with st.spinner("Fetching sitemap..."):
            try:
                urls_to_crawl = asyncio.run(fetch_sitemap(user_input))
                st.success(f"Found {len(urls_to_crawl)} URLs in sitemap")
                # Limit the number of URLs to crawl
                urls_to_crawl = urls_to_crawl[:num_results]
            except Exception as e:
                st.error(f"Error fetching sitemap: {str(e)}")
    
    elif input_type == "Google Search Query":
        st.info(f"Performing Google search for: {user_input}")
        with st.spinner("Searching..."):
            try:
                urls_to_crawl = get_urls_from_google(user_input, num_results=num_results)
                st.success(f"Found {len(urls_to_crawl)} URLs from search")
            except Exception as e:
                st.error(f"Error performing search: {str(e)}")
    
    # Perform the crawl if we have URLs
    if urls_to_crawl:
        progress_bar = st.progress(0)
        st.info(f"Crawling {len(urls_to_crawl)} URLs...")
        
        # Run the crawler
        asyncio.run(crawl_list_of_urls(urls_to_crawl, progress_bar))
        progress_bar.progress(1.0)
        st.success(f"Crawling completed! {len(st.session_state.crawl_results)} results available.")

# Display crawl results
if st.session_state.crawl_results:
    st.subheader(f"Crawl Results ({len(st.session_state.crawl_results)} URLs)")
    
    for i, result in enumerate(st.session_state.crawl_results):
        with st.expander(f"{i+1}. {result['title']} ({result['url']})"):
            st.write(f"**URL:** {result['url']}")
            st.write(f"**Status Code:** {result['status_code']}")
            if result['description']:
                st.write(f"**Description:** {result['description']}")
            st.write(f"**Content Type:** {result['content_type']}")
            st.write(f"**Content Length:** {result['content_length']} characters")
            
            tab1, tab2 = st.tabs(["Content Preview", "Full Content"])
            with tab1:
                st.markdown(result['content'][:1000] + ("..." if len(result['content']) > 1000 else ""))
            with tab2:
                st.markdown(result['content'])