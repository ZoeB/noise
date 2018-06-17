#!/usr/local/bin/python3

# Noise (an Android: Netrunner deck builder)

import collections
import json
import os
import re
import textwrap

# Define interface
class Interface:
	errorBuffer = []
	outputBuffer = []

	def addError(self, error):
		self.errorBuffer.append(error)

	def addOutput(self, output):
		self.outputBuffer.append(output)

	def clearErrors(self):
		self.errorBuffer = []

	def clearOutputs(self):
		self.outputBuffer = []

	def output(self, messages):
		if not messages:
			return

		for message in messages:
			print(message)

	def printErrors(self):
		print('\033[0;31m', end='')
		self.output(self.errorBuffer)
		self.clearErrors()
		print('\033[0m', end='')

	def printOutputs(self):
		self.output(self.outputBuffer)
		self.clearOutputs()

	def returnOutput(self):
		output = self.outputBuffer
		self.clearOutputs()
		return output

# Define functions
def addCard(card):
	if card['type_code'] == 'identity':
		io.addError('Be an identity, don\'t add the identity')
		return False

	if not identity:
		io.addError('Be an identity before adding things')
		return False

	# Don't add out-of-side cards
	if card['side_code'] != identity['side_code']:
		io.addError('Pick a side')
		return False

	# Don't add out-of-faction agendas
	if card['type_code'] == 'agenda' and not card['faction_code'] in [identity['faction_code'], 'neutral-corp']:
		io.addError('You can only add neutral and in-faction agendas')
		return False

	cardName = card['title']

	if not cardName in deck:
		deck[cardName] = card # Add the first copy of this card to the deck
		deck[cardName]['quantity'] = 1
		return True
	elif deck[cardName]['quantity'] == card['deck_limit']:
		return False
	else:
		deck[cardName]['quantity'] += 1 # Add another copy of this card to the deck
		return True

def addCards(item, quantity=False):
	if not item:
		return False

	if not item:
		return False

	for card in cards:
		if card['title'] == item:
			break

	if card['title'] != item:
		return False

	if not quantity:
		quantity = int(card['quantity'])

	for i in range(quantity):
		success = addCard(card)

		if not success:
			break

def addCycle(item):
	if not item in cyclesFlipped:
		return False

	cycleCode = cyclesFlipped[item]

	for pack in packs:
		if pack['cycle_code'] == cycleCode:
			addPack(pack['name'])

def addPack(item):
	if not item in packsFlipped:
		return False

	packCode = packsFlipped[item]

	for card in cards:
		if card['pack_code'] == packCode:
			for i in range(int(card['quantity'])):
				success = addCard(card)
				io.clearErrors()

				if not success:
					break

def describe(item):
	if not item:
		return False

	if item == 'cycles':
		describeCycles()
	if item == 'decks':
		describeDecks()
	if item == 'sides':
		describeSides()
	else:
		describeCard(item) or describePack(item) or describeCycle(item) or describeFaction(item) or describeSide(item) or describeDeck(item) # Try packs before cycles, for those that are both

def describeCard(item):
	if not item:
		return False

	for card in cards:
		if card['title'] == item:
			break

	if card['title'] != item:
		return False

	if card['uniqueness']:
		io.addOutput(format(card['title']) + ' (Unique)')
	else:
		io.addOutput(format(card['title']))

	for key in ['type_code', 'keywords', 'faction_code', 'cost', 'faction_cost', 'text', 'flavor']:
		if key not in card:
			continue

		if key in ['cost', 'faction_cost']:
			text = str(card[key])
		elif key in ['faction_code', 'type_code']:
			text = card[key]
		else:
			text = format(card[key])

		if not text:
			continue

		if key == 'faction_code':
			io.addOutput(factionsDict[text])
		elif key == 'type_code':
			io.addOutput(typesDict[text])
		elif key == 'cost':
			io.addOutput('Cost: ' + text)
		elif key == 'faction_cost':
			if not identity or card['faction_code'] != identity['faction_code']:
				io.addOutput('Influence value: ' + text)
		else:
			io.addOutput(text)

	return True

