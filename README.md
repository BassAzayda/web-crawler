# Web Crawler App

A simple web crawler application built with Streamlit that allows you to:
- Crawl individual web pages
- Process entire sitemaps
- Search Google and crawl the results

## Features

- Backend-only solution using requests (no browser required)
- Converts HTML to clean Markdown
- Supports basic authentication and custom headers
- Handles sitemaps
- Google search integration
- Downloadable results

## Setup

1. Clone this repository
2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   
   Or manually set up:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Enter a URL, sitemap URL, or search query in the input field
2. Configure authentication if needed in the sidebar
3. Adjust crawler settings as needed
4. Click "Start Crawling"
5. View and download the results

## Requirements

See `requirements.txt` for the full list of dependencies.

## License

MIT License

## Contributing

Feel free to open issues or submit pull requests!