import os
import time
import requests
from typing import List
from bs4 import BeautifulSoup
import pandas as pd

response = requests.get("http://ufcstats.com/statistics/events/completed?page=all")

def extract_event_links(html: str) -> List[str]:
    soup = BeautifulSoup(html, 'html.parser')

    event_links = []
    event_rows = soup.select('tr.b-statistics__table-row')

    for row in event_rows:
        link = row.select_one('a.b-link.b-link_style_black')
        if link:
            event_url = link.get('href')
            if event_url and 'event-details' in event_url:
                event_links.append(event_url)
    return event_links

event_links = extract_event_links(response.content)

event_dict = {
    "Event": ["-"],
    "Date": ["-"],
    "WL": [""],
    "Victory_Result": ["-"],
    "Victory_Method": ["-"],
    "Round": ["-"],
    "Time": ["-"],
    "Weight_Class": ["-"],
    "Winner": ["-"],
    "Title": [0],
    "Fight_Bonus": [0],
    "Perf_Bonus": [0],
    "Sub_Bonus": [0],
    "KO_Bonus": [0]
}

fighter_A_dict = {
    "Fighter_name": ["-"],
    "Fighter_KD": ["-"],
    "Fighter_STR": ["-"],     
    "Fighter_TD": ["-"],
    "Fighter_SUB": ["-"],
}

fighter_B_dict = {
    "Fighter_name": ["-"],
    "Fighter_KD": ["-"],
    "Fighter_STR": ["-"],
    "Fighter_TD": ["-"],
    "Fighter_SUB": ["-"]
}

fight_data = pd.DataFrame(event_dict)
A_data = pd.DataFrame(fighter_A_dict)
B_data = pd.DataFrame(fighter_B_dict)

rc = 0

RUN_LIMIT = 20  # Limit number of events to scrape for testing

for i in range(min(len(event_links), RUN_LIMIT)):
    url = event_links[i]
    print(f"Processing event {i+1}/{min(len(event_links), RUN_LIMIT)}: {url}")

    # Add delay to avoid overwhelming the server
    if i > 0:
        time.sleep(1)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    event_title = soup.find('span', class_ = "b-content__title-highlight").get_text(strip=True)

    date_and_loc = soup.find_all('li', class_ = "b-list__box-list-item")

    event_loc = {}

    for tag in date_and_loc:
        title_text = tag.find('i').get_text(strip=True)
        all_text = tag.get_text(strip=True)
        event_loc[title_text] = all_text.replace(title_text, "")

    fights = soup.find_all('tr', class_='b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click')

    for fight in fights:
        fight_data.loc[rc, "Event"] = event_title
        fight_data.loc[rc, "Date"] = event_loc["Date:"]
        fight_data.loc[rc, "Location"] = event_loc["Location:"]

        #win/loss
        fight_details = fight.find_all('td')
        fight_data.loc[rc, "WL"] = fight_details[0].get_text(strip=True).upper()
        #fight names
        fighter_names = fight_details[1].find_all('p')
        A_data.loc[rc, "Fighter_name"] = fighter_names[0].get_text(strip=True)
        B_data.loc[rc, "Fighter_name"] = fighter_names[1].get_text(strip=True)

        fight_data.loc[rc, "Winner"] = fighter_names[0].get_text(strip=True)
        #fight statistics
        KD = fight_details[2].find_all('p')
        A_data.loc[rc, "Fighter_KD"] = KD[0].get_text(strip=True)
        B_data.loc[rc, "Fighter_KD"] = KD[1].get_text(strip=True)

        STR = fight_details[3].find_all('p')
        A_data.loc[rc, "Fighter_STR"] = STR[0].get_text(strip=True)
        B_data.loc[rc, "Fighter_STR"] = STR[1].get_text(strip=True)

        TD = fight_details[4].find_all('p')
        A_data.loc[rc, "Fighter_TD"] = TD[0].get_text(strip=True)
        B_data.loc[rc, "Fighter_TD"] = TD[1].get_text(strip=True)

        SUB = fight_details[5].find_all('p')
        A_data.loc[rc, "Fighter_SUB"] = SUB[0].get_text(strip=True)
        B_data.loc[rc, "Fighter_SUB"] = SUB[1].get_text(strip=True)

        fight_data.loc[rc, "Weight_Class"] = fight_details[6].get_text(strip=True)
        img_list = fight_details[6].find_all('img')
        img_dn = {"belt.png":0, "fight.png":0, "perf.png":0, "sub.png":0, "ko.png":0}
        if len(img_list) != 0:
            for img in img_list:
                src = img.get('src')
                #last thing in the hyperlik will reveal what type of symbol it has
                key = src.split('/')[-1]
                img_dn[key] = 1

        fight_data.loc[rc, "Title"] = img_dn["belt.png"]
        fight_data.loc[rc, "Fight_Bonus"] = img_dn["fight.png"]
        fight_data.loc[rc, "Perf_Bonus"] = img_dn["perf.png"]
        fight_data.loc[rc, "KO_Bonus"] = img_dn["ko.png"]
        fight_data.loc[rc, "Sub_Bonus"] = img_dn["sub.png"]

        method = fight_details[7].get_text(strip=True)
        # Split method text - typically format is like "KO/TKO" or "Decision - Unanimous"
        if method:
            fight_data.loc[rc, "Victory_Method"] = method
            # Extract result type (first word before space or entire string if no space)
            fight_data.loc[rc, "Victory_Result"] = method.split()[0] if method else ""
        else:
            fight_data.loc[rc, "Victory_Method"] = ""
            fight_data.loc[rc, "Victory_Result"] = ""
        fight_data.loc[rc, "Round"] = fight_details[8].get_text(strip=True)
        fight_data.loc[rc, "Time"] = fight_details[9].get_text(strip=True)

        rc += 1

