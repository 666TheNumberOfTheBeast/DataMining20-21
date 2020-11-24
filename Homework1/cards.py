# Pick the first 5 cards from the deck

import random

cardNumbers = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
cardSuits   = ['Clubs', 'Diamonds', 'Hearts', 'Spades']

def pickCard():
    randomNumber = random.choice(cardNumbers)
    randomSuit   = random.choice(cardSuits)
    randomCard   = randomNumber,randomSuit
    return randomCard

n = 5
pickedCards = []

for i in range(0,n):
    card = pickCard()

    while(card in pickedCards):
        card = pickCard()

    print(card)
    pickedCards.append(card)
