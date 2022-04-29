import json
import random
import logging
import re

from numpy import add

COLOR_CODES = ['W','U','B','R','G', 'C']

base_mana_produced = {
            'W': 0,
            'U': 0,
            'B': 0,
            'R': 0,
            'G': 0,
            'C': 0,
            'A': 0 # Any
        }

def load_card_list():
    with open("AtomicCards.json", "r", encoding='utf-8') as context:
        cards = json.load(context)
        card_list = cards['data']
    return card_list

# TODO: Maybe create a "permanent" that has notions of tapped / untapped, damage marked, and summoning sickness?
class MagicCard:
    def __init__(self, name, mana_cost, cmc, typeline, types, text, sub_types, super_types, power, toughness):
        self.name = name
        self.mana_cost = mana_cost
        self.cmc = cmc
        self.typeline = typeline
        self.types = types
        self.text = text
        self.sub_types = sub_types
        self.super_types = super_types
        self.power = power
        self.toughness = toughness
        # TODO: Support Planeswalkers
        # Derived
        self.parsed_mana_cost = self.parse_mana_cost()
        self.text_lines = self.text.lower().split('\n')
        self.enters_tapped = self.check_enters_tapped()
        self.is_permanent = self.check_is_permanent()
        self.mana_production = self.mana_produced()
        self.produces_mana = (self.mana_production != base_mana_produced)

    def parse_mana_cost(self):
        if self.mana_cost:
            return self.mana_cost.rstrip('}').lstrip('{').split('}{')
        else:
            return None

    def check_enters_tapped(self):
        if 'Creature' in self.types:
            return True

    def check_is_permanent(self):
        perm_list = ['Creature', 'Artifact', 'Enchantment', 'Planeswalker']
        if any(item in perm_list for item in self.types):
            return True

    def mana_produced(self):
        mana_strings = [
            'add {W}',
            'add {U}',
            'add {B}',
            'add {R}',
            'add {G}',
            'mana of any color',
        ]
        mana_produced = base_mana_produced.copy()
        for line in self.text_lines:
            add_split = line.split('add ')
            if len(add_split) > 1:
                # This won't be perfect, so we'll want a smarter way to template this
                for after_add in add_split[1:]:
                    for col in COLOR_CODES:
                        color_code = '{'+col.lower()+'}'
                        text_split_by_color = after_add.split(color_code)
                        mana_produced[col] += len(text_split_by_color) - 1
                    mana_produced['A'] += len(after_add.split('mana of any color')) - 1

                # TODO: Make this max after each line, to prevent double counting something like 'Crystal Vein'
        return mana_produced

    def __repr__(self):
        return f'|{self.name}|'
                


class CardGroup:
    def __init__(self, cards):
        self.cards = cards

    def shuffle(self):
        self.cards = random.shuffle(self.cards)

    def find_cards_by_name(self, name: str):
        return [c for c in self.cards if c.name == name]

    def move_card_list(self, list_of_cards, target_card_group):
        for c in list_of_cards:
            self.move_card(card=c, target_card_group=target_card_group)

    def card_index(self, card):
        return self.cards.index(card)

    def move_card(self, card, target_card_group):
        # Assumes you move to bottom, where order matters
        if len(self.cards) > 0:
            popped_card = self.cards.pop(self.card_index(card))
            target_card_group.cards.append(popped_card)
    

class MagicDeck:
    def __init__(self, filepath: str, type: str = 'text', commander_list: str = None):
        self.filepath = filepath
        self.type = type  # default to text list
        self.commander_list = commander_list
        initial_decklist = self.load_deck_list()
        self.deck_list_raw = initial_decklist
        self.deck_list_details = self.pull_data_for_decklist()
        self.drawable_deck = CardGroup(self.make_drawable_deck())

    def initialize_deck(self, decklist: list):
        # Allow for reinitialization of deck
        self.deck_list_raw = decklist
        self.deck_list_details = self.pull_data_for_decklist()
        self.drawable_deck = CardGroup(self.make_drawable_deck())

    def load_deck_list(self):
        # TODO: make this read .cod files as well
        dl = []
        with open(self.filepath) as f:
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

    def pull_data_for_decklist(self):
        # TODO: Entry Caching?
        card_list = load_card_list()
        processed_decklist = []
        for entry in self.deck_list_raw:
            try:
                name = entry['card_name']
                num_copies = entry['num_copies']
                card_json = card_list[name][0]  # Get entry from list
                mana_cost = card_json.get('manaCost', None)  # Lands don't have a mana cost (nor do some spells)
                cmc = card_json['convertedManaCost']
                typeline = card_json['type']
                types = card_json['types']
                text = card_json['text']
                sub_types = card_json['subtypes']
                super_types = card_json['supertypes']
                if 'Creature' in types:
                    power = card_json['power']
                    toughness = card_json['toughness']
                else:
                    power = None
                    toughness = None
                mtg_card = MagicCard(
                    name=name,
                    mana_cost=mana_cost,
                    cmc=cmc,
                    typeline=typeline,
                    types=types,
                    text=text,
                    sub_types=sub_types,
                    super_types=super_types,
                    power=power,
                    toughness=toughness)
                card_dict = {
                    'name': name,
                    'num_copies': num_copies,
                    'card': mtg_card
                }
                processed_decklist.append(card_dict)
            except:
                print(card_json)
                logging.error('Error importing card {}'.format(entry['card_name']))
        return processed_decklist

    def make_drawable_deck(self):
        drawable_list = []
        for entry in self.deck_list_details:
            num_copies = entry['num_copies']
            card = entry['card']
            for i in range(0, num_copies):
                drawable_list.append(card)
        return drawable_list