#merge the dfs
final_df = pd.DataFrame()

for row in range(len(A_data)):
    hash_input = A_data.loc[row, "Fighter_name"] + B_data.loc[row, "Fighter_name"] + fight_data.loc[row, "Date"]
    hash_value = hash(hash_input)
    should_swap = hash_value%2==0

    # Create row dict with alternating red/blue fighters
    if should_swap:
        # B is Red, A is Blue
        row_dict = {
            "RedFighter": B_data.loc[row, "Fighter_name"],
            "BlueFighter": A_data.loc[row, "Fighter_name"],
            "RedFighter_KD": B_data.loc[row, "Fighter_KD"],
            "BlueFighter_KD": A_data.loc[row, "Fighter_KD"],
            "RedFighter_STR": B_data.loc[row, "Fighter_STR"],
            "BlueFighter_STR": A_data.loc[row, "Fighter_STR"],
            "RedFighter_TD": B_data.loc[row, "Fighter_TD"],
            "BlueFighter_TD": A_data.loc[row, "Fighter_TD"],
            "RedFighter_SUB": B_data.loc[row, "Fighter_SUB"],
            "BlueFighter_SUB": A_data.loc[row, "Fighter_SUB"],
        }
    else:
        # A is Red, B is Blue
        row_dict = {
            "RedFighter": A_data.loc[row, "Fighter_name"],
            "BlueFighter": B_data.loc[row, "Fighter_name"],
            "RedFighter_KD": A_data.loc[row, "Fighter_KD"],
            "BlueFighter_KD": B_data.loc[row, "Fighter_KD"],
            "RedFighter_STR": A_data.loc[row, "Fighter_STR"],
            "BlueFighter_STR": B_data.loc[row, "Fighter_STR"],
            "RedFighter_TD": A_data.loc[row, "Fighter_TD"],
            "BlueFighter_TD": B_data.loc[row, "Fighter_TD"],
            "RedFighter_SUB": A_data.loc[row, "Fighter_SUB"],
            "BlueFighter_SUB": B_data.loc[row, "Fighter_SUB"],
        }

    # Add fight data columns
    row_dict.update({
        "Event": fight_data.loc[row, "Event"],
        "Date": fight_data.loc[row, "Date"],
        "Location": fight_data.loc[row, "Location"],
        "WL": fight_data.loc[row, "WL"],
        "Winner": fight_data.loc[row, "Winner"],
        "Victory_Result": fight_data.loc[row, "Victory_Result"],
        "Victory_Method": fight_data.loc[row, "Victory_Method"],
        "Round": fight_data.loc[row, "Round"],
        "Time": fight_data.loc[row, "Time"],
        "Weight_Class": fight_data.loc[row, "Weight_Class"],
        "Title": fight_data.loc[row, "Title"],
        "Fight_Bonus": fight_data.loc[row, "Fight_Bonus"],
        "Perf_Bonus": fight_data.loc[row, "Perf_Bonus"],
        "Sub_Bonus": fight_data.loc[row, "Sub_Bonus"],
        "KO_Bonus": fight_data.loc[row, "KO_Bonus"]
    })

    # Append to final dataframe
    final_df = pd.concat([final_df, pd.DataFrame([row_dict])], ignore_index=True)

# Save to data directory instead of hardcoded path
output_path = os.path.join(os.path.dirname(__file__), 'data', 'UFC_Events.csv')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
final_df.to_csv(output_path, index=False)
print(f"Saved {len(final_df)} fights to {output_path}")
