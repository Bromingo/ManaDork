import logging
import json
import re
from scipy.stats import hypergeom
import pprint

MANA_MAP = {
    'W': 'White',
    'U': 'Blue',
    'B': 'Black',
    'R': 'Red',
    'G': 'Green'
}

def load_card_list():
    cards = json.load(open('AllCards.json'))
    return cards

class MagicAnalysis(object):
    def load_deck_list(self, filename):
        dl = []
        with open(filename) as f:
            for line in f:
                temp_item = {}
                cleaned_entry = line.rstrip()
                split_entry = cleaned_entry.split(' ')
                if split_entry[0].isdigit() == True:
                    temp_item['num_copies'] = int(split_entry[0])
                    temp_item['card_name'] = " ".join(split_entry[1:])
                else:
                    temp_item['num_copies'] = 1
                    temp_item['card_name'] = cleaned_entry
                if len(temp_item['card_name']) > 0:
                    dl.append(temp_item)
        return dl

    def pull_data_for_decklist(self, infile):
        decklist = self.load_deck_list(infile)
        card_list = load_card_list()
        processed_decklist = []
        for entry in decklist:
            try:
                name = entry['card_name']
                num_copies = entry['num_copies']
                card_json = card_list[name]
                mana_cost = card_json['manaCost']
                cmc = card_json['convertedManaCost']
                typeline = card_json['type']
                types = card_json['types']
                sub_types = card_json['subtypes']
                super_types = card_json['supertypes']
                if 'Creature' in types:
                    power = card_json['power']
                    toughness = card_json['toughness']
                else:
                    power = None
                    toughness = None
                card_dict = {
                    'name': name,
                    'num_copies': num_copies,
                    'mana_cost': mana_cost,
                    'cmc': cmc,
                    'typeline': typeline,
                    'types': types,
                    'sub_types': sub_types,
                    'super_types': super_types,
                    'power': power,
                    'toughness': toughness
                }
                processed_decklist.append(card_dict)
            except:
               logging.error('Error importing card {}'.format(entry['card_name']))
        return processed_decklist

    def count_mana(self, decklist):
        count_entry = {
            'total_symbols': 0,
            'total_cards_of_color': 0,
            'symbol_counts': {},
            'hybrid_symbol_counts': {}
        }
        #TODO: perhaps refactor this dict?
        mana_dict = {
            'White': count_entry,
            'Blue': count_entry,
            'Black': count_entry,
            'Red': count_entry,
            'Green': count_entry
        }
        return_list = []
        for card in decklist:
            card['mana_counts'] = self.count_card_mana(card)
            return_list.append(card)
        return return_list

    def count_card_mana(self, card):
        mana_string = card['mana_cost']
        mana_symbols = [x for x in re.split('\{|\}', mana_string) if len(x)>0]
        color_list = ['W', 'U', 'B', 'R', 'G']
        half_color_list = ['2/W', '2/U', '2/B', '2/R', '2/G']
        hybrid_list = ['W/U', 'U/B', 'B/R', 'R/G', 'G/W', 'W/B', 'U/R', 'B/G', 'R/W', 'G/U']
        full_dict = {
            'color': color_list,
            'half_color': half_color_list,
            'hybrid': hybrid_list
        }
        return_dict = {}
        for key in full_dict:
            self.list_counter(full_dict[key], mana_symbols, key, return_dict)
        return return_dict

    def list_counter(self, iterlist, countlist, key, targetdict):
        entry_dict = {}
        for entry in iterlist:
            entry_count = countlist.count(entry)
            entry_dict[entry] = entry_count
        targetdict[key] = entry_dict

    def run(self):
        infile = '''test_deck.txt'''

        cleaned_list = self.pull_data_for_decklist(dl)
        counted_mana = self.count_mana(cleaned_list)
        summarize_mana = self.summarize_mana(counted_mana)
        p = pprint.PrettyPrinter(indent=4)
        p.pprint(cleaned_list)
        p.pprint(counted_mana)

    def main_run(self):
        try:
            self.run()
        except Exception as e:
            logging.error(e)


if __name__ == '__main__':
    MagicAnalysis().main_run()