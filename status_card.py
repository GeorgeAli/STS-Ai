from spirecomm.spire.power import Power
from spirecomm.spire.card import Card, CardType
from spirecomm.spire.character import Intent
import math
#This is status_card
#Unplayed : cannot be played in your hand
def addcard(gamestate, name, pile, cardobj = False):
    newstate = gamestate
    #newcard = card(name, name, card_type, "", upgrades=0, has_target=False, cost=0, uuid="", misc=0, price=0, is_playable=False, exhausts=False):
    if not isinstance(cardobj, bool):
        newcard = cardobj
    else:
        newcard = Card(name = name, upgrades = 0, cost = cards[name][0], card_id = 'temp', card_type = 1, rarity = 'temp')
    if pile == 'discard_pile':
        newstate.discard_pile.append(newcard)
    if pile == 'hand':
        newstate.hand.append(newcard)
    if pile == 'draw_pile':
        newstate.hand.append(newcard)
    if pile == 'exhaust_pile':
        newstate.exhaust_pile.append(newcard)

        for power_player in newstate.player.powers:
            #dark embrace Whenever a card is Exhausted, draw 1 card.
            if power_player.power_name == "Dark Embrace":
                newstate = draw(newstate, 1)

            #feel no pain Whenever a card is Exhausted, gain 3 Block.
            if power_player.power_name == "Feel No Pain":
                newstate = addblock(newstate, power_player.amount)

            #sentinel Gain 5 Block. If this card is Exhausted, gain 2(3) energy.
            if power_player.power_name == "Sentinel":
                newstate.player.energy = newstate.player.energy + powers.amount

    return newstate
#Slimed : Exhuast
def Slimed(gamastate, upgrade):
  newstate = gamestate
  newstate = addcard(newstate ,"Slimed",'exhuast_plie')
  return newstate

def Burn(gamastate,upgrade):
    newstate = gamestate
    return newstate
    
def Dazed(gamastate, upgrade):
    newstate = gamestate
    return newstate

def Wound(gamastate, upgrade):
    newstate = gamestate
    return newstate
    
def Void(gamastate, upgrade):
    newstate = gamestate
    return newstate

#dict of cards
#cost, target, function, type, ethereal
#target true = card can target enemy
#target false = card just gets played
#type = A for Attack,  P for Power, S for Skill, ST for Status
#ethereal = whether the card is exhausted after end of turn
#choose_headbut(), choose_armaments() = False, if not need

# unplayable_card cost?
cards = {
'Slimed' : [1, False, Slimed, 'ST', False, False],
'Burn' : [0, False, Burn, 'ST', False, False],
'Dazed' : [0, False, Dazed, 'ST', True, False],
'Wound' : [0, False, Wound, 'ST', False, False],
'Void' : [0, False, Void, 'ST', True, False],

}
