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

event_dict = {"Event": ["-"],
       "Date": ["-"],
       "location": ["-"],
       "WL": [""],
       "Fighter_A": ["-"],
       "Fighter_B": ["-"],
       "Fighter_A_KD": ["-"],
       "Fighter_B_KD": ["-"],
       "Fighter_A_STR": ["-"],
       "Fighter_B_STR": ["-"],
       "Fighter_A_TD": ["-"],
       "Fighter_B_TD": ["-"],
       "Fighter_A_SUB": ["-"],
       "Fighter_B_SUB": ["-"],
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

fight_data = pd.DataFrame(event_dict)

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
        fight_data.loc[rc, "Fighter_A"] = fighter_names[0].get_text(strip=True)
        fight_data.loc[rc, "Fighter_B"] = fighter_names[1].get_text(strip=True)

        fight_data.loc[rc, "Winner"] = fighter_names[0].get_text(strip=True)
        #fight statistics
        KD = fight_details[2].find_all('p')
        fight_data.loc[rc, "Fighter_A_KD"] = KD[0].get_text(strip=True)
        fight_data.loc[rc, "Fighter_B_KD"] = KD[1].get_text(strip=True)

        STR = fight_details[3].find_all('p')
        fight_data.loc[rc, "Fighter_A_STR"] = STR[0].get_text(strip=True)
        fight_data.loc[rc, "Fighter_B_STR"] = STR[1].get_text(strip=True)

        TD = fight_details[4].find_all('p')
        fight_data.loc[rc, "Fighter_A_TD"] = TD[0].get_text(strip=True)
        fight_data.loc[rc, "Fighter_B_TD"] = TD[1].get_text(strip=True)

        SUB = fight_details[5].find_all('p')
        fight_data.loc[rc, "Fighter_A_SUB"] = SUB[0].get_text(strip=True)
        fight_data.loc[rc, "Fighter_B_SUB"] = SUB[1].get_text(strip=True)

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

# Save to data directory instead of hardcoded path
output_path = os.path.join(os.path.dirname(__file__), 'data', 'UFC_Events.csv')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
fight_data.to_csv(output_path, index=False)
print(f"Saved {len(fight_data)} fights to {output_path}")
