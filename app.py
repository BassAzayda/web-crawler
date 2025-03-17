# ChatGPT

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
    """Process a crawl result and return formatted output for Streamlit."""
    output = []
    output.append(f"Successfully crawled: {result.url}")

    if hasattr(result, 'status_code') and result.status_code:
        output.append(f"Status Code: {result.status_code}")
    if hasattr(result, 'metadata') and result.metadata:
        title = result.metadata.get('title', 'No title')
        output.append(f"Title: {title}")
        description = result.metadata.get('description')
        if description:
            preview_desc = description if len(
                description) <= 150 else description[:150] + "..."
            output.append(f"Description: {preview_desc}")

    content = ""
    if hasattr(result, 'markdown') and result.markdown:
        if hasattr(result.markdown, 'fit_markdown') and result.markdown.fit_markdown:
            content = result.markdown.fit_markdown
            output.append(
                f"\nLLM-friendly Markdown (length: {len(content)} chars)")
        elif isinstance(result.markdown, str):
            content = result.markdown
            output.append(f"\nMarkdown (length: {len(content)} chars)")
    elif hasattr(result, 'html') and result.html:
        output.append(f"\nHTML content length: {len(result.html)} chars")
        content = result.html
    else:
        output.append("No content available.")

    return "\n".join(output), content


async def fetch_sitemap(url):
    """Fetch and parse sitemap XML to extract all URLs."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            xml_text = await response.text()
            root = ET.fromstring(xml_text)
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            return [elem.text for elem in root.findall("ns:url/ns:loc", ns)]


async def crawl_list_of_urls(urls, combined_markdown_output="", write_to_file=False):
    """Crawl a list of URLs using common settings and append full markdown content."""
    st.write(f"URLs to crawl: {urls}")

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
        content_filter=PruningContentFilter(
            threshold=0.2, threshold_type="fixed")
    )

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

    progress_bar = st.progress(0)
    status_text = st.empty()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(urls, config=run_conf)
        for idx, result in enumerate(results):
            progress = (idx + 1) / len(results)
            progress_bar.progress(progress)
            status_text.text(f"Processing URL {idx + 1} of {len(results)}")

            if result.success:
                output, content = await process_result(result)
                st.write(output)
                combined_markdown_output += f"\n\n<!-- URL: {result.url} -->\n\n" + content
            else:
                st.error(
                    f"Failed to crawl {result.url}: {result.error_message}")

    if write_to_file:
        output_filename = "sitemap_output.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(combined_markdown_output)
        st.success(f"Combined markdown written to {output_filename}")

    return combined_markdown_output


async def crawl_sitemap(sitemap_url):
    """Crawl all URLs found in the sitemap and write full markdown content to a file."""
    urls = await fetch_sitemap(sitemap_url)
    st.write(f"Found {len(urls)} URLs in sitemap.")
    await crawl_list_of_urls(urls, write_to_file=True)


async def crawl_using_query(query):
    """Perform a Google search using the provided query and crawl the resulting URLs."""
    with st.spinner('Searching Google...'):
        urls = get_urls_from_google(query, num_results=10)
    await crawl_list_of_urls(urls)


def main():
    st.title("Web Crawler App")
    st.write("Enter a sitemap URL, webpage URL, or search query to start crawling.")

    input_text = st.text_input(
        "Enter URL or search query:", "https://docs.crawl4ai.com/sitemap.xml")

    if st.button("Start Crawling"):
        if input_text:
            if input_text.lower().endswith(".xml"):
                st.info(f"Processing sitemap: {input_text}")
                asyncio.run(crawl_sitemap(input_text))
            else:
                if is_valid_url(input_text):
                    st.info(f"Processing URL: {input_text}")
                    asyncio.run(crawl_list_of_urls([input_text]))
                else:
                    st.info(f"Processing search query: {input_text}")
                    asyncio.run(crawl_using_query(input_text))
        else:
            st.warning("Please enter a URL or search query.")


if __name__ == "__main__":
    main()
