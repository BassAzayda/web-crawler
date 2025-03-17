# Web Crawler Streamlit App

A web crawling application built with Streamlit that allows you to extract content from websites in markdown format. This app supports crawling individual URLs, sitemaps, and search engine results.

## Features

- **Multiple Input Options**:
  - Crawl a single webpage URL
  - Process an entire sitemap
  - Perform a Google search and crawl the results

- **Content Extraction**:
  - Extracts LLM-friendly markdown when available
  - Falls back to regular markdown or HTML content
  - Preserves metadata like titles and descriptions

- **User Interface**:
  - Interactive Streamlit dashboard
  - Progress tracking for crawl operations
  - Expandable result previews
  - Export functionality to save results

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/web-crawler-app.git
   cd web-crawler-app
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up crawl4ai resources:
   ```bash
   crawl4ai-setup
   ```

## Usage

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Use the sidebar to configure your crawl:
   - Select input type (Single URL, Sitemap URL, or Google Search Query)
   - Enter the URL or query
   - Adjust the number of results to crawl
   - Click "Start Crawling"

4. View and export results:
   - Browse through the crawled content in the expandable sections
   - Export results to a markdown file using the export button

## Deployment

You can deploy this app to Streamlit Sharing for free by following these steps:

1. Push your code to GitHub
2. Visit [Streamlit Sharing](https://share.streamlit.io/) and sign in
3. Create a new app and connect it to your GitHub repository
4. Configure deployment settings and deploy

## Acknowledgments

This application uses the following libraries:
- Streamlit for the web interface
- crawl4ai for web crawling functionality
- googlesearch-python for search capabilities

## License

MIT