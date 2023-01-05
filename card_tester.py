import argparse
import json
from textwrap import indent
from MagicEntities import load_card_list

def main():
    parser = argparse.ArgumentParser(description='Print a card entry')
    parser.add_argument('--card', metavar='C', type=str)
    args = parser.parse_args()
    card_list = load_card_list()
    card = card_list.get(args.card)
    print(json.dumps(card,indent=2))

if __name__=='__main__':
    main()