def describeCycle(item):
	if not item:
		return False

	for cycle in cycles:
		if cycle['name'] == item:
			break

	if cycle['name'] != item:
		return False

	io.addOutput('The ' + cycle['name'] + ' cycle has the following packs:')

	for pack in packs:
		if pack['cycle_code'] == cycle['code']:
			io.addOutput(pack['name'])

	return True

def describeCycles():
	io.addOutput('Android: Netrunner has the following cycles:')

	for cycle in cycles:
		io.addOutput(cycle['name'])

	return True

def describeDeck(item):
	if not item:
		return False

	for deck in prebuiltDecks:
		if deck['name'] == item:
			break

	if deck['name'] != item:
		return False

	io.addOutput('The ' + deck['name'] + ' deck has the following cards:')

	for cardCode, quantity in deck['cards'].items():
		for card in cards:
			if card['code'] == cardCode:
				io.addOutput(str(quantity) + 'x ' + card['title'])
				break

	return True

def describeDecks():
	io.addOutput('Android: Netrunner has the following prebuilt decks:')

	for prebuiltDeck in prebuiltDecks:
		io.addOutput(prebuiltDeck['name'])

	return True

def describeFaction(item):
	if not item:
		return False

	for faction in factions:
		if faction['name'] == item:
			break

	if faction['name'] != item:
		return False

	io.addOutput('The ' + faction['name'] + ' faction has the following IDs:')

	for card in cards:
		if card['faction_code'] == faction['code'] and card['type_code'] == 'identity':
			io.addOutput(card['title'])

	return True

def describePack(item):
	if not item:
		return False

	for pack in packs:
		if pack['name'] == item:
			break

	if pack['name'] != item:
		return False

	io.addOutput('The ' + pack['name'] + ' pack has the following cards:')

	for card in cards:
		if card['pack_code'] == pack['code']:
			io.addOutput(card['title'])

	return True

def describeSide(item):
	if not item:
		return False

	for side in sides:
		if side['name'] == item:
			break

	if side['name'] != item:
		return False

	io.addOutput('The ' + side['name'] + ' side has the following factions:')

	for faction in factions:
		if faction['side_code'] == side['code']:
			if faction['is_mini']:
				io.addOutput(faction['name'] + ' (Mini)')
			else:
				io.addOutput(faction['name'])

	return True

def describeSides():
	io.addOutput('The two sides are Corp and Runner.')

def flattenToDict(multiDict, key, value):
	singleDict = {}

	for entry in multiDict:
		entryKey = entry[key]
		entryValue = entry[value]
		singleDict[entryKey] = entryValue

	return singleDict

def flattenToList(multiDict, value):
	list = []

	for entry in multiDict:
		entryValue = entry[value]
		list.append(entryValue)

	return list

def flipDict(dictionary):
	return {value: key for key, value in dictionary.items()} # From https://stackoverflow.com/a/483833

def format(text):
	# Bold text
	text = text.replace('<strong>', '\033[1m')
	text = text.replace('</strong>', '\033[0m')

	# Champions, errata
	for keyword in ['champion', 'errata']:
		text = re.sub('[\n]?<' + keyword + '>.*<\/' + keyword + '>', '', text)

	# Clicks
	text = text.replace('[click], [click], [click]', '3 clicks')
	text = text.replace('[click], [click]', '2 clicks')
	text = re.sub('^\[click\]', 'Click', text)
	text = text.replace('\n[click]', '\nClick')
	text = text.replace('[click]', 'click')

	# Credits, recurring credits
	for find, replace in {'recurring-credit':'recurring credit', 'credit':'credit'}.items():
		text = re.sub('^1\[' + find + '\]', '1 ' + replace, text)
		text = re.sub('\n1\[' + find + '\]', '\n1 ' + replace, text)
		text = text.replace('[' + find + ']', ' ' + replace + 's')

	# Factions
	for find, replace in factionsDict.items():
		text = text.replace('[' + find + ']', replace)

	# Link, MU, trace
	for find, replace in {'[link]':' link', '[mu]':' MU', '<trace>':'', '</trace>':':'}.items():
		text = text.replace(find, replace)

	# Subroutines
	text = text.replace('[subroutine]', 'Subroutine:')

	# Trash
	text = re.sub('^\[trash\]', 'Trash', text)
	text = text.replace('\n[trash]', '\nTrash')
	text = text.replace('[trash]', 'trash')

	# Punctuation
	text = text.replace('…', '...')

	# Word wrap
	text = str.join('\n', textwrap.wrap(text, 72))

	return text

