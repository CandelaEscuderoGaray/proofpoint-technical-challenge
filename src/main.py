import csv
from datetime import datetime

# Function to read the csv file and return a list of rows
def read_csv(file_path):
    rows = []

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            rows.append(row)

    return rows


#Funtion to normalized a string, remove leading and trailing spaces, convert to lowercase and 
# replace multiple spaces with a single space
def normalize_string(value):
    value = value.strip().lower()
    value = " ".join(value.split())
    return value


#Function to parse a number, if the value is not a valid number or is negative, return 0
def parse_number(value):
    try:
        number = int(value)
        if number < 0:
            return 0
        return number
    except ValueError:
        return 0


#Function to parse the tittle, if the tittle is empty, return "Untitled Episode"
def parse_tittle(value):
    tittle = value.strip()

    if tittle == "":
        return "Untitled Episode"
    return tittle


#Function to parse the date, if the date is not in the format "YYYY-MM-DD", return "Unknown"
def parse_date(value):
    date = value.strip()
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return date
    except ValueError:
        return "Unknown"

#Function to calculate the priority of an episode, the higher the priority, the more complete the information is
def priority(ep):

    air_date_score = 1 if ep["Air Date"] != "Unknown" else 0
    title_score = 1 if ep["Episode Title"] != "Untitled Episode" else 0

    season_score = 1 if ep["Season Number"] > 0 else 0
    episode_score = 1 if ep["Episode Number"] > 0 else 0

    return (
        air_date_score,
        title_score,
        season_score,
        episode_score
    )

#Function to generate duplicate keys for an episode, the keys are generated based on the rules provided
def duplicate_keys(ep):

    series = normalize_string(ep["Series Name"])
    tittle = normalize_string(ep["Episode Title"])

    season = ep["Season Number"]
    episode = ep["Episode Number"]

    keys = []

    # Rule 1
    keys.append(("A", series, season, episode))

    # Rule 2
    keys.append(("B", series, 0, episode, tittle))

    # Rule 3
    keys.append(("C", series, season, 0, tittle))

    return keys


#Function to check for duplicate episodes, if there are duplicate episodes, return a the "best" episode,
# which is the one with the most complete information (not "Unknown" or "Untitled Episode")
#if there are multiple episodes with the same information, return the first one found
def deduplicate(episodes):

    unique = {}
    key_map = {}

    for episode in episodes:

        keys = duplicate_keys(episode)

        found_episode = None

        for key in keys:
            if key in key_map:
                found_episode = key_map[key]
                break

        if found_episode is None:
            unique[id(episode)] = episode

            for key in keys:
                key_map[key] = episode

        else:
            existing = found_episode

            if priority(episode) > priority(existing):

                for key in duplicate_keys(existing):
                    key_map.pop(key, None)

                for key in keys:
                    key_map[key] = episode

                unique[id(episode)] = episode
                unique.pop(id(existing), None)

    return list(unique.values())

#Function to normalized a row 
def normalize_row(row):

    seriesName = normalize_string(row["Series Name"])

    #if series name is empty, discard the row
    if seriesName == "":
        return None
    
    season = parse_number(row["Season Number"])
    episode = parse_number(row["Episode Number"])
    tittle = parse_tittle(row["Episode Title"])
    air_date = parse_date(row["Air Date"])

    if episode == 0 and tittle == "Untitled Episode" and air_date == "Unknown":
        return None

    return {
        "Series Name": seriesName,
        "Season Number": season,
        "Episode Number": episode,
        "Episode Title": tittle,
        "Air Date": air_date
    }

#Function to write the clean data to a new csv file
def write_clean_csv(episodes, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Series Name", 
            "Season Number", 
            "Episode Number", 
            "Episode Title", 
            "Air Date"
            ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for episode in episodes:
            writer.writerow({
                "Series Name": episode["Series Name"],
                "Season Number": episode["Season Number"],
                "Episode Number": episode["Episode Number"],
                "Episode Title": episode["Episode Title"],
                "Air Date": episode["Air Date"]
            })


def write_report(
    input_records,
    output_records,
    discarded,
    corrected,
    duplicates,
    output_path
):

    with open(output_path, "w", encoding="utf-8") as f:

        f.write("# Data Quality Report\n\n")

        f.write(f"Total input records: {input_records}\n")
        f.write(f"Total output records: {output_records}\n")
        f.write(f"Discarded entries: {discarded}\n")
        f.write(f"Corrected entries: {corrected}\n")
        f.write(f"Duplicates detected: {duplicates}\n\n")

        f.write("## Deduplication Strategy\n\n")
        f.write(
            "Episodes are considered duplicates based on normalized "
            "Series Name combined with Season Number, Episode Number "
            "or Episode Title when one of the numbers is missing.\n\n"
        )

        f.write(
            "When duplicates are detected, the record with the highest "
            "priority is kept using the following order:\n\n"
        )

        f.write("- Valid Air Date over 'Unknown'\n")
        f.write("- Known Episode Title over 'Untitled Episode'\n")
        f.write("- Valid Season and Episode numbers\n")
        f.write("- If still tied, keep the first record encountered\n")



def main():
    input_path = "data/episodes.csv"

    rows = read_csv(input_path)

    input_count = len(rows)

    normalize_rows = []

    discarded = 0

    # Normalize the data and discard invalid rows
    for row in rows:
        normalized = normalize_row(row)

        if normalized is not None:
            normalize_rows.append(normalized)
        else:
            discarded += 1
    
    before_deduplication = len(normalize_rows)
    # Deduplicate the rows based on the rules provided
    normalize_rows = deduplicate(normalize_rows)

    duplicates = before_deduplication - len(normalize_rows)

    # Sort the rows by Series Name, Season Number and Episode Number
    normalize_rows.sort(key=lambda x: (
        x["Series Name"], 
        x["Season Number"], 
        x["Episode Number"]
            )
        )  
    
    print("Valid rows:", len(normalize_rows))

    for row in normalize_rows:
        print(row)

    # Save the clean data to a new csv file
    output_csv = "../output/episodes_clean.csv"

    write_clean_csv(normalize_rows, output_csv)
    # Generate the report
    write_report(
        input_records=input_count,
        output_records=len(normalize_rows),
        discarded=discarded,
        corrected=input_count - discarded - duplicates,
        duplicates=duplicates,
        output_path="../output/report.md"
    )


if __name__ == "__main__":
    main()