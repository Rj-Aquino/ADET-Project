import requests
from bs4 import BeautifulSoup
import csv

# URL of the webpage with banner data
URL = "https://www.eurogamer.net/honkai-star-rail-next-banner-current-list-all-history-9321"

# Headers to mimic a browser visit
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# Fetch the page content
response = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(response.text, "html.parser")

# Locate the table
table = soup.find("table")  # Finds the first table on the page
rows = table.find_all("tr")  # Get all rows

# Extract data
banner_data = []
for row in rows[1:]:  # Skip the header row
    cols = row.find_all("td")
    if len(cols) == 4:  # Ensure correct column count
        banner_name = cols[0].text.strip()
        five_star = cols[1].text.strip()
        four_star = cols[2].text.strip()
        banner_dates = cols[3].text.strip()
        
        banner_data.append([banner_name, five_star, four_star, banner_dates])

# Save data to CSV
csv_filename = "hsr_banner_history_eurogamer.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Banner Name", "5-Star Character", "4-Star Characters", "Banner Dates"])
    writer.writerows(banner_data)

print(f"✅ HSR banner data successfully scraped and saved to {csv_filename}!")