def getDeckName():
	if deckName:
		io.addOutput(deckName)
	else:
		io.addError('You haven\'t yet named your deck')

def getIdentity():
	if identity:
		io.addOutput(identity['title'])
	else:
		io.addError('You aren\'t anyone yet')

def help():
	io.addOutput('Commands:')

	for command, arguments in validCommandVerbs.items():
		io.addOutput(command + ' ' + arguments)

	io.addOutput('Try describing sides, cycles, or decks, then exploring the results.')

def listDeck():
	output = []
	cards = 0
	influenceSpent = 0
	orderedDeck = collections.OrderedDict(sorted(deck.items()))
	typeTallies = tallyTypes(deck)

	for typeCode, typeQuantity in typeTallies.items():
		typeName = typesDict[typeCode]
		output.append(typeName + ' (' + str(typeQuantity) + ')')

		for cardName, card in orderedDeck.items():
			if card['type_code'] != typeCode:
				continue

			if card['faction_code'] != identity['faction_code']:
				influenceCost = int(card['faction_cost']) * int(card['quantity'])
				influenceSpent += influenceCost
				output.append(str(card['quantity']) + 'x ' + cardName + ' (' + str(influenceCost) + ' influence value)')
			else:
				output.append(str(card['quantity']) + 'x ' + cardName)

			cards += int(card['quantity'])

		output.append('')

	for line in output:
		io.addOutput(line)

	if identity:
		io.addOutput(str(influenceSpent) + ' influence spent (max ' + str(identity['influence_limit']) + ', available ' + str(identity['influence_limit'] - influenceSpent) + ')')
		io.addOutput(str(cards) + ' cards (min ' + str(identity['minimum_deck_size']) + ')')

def listDeckFiles():
	deckFilenames = os.listdir('decks')

	for deckFilename in deckFilenames:
		io.addOutput(deckFilename)

def listDeckInJintekiFormat():
	orderedDeck = collections.OrderedDict(sorted(deck.items()))

	for cardName, card in orderedDeck.items():
		io.addOutput(str(card['quantity']) + ' ' + cardName)

def listKeys(dict):
	return list(dict.keys())

# Either returns the one exact match, or prints the multiple / zero matches
def match(name, type):
	if not name or not type:
		return

	name = name.lower()

	if type == 'card':
		list = cardsList
	if type == 'command':
		list = validCommandVerbsList
	elif type == 'cycle':
		list = cyclesList
	elif type == 'deck':
		list = listKeys(deck)
	elif type == 'faction':
		list = factionsList
	elif type == 'identity':
		list = identitiesList
	elif type == 'pack':
		list = packsList
	elif type == 'prebuiltDeck':
		list = prebuiltDecksList
	elif type == 'side':
		list = sidesList
	elif type == 'describable':
		list = itemsList + ['cycles', 'decks', 'sides']
	else:
		list = itemsList

	# First, try to find an exact match
	for item in list:
		if name == item.lower():
			return item

	# Second, try to find a partial match
	matches = []

	for item in list:
		if name in item.lower():
			matches.append(item)

	# A single partial match was found
	if len(matches) == 1:
		return matches.pop()

	# Multiple partial matches were found
	if matches:
		io.addError('Multiple matches:')

		for match in matches:
			io.addError(match)

		return False

	# No matches were found
	io.addError('No matches')
	return False

def purge():
	global deck
	deck = {}

