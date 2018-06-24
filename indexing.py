#!/usr/local/bin/python3

# Indexing (an Android: Netrunner card sorter)

import json
import os

def flattenToList(multiDict, value, order=False):
	if not order:
		order = value

	# Order...
	multiDict = sorted(multiDict, key=lambda item: item[order])

	# ...and extract
	list = []

	for entry in multiDict:
		entryValue = entry[value]
		list.append(entryValue)

	return list

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
		if segregate:
			file = open('binders/segged/' + faction + '.txt', 'w+')
		else:
			file = open('binders/defragged/' + faction + '.txt', 'w+')

		cardsByType = group(inFactionCards, 'type_code')
		sideOrder = inFactionCards[1]['side_code']
		page = 0
		cardNumber = 9

		if sideOrder == 'runner':
			types = ['identity', 'event', 'hardware', 'program', 'resource', 'apex', 'adam', 'sunny-lebeau']
		elif sideOrder == 'corp':
			types = ['identity', 'agenda', 'asset', 'operation', 'ice', 'upgrade']
		else:
			continue

		for type in types:
			for typeMatch, inTypeCards in cardsByType.items():
				if typeMatch != type:
					continue

				inTypeCards = flattenToList(inTypeCards, 'title', 'code')

				if segregate:
					cardNumber = 9

				for cardName in inTypeCards:
					cardNumber = cardNumber + 1

					if cardNumber == 10:
						cardNumber = 1
						page = page + 1

						if page != 1:
							file.write('\n')

						if segregate:
							file.write('Page ' + str(page) + ' (' + type + ')\n\n')
						else:
							file.write('Page ' + str(page) + '\n\n')

					file.write('\t' + cardName + '\n')

		file.close()

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

# Merge mini factions together
for card in cards:
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
			card['faction_code'] = 'mini'

index(True)
index(False)

exit()
