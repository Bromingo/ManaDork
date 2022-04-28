from MagicEntities import MagicDeck, CardGroup
import random

class GameField(MagicDeck):
    def __init__(self, filepath: str, type: str = 'text', commander: str = None):
        super().__init__(filepath, type, commander)
        self.library = self.drawable_deck #initialize library to drawable deck, already a group
        # TODO: create class for zones with zone specific functions
        self.hand = CardGroup([])
        self.command_zone = CardGroup([])
        self.graveyard = CardGroup([])
        self.exile = CardGroup([])
        self.untapped = CardGroup([])
        self.tapped = CardGroup([])
        self.hand_size_limit = 7
        if commander:
            self.format = 'Commander'
            self.life_total = 40
            self.prepare_commander_deck()
        else:
            self.format = 'Other'
            self.life_total = 20

    def tap_card(self, card):
        self.untapped.move_card(card, self.tapped)

    def untap_card(self, card):
        self.tapped.move_card(card, self.untapped)

    def untap_all(self):
        self.tapped.move_card_list(self.tapped.cards, self.untapped)

    def check_handsize(self):
        return len(self.cards) > self.hand_size_limit
