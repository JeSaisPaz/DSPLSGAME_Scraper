import json
from openpyxl import Workbook

def read_games_json(filename):
    """Read the JSON file and return the data."""
    with open(filename, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError:
            print("Error reading JSON file.")
            return None

def write_games_to_excel(games_data, output_filename):
    """Write the game information to an Excel file."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Games"

    # Define the headers
    headers = ["MediaFire Link", "Game Name", "Cover URL", "Title ID", "Region"]
    sheet.append(headers)

    # Populate the rows with data
    for link, metadata in games_data["DATA"].items():
        sheet.append([
            link,
            metadata.get("name", "Unknown"),
            metadata.get("cover_url", "N/A"),
            metadata.get("title_id", "N/A"),
            metadata.get("region", "N/A"),
        ])
    
    # Save the workbook to a file
    workbook.save(output_filename)
    print(f"Data successfully written to {output_filename}")

def main():
    filename = "games.json"
    output_filename = "games.xlsx"
    games_data = read_games_json(filename)
    
    if games_data:
        write_games_to_excel(games_data, output_filename)

if __name__ == "__main__":
    main()
