# HomeFinder - Real Estate Property Scraper

HomeFinder is a web scraping application designed to find homes for sale at specific price points and locations. It extracts property information from multiple real estate websites and allows you to filter, view, and export the results.

## Features

- Search for properties on multiple real estate websites (Zillow, Realtor.com, Redfin)
- Filter by location, price range, number of bedrooms, and bathrooms
- Store property data in a local SQLite database
- Export results to CSV or JSON formats
- Customizable search parameters
- Web interface for easy searching

## Requirements

- Python 3.7 or higher
- Chrome browser (for Selenium-based scrapers)
- Internet connection

## Installation

1. Clone this repository or download the files to your computer.

2. Navigate to the project directory:
   ```
   cd homefinder
   ```

3. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

4. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

Use the included run script to quickly get started:

- Windows: `run.bat`
- macOS/Linux: `./run.sh` (you may need to make it executable with `chmod +x run.sh`)

This script will:
1. Set up a virtual environment
2. Install dependencies
3. Prompt you to choose between:
   - Command-line interface
   - Web interface

### Command-Line Interface

Run the application with default settings:

```
python app.py
```

This will search for properties in Denver, CO with any price range using all available sources.

### Web Interface

Start the web interface with:

```
python web_app.py
```

Then open your browser and navigate to http://localhost:5000

### Customizing Your Search

Specify a location and price range:

```
python app.py --location "New York, NY" --min-price 500000 --max-price 1000000
```

Choose specific sources to scrape:

```
python app.py --sources "zillow,realtor"
```

Filter by bedrooms and bathrooms:

```
python app.py --filter-beds 3 --filter-baths 2
```

Limit the number of results:

```
python app.py --limit 10
```

### Exporting Results

Export results to CSV:

```
python app.py --export csv --output my_properties
```

Export results to JSON:

```
python app.py --export json --output my_properties
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--location` | Location to search for properties | Denver, CO |
| `--min-price` | Minimum property price | 0 |
| `--max-price` | Maximum property price | 1000000 |
| `--sources` | Comma-separated list of sources to scrape | zillow,realtor,redfin |
| `--export` | Export format (csv or json) | None |
| `--output` | Output filename (without extension) | properties |
| `--filter-beds` | Minimum number of bedrooms | None |
| `--filter-baths` | Minimum number of bathrooms | None |
| `--limit` | Limit the number of displayed results | None |

## Deployment

### GitHub

To push the application to GitHub:

1. Run the included setup script:
   - Windows: `setup_github.bat`
   - macOS/Linux: `./setup_github.sh` (you may need to make it executable with `chmod +x setup_github.sh`)

2. When prompted, enter your GitHub credentials or personal access token.

### Web Hosting

#### Heroku

1. Create a Heroku account if you don't have one
2. Install the Heroku CLI
3. Login to Heroku: `heroku login`
4. Create a new Heroku app: `heroku create your-app-name`
5. Push to Heroku: `git push heroku main`

#### PythonAnywhere

1. Sign up for a PythonAnywhere account
2. From the Dashboard, select "Web" tab and then "Add a new web app"
3. Follow the wizard, selecting "Flask" as your web framework
4. Set up a Git repository: 
   ```
   cd ~/mysite
   git clone https://github.com/trevden810/homefinder.git
   ```
5. Configure your web app to point to the Flask application in `web_app.py`

#### Azure App Service

1. Create an Azure account if you don't have one
2. Install Azure CLI: `az login`
3. Create a resource group: `az group create --name myResourceGroup --location eastus`
4. Create App Service plan: `az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku B1 --is-linux`
5. Create web app: `az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name your-app-name --runtime "PYTHON|3.8" --deployment-local-git`
6. Deploy your app: `git push azure main`

## Database

Property data is stored in a SQLite database located at `database/properties.db`. You can access this database using any SQLite client to perform custom queries.

## Extending the Application

### Adding New Sources

To add a new property source:

1. Create a new scraper class in the `scrapers` directory, inheriting from `BaseScraper`.
2. Implement the `search` method to extract property data.
3. Add the new source to the list of available sources in `app.py`.

### Customizing Property Data

To modify the property data model:

1. Update the `Property` class in `models/property.py`.
2. Update the database schema in `database/db_handler.py`.
3. Update the scraper classes to extract the new data fields.

## Troubleshooting

### Common Issues

- **Selenium driver issues**: Make sure you have Chrome installed and up to date.
- **Rate limiting**: If you're getting blocked by websites, try increasing the `REQUEST_DELAY` in `config/settings.py`.
- **Parsing errors**: Website layouts may change over time. Check the scraper implementation and update CSS selectors if needed.
- **Deployment issues**: For web hosting, ensure the web server can access Chrome for Selenium-based scraping.

## Legal Considerations

This application is for educational purposes only. Be aware that web scraping may violate the terms of service of some websites. Always review the terms of service for each website before scraping their content.
