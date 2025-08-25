import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouMathTableScraper:
    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def fetch_page(self) -> Optional[BeautifulSoup]:
        """Fetch the webpage and return BeautifulSoup object"""
        try:
            logger.info(f"Fetching page: {self.url}")
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("Page fetched successfully")
            return soup
            
        except requests.RequestException as e:
            logger.error(f"Error fetching page: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def extract_tables(self, soup: BeautifulSoup) -> List[pd.DataFrame]:
        """Extract all tables from the page and convert to pandas DataFrames"""
        tables = []
        
        # Find all table elements
        table_elements = soup.find_all('table')
        logger.info(f"Found {len(table_elements)} tables on the page")
        
        for i, table in enumerate(table_elements):
            try:
                # Extract table data
                table_data = []
                rows = table.find_all('tr')
                
                for row in rows:
                    # Extract cells from each row
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    
                    if row_data:  # Only add non-empty rows
                        table_data.append(row_data)
                
                if table_data:
                    # Create DataFrame
                    df = pd.DataFrame(table_data)
                    
                    # Set first row as header if it looks like headers
                    if len(df) > 1:
                        # Check if first row contains header-like text
                        first_row = df.iloc[0].astype(str)
                        if any('peso' in str(cell).lower() or 'pesa' in str(cell).lower() or 
                               'grammi' in str(cell).lower() or 'kg' in str(cell).lower() 
                               for cell in first_row):
                            df.columns = df.iloc[0]
                            df = df.iloc[1:].reset_index(drop=True)
                    
                    # Clean up the DataFrame
                    df = df.dropna(how='all')  # Remove completely empty rows
                    df = df.replace('', pd.NA)  # Replace empty strings with NA
                    
                    tables.append(df)
                    logger.info(f"Table {i+1} extracted with shape: {df.shape}")
                    
            except Exception as e:
                logger.error(f"Error extracting table {i+1}: {e}")
                continue
        
        return tables
    
    def save_tables_to_csv(self, tables: List[pd.DataFrame], base_filename: str = "youmath_tables"):
        """Save all tables to separate CSV files"""
        for i, df in enumerate(tables):
            filename = f"{base_filename}_table_{i+1}.csv"
            try:
                df.to_csv(filename, index=False, encoding='utf-8')
                logger.info(f"Table {i+1} saved to {filename}")
            except Exception as e:
                logger.error(f"Error saving table {i+1}: {e}")
    
    def display_table_summaries(self, tables: List[pd.DataFrame]):
        """Display summary information for all tables"""
        print(f"\n{'='*60}")
        print(f"TABLE EXTRACTION SUMMARY")
        print(f"{'='*60}")
        
        for i, df in enumerate(tables):
            print(f"\nTable {i+1}:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  First few rows:")
            print(df.head().to_string())
            print(f"  {'-'*40}")
    
    def scrape_and_process(self) -> List[pd.DataFrame]:
        """Main method to scrape and process tables"""
        # Fetch the page
        soup = self.fetch_page()
        if not soup:
            logger.error("Failed to fetch page")
            return []
        
        # Extract tables
        tables = self.extract_tables(soup)
        
        if not tables:
            logger.warning("No tables found on the page")
            return []
        
        # Display summaries
        self.display_table_summaries(tables)
        
        # Save to CSV files
        self.save_tables_to_csv(tables)
        
        return tables

def main():
    """Main execution function"""
    # URL from the original file
    url = 'https://www.youmath.it/domande-a-risposte/view/8005-quanto-pesa.html'
    
    # Create scraper instance
    scraper = YouMathTableScraper(url)
    
    # Scrape and process tables
    tables = scraper.scrape_and_process()
    
    if tables:
        print(f"\n✅ Successfully extracted {len(tables)} tables!")
        print(f"📁 Tables saved as CSV files in the current directory")
        
        # Return tables for further processing if needed
        return tables
    else:
        print("❌ No tables were extracted")
        return []

if __name__ == "__main__":
    # Add a small delay to be respectful to the server
    time.sleep(1)
    main()