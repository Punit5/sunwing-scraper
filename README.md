# Sunwing Package Scraper & Web App

A modern web application for browsing Sunwing vacation packages with advanced filtering and sorting capabilities.

## Features

- **Live Data Fetching**: Real-time data from Sunwing's API
- **Interactive Web Interface**: Modern, responsive design
- **Advanced Filtering**: Filter by destination, country, star rating, duration, and price range
- **Dynamic Sorting**: Click any column header to sort data
- **Multiple Departure Cities**: Support for Vancouver (YVR) and Toronto (YYZ)
- **Auto-populated Filters**: Filter options dynamically generated from live data

## Quick Start

### Web Application (Deployed on Vercel)
Visit the live application: [https://sunwing-scraper.vercel.app](https://sunwing-scraper.vercel.app)

### Local Development

1. **Install Dependencies**:
   ```bash
   python -m venv myvenv
   source myvenv/bin/activate  # On Windows: myvenv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Web Application Locally**:
   ```bash
   ./myvenv/bin/python app.py
   ```
   Visit: http://localhost:5001

3. **Run Original Script** (generates HTML files):
   ```bash
   ./run_sunwing_deals.sh
   ```

### Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## Usage

### Web Application
1. Open http://localhost:5001 in your browser
2. Select a departure city (YVR or YYZ) from the dropdown
3. Use the filters to narrow down results:
   - **Destination**: Filter by specific destinations
   - **Country**: Filter by country
   - **Star Rating**: Minimum star rating (3+, 4+, 5 stars)
   - **Duration**: Filter by trip duration
   - **Price Range**: Set minimum and maximum price limits
4. Click any column header to sort the results
5. Click "Book" links to go directly to Sunwing's booking page

### Command Line
```bash
# Default: YVR and YYZ
./run_sunwing_deals.sh

# Custom gateways
./myvenv/bin/python sunwing_deals.py --gateways YVR --output-dir ./output
```

## Project Structure

```
sunwing_scraper/
├── app.py                  # Flask web application
├── sunwing_deals.py        # Original scraper script
├── run_sunwing_deals.sh    # Shell script to run scraper
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Web interface template
├── myvenv/                # Virtual environment (excluded from git)
└── *.html                 # Generated HTML files (excluded from git)
```

## API Endpoints

- `GET /` - Web interface
- `GET /api/packages/{gateway}` - JSON API for package data
  - `gateway`: YVR or YYZ

## Dependencies

- **Flask**: Web framework
- **Requests**: HTTP client for API calls
- **Python 3.7+**: Required Python version

## Development

The application fetches data from Sunwing's public API and presents it in a user-friendly format. All filtering and sorting happens client-side for fast, responsive interactions.

## License

This project is for educational purposes only. Please respect Sunwing's terms of service when using their data.