def read(filename):
	if not filename:
		return

	if filename[-4:] == '.jin':
		readJinteki(filename)
	elif filename[-4:] == '.txt':
		readText(filename)
	else:
		filename = str(filename) + '.txt'
		readText(filename)

def readJinteki(filename):
	if not filename:
		return

	pass

def readText(filename):
	if not filename:
		return

	if '/' not in filename:
		filename = 'decks/' + filename

	try:
		file = open(os.path.expanduser(filename))
	except:
		io.addError('Sorry, I couldn\'t read that file')
		return

	lines = file.readlines()
	cleanLines = []

	for line in lines:
		for nuisance in ['●', '🦄']:
			line = line.replace(nuisance, '')
			locationOfRemovableEnding = line.find(' (')

			if locationOfRemovableEnding != -1:
				line = line[:locationOfRemovableEnding]

		line = line.strip()

		if line != '':
			cleanLines.append(line)

	setDeckName(cleanLines[0])
	setIdentity(cleanLines[1])
	cleanLines = cleanLines[2:]

	for cleanLine in cleanLines:
		if len(cleanLine) > 3 and cleanLine[1:3] == 'x ':
			addCards(cleanLine[3:], int(cleanLine[0]))

	file.close()
	io.addOutput(filename + ' read')

def removeCard(item, quantity=False):
	global deck

	if not item:
		return False

	item = match(item, 'deck')

	if not item:
		return False

	if not item in deck:
		return False

	if quantity and deck[item]['quantity'] > quantity:
		deck[item]['quantity'] -= quantity
	else:
		del deck[item]

def setDeckName(newDeckName):
	global deckName

	deckName = newDeckName

def setIdentity(item):
	global identity

	item = match(item, 'identity')

	if not item:
		return False

	for card in cards:
		if card['title'] == item:
			break

	if card['title'] != item:
		return False

	if card['type_code'] != 'identity':
		return False

	if identity and card['side_code'] != identity['side_code']:
		purge()

	identity = card
	return True

def subset(cards, typeCode):
	subset = []

	for card in cards:
		if card['type_code'] == typeCode:
			subset.append(card)

	return subset

def tallyTypes(cards):
	types = {}

	for cardName, card in cards.items():
		if not 'type_code' in card:
			continue

		typeCode = card['type_code']

		if typeCode in types:
			types[typeCode] += int(card['quantity'])
		else:
			types[typeCode] = int(card['quantity'])

	return types

def use(item):
	if not item in prebuiltDecksList:
		return False

	for deck in prebuiltDecks:
		if deck['name'] == item:
			break

	if deck['name'] != item:
		return False

	# First, be the ID
	for cardCode, quantity in deck['cards'].items():
		for card in cards:
			if card['code'] == cardCode and card['type_code'] == 'identity':
				setIdentity(card['title'])
				break # break 2 would be ideal

	# Second, add the other cards
	for cardCode, quantity in deck['cards'].items():
		for card in cards:
			if card['code'] == cardCode and card['type_code'] != 'identity':
				addCards(card['title'], quantity)
				break

def write(filename=False):
	if not filename:
		filename = 'decks/' + deckName

	if filename[-4:] == '.jin':
		format = 'Jinteki'
	elif filename[-4:] == '.txt':
		format = 'Text'
	else:
		filename = str(filename) + '.txt'
		format = 'Text'

	if '/' not in filename:
		filename = 'decks/' + filename

	try:
		file = open(os.path.expanduser(filename), 'w+')
	except:
		io.addError('Sorry, I couldn\'t open that file')
		return

	getDeckName()
	io.addOutput('')
	getIdentity()
	io.addOutput('')

	if format == 'Jinteki':
		listDeckInJintekiFormat()
	else:
		listDeck()

	file.write(str.join('\n', io.returnOutput()))
	file.close()
	io.addOutput(filename + ' written')

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

