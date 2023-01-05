from tkinter.tix import Tk
from game_runner import GameField, GameRunner
import pdb

## Initialize ##
# pg_field = GameField('decks/test', commander_list=["Atraxa, Praetors' Voice"])
# pg_field.setup_game()
# pg_field.display_game()
# pg_field.draw_cards(2)
# pg_field.play_card_by_name('Arcane Sanctum')
# pg_field.play_card_by_name('Bayou')
# pg_field.play_card_by_name('Grand Coliseum')
# pg_field.play_card_by_name('Forest')
# pg_field.play_card_by_name('Swamp')
# pg_field.display_game()
# print(pg_field.can_cast(pg_field.hand.find_cards_by_name('Colossal Dreadmaw')[0]))
# print(pg_field.can_cast(pg_field.hand.find_cards_by_name('Abzan Charm')[0]))
# pg_field.main_phase_sim()
# pg_field.display_game()
# print(pg_field.untapped.max_mana_across_sources())

pg_runner = GameRunner('decks/Atraxa', commander_list=["Atraxa, Praetors' Voice"])
while pg_runner.turn < 10:
    pg_runner.display_game()
    pg_runner.take_turn()