import yaml
import pandas as pd
from datetime import datetime

# YAML file path
yaml_file = "banners.yaml"

# Load YAML data
with open(yaml_file, "r") as file:
    data = yaml.safe_load(file)

# Extract five-star characters only
five_star_characters = data.get("fiveStarCharacters", [])

# Prepare data for DataFrame
banner_data = []

for character in five_star_characters:
    name = character.get("name", "")
    versions = character.get("versions", [])
    dates = character.get("dates", [])
    
    for i, date in enumerate(dates):
        start_date_str = date.get("start")
        end_date_str = date.get("end")
        
        # Split version into version_no and phase_no
        if i < len(versions):
            version_parts = versions[i].split(".")
            version_no = f"{version_parts[0]}.{version_parts[1]}"  # Main version (e.g., 1.0)
            phase_no = int(version_parts[2]) if len(version_parts) > 2 else 1  # Phase number (default to 1 if missing)
        else:
            version_no = "0.0"
            phase_no = 1

        if start_date_str and end_date_str:
            # Convert date strings to datetime objects
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        else:
            print(f"⚠️ Missing date for {name} in version {versions[i] if i < len(versions) else 'Unknown'}")
            continue  # Skip to the next entry if dates are missing

        # Calculate duration in days
        duration_days = (end_date - start_date).days

        # Append processed data
        banner_data.append([
            name,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            duration_days,
            version_no,
            phase_no
        ])

# Create a DataFrame
Genshin_Banner = pd.DataFrame(banner_data, columns=["Character", "Start_Date", "End_Date", "Duration_Days", "version_no", "phase_no"])

# Ensure date columns are in datetime format
Genshin_Banner['Start_Date'] = pd.to_datetime(Genshin_Banner['Start_Date'])
Genshin_Banner['End_Date'] = pd.to_datetime(Genshin_Banner['End_Date'])

# Add ReleaseOrder column
Genshin_Banner['ReleaseOrder'] = range(1, len(Genshin_Banner) + 1)

# Create new columns for DaysSinceLastRerun and IsRerun
Genshin_Banner['DaysSinceLastRerun'] = None
Genshin_Banner['IsRerun'] = 0  # Initialize as 0 for first-time appearances

# Calculate DaysSinceLastRerun and IsRerun
for character in Genshin_Banner['Character'].unique():
    character_banners = Genshin_Banner[Genshin_Banner['Character'] == character].sort_values(by='Start_Date')
    
    previous_date = None
    for index, row in character_banners.iterrows():
        if previous_date is not None:
            # Calculate days since last rerun
            days_diff = (row['Start_Date'] - previous_date).days
            Genshin_Banner.at[index, 'DaysSinceLastRerun'] = days_diff
            Genshin_Banner.at[index, 'IsRerun'] = 1  # Set as 1 for reruns
        else:
            # First appearance, no rerun yet
            Genshin_Banner.at[index, 'DaysSinceLastRerun'] = 0
            Genshin_Banner.at[index, 'IsRerun'] = 0  # Keep as 0 for first-time appearances
        
        previous_date = row['Start_Date']

# Fill NaN values in DaysSinceLastRerun with 0 and convert to integer type
Genshin_Banner['DaysSinceLastRerun'] = Genshin_Banner['DaysSinceLastRerun'].fillna(0).astype(int)

# Save updated DataFrame to CSV
csv_filename = "genshin_banner_history.csv"
Genshin_Banner.to_csv(csv_filename, index=False, encoding="utf-8")

print(f"✅ Banner data successfully extracted from YAML and saved to {csv_filename}!")
