#!/usr/local/bin/python3

# Indexing (an Android: Netrunner card sorter)

import argparse
import json
import os

def group(cards, attribute='type_code'):
	groups = {}

	for card in cards:
		if not attribute in card:
			continue

		group = card[attribute]

		if not group in groups:
			groups[group] = []

		groups[group].append(card)

	return groups

def index(segregate=False):
	cardsByFaction = group(cards, 'faction_code')

	for faction, inFactionCards in cardsByFaction.items():
		file = open('binders/' + faction + '.txt', 'w+')
		cardsByType = group(inFactionCards, 'type_code')
		output = []

		output.append(indexBySideAndType(cardsByType, segregate, 'runner_mini', miniFactions))
		output.append(indexBySideAndType(cardsByType, segregate, 'runner', runnerTypes))
		output.append(indexBySideAndType(cardsByType, segregate, 'corp', corpTypes))

		output = filter(None, output)
		file.write(str.join('\n', output))
		file.close()

def indexBySideAndType(cardsByType, segregate, side, types):
	output = ''
	page = 0
	cardNumber = columns * rows

	for type in types:
		for typeMatch, inTypeCards in cardsByType.items():
			if typeMatch != type:
				continue

			inTypeCards = [card for card in inTypeCards if card['side_code'] == side]
			inTypeCards = sorted(inTypeCards, key=lambda item: item['code']) # Sort cards by their code

			if segregate:
				cardNumber = columns * rows

			for card in inTypeCards:
				while card['quantity'] > 0:
					cardNumber = cardNumber + 1

					if cardNumber == columns * rows + 1:
						cardNumber = 1
						page = page + 1

						if page != 1:
							output = output + '\n'

						if segregate:
							output = output + 'Page ' + str(page) + ' (' + type + ')\n\n'
						else:
							output = output + 'Page ' + str(page) + '\n\n'

					output = output + '\t' + card['title'] + '\n'
					card['quantity'] -= depth

	return output

parser = argparse.ArgumentParser()
parser.add_argument('-2', '--revised-core', action='store_true', help='include revised core set cards')
parser.add_argument('-c', '--col', default=3, help='number of columns in a page')
parser.add_argument('-d', '--depth', default=3, help='number of cards each cell can store')
parser.add_argument('-m', '--mini', action='store_true', help='merge together neutral runner and mini factions')
parser.add_argument('-n', '--neutral', action='store_true', help='merge together neutral runner and neutral corp factions')
parser.add_argument('-r', '--row', default=3, help='number of rows in a page')
parser.add_argument('-s', '--seg', action='store_true', help='segregate each group onto separate pages')
args = parser.parse_args()

columns = int(args.col)
depth = int(args.depth)
mergeMini = args.mini
mergeNeutral = args.neutral
revisedCore = args.revised_core
rows = int(args.row)
segregate = args.seg

# Hardwire ordering that's not explicitly in the data set
corpTypes = ['identity', 'agenda', 'asset', 'operation', 'ice', 'upgrade']
runnerTypes = ['identity', 'event', 'hardware', 'program', 'resource']
miniFactions = ['apex', 'adam', 'sunny-lebeau']

# Load in data
dataDir = 'netrunner-cards-json'

cards = []
packDir = dataDir + '/pack'

try:
	packDirListing = os.listdir(packDir)
except:
	print('I can\'t find the card data.  Please try typing in the following:')
	print('git clone git@github.com:Alsciende/netrunner-cards-json.git')
	exit()

for packFilename in packDirListing:
	if packFilename[-5:] != '.json' or packFilename == 'draft.json':
		# Ignore files that shouldn't be there (e.g. Vim's swap file)
		continue

	packFilename = packDir + '/' + packFilename
	packData = json.load(open(packFilename, 'r'))

	for card in packData:
		cards.append(card)

factions = json.load(open(dataDir + '/factions.json'))

if not revisedCore:
	cardsWithoutRevisedCore = []

	for card in cards:
		if card['pack_code'] != 'core2':
			cardsWithoutRevisedCore.append(card)

	cards = cardsWithoutRevisedCore
	cardsWithoutRevisedCore = None

# Label revised core cards unambiguously; group neutral factions; merge mini factions together
for card in cards:
	if card['pack_code'] == 'core2':
		card['title'] = card['title'] + ' (revised core)'

	if mergeNeutral:
		if card['faction_code'] in ['neutral-runner', 'neutral-corp']:
			card['faction_code'] = 'neutral'

	for faction in factions:
		if faction['code'] != card['faction_code']:
			continue

		if faction['is_mini']:
			if card['type_code'] == 'identity':
				card['code'] = 'A' + card['code']
			elif card['type_code'] == 'event':
				card['code'] = 'B' + card['code']
			elif card['type_code'] == 'hardware':
				card['code'] = 'C' + card['code']
			elif card['type_code'] == 'program':
				card['code'] = 'D' + card['code']
			elif card['type_code'] == 'resource':
				card['code'] = 'E' + card['code']

			card['type_code'] = card['faction_code']
			card['side_code'] = 'runner_mini'

			if mergeMini and mergeNeutral:
				card['faction_code'] = 'neutral'
			elif mergeMini:
				card['faction_code'] = 'neutral-runner'
			else:
				card['faction_code'] = 'mini'

index(segregate)
exit()