cycles = json.load(open(dataDir + '/cycles.json'))
factions = json.load(open(dataDir + '/factions.json'))
packs = json.load(open(dataDir + '/packs.json'))
prebuiltDecks = json.load(open(dataDir + '/prebuilts.json'))
sides = json.load(open(dataDir + '/sides.json'))
types = json.load(open(dataDir + '/types.json'))

factionsDict = flattenToDict(factions, 'code', 'name')
cyclesDict = flattenToDict(cycles, 'code', 'name')
packsDict = flattenToDict(packs, 'code', 'name')
sidesDict = flattenToDict(sides, 'code', 'name')
typesDict = flattenToDict(types, 'code', 'name')

cyclesFlipped = flipDict(cyclesDict)
packsFlipped = flipDict(packsDict)

cardsList = sorted(set(flattenToList(cards, 'title')))
cyclesList = sorted(set(flattenToList(cycles, 'name')))
factionsList = sorted(set(flattenToList(factions, 'name')))
packsList = sorted(set(flattenToList(packs, 'name')))
prebuiltDecksList = sorted(set(flattenToList(prebuiltDecks, 'name')))
sidesList = sorted(set(flattenToList(sides, 'name')))

itemsList = sorted(set(cardsList + cyclesList + factionsList + packsList + sidesList + prebuiltDecksList))

identitiesList = sorted(set(flattenToList(subset(cards, 'identity'), 'title')))

# Make deck directory, if necessary
if not os.path.exists('decks'):
	os.makedirs('decks')

# Setup
deck = {}
deckName = False
identity = False
io = Interface()

validCommandVerbs = {'add':'[card]', 'describe':'[card, pack, cycle]', 'files':'', 'help':'', 'id':'[card]', 'jinlist':'', 'list':'', 'name':'[name your deck]', 'purge':'', 'quit':'', 'read':'[filename]', 'remove':'[card]', 'use':'[deck]', 'write':'[filename]'}
validCommandVerbsList = listKeys(validCommandVerbs)

while True:
	# Split command by whitespace
	command = input().split()
	commandVerb = False
	commandQuantity = False
	commandProperNoun = False

	# Work out the command's verb
	if not command:
		help()
		io.printErrors()
		io.printOutputs()
		continue

	commandVerb = match(command[0].lower(), 'command')
	command = command[1:]

	if not commandVerb:
		help()
		io.printErrors()
		io.printOutputs()
		continue

	# If the second word's a single digit number, and not 0, then that's a quantity.  Pop it off.
	if command and len(command[0]) == 1 and command[0].isdigit() and int(command[0]) > 0:
		commandQuantity = int(command[0])
		command = command[1:]

	# The remainder, if there is any, is the proper noun
	if command:
		commandProperNoun = str.join(' ', command)

	if commandVerb == 'add':
		item = match(commandProperNoun, 'all')

		if item:
			addCards(item, int(commandQuantity)) or addPack(item) or addCycle(item)

	elif commandVerb == 'describe':
		describe(match(commandProperNoun, 'describable'))
	elif commandVerb == 'files':
		listDeckFiles()
	elif commandVerb == 'help':
		help()
	elif commandVerb == 'id':
		if commandProperNoun:
			setIdentity(commandProperNoun)
		else:
			getIdentity()
	elif commandVerb == 'jinlist':
		listDeckInJintekiFormat()
	elif commandVerb == 'list':
		listDeck()
	elif commandVerb == 'name':
		if commandProperNoun:
			setDeckName(commandProperNoun)
		else:
			getDeckName()
	elif commandVerb == 'purge':
		purge()
	elif commandVerb == 'quit':
		exit()
	elif commandVerb == 'read':
		if commandProperNoun:
			read(commandProperNoun)
		else:
			io.addError('Please specify a filename to read')
	elif commandVerb == 'remove':
		removeCard(commandProperNoun, int(commandQuantity))
	elif commandVerb == 'use':
		item = match(commandProperNoun, 'prebuiltDeck')

		if item:
			use(item)

	elif commandVerb == 'write':
		if commandProperNoun:
			write(commandProperNoun)
		else:
			write(commandProperNoun)

	io.printErrors()
	io.printOutputs()
