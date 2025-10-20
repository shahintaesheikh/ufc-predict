import string
import datetime
import re
import os
import logging
import time
import requests
from typing import Optional, Union, List, Dict
from bs4 import BeautifulSoup
import pandas as pd
from utils import (
    basic_request,
    setup_basic_file_paths,
    setup_logger,
    save_ndjson,
    format_error
)

"""

RUN_ONLY_ONE = False
RUN_LIMIT = 20
IS_IC_DEBUG = False

PROJECT_NAME = 'scrape-ufc-events'
LOGGER = None



def get_all_events() -> List[str]:
    url = 'http://ufcstats.com/statistics/events/completed?page=all'

    LOGGER.info('Fetching all completed events from %s', url)

    try:
        html = basic_request = (url, LOGGER)
    except RuntimeError as e:
        LOGGER.error('Failed to fetch events page: %s', format_error(e))
        return []
    
    event_links = extract_event_links(html)
    LOGGER.info('Found %d events', len(event_links))

    return event_links

def exctract_event_info(soup : BeautifulSoup) -> dict:
    try:
        event_name = soup.select_one('span.b-content__title-highlight').get_text(strip = True)
        if event_name:
            event_name = event_name.get_text(strip=True)
    except AttributeError:
        event_name = None
    
    try:
        list_items = soup.select('li.b-list__box-list-item') 

        event_date = None
        event_loc = None

        for item in list_items:
            text = item.get_text(strip=True)
            if 'Date:' in text:
                event_date = text.split('Date:')[1].strip()
                try:
                    event_date = str(datetime.datetime.strptime(event_date, '%B %d, %Y').date())
                except:
                    pass
            elif 'Location:' in text:
                event_loc = text.split('Location:')[1].strip()
    except:
        event_date = None
        event_loc = None
    return {
        'event_name' : event_name,
        'event_date' : event_date,
        'event_location' : event_loc
    }

def exctract_fight_data(fight_row, event_info:dict) -> dict:
    fight_data = {}
    
    fight_data.update(event_info)

    try:
        cells = fight_row.select('td.b-fight-details__table-col')

        fighters_cell = cells[0] if len(cells) > 0 else None

        if fighters_cell:
            fighter_links = fighters_cell.select('a')
            if len(fighter_links) >= 2:
                fight_data['fighter1'] = fighter_links[0].get_text(strip = True)
                fight_data['fighter2'] = fighter_links[1].get_text(strip = True)

        win_indicator = cells.select('b-flag__text').get_text(strip=True)
        for cell in cells:


"""

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
       "Title": [0],
       "Fight_Bonus": [0],
       "Perf_Bonus": [0],
       "Sub_Bonus": [0],
       "KO_Bonus": [0]
    }

fight_data = pd.DataFrame(event_dict)

for i in range(len(event_links)):
    url = event_links[i]
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    event_dict["Event"] = soup.find('span', class_ = "b-content__title-highlight").get_text(strip=True)

