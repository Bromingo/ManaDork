from MagicEntities import MagicDeck, CardGroup
from MagicEntities import NoMatchingSourcesException, CardNotFoundException
import collections
import functools
import operator
from tabulate import tabulate
import random
import itertools
import pdb

#TODO Handle Phases statefully

class NoCastableCards(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

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
        for commander in self.commander_list:
            commander = self.library.find_cards_by_name(commander)
            commanders += commander
        self.library.move_card_list(commanders, self.command_zone)

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
            self.draw_a_card()



    def unplay_card(self, card):
        for zone in [self.tapped, self.untapped, self.graveyard]:
            pdb.set_trace()
            try:
                zone.move_card(card, self.hand)
                break
            except CardNotFoundException:
                continue

    def unplay_card_by_name(self, card_name):
        for zone in [self.tapped, self.untapped, self.graveyard]:
            pdb.set_trace()
            try:
                cards = self.hand.find_cards_by_name(card_name)
                if len(cards) > 0:
                    zone.move_card(cards[0], self.hand)
                break
            except CardNotFoundException:
                continue

    def play_card(self, card):
            # Right now, overloading tapped for summoning sickness
            if card.is_permanent:
                if card.enters_tapped:
                    self.hand.move_card(card, self.tapped)
                else:
                    self.hand.move_card(card, self.untapped)
            else:
                self.hand.move_card(card, self.graveyard)

    def play_card_by_name(self, name):
        cards = self.hand.find_cards_by_name(name)
        if len(cards) > 0:
            self.play_card(cards[0])

    def get_mana_sources(self):
        return CardGroup([card for card in self.untapped.cards if card.produces_mana])

    def can_cast(self,card, mana_source_override=CardGroup([])):
        if len(mana_source_override) > 0:
            temp_mana_sources = mana_source_override
        else:
            temp_mana_sources = self.get_mana_sources()
        tapped_sources = CardGroup([])
        mana_cost_dict = card.get_mana_cost_dict()
        non_generic_cost = mana_cost_dict['mana_symbols']

        # TODO: Handle Hybrid Mana
        # Most likely, this needs to be done in lowest_score_matching_mana_source
        for k in non_generic_cost:
            try:
                targeted_mana_source = temp_mana_sources.lowest_score_matching_mana_source(k)
                temp_mana_sources.move_card(targeted_mana_source, tapped_sources)
            except NoMatchingSourcesException:
                return CardGroup([]) # TODO: make this actually exit
        generic_mana = mana_cost_dict['generic']
        if generic_mana > 0:
            try:
                generic_sources = temp_mana_sources.lowest_score_mana_sources(generic_mana)
                for source in generic_sources:
                    temp_mana_sources.move_card(source, tapped_sources)
            except NoMatchingSourcesException:
                return CardGroup([])
        return tapped_sources # Return just the list of sources

    def setup_game(self):
        self.library.shuffle()
        self.draw_cards(7)

    def display_game(self):
        library_count = self.library.length
        print("Library: {:<8}".format(library_count))
        if len(self.commander_list) > 0:
            print("CZ: {:<8}".format("&".join([str(card) for card in self.command_zone.cards]) ))
        # create card sets
        cards = [self.hand.cards, self.untapped.cards, self.tapped.cards, self.graveyard.cards]
        rotated_list = list(map(list, itertools.zip_longest(*cards, fillvalue=None)))
        print(tabulate(rotated_list, headers=['hand','untapped', 'tapped', 'gy']))


class GameRunner(GameField):
    def __init__(self, filepath: str, type: str = 'text', commander_list: list = None):
        super().__init__(filepath,type,commander_list)
        self.setup_game() # Initialize things
        self.turn = 0
        self.turn_array = []
        self.action_array = []

    def beginning_phase(self):
        self.untap_all() # untap
        self.check_upkeep() # upkeep
        self.draw_a_card()
        # TODO Remove Summoning Sickness

    def play_best_land(self):
        # Really, want to play a land that enables a play that turn
        # Probably just need to try every land honestly
        lands = self.hand.find_cards_by_type('Land')
        if len(lands) > 0:
            land_to_play = max(lands, key=lambda x: x.mana_score)
            self.play_card(land_to_play)

    def best_castable_card_sim(self, mana_source_override=CardGroup([])):
        castables = self.hand.find_cards_exclude_type('Land') # + self.command_zone.cards # TODO handle command zone
        castable_card_list = []
        for card in castables:
            mana_sources = self.can_cast(card, mana_source_override)
            if len(mana_sources)>0:
                castable_card_list.append(card) # TODO: make this draw mana
        if len(castable_card_list) == 0:
            raise NoCastableCards
        mana_castable = [card for card in castable_card_list if card.produces_mana]
        if len(mana_castable) > 0:
            prioritize_list = mana_castable
            is_mana = True
        else:
            prioritize_list = castable_card_list
            is_mana = False
        best_castable = max(prioritize_list, key=lambda x: x.cmc)
        return {'card': best_castable, 'cmc': best_castable.cmc, 'is_mana': is_mana}

    def main_phase_sim(self):
        lands = CardGroup(self.hand.find_cards_by_type('Land'))
        castable_cards = []
        turn_status = {}
        if len(lands) > 0:
            for land in lands.cards:
                temp_mana = self.get_mana_sources()
                lands.move_card(land, temp_mana)
                try:
                    castable_card_dict = self.best_castable_card_sim(temp_mana)
                    castable_card_dict['land'] = land
                    castable_cards.append(castable_card_dict)
                except NoCastableCards:
                    continue
        else:
            turn_status['land_played'] = False
            try:
                castable_card_dict = self.best_castable_card_sim()
                castable_cards.append(castable_card_dict)
            except NoCastableCards:
                turn_status = {}

        reinit_lands = CardGroup(self.hand.find_cards_by_type('Land'))
        if len(castable_cards) == 0:
            turn_status['spell_cast'] = False
            if len(reinit_lands) > 0:
                turn_status['land_played'] = True
                land_to_play = max(reinit_lands.cards, key=lambda x: x.mana_score)
                self.play_card_by_name(land_to_play.name)
            else:
                turn_status['land_played'] = False
        else:
            turn_status['spell_cast'] = True
            best_castable_card_entry = max(castable_cards, key=lambda x: x['cmc'])

            if best_castable_card_entry.get('land') is not None:
                turn_status['land_played'] = True
                self.play_card_by_name(best_castable_card_entry['land'].name)
            else:
                turn_status['land_played'] = False
            self.play_card_by_name(best_castable_card_entry['card'].name)
        return turn_status

    def take_turn(self):
        self.beginning_phase()
        turn_status = self.main_phase_sim()
        self.turn_array.append(turn_status)
        self.turn+=1
