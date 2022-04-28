import mtgdeck
import os
import argparse
import pdb




def convert_decks(folder_name):
    cwd = os.path.abspath('.')
    folder_path = os.path.join(cwd, folder_name)

    list_of_deck = os.listdir(folder_path)
    for deck in list_of_deck:
        name_decomp = deck.split('.')
        if name_decomp[1] == 'cod':
            deck_path = os.path.join(folder_path,deck)
            target_path = os.path.join(folder_path, name_decomp[0])
            src = open(deck_path)
            target = open(target_path, 'w')
            decklist = mtgdeck.load(src, cls=mtgdeck.CockatriceDecoder)
            mtgdeck.dump(decklist, target, cls=mtgdeck.MagicOnlineEncoder)

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('folder_name', nargs='+')
    args = parser.parse_args()
    convert_decks(args.folder_name[0])

if __name__ == '__main__':
    main()