import string
import datetime
import re
import os
import logging
import time
from typing import Optional, Union
import pint
from bs4 import BeautifulSoup
from icecream import ic
from utils import (
    basic_request,
    setup_basic_file_paths,
    setup_logger,
    save_ndjson,
    format_error
)

#global variables
RUN_ONLY_ONE = False
RUN_25_ITR = True #for testin for now
IS_IC_DEBUG = False

PROJECT_NAME = 'scrape-ufc'
LOGGER = None

#returns set with links for each fighter
def extract_fighter_pagelinks(html: str) -> set[str]:
    soup = BeautifulSoup(html, 'html.parser')

    tags = soup.select('tr.b-statistics__table-row a')
    links = [tag.get('href') for tag in tags]

    unique_links = set(links)

    return unique_links

def get_fighters() -> set[str]:
    letters = string.ascii_lowercase
    all_links = set()

    for letter in letters:
        LOGGER.info('Exctracting letters %s', letter)

        url = f'http://ufcstats.com/statistics/fighters?char={letter}&page=all'
        try:
            html = basic_request(url, LOGGER)
        except RuntimeError:
            continue

        links = extract_fighter_pagelinks(html)

        all_links.update(links)

        if RUN_ONLY_ONE:
            break

    LOGGER.info('Found %d unique links', len(all_links))

    return all_links

#exctract data from profile html
def extract_bio(soup: BeautifulSoup, fighter_name: str) -> dict:
    try:
        physical_data = soup.select_one(
            '.b-list__info-box.b-list__info-box_style_small-width')\
            .get_text(strip=True, separator='_').split('_')
        if IS_IC_DEBUG:
            ic(physical_data)
        try:
            height = physical_data[1]
        except IndexError:
            height = None
        try: 
            weight = physical_data[3]
        except IndexError:
            weight = None
        try:
            reach = physical_data[5]
        except IndexError:
            reach = None
        try:
            stance = physical_data[7]
        except IndexError:
            reach = None
        try:
            dob = physical_data[9]
        except IndexError:
            dob = None
        
        def weight_to_kg(weight: str):
            digit_weight = re.match(r'(\d+)', weight).group(0)
            if digit_weight:
                if 'lbs' in weight:
                    weight_in_kg = round(int(digit_weight)*0.453592, 2)
            else:
                weight_in_kg = None
            
            return weight_in_kg
        
        if weight and "--" != weight:
            weight_kg = weight_to_kg(weight)
        else:
            weight_kg = None

        if dob and "--" != dob:
            try:
                date_of_birth = str(datetime.datetime.strptime(dob, '%b %d, %Y').date())
            except:
                date_of_birth = None
        else:
            date_of_birth = None
        
        def convert_height_cm(height: str) ->int:
            ureg = pint.UnitRegistry()
            h_feet, h_inches = height.split(' ')

            try:
                h_feet, h_inches = int(re.match(r'(\d+)', h_feet).group(0)), int(re.match(r'(\d+)', h_inches).group(0))

                default_height = h_feet*ureg.foot + h_inches*ureg.inch
                height_cm = default_height.to(ureg.centimeter)

                height_cm = round(height_cm.magnitude, 2)
            except:
                height_cm = None

            return height_cm
        
        if height and "--" != height:
            height_cm = convert_height_cm(height)
        else:
            height_cm = None

        def convert_reach_cm(reach:str) -> int | None:
            reach_in_inch = reach if reach != "--" else None
            if reach_in_inch:
                reach_in_cm = int(reach_in_inch.split('"')[0])*2.54
            else:
                reach_in_cm = None
            return reach_in_cm

        if reach and "--" != reach:
            reach_cm = convert_reach_cm(reach)
        else:
            reach_cm = None
    except Exception as e:
        LOGGER.warning('Exception for %s on extract_bio_data() %s', fighter_name, format_error(e))
        height_cm = reach_cm = weight_kg = stance = date_of_birth = None

    bio_data = {
        "height_cm" : height_cm,
        "weight_kg" : weight_kg,
        "reach_cm" : reach_cm,
        "stance" : stance,
        "date_of_birth" : date_of_birth
    }

    return bio_data

def extract_career(soup: BeautifulSoup, fighter_name : str) -> dict:
    try:
        #get career data and turn into list
        career_data = soup.select_one('.b-list__info-box.b-list__info-box_style_middle-width')\
        .get_text(strip=True, separator='_').split('_')

        ss_landed_per_minute = float(career_data[2])
        ss_accuracy = float(career_data[4].replace('%', ''))
        ss_absorbed_per_minute = float(career_data[6])
        ss_defence = float(career_data[8].replace('%',''))
        avg_td_per_15 = float(career_data[10])
        td_accuracy = float(career_data[12].replace('%', ''))
        td_defence = float(career_data[14].replace('%',''))
        average_sub_attempted_per_15 = float(career_data[2])

    except Exception as e:
        LOGGER.warning('Exception for %s on extract_career_data(): %s', fighter_name, format_error(e))

        ss_landed_per_minute = None
        ss_accuracy = None
        ss_absorbed_per_minute =None
        ss_defence = None
        avg_td_per_15 = None
        td_accuracy =None
        td_defence = None
        average_sub_attempted_per_15 =None

    career_dict = {
        "ss_landed_per_minute" : ss_landed_per_minute,
        "ss_accuracy" : ss_accuracy,
        "ss_absorbed_per_min" : ss_absorbed_per_minute,
        "ss_defence" : ss_defence,
        "avg_td_per_15" : avg_td_per_15,
        "td_accuracy" : td_accuracy,
        "td_defence" : td_defence,
        "avg_sub_attempt_per_15" : average_sub_attempted_per_15
    }
    
    return career_dict

def extract_fighter_data(fighter_html:str) -> dict:
    soup = BeautifulSoup(fighter_html, 'html.parser')

    try:
        fighter_name = soup.select_one(
            '.b-content__title-highlight').get_text(strip = True)
    except AttributeError:
        fighter_name = None

    try:
        win,loss,draw = soup.select_one(
            '.b-content__title-record').get_text(strip = True)\
            .split(' ',maxsplit=1)[-1]\
            .strip()\
            .split(' ')[0]\
            .strip()\
            .split('-')

        win, loss, draw = int(win), int(loss), int(draw)
    except (AttributeError, ValueError):
        win = None
        loss = None
        draw = None

    try:
        nickname = soup.select_one('.b-content__Nickname').get_text(strip = True)
        if nickname == "":
            nickname = None
    except AttributeError:
        nickname = None
    
    bio_data = extract_bio(soup, fighter_name)
    career_data = extract_career(soup, fighter_name)

    fighter_data = {
        "name" : fighter_name,
        "nickname" : nickname,
        "wins" : win,
        "losses" : loss,
        "draws" : draw,
        "height_cm" : bio_data['height_cm'],
        "weight_kg" : bio_data['weight_kg'],
        "reach_cm" : bio_data['reach_cm'],
        "stance" : bio_data['stance'],
        "dob" : bio_data['date_of_birth'],
        "ss_landed_per_minute" : career_data['ss_landed_per_minute'],
        "ss_accuracy" : career_data['ss_accuracy'],
        "ss_absorbed_per_min" : career_data['ss_absorbed_per_min'],
        "ss_defence" : career_data['ss_defence'],
        "avg_td_per_15" : career_data['avg_td_per_15'],
        "td_accuracy" : career_data['td_accuracy'],
        "td_defence" : career_data['td_defence'],
        "avg_sub_attempt_per_15" : career_data['avg_sub_attempt_per_15']
    }

    return fighter_data

def get_n_extract_fighter_data(link: str)->dict:
    try:
        page = basic_request(link, LOGGER)
    except RuntimeError as e:
        raise RuntimeError from e
    
    fighter_dict = extract_fighter_data(page)

    return fighter_dict

def executer() -> None:
    global LOGGER

    _, data_folder, _, _, log_file_path = setup_basic_file_paths(
        PROJECT_NAME)
    
    LOGGER = setup_logger(log_file_path)

    fighter_links = get_fighters()

    #save file for all fighters
    ndjson_file_path = os.path.join(data_folder, 'fighter_data.ndjson')

    #get data for each fighter
    for i, fighter in enumerate(fighter_links):
        LOGGER.info('Processing %d out of %d. Fighter url: %s', i, len(fighter_links), fighter)
        try:
            fighter_data = get_n_extract_fighter_data(fighter)

            save_ndjson(fighter_data, ndjson_file_path)

            if RUN_ONLY_ONE:
                break
            if RUN_25_ITR and i == 24:
                break
        except RuntimeError:
            LOGGER.debug('Skipping fighter due to requests error : %s', fighter)

            if RUN_ONLY_ONE:
                break
            if RUN_25_ITR and i == 24:
                break

            continue
    LOGGER.info('Finished executor')

if __name__ == '__main__':
    executer()
