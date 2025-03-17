# Web Crawler App

A Streamlit-based web crawler application that can:
- Crawl websites from a sitemap URL
- Crawl individual web pages
- Search Google and crawl the results

## Features

- Support for sitemap.xml parsing
- Google search integration
- Markdown content generation
- Progress tracking
- User-friendly interface
- Rotating user agents for better crawling

## Installation

1. Clone this repository:
```bash
git clone <your-repository-url>
cd web-crawler
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Install Chrome/Chromium (required for crawl4ai):
```bash
crawl4ai-setup
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Enter one of the following in the input field:
   - A sitemap URL (ending in .xml)
   - A webpage URL
   - A search query

4. Click "Start Crawling" and watch the results appear!

## Notes

- The app uses async operations for efficient crawling
- Progress is shown in real-time
- Results can be saved to a markdown file
- Respects robots.txt and implements polite crawling

## License

MIT License

## Contributing

Feel free to open issues or submit pull requests!