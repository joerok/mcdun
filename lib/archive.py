## dead code; archive laded by hand, don't know if there's value to reloading it

import requests
from bs4 import BeautifulSoup as bs4
import os
import lib.cloud as cloud
import html
import gzip

URL = "https://minecraft.wiki/w/Dungeons:"
DATA_DIR = 'data'
CATEGORIES = [
    'armor',
    'artifact',
    'melee weapon',
    'ranged weapon'
]

def clean_armor_html(name, doc): pass
def clean_artifact_html(name, doc): pass
def clean_melee_weapon_html(name, doc): pass
def clean_ranged_weapon_html(name, doc): pass

CATEGORY_CLEANERS = {
    'armor': clean_armor_html,
    'artifact': clean_artifact_html,
    'melee weapon': clean_melee_weapon_html,
    'ranged weapon': clean_ranged_weapon_html
}

def source(url):
    if (s := requests.get(URL + url)) and s.status_code == 200:
        return s

def get_items():
    if (s := source('Items')):
        items = bs4(s.content, 'html.parser').find_all(class_='sprite-text')
        for link, name in set(map(lambda _items: (str(_.parent).split(':',1)[1].split('"')[0], _.parent.text), items)):
            if (s := source(link)):
                with open(f'{DATA_DIR}item_{link}.html', 'w+') as f:
                    f.write(s.content.decode('utf-8'))
            else:
                print(f'item {name} could not be read')

from collections import defaultdict

def _clean_melee_weapon_html(name, doc):
    print("cleaning", name)
    info = parse_melee_weapon_infobox(doc.find(class_='infobox'))
    info['Quote'] = doc.find(class_='mcwiki-quote').text.strip()
    info['Obtaining'] = get_siblings_between_tags(doc.find(id='Obtaining').parent, doc.find(id="Usage").parent)
    info["Obtaining"] = list(map(lambda _: (_.text and _.text.strip()), info["Obtaining"]))
    places = ["Missions", "Events", "Ancients", "Merchants"]
    obtaining = defaultdict(list)
    place = None
    for _ in info["Obtaining"]:
        if 'Listed diff' in _: continue
        if _ in places:
            place = _
        elif place:
            obtaining[place].extend(_.split("\n"))
    info["Obtaining"] = obtaining
    info['Properties'] = get_siblings_between_tags(doc.find(id='Properties').parent, doc.find(id="Stats").parent)
    for section in info["Properties"]:
        if section.find('li'):
            info["Properties"] = list(map(lambda _: _.text.strip() if not _.find('a') else _.find('a')["href"], section.find_all('li')))
    stats = get_siblings_between_tags(doc.find(id='Stats').parent, doc.find(id="Sounds").parent)
    combo, power = None, None
    for _ in stats:
        if _.find('tbody'):
            table = _
            headers = list(map(lambda _: _.text.strip(), table.find_all('th')))
            if not combo:
                combo = {}
                for row in table.find_all('tr')[1:]:
                    data = list(map(lambda _: _.text.strip(), row.find_all('td')))
                    key = data.pop(0)
                    combo[key] = dict(zip(headers, data))
            elif not power:
                power = {}
                for row in table.find_all('tr')[1:]:
                    data = list(map(lambda _: _.text.strip(), row.find_all('td')))
                    key = data.pop(0)
                    power[key] = dict(zip(headers, data))
    info['Combo'] = combo
    info['Power'] = power
    from pprint import pprint
    pprint(info)


CATEGORY_CLEANERS['melee weapon'] = _clean_melee_weapon_html

def get_siblings_between_tags(start, end):    
    siblings = []
    current_tag = start.next_sibling

    while current_tag and current_tag != end:
        if current_tag.name:
            siblings.append(current_tag)
        current_tag = current_tag.next_sibling
    return siblings

def archive_to_cloud():
    for file in os.listdir(DATA_DIR):
        name = html.unescape(file.split('.html.gz')[0])        
        cloud.upload_blob(cloud.get_bucket(), os.path.join(DATA_DIR, file), name)

def clean_archive():
    for name in os.listdir(DATA_DIR):
        try:
            with gzip.open(os.path.join(DATA_DIR, name), 'r') as f:
                doc = bs4(f.read(),'html.parser')
            category = list(doc.find(class_='infobox-rows').find('tr').find_all('a'))[-1].text.lower()
            if category in CATEGORIES:
                CATEGORY_CLEANERS[category](name, doc)
        except Exception as e:
            ## capes, pets, and listings are not interesting
            pass

def parse_melee_weapon_infobox(infobox):
    info = dict()
    for th in infobox.find_all('th'):
        info[th.text.strip()] = th.parent.find('td')
    try:
        info['Rarity'] = info['Rarity'].text.strip()
        info['Power'] = float(info['Power'].text)
        info['Speed'] = float(info['Speed'].text)
        info['Area'] = float(info['Area'].text)

        # Properties
        # Items without properties: pickaxe, katana, mace, sword
        if 'Properties' in info:
            info['Properties'] = info['Properties'].find('p').text.strip()
        else:
            info['Properties'] = ""

        if 'Enchantment' in info:
            info['Enchantment'] = list(map(lambda _: (_.parent.parent.find('a')['href'], _.text.strip()), info['Enchantment'].find_all(class_='sprite-text')))
        else:
            info['Enchantment'] = []

        if 'Damage type' in info:
            del info['Damage type']
            # damage type is covered by Properties below

        if 'Combo' in info:
            del info['Combo']
            # combo is covered by Stats below

        info['Soulinformation'] = ('Does accept' in info['Soulinformation'].text, 'Does grant' in info['Soulinformation'].text)
        info['Runes'] = list(map(lambda _: (_['alt'], _['src']), info['Runes'].find_all('img')))
        info['Variants'] = list(map(lambda _: (_.parent['href'], _.text.strip()), info['Variants'].find_all(class_='sprite-text')))
        info['Type'] = info['Type'].text.strip()
        info['Level ID'] = info['Level ID'].text.strip()

        return info
    except Exception as e:
        print(e)


