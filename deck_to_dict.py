import mtgdeck
import os
import argparse
import pdb
from deck_analysis import MagicAnalysis

def deck_to_dict(folder_name):
    cwd = os.path.abspath('.')
    folder_path = os.path.join(cwd, folder_name)

    list_of_deck = os.listdir(folder_path)
    for deck in list_of_deck:
        name_decomp = deck.split('.')
        deck_path = os.path.join(folder_path,deck)
        src = open(deck_path)
        decklist = mtgdeck.load(src, cls=mtgdeck.MagicOnlineDecoder)
        pdb.set_trace()



def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('folder_names', nargs='+')
    args = parser.parse_args()
    deck_to_dict(args.folder_names[0])


if __name__ == '__main__':
    main()