from matplotlib.style import available
from MagicEntities import MagicDeck, CardGroup
import collections
import functools
import operator
import random

#TODO Handle Phases statefully

class GameField(MagicDeck):
    def __init__(self, filepath: str, type: str = 'text', commander_list: list = None):
        super().__init__(filepath, type, commander_list)
        self.library = self.drawable_deck #initialize library to drawable deck, already a group
        # TODO: create class for zones with zone specific functions
        self.hand = CardGroup([])
        self.command_zone = CardGroup([])
        self.graveyard = CardGroup([])
        self.exile = CardGroup([])
        self.untapped = CardGroup([])
        self.tapped = CardGroup([])
        self.hand_size_limit = 7
        if commander_list:
            self.format = 'Commander'
            self.life_total = 40
            self.prepare_commander_deck()
        else:
            self.format = 'Other'
            self.life_total = 20
            
    def prepare_commander_deck(self):
        commanders = []
        for commander in self.commanders:
            commander = self.library.find_cards_by_name(commander)
            commanders += commander
        self.library.move_card_list(commanders, self.hand)

    def tap_card(self, card):
        self.untapped.move_card(card, self.tapped)

    def untap_card(self, card):
        self.tapped.move_card(card, self.untapped)

    def untap_all(self):
        self.tapped.move_card_list(self.tapped.cards, self.untapped)

    def check_upkeep(self):
        pass

    def check_handsize(self):
        return len(self.cards) > self.hand_size_limit

    def draw_a_card(self):
        self.library.move_card(self.library.cards[0], self.hand)
    
    def draw_cards(self, n):
        for i in range(0,n):
            self.draw_card()

    def play_card(self, card):
        # TODO: check if enters tapped
        # Right now, overloading tapped for summoning sickness
        if card.is_permanent:
            if card.enters_tapped:
                self.hand.move_card(card, self.tapped)
            else:
                self.hand.move_card(card, self.untapped)
        # For now, won't handle instants and sorceries
    
    def mana_sources(self):
        return CardGroup([card for card in self.untapped.cards if card.produces_mana])

    def can_cast(self,card): 
        temp_mana_sources = self.mana_sources()
        tapped_sources = CardGroup([])
        mana_cost = card.mana_cost
        non_generic_cost = [a for a in mana_cost if not a.is_numeric()]
        # TODO: Handle Hybrid Mana
        for k in non_generic_cost:
            matching_sources = [card for card in temp_mana_sources.cards if card.mana_production[k] > 0]
            if len(matching_sources) == 0:
                return []
            else:
                # TODO: Handle prioritization of mana sources
                # currently, this could chose your only red source as your green mana
                remove_card = random.choice(matching_sources)
                temp_mana_sources.move_card(remove_card, tapped_sources)
        generic_mana = [a for a in mana_cost if a.is_numeric()]
        if len(generic_mana) > 0:
            generic_sources_needed = int(generic_mana)
            if generic_sources_needed > len(temp_mana_sources):
                return []
            else:
                for i in range(0,generic_sources_needed):
                    remove_card = random.choice(temp_mana_sources)
                    temp_mana_sources.move_card(remove_card, tapped_sources)
        return tapped_sources.cards # Return just the list of sources

    def setup_game(self):
        self.library.shuffle()
        self.draw_cards(7)

    

class GameRunner(GameField):
    def __init__(self, filepath: str, type: str = 'text', commander_list: list = None):
        super.__init__(filepath,type,commander_list)
        self.setup_game() # Initialize things
        self.turn = 0

    def beginning_phase(self):
        self.untap_all() # untap
        self.check_upkeep() # upkeep
        self.draw_a_card()
        # TODO Remove Summoning Sickness



    def main_phase(self):
        self.play_land()

    def take_turn(self):
        self.beginning_phase()
        self.turn+=1
