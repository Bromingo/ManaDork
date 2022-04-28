import logging

import re
from scipy.stats import hypergeom
import pprint
from MagicEntities import MagicDeck

MANA_MAP = {
    'W': 'White',
    'U': 'Blue',
    'B': 'Black',
    'R': 'Red',
    'G': 'Green'
}

class MagicAnalysis(MagicDeck):
    def __init__(self, filepath: str, type: str = 'text', commander: str = None):
        super().__init__(filepath, type, commander)

    def count_mana(self):
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
        for card in self.deck_list_details:
            card['mana_counts'] = self.count_card_mana(card)
            return_list.append(card)
        return return_list

    def count_card_mana(self, card):
        mana_string = card['mana_cost']
        mana_symbols = [x for x in re.split('\{|\}', mana_string) if len(x) > 0]
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
        counted_mana = self.count_mana()
        p = pprint.PrettyPrinter(indent=4)
        p.pprint(counted_mana)

    def main_run(self):
        try:
            self.run()
        except Exception as e:
            logging.error(e)


if __name__ == '__main__':
    Deck = MagicDeck('decks/Atraxa', commander="Atraxa, Praetors' Voice")
    analysis = MagicAnalysis('decks/Atraxa', commander="Atraxa, Praetors' Voice")
    #print(analysis.run())
    print(Deck.drawable_deck.cards)
    import pdb
    pdb.set_trace()
