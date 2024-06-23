
import copy
import random
import os, sys
#from maxtree import SimGame
from spirecomm.spire.power import Power
from spirecomm.spire.card import Card, CardType
from spirecomm.spire.character import Intent
import math
#THIS IS PARTLY PSEUDOCODE
#WEAK AND VULNERABLE APPLIES AFTER STRENGTH
class Card:
    def __init__(self, card_id, name, card_type, rarity, upgrades=0, has_target=False, cost=0, uuid="", misc=0, price=0, is_playable=False, exhausts=False):
        self.card_id = card_id
        self.name = name
        self.type = card_type
        self.rarity = rarity
        self.upgrades = upgrades
        self.has_target = has_target
        self.cost = cost
        self.uuid = uuid
        self.misc = misc
        self.price = price
        self.is_playable = is_playable
        self.exhausts = exhausts

def dealdmg(gamestate, damage, monster, attacknum = 1):
    newstate = gamestate

    for pplayer in newstate.player.powers:
        if pplayer.power_name == "Strength":
            damage += pplayer.amount
    for pplayer in newstate.player.powers:
        if pplayer.power_name == "Weakened":
            #round down
            damage = math.floor(damage * 0.75)

    #debugging
    # original_stdout = sys.stdout
    # with open('dealdmg.txt', 'w') as f:
    #     sys.stdout = f
    #     print('param monster = ' + str(monster))
    #     for index, object in enumerate(newstate.monsters):
    #         print('index = ' + str(index) +' monster = ' + object.name)
    # sys.stdout = original_stdout


    for pmonster in newstate.monsters[monster].powers:
        if pmonster.power_name == "Vulnerable":
            #round down
            damage = math.floor(damage * 1.5)

    #rage 0 cost Whenever you play an Attack this turn, gain 3 Block
    ####

    ### THIS SHOULD NOT BE HERE, Attack refers to the type of card, not damage dealt

    ###
    # for p_player in newstate.player.powers:
    #     if p_player.power_name == "Rage":
    #         newstate = addblock(newstate, p_player.amount)

    #double tap  This turn, your next 1(2) Attack is played twice.
    for power_player in newstate.player.powers:
        if power_player.power_name == "Double Tap":
            attacknum = attacknum+attacknum
            power_player.amount = power_player.amount - 1
            if power_player.amount == 0:
                newstate.player.powers.remove(power_player)

    for x in range(attacknum):
    
    #need to check block. if block is existed, reduce block. Not the HP
        if newstate.monsters[monster].block > 0 :
            if newstate.monsters[monster].block < damage:
                # remain
                left = damage - newstate.monsters[monster].block

                newstate.monsters[monster].block = 0
                newstate.monsters[monster].current_hp -= left
                # if newstate.monsters[monster].current_hp <= 0:
                #     newstate.monsters.remove(newstate.monsters[monster])
                #     return newstate

        else:
            newstate.monsters[monster].current_hp -= damage
            # if newstate.monsters[monster].current_hp <= 0:
                # newstate.monsters.remove(newstate.monsters[monster])
                # return newstate

    return newstate

# monster.move_base_damage = basic damage without monster.powers
# monster.move_adjust_damage = damage applied monster.powers
# monswer.move_hit = attack_num
# if monster is dead move_base_damage = -1, and move_adjust_damage = -1
def player_take_damage(gamestate):

    newstate = gamestate

    #check all monsters
    for monster in range(len(newstate.monsters)):
        # check is_monster_dead
    	if not newstate.monsters[monster].is_gone:
            # Attack n times
            for attackmum in range(newstate.monsters[monster].move_hits):
                # lose block first
                if newstate.player.block > 0:
                    if newstate.monsters[monster].block < newstate.monsters[monster].move_adjusted_damage:
                        left = newstate.monsters[monster].move_adjusted_damage - newstate.player.block
                        newstate.player.block = 0
                        newstate.player.current_hp - left
                    else:
                        newstate.player.block -= newstate.monsters[monster].move_adjusted_damage
            	# lose hp if no block
                else:
                    newstate.player.current_hp -= newstate.monsters[monster].move_adjusted_damage
            	#flame barrier 2 cost Gain 12 Block. Whenever you are attacked this turn, deal 4 damage to the attacker.
                for player_power in newstate.player.powers:
                    if player_power.power_name == "Flame Barrier":
                        newstate = dealdmg(newstate, player_power.amount, monster)
    # only this turn
    for player_power in newstate.player.powers:
        if player_power.power_name == "Flame Barrier":
            newstate.player.powers.remove(player_power)

    return newstate

def healing(newstate, amount):
    newstate = gamestate
    newstate.player.current_hp += amount
    return newstate

# Dexterity is applied before Frail.
def addblock(gamestate, block):
    newstate = gamestate

    for debuff_player in newstate.player.powers:
        if debuff_player.power_name == "Frail":
        #round down
           block = math.floor(block * 0.75)

    for player_power in newstate.player.powers:
        if player_power.power_name == "Dexterity":
            newstate.player.block += player_power.amount
        #juggernaut dealdmg to random monster
        if player_power.power_name == "Juggernaut":
            x = random.randrange(len(newstate.monsters))
            newstate = dealdmg(newstate, player_power.amount, newstate.monsters[x])
    #add block
    newstate.player.block += block

    return newstate

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

def dealvulnerable(gamestate, amount, monster):
    newstate = gamestate


    for pmonster in newstate.monsters[monster].powers:
        if pmonster.power_name == 'Vulnerable':
            pmonster.amount += amount
            return newstate

    newvulnerable = Power('Vulnerable', 'Vulnerable', amount)
    newstate.monsters[monster].powers.append(newvulnerable)

    return newstate

def dealweak(gamestate, amount, monster):
    newstate = gamestate
            
    for pmonster in newstate.monsters[monster].powers:
        if pmonster.power_name == 'Weakened':
            pmonster.amount += amount
            return newstate

    newvulnerable = Power('Weakened', 'Weakened', amount)
    newstate.monsters[monster].powers.append(newvulnerable)

    return newstate

def player_gain_strength(gamestate, amount):
    newstate = gamestate

    is_it_exisited = False

    for power_player in newstate.player.powers:
        if power_player.power_name == "Strength":
            power_player.amount = power_player.amount + amount
            is_it_exisited = True

    if not is_it_exisited:
        New_power = Power("Strength", "Strength", amount)
        New_power.just_applied = True
        newstate.player.powers.append(New_power)

    return newstate

def monster_lose_strength(gamestate, amount, monster):
    newstate = gamestate

    for power_monster in newstate.monsters[monster].powers:
        if power_monster.power_name == "Strength":
            power_monster.amount = power_monster.amount - amount

    return newstate


def draw(gamestate, amount):
    newstate = gamestate

    #check deck
    #if not enough cards add discards_pile to deck, and reset discard_pile
    can_draw = True # it is for "Battle Trance", which is cannot draw card for this turn

    for power_player in newstate.player.powers:
         if power_player.power_name == "No Draw":
             can_draw = False

    left = amount - len(newstate.draw_pile)

    # original_stdout_ = sys.stdout
    """
    with open('a0_test.txt', 'a') as f:
         sys.stdout = f  # Change the standard output to the file we created.
         print("AMOUNT: "+str(amount))
         print("DRAW_PILE: "+str(len(gamestate.draw_pile)))
         print("DISCARD_PILE: " + str(len(gamestate.discard_pile)))
         print("LEFT: " + str(left))
         print("hand: " + str(len(newstate.hand)))
         #if len(newstate.draw_pile) == 0:
         # add discard_pile to draw_pile
            #newstate.draw_pile = copy.deepcopy(newstate.discard_pile)
         # reset the discard_pile
            #newstate.discard_pile.clear()
         #print("After: ")
         #print("DRAW_PILE: "+str(len(newstate.draw_pile)))
         #print("DISCARD_PILE: " + str(len(newstate.discard_pile)))
         #for card in newstate.draw_pile:
         #    print("cardname : " + str(card.name))

         #print("LEFT: " + str(left))
         #print("hand: " + str(len(newstate.hand)))
         print("NEXT")
         print(" ")
         sys.stdout = original_stdout_  # Reset the standard output to its original value
    """
    if can_draw:

        if len(newstate.draw_pile) < amount :
            #left = amount - len(newstate.draw_pile)

            for x in range(len(newstate.draw_pile)):
                #max hand
                if len(newstate.hand) != 10:
                    # chosen_card randomly
                    cardindex = random.randrange(len(newstate.draw_pile))
                    # add chosen_card to hand
                    newstate.hand.append(newstate.draw_pile[cardindex])
                    # remove chosen_card from draw_pile
                    newstate.draw_pile.pop(cardindex)

                    #Could be infinite loops.
                    #evolve 1 cost Whenever you draw a Status, draw 1 card to fucntion called draw
                    for player_power in newstate.player.powers:
                            if player_power.power_name == "Evolve":
                                if newstate.draw_pile[cardindex].type == CardType.STATUS:
                                    newstate = draw(newstate, 1)

                    #fire breathing 1 cost Whenever you draw a Status or Curse card, deal 6(10) damage to all enemies.
                            if player_power.power_name == "Fire Breathing":
                                if newstate.draw_pile[cardindex].type == CardType.STATUS:
                                    for monster in range(len(newstate.monsters)):
                                        newstate = dealdmg(newstate, power_player.amount, monster)

                                if newstate.draw_pile[cardindex].type == CardType.CURSE:
                                    for monster in range(len(newstate.monsters)):
                                        newstate = dealdmg(newstate, power_player.amount, monster)
                """
                original_stdout_4 = sys.stdout
                with open('a1_test.txt', 'a') as e:
                     sys.stdout = e  # Change the standard output to the file we created.
                     print("AMOUNT: " + str(amount))
                     print("DRAW_PILE: "+str(len(gamestate.draw_pile)))
                     print("DISCARD_PILE: " + str(len(gamestate.discard_pile)))
                     print("LEFT: " + str(left))
                     print("hand: " + str(len(newstate.hand)))
                     #if len(newstate.draw_pile) == 0:
                     # add discard_pile to draw_pile
                        #newstate.draw_pile = copy.deepcopy(newstate.discard_pile)
                     # reset the discard_pile
                        #newstate.discard_pile.clear()
                     #print("After: ")
                     #print("DRAW_PILE: "+str(len(newstate.draw_pile)))
                     #print("DISCARD_PILE: " + str(len(newstate.discard_pile)))
                     #for card in newstate.draw_pile:
                     #    print("cardname : " + str(card.name))

                     #print("LEFT: " + str(left))
                     #print("hand: " + str(len(newstate.hand)))
                     print("NEXT")
                     print(" ")
                     sys.stdout = original_stdout_4  # Reset the standard output to its original value
            
                # add discard_pile to draw_pile
                newstate.draw_pile = copy.deepcopy(newstate.discard_pile)
                
                original_stdout_0 = sys.stdout
                with open('a2_test.txt', 'a') as b:
                     sys.stdout = b  # Change the standard output to the file we created.
                     print("AMOUNT: "+str(amount))
                     print("DRAW_PILE: "+str(len(gamestate.draw_pile)))
                     print("DISCARD_PILE: " + str(len(gamestate.discard_pile)))
                     print("LEFT: " + str(left))
                     print("hand: " + str(len(newstate.hand)))
                     #if len(newstate.draw_pile) == 0:
                     # add discard_pile to draw_pile
                        #newstate.draw_pile = copy.deepcopy(newstate.discard_pile)
                     # reset the discard_pile
                        #newstate.discard_pile.clear()
                     #print("After: ")
                     #print("DRAW_PILE: "+str(len(newstate.draw_pile)))
                     #print("DISCARD_PILE: " + str(len(newstate.discard_pile)))
                     #for card in newstate.draw_pile:
                     #    print("cardname : " + str(card.name))

                     #print("LEFT: " + str(left))
                     #print("hand: " + str(len(newstate.hand)))
                     print("NEXT")
                     print(" ")
                     sys.stdout = original_stdout_0  # Reset the standard output to its original value
                
                # reset the discard_pile
                newstate.discard_pile.clear()
            
            for x in range(left):
                #max hand
                if len(newstate.hand) != 10:
                    
                    original_stdout_1 = sys.stdout
                    with open('a3_test.txt', 'a') as c:
                         sys.stdout = c  # Change the standard output to the file we created.
                         print("AMOUNT: "+str(amount))
                         print("DRAW_PILE: "+str(len(gamestate.draw_pile)))
                         print("DISCARD_PILE: " + str(len(gamestate.discard_pile)))
                         print("LEFT: " + str(left))
                         print("hand: " + str(len(newstate.hand)))
                         #if len(newstate.draw_pile) == 0:
                         # add discard_pile to draw_pile
                            #newstate.draw_pile = copy.deepcopy(newstate.discard_pile)
                         # reset the discard_pile
                            #newstate.discard_pile.clear()
                         #print("After: ")
                         #print("DRAW_PILE: "+str(len(newstate.draw_pile)))
                         #print("DISCARD_PILE: " + str(len(newstate.discard_pile)))
                         #for card in newstate.draw_pile:
                         #    print("cardname : " + str(card.name))

                         #print("LEFT: " + str(left))
                         #print("hand: " + str(len(newstate.hand)))
                         print("NEXT")
                         print(" ")
                         sys.stdout = original_stdout_1  # Reset the standard output to its original value
                    
                    # chosen_card randomly
                    cardindex = random.randrange(len(newstate.draw_pile))
                    # add chosen_card to hand

                    newstate.hand.append(newstate.draw_pile[cardindex])
                    #evolve 1 cost Whenever you draw a Status, draw 1 card to fucntion called draw
                    # remove chosen_card from draw_pile
                    newstate.draw_pile.pop(cardindex)

                    for player_power in newstate.player.powers:
                        if player_power.power_name == "Evolve":
                            if newstate.draw_pile[cardindex].type == CardType.STATUS:
                                    newstate = draw(newstate, 1)

                    #fire breathing 1 cost Whenever you draw a Status or Curse card, deal 6(10) damage to all enemies.
                            if player_power.power_name == "Fire Breathing":
                                if newstate.draw_pile[cardindex].type == CardType.STATUS:
                                    newstate = draw(newstate, 1)
                                if newstate.draw_pile[cardindex].type == CardType.CURSE:
                                    newstate = draw(newstate, 1)
                    """
                

        else:
            for x in range(amount):
                #max hand
                if len(newstate.hand) != 10:
                    # chosen_card randomly
                    cardindex = random.randrange(len(newstate.draw_pile))
                    # add chosen_card to hand
                    newstate.hand.append(newstate.draw_pile[cardindex])
                    # remove chosen_card from draw_pile
                    newstate.draw_pile.pop(cardindex)


    if len(newstate.draw_pile) == 0:
        # add discard_pile to draw_pile
        newstate.draw_pile = copy.deepcopy(newstate.discard_pile)
        # reset the discard_pile
        newstate.discard_pile.clear()


    return newstate

def upgrade(card):
    if card.name == "Searing Blow":
        card.upgrades += 1
    elif card.upgrades > 1:
        card.upgrades = 1
    return card


# Effect at end of turn
def end_of_turn(gamestate):
    newstate = gamestate

    # Take demage from the monsters
    newstate = player_take_damage(newstate)

    #check
    #Pride : Innate, Ate the end of turn, put a copy of this card on top of your draw pile. Exhuast
	#Innate : Start each combat with this card in your hand
    ##what does this do? -anthony
    Pride = False
    for card in newstate.hand:
        if card.name == "Pride":
              Pride = True

    #combust At the end of your turn, lose 1 HP and deal 5 damage to ALL enemies
    for power_player in newstate.player.powers:
        if power_player.power_name == "Combust":
            newstate.player.current_hp -= power_player.powers.damage
            #deal power_player.amount dmage to All
            for monster in range(len(newstate.monsters)):
                newstate = dealdmg(newstate, power_player.amount, monster)

            #rupture 1 cost Whenever you lose HP from a card, gain 1 Strength
            for player_power in newstate.player.powers:
                if player_power.power_name == "Rupture":
                    newstate = player_gain_strength(newstate, player_power.amount)

    #flex At the end of your turn, lose 2(4) Strength.
        if power_player.power_name == "Flex":
            newstate = player_gain_strength(newstate, power_player.amount)

    #metallicize At the end of your turn, gain 3(4) Block.
        if power_player.power_name == "Metallicize":
            newstate = addblock(newstate, power_player.amount)

    #deal poison damage, reduces poison stack
    #monster
    for monster in range(len(newstate.monsters)):
        for pmonster in newstate.monsters[monster].powers:
            if pmonster.power_name == "Poison":
                if newstate.monsters[monster].block > 0:
                    if newstate.monsters[monster].block < pmonster.amount:
                        left = pmonster.amount - newstate.monsters[monster].block
                        newstate.monsters[monster].block = 0
                        newstate.monsters[monster].current_hp - left
                    else:
                        newstate.monsters[monster].block -= pmonster.amount
                else:
                    newstate.monsters[monster].current_hp -= pmonster.amount
    #player
    for power_player in newstate.player.powers:
        if power_player.power_name == "Poison":
            # if moster has block reduce block, instead of current HP
            if newstate.player.block > 0 :
                if newstate.player.block < power_player.amount:
                    left = power_player.amount - newstate.player.block
                    newstate.player.block = 0
                    newstate.player.current_hp -= power_player.amount
                else:
                    newstate.player.block -= power_player.amount
            else:
                newstate.player.current_hp -= power_player.amunt

    #lose buff, and debuff
    for power_player in newstate.player.powers:

        if power_player.power_name == "Strength":
            if power_player.amount > 0:
                power_player.amount -= 1

        if power_player.power_name == "Weakened":
            if power_player.amount > 0:
                power_player.amount -= 1

        if power_player.power_name =="Vulnerable":
            if power_player.amount > 0:
                power_player.amount -= 1

        if power_player.power_name == "Dexterity":
            #buff
            if power_player.amount > 0:
                power_player.amount -= 1
            #debuff
            elif power_player.amount <0:
                power_player.amount += 1

        if power_player.power_name == "Frail":
            if power_player.amount > 0:
                power_player.amount -= 1
    for m in newstate.monsters:
        for power_monster in m.powers:

            if power_monster.power_name == "Strength":
                if power_monster.amount > 0:
                    power_monster.amount -= 1

            if power_monster.power_name == "Weakened":
                if power_monster.amount > 0:
                    power_monster.amount -= 1

            if power_monster.power_name == "Vulnerable":
                if power_monster.amount > 0:
                    power_monster.amount -= 1

            if power_monster.power_name == "Dexterity":
                #buff
                if power_monster.amount > 0:
                    power_monster.amount -= 1
            #debuff
            elif power_monster.amount < 0:
                power_monster.amount += 1

            if power_monster.power_name == "Frail":
                if ppower_monster.amount > 0:
                    power_monster.amount -= 1

    # Lose moster blocks
    for monster in range(len(newstate.monsters)):
        newstate.monsters[monster].block = 0



    #ethereal check, if card is ethereal, exhaust it
    #ethereal : If you manage to discard the card from your hand, it won't get Exhausted.
    for card in newstate.hand:
        if card.name in ['Apparition', "Ascender's Bane", 'Carnage', "Ascender's Bane+", 'Carnage+', 'Clumsy', 'Clumsy+', 'Dazed', 'Dazed+', 'Echo Form', 'Ghostly Armor', 'Ghostly Armor+', 'Void', 'Void+', 'Deva Form']:
            newstate = addcard(newstate, card.name, 'exhaust_pile', card)
            newstate.hand.remove(card)
        else:
            newstate = addcard(newstate, card.name, 'discard_pile', card)
            newstate.hand.remove(card)

    return newstate

def start_of_turn(gamestate):
    newstate = gamestate

    #reset energy/mana
    newstate.player.energy = 3
    for player_power in newstate.player.powers:
        if player_power.power_name == "Energized":
            newstate.player.energy = newstate.player.energy + player_power.amount

    #at the start of your turn, Block no longer expires
    # else do reset the block
    barricadetrigger = False
    for player_power in newstate.player.powers:
        if player_power.power_name == "Barricade":
            # keep the block
            barricadetrigger = True

    if not barricadetrigger:
        newstate.player.block = 0
    #demon form 3 cost At the start of each turn, gain 2 Strength.
    for player_power in newstate.player.powers:
        if player_power.power_name == "Demon Form":
            newstate = player_gain_strength(newstate, player_power.amount)

    #brutality 0 cost (Innate.) At the start of your turn, lose 1 HP and draw 1 card.
    #Warning : Even if player has block, lose hp
        if player_power.power_name == "Brutality":
            newstate.player.current_hp -= 1
            newstate = draw(newstate, 1)

            #rupture 1 cost Whenever you lose HP from a card, gain 1 Strength
            for player_power in newstate.player.powers:
                if player_power.power_name == "Rupture":
                    newstate = player_gain_strength(newstate, player_power.amount)

    #Draw Cards initial is 5
    newstate = draw(newstate, 5)

    return newstate


#anger 0 cost Deal 6 damage. Add a copy of this card to your discard pile.
def Anger(gamestate, hitmonster, Upgrade):
    #gamestate class = Game (Object)
    #hitmonster class = Monster (int)
    newstate = gamestate
    if Upgrade :
        #deal 8 damge
        newstate = dealdmg(newstate, 8, hitmonster)
        newstate = addcard(newstate, "Anger", 'discard_pile')
        return newstate
    else :
        #deal 6 damage
        newstate = dealdmg(newstate, 6, hitmonster)
        #add a copy of this card to your discard pile
        newstate = addcard(newstate, "Anger", 'discard_pile')
        return newstate
#helper function for armaments
def choose_Armaments (gamestate, cardindex, upgrade):
    newstate = gamestate
    a_list = []
    for card in range(len(newstate.hand)):
        if card.name not in ["Ascender's Bane","Clumsy","Curse of the Bell","Doubt","Injury","Necronomicurse","Normality","Pain","Parasite","Regret","Shame","Writhe","Burn","Dazed","Void","Wound"]:
            if (card.upgrades == 0) or (card.name == "Searing Blow"):
                list.append(-1, card)

    return a_list

#armaments 1 cost Gain 5 Block. Upgrade a card in your hand for the rest of combat.
def Armaments(gamestate, cardindex, Upgrade):
    newstate = gamestate
    #add 5 block
    newstate = addblock(newstate, 5)
    if Upgrade:
        #upgrade all card in your hand for the rest of combat
        for card in newstate.hand:
            newstate = upgrade(card)
        return newstate
    else:
        #upgrade one card in your hand.
        newstate = upgrade(newstate.hand[cardindex])
        return newstate
        #somehow return a new gamestate for every card which can be upgraded

#barricade 3 cost Block no longer expires at the start of your turn.
def Barricade(gamestate, Upgrade):
    newstate = gamestate
    #make new object new_power
    New_power = Power("Barricade", "Barricade", 0)
    newstate.player.powers.append(New_power)

    return newstate

#bash 2 cost Deal 8damage. Apply 2 Vulnerable.
def Bash(gamestate, hitmonster, Upgrade):
    newstate = gamestate

    if Upgrade:
        #deal 10 damage
        newstate = dealdmg(newstate, 10, hitmonster)
        #apply 3 vulnerable
        newstate = dealvulnerable(newstate, 3, hitmonster)
        return newstate
    else:
        #deal 8 damage
        newstate = dealdmg(newstate, 8, hitmonster)
        #apply 2 vulnerable
        newstate = dealvulnerable(newstate, 2, hitmonster)
        return newstate

#battle trance 0 cost Draw 3 cards. You cannot draw additional cards this turn.
def Battle_Trance(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        #Draw 4 Cards
        newstate = draw(gamestate, 4)
    else:
        #Draw 3 Cards
        newstate = draw(gamestate, 3)
    #Cannot draw additional Cards this turn
    New_power = Power("No Draw", "No Draw", 0)
    newstate.player.powers.append(New_power)

    return newstate

#berserk 0 cost Gain 2 Vulnerable. Gain 1 Energy at the start of your turn.
def Berserk(gamestate, Upgrade):
    newstate = gamestate

    New_power = Power("Energized", "Energized", 1)
    newstate.player.powers.append(New_power)

    if Upgrade:
        #Gain 1 Vulnerable
        New_power_ = Power("Vulnerable", "Vulnerable", 1)
        newstate.player.powers.append(New_power_)
    else :
        #Gain 2 Vulnerable
        New_power_ = Power("Vulnerable", "Vulnerable", 2)
        newstate.player.powers.append(New_power_)

    return newstate

#blood for blood 4 cost Cost 1 less energy for each time you lose HP in combat. Deal 18 damage.
def Blood_For_Blood(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    #if lose HP in combat
    if Upgrade:
        #cost is 3, Cost 1 less energy for each time you lose HP in combat
        #Cost 1 less energy for each time
        #Deal 22 damage
        newstate = dealdmg(newstate, 22, hitmonster)
    else :
        #cost is 4, Cost 1 less energy for each time you lose HP in combat
        #Cost 1 less energy for each time
        #Deal 18 damage
        newstate = dealdmg(newstate, 18, hitmonster)

    return newstate

#bloodletting 0 cost Lose 3 HP. Gain 1 Energy.
def Bloodletting(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        # lose 3 HP
        newstate.player.current_hp = newstate.player.current_hp - 3
        # Gain 2 Energy.
        newstate.player.energy += 2
    else:
        # lose 3 HP
        newstate.player.current_hp = newstate.player.current_hp - 3
        # Gain 1 Energy.
        newstate.player.energy += 1

    return newstate

#bludgeon 3 cost Deal 32 damage.
def Bludgeon(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade :
        #deal 42 damage
        newstate = dealdmg(newstate, 42, hitmonster)
    else:
        #deal 32 damage
        newstate = dealdmg(newstate, 32, hitmonster)
    return newstate

#body slam 1 cost   Deal damage equal to your current Block.
def Body_Slam(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        #cost is 0,
        #deal damage equal to your current Block.
        newstate = dealdmg(newstate, newstate.player.block, hitmonster)
    else:
        #cost is 1,
        #deal damage equal to your current Block.
        newstate = dealdmg(newstate, newstate.player.block, hitmonster)

    return newstate

#brutality 0 cost (Innate.) At the start of your turn, lose 1 HP and draw 1 card.
#It is not different between Upgraded or not.
def Brutality(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    New_power = Power("Brutality", "Brutality", 1)
    newstate.player.powers.append(New_power)
    return newstate

#burning pact 1 cost Exhaust 1 card. Draw 2 cards.
def Burning_Pact(gamestate, cardindex, Upgrade):
    newstate = gamestate
    #Exhaust 1 card
    newstate = addcard (newstate, newstate.hand[cardindex].name, 'exhaust_pile', newstate.hand[cardindex])

    if Upgrade :
         #Draw 3 cards
         newstate = draw(newstate, 3)
    else :
         #Draw 2 cards
         newstate = draw(newstate, 2)
    return newstate

#carnage 2 cost Ethereal. Deal 20(28) damage
def Carnage (gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade :
        # deal 20 damage
        newstate = dealdmg(newstate, 28, hitmonster)
    else:
        # deal 20 damage
        newstate = dealdmg(newstate, 20, hitmonster)
    return newstate

#clash 0 cost Can only be played if every card in your hand is an Attack. Deal 14 damage.
def Clash (gamestate, hitmonster, Upgrade):
    newstate = gamestate

    #count how many attack in your hand
    is_it_all_attack = 0
    for card_type in newstate.hand:
        if card_type.type == CardType.ATTACK:
            is_it_all_attack += 1

    #check is_an_attack_in_hand
    if is_it_all_attack == len(newstate.hand):
        if Upgrade:
            #deal 18 damage
            newstate = dealdmg(newstate, 18, hitmonster)
        else :
            #deal 14 damage
            newstate = dealdmg(newstate, 14, hitmonster)

    return newstate

#cleave 1 cost Deal 8 damage to ALL enemies.
def Cleave (gamestate, hitmonster, Upgrade):
    newstate = gamestate
    #hitmonster is list such as monster = [moster1, moster2, moster3]
    #attack monster1, monster2, and monster3
    if Upgrade :
        for num in range(len(newstate.monsters)):
            #deal 11 damage to ALL enemies
            newstate = dealdmg(newstate, 11, num)
    else :
        for num in range(len(newstate.monsters)):
            #deal 8 damgae to ALL enemies
            newstate = dealdmg(newstate, 8, num)

    return newstate

#clothsline 2 cost Deal 12 damage. Apply 2 Weak.
def Clothesline (gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade :
        #deal 14 damage
        newstate = dealdmg(newstate, 14, hitmonster)
        #apply 3 weak
        newstate = dealweak(newstate, 3, hitmonster)

    else:
        #deal 12 damage
        newstate = dealdmg(newstate, 12, hitmonster)
        #apply 2 weak
        newstate = dealweak(newstate, 2, hitmonster)

    return newstate

#combust 1 cost At the end of your turn, lose 1 HP and deal 5 damage to ALL enemies.

def Combust(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        New_power = Power("Combust", "Combust", 7)
        newstate.player.powers.append(New_power)
    else:
        New_power = Power("Combust", "Combust", 5)
        newstate.player.powers.append(New_power)

    return newstate

#corruption 3 cost Skills cost 0. Whenever you play a Skill, Exhaust it.
# Need to modify
def Corruption(gamestate, Upgrade):
    newstate = gamestate
    #cost is taken from game
    # Set the skill cost 0
    # When you play the skill
    # Exhaust it

    for card in newstate.hand:
        if card.type == CardType.SKILL:
            card.cost = 0
            card.exhaust = True

    for card in newstate.discard_pile:
        if card.type == CardType.SKILL:
            card.cost = 0
            card.exhaust = True

    for card in newstate.draw_pile:
        if card.type == CardType.SKILL:
            card.cost = 0
            card.exhaust = True

    for card in newstate.exhaust_pile:
        if card.type == CardType.SKILL:
            card.cost = 0
            card.exhaust = True

    return newstate

#dark embrace 2 cost Whenever a card is Exhausted, draw 1 card.
def Dark_Embrace(gamestate, Upgrade):
    newstate = gamestate

    New_power = Power("Dark Embrace", "Dark Embrace", 0)
    newstate.player.powers.append(New_power)

    return newstate

#defend 1 cost Gain 5 Block.
def Defend (gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        #add 8 block
        newstate = addblock(newstate, 8)
    else:
        #add 5 block
        newstate = addblock(newstate, 5)
    return newstate

#demon form 3 cost At the start of each turn, gain 2 Strength.
def Demon_Form(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        #at the start of each turn, gain 3 Strength
        New_power = Power("Demon Form", "Demon Form", 3)
        newstate.player.powers.append(New_power)
    else:
        #at the start of each turn, gain 2 Strength
        New_power = Power("Demon Form", "Demon Form", 2)
        newstate.player.powers.append(New_power)

    return newstate

#disarm 1 cost Enemy loses 2 Strength. Exhaust.
def Disarm(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade :
        #Enemy loses 3 Strength
        newstate = monster_lose_strength(newstate, 3, hitmonster)
    else :
        #Enemy loses 2 Strength.
        newstate = monster_lose_strength(newstate, 2, hitmonster)

    #Exhaust
    newstate = addcard(newstate, "Disarm", 'exhaust_pile')
    return newstate

#double tap 1 cost This turn, your next Attack is played twice.
def Double_Tap(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade :
        # your next 2 Attack are played twice
        New_power = Power("Double Tap", "Double Tap", 2)
        newstate.player.powers.append(New_power)
    else:
        New_power = Power("Double Tap", "Double Tap", 1)
        newstate.player.powers.append(New_power)
        # your next Attack is played twice

    return newstate

#dropkick 1 cost Deal 5 damage. If the enemy is Vulnerable, gain 1 energy and draw 1 card.
#
def Dropkick(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        #deal 8 damage
        newstate =dealdmg(newstate,8,hitmonster)
    else:
        #deal 5 damage
        newstate = dealdmg(newstate, 5, hitmonster)

    for pmonster in newstate.monsters[hitmonster].powers:
        #Gain 1 energy, and draw 1 card
        if pmonster.power_name ==  "Vulnerable":
            newstate.player.energy += 1
            newstate = draw(newstate, 1)
    return newstate

#dual wield 1 cost Create a copy of an Attack or Power card in your hand.
def Dual_Wield(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        #random for now
        cardindex = random.randrange(len(newstate.hand))
        for card in newstate.hand:
            if card.type == CardType.ATTACK or card.type == CardType.POWER:
                #add Create two copy of an Attack or Power Card.
                newstate = addcard(newstate, newstate.hand[cardindex].name, 'hand', newstate.hand[cardindex])
                newstate = addcard(newstate, newstate.hand[cardindex].name, 'hand', newstate.hand[cardindex])
    else:
        #random for now
        cardindex = random.randrange(len(newstate.hand))
        for card in newstate.hand:
            if card.type == CardType.ATTACK or card.type == CardType.POWER:
                #add Create a copy of an Attack or Power Card.
                newstate = addcard(newstate, newstate.hand[cardindex].name, 'hand', newstate.hand[cardindex])

    return newstate

#entrench 2(1) cost Double your current Block.
def Entrench(gamestate, Upgrade):
    newstate = gamestate

    newstate.player.block = newstate.player.block * 2

    return newstate

#evolve 1 cost Whenever you draw a Status, draw 1 card.
#Add draw
def Evolve(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        # Draw 2 cards, if you draw a Status
        New_power = Power("Evolve", "Evolve", 2)
        newstate.player.powers.append(New_power)
    else:
        #add Draw card, if you draw a Status
        New_power = Power("Evolve", "Evolve", 1)
        newstate.player.powers.append(New_power)
    return newstate

#exhume 1 cost Place a card from your Exhaust pile into your hand. Exhaust.
def Exhume(gamestate, Upgrade):
    newstate = gamestate
    # random for now
    cardindex = random.randrange(len(newstate.exhaust_pile))
    #add Place a card from your Exhaust pile
    newstate = addcard(gamestate, newstate.exhaust_pile[cardindex].name, 'hand')
    #Exhaust
    newstate = addcard(newstate, "Exhume", 'exhaust_pile')

    return newstate

#feed 1 cost Deal 10 damage. If this kills a non-minion enemy, gain 3 permanent Max HP. Exhaust.
def Feed(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade :
        # deal 12 damage
        newstate = dealdmg(newstate, 12, hitmonster)
        # if monster is dead
        if newstate.monsters[hitmonster].current_hp <= 0:
            # gain 4 permanent Max HP
            newstate.player.max_hp =newstate.player.max_hp + 4
            newstate = addcard(newstate, "Feed", 'exhaust_pile')

    else :
        # deal 14 damage
        newstate = dealdmg(newstate, 10, hitmonster)
        # if monster is dead
        if newstate.monsters[hitmonster].current_hp <= 0:
            # gain 3 permanent Max HP
            newstate.player.max_hp =newstate.player.max_hp + 3
            newstate = addcard(newstate, "Feed", 'exhaust_pile')

    return newstate

#feel no pain 1 cost Whenever a card is Exhausted, gain 3 Block.
def Feel_No_Pain(gamestate, Upgrade):
    newstate = gamestate

    if Upgrade :
        #check if a card is Exhausted, whenever after playing Feel No pain
        #gain 4 Block
        New_power = Power("Feel No Pain", "Feel No Pain", 4)
        newstate.player.powers.append(New_power)
    else:
        #check if a card is Exhausted, whenever after playing Feel No pain
        #gain 3 Block
        New_power = Power("Feel No Pain", "Feel No Pain", 3)
        newstate.player.powers.append(New_power)

    return newstate

#fiend fire 2 cost Exhaust your all hand. Deal 7(10) damage for each Exhausted card. Exhaust.
def Fiend_Fire(gamestate, hitmonster, Upgrade):
    newstate = gamestate

    number_of_exhaust = len(newstate.hand)
    #exhaust your all hand
    for current_hand in newstate.hand:
        newstate = addcard(newstate, current_hand.name, 'exhaust_pile', current_hand)
    newstate.hand = []

    if Upgrade:
        newstate = dealdmg(newstate, 10*number_of_exhaust, hitmonster)
    else:
        newstate = dealdmg(newstate, 7*number_of_exhaust, hitmonster)

    newstate = addcard(newstate, "Fiend Fire", 'exhaust_pile')
    return newstate

#fire breathing 1 cost Whenever you draw a Status or Curse card, deal 6(10) damage to all enemies.

def Fire_Breathing(gamestate, hitmonster, Upgrade):
    newstate = gamestate

    # Whenever you draw a Status or Curse card
    if Upgrade :
        New_power = Power("Fire Breathing", "Fire Breathing", 10)
        newstate.player.powers.append(New_power)
    else :
        New_power = Power("Fire Breathing", "Fire Breathing", 6)
        newstate.player.powers.append(New_power)

    return newstate

#flame barrier 2 cost Gain 12 Block. Whenever you are attacked this turn, deal 4 damage to the attacker.
def Flame_Barrier(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade :
        #Gain 16 Block
        newstate = addblock(newstate, 16)
        #whenever you are attacked this turn
            #how to represent attacker?
        New_power = Power("Flame Barrier", "Flame Barrier", 6)
        newstate.player.powers.append(New_power)

    else:
        #Gain 12 Block
        newstate = addblock(newstate, 12)
        newstate.Flame_Barrier = True
            #whenever you are attacked this turn
            #how to represent attacker?
        New_power = Power("Flame Barrier", "Flame Barrier", 4)
        newstate.player.powers.append(New_power)

    return newstate

#flex 0 cost 2 Strength. At the end of your turn, lose 2 Strength.
def Flex(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade :
        #gain 4 Strength
        player_gain_strength(newstate, 4)
        #end_of_turn lose 4 Strength
        New_power = Power("Strength", "Strength", -4)
        newstate.player.powers.append(New_power)
    else:
        #gain 2 Strength
        player_gain_strength(newstate, 2)
        #end_of_turn lose 2 Strength
        New_power = Power("Strength", "Strength", -2)
        newstate.player.powers.append(New_power)

    return newstate

#ghostly armor 1 cost Ethereal. Gain 10 Block.
def Ghostly_Armor(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade :
        #Gain 13 Block
        newstate = addblock(newstate,13)
    else :
        #Gain 10 Block
        newstate = addblock(newstate, 10)
    return newstate

#havoc 1 cost Play the top card of your draw pile and Exhaust it.
def Havoc(gamestate, Upgrade):
    newstate = gamestate
    card = random.randrange(len(newstate.draw_pile))
    newstate = addcard(newstate, newstate.hand[card].name, 'hand')
    # Play the top card of your draw pile
    # Exhaust it
    return newstate

#helper function for headbutt
def choose_Headbutt(gamestate, index, Upgrade):
    newstate = gamestate
    a_list = []

    for monster in range(len(newstate.monsters)):
        for card in range(len(newstate.discard_pile)):
            a_list.append([monster,card]);

    return a_list

#headbutt 1 cost Deal 9 damage. Place a card from your discard pile on top of your draw pile.
def Headbutt(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        #deal 12 damage
        newstate = dealdmg(newstate,12, hitmonster)
        #add Place a card from your discard pile on top of your draw pile.
    else :
        #deal 9 damage
        newstate = dealdmg(newstate, 9, hitmonster)
        #add  Place a card from your discard pile on top of your draw pile.
    return newstate

#heavy blade 2 cost Deal 14 damage. Strength affects Heavy Blade 3 times.
def Heavy_Blade(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        #Strength affects Heavy Blade 5 times
        for power_player in newstate.player.powers:
            if power_player.power_name == "Strength":
                power_player.amount = power_player.amount * 5

        newstate = dealdmg(newstate, 14, hitmonster)

        # reset the affects after dealdmg
        if power_player in newstate.player.powers:
            if power_player.power_name == "Strength":
                power_player.amount = power_player.amount / 5

    else:
        #Strength affects Heavy Blade 3 times
        for power_player in newstate.player.powers:
            if power_player.power_name == "Strength":
                power_player.amount = power_player.amount * 3

        newstate = dealdmg(newstate, 14, hitmonster)

        # reset the affects after dealdmg
        if power_player in newstate.player.powers:
            if power_player.power_name == "Strength":
                power_player.amount = power_player.amount / 3

    return newstate

#hemokinesis 1 cost Lose 3 HP. Deal 14 damage.
def Hemokinesis(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade :
        # lose 2 HP
        newstate.player.current_hp =newstate.player.current_hp - 2

        #rupture 1 cost Whenever you lose HP from a card, gain 1 Strength
        for player_power in newstate.player.powers:
            if player_power.power_name == "Rupture":
                newstate = player_gain_strength(newstate, player_power.amount)

        # Deal 18 Damage
        newstate = dealdmg(newstate, 18, hitmonster)
    else:
        # lose 3 HP
        newstate.player.current_hp =newstate.player.current_hp - 3

        #rupture 1 cost Whenever you lose HP from a card, gain 1 Strength
        for player_power in newstate.player.powers:
            if player_power.power_name == "Rupture":
                newstate = player_gain_strength(newstate, player_power.amount)

        # Deal 14 Damage
        newstate = dealdmg(newstate, 14, hitmonster)

    return newstate

#immolate 2 cost Deal 21 damage to ALL enemies. Add a Burn to your discard pile.
def Immolate(gamestate, Upgrade):
    newstate = gamestate

    if Upgrade:
        for x in range(len(newstate.mosters)):
            # Deal 28 Damage
            newstate = dealdmg(newstate, 28, x)
    else:
        for x in range(len(newstate.monsters)):
            # Deal 21 Damage
            newstate = dealdmg(newstate, 21, x)
    newstate = addcard(newstate, "Burn", 'discard_pile')

    return newstate

#impervious 2 cost Gain 30 Block. Exhaust.
def Impervious(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        #gain 40 Block
        newstate = addblock(newstate, 40)
        newstate = addcard(newstate, "Impervious", 'exhaust_pile')
    else:
        #gain 30 Block
        newstate = addblock(newstate, 30)
        newstate = addcard(newstate, "Impervious", 'exhaust_pile')

    return newstate

#infernal blade 1 cost Add a random Attack to your hand. It costs 0 this turn. Exhaust.
def Infernal_Blade(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        # cost is 0
        #add a random Attack to your hand
        #set the Attack costs 0 this turn
        newstate = addcard(newstate, "Infernal Blade", 'exhaust_pile')
    else :
        # cost is 1
        #add a random Attack to your hand
        #set the Attack costs 0 this turn
        newstate = addcard(newstate, "Infernal Blade", 'exhaust_pile')

    return newstate

#inflame 1 cost Gain 2 Strength.
def Inflame(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        # Gain 3 Strength
        player_gain_strength(newstate, 3)
    else :
        # Gain 2 Strength
        player_gain_strength(newstate, 2)
    return newstate

#intimidate 0 cost Apply 1 Weak to ALL enemies. Exhaust.
def Intimidate(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        #add apply 2 weeak to All enemies.
        for x in range(len(newstate.monsters)):
            newstate = dealweak(newstate, 2, x)

        newstate = addcard(newstate, "Intimidate", 'exhaust_pile')
    else:
        #add apply 1 weeak to All enemies.
        for x in range(len(newstate.monsters)):
            newstate = dealweak(newstate, 1, x)

        newstate = addcard(newstate, "Intimidate", 'exhaust_pile')

    return newstate

#iron wave 1 cost Gain 5 Block. Deal 5 damage.
def Iron_wave(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade :
        #Gain 7 Block
        newstate = addblock(newstate, 7)
        #Deal 7 Damage
        newstate = dealdmg(newstate, 7, hitmonster)

    else:
        #Gain 5 Block
        newstate = addblock(newstate, 5)
        #Deal 5 Damage
        newstate = dealdmg(newstate, 5, hitmonster)
    return newstate

#juggernaut 2 cost Whenever you gain Block, deal 5 damage to a random enemy.
def Juggernaut(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    #Whenever you Gain Block,
    if Upgrade:
        #deal 7 damage to a random enemy
        New_power = Power("Juggernaut", "Juggernaut", 7)
        newstate.player.powers.append(New_power)
    else:
        #deal 5 damage to a random enemy
        New_power = Power("Juggernaut", "Juggernaut", 5)
        newstate.player.powers.append(New_power)

    return newstate

#limit break 1 cost Double your Strength. Exhaust.
def Limit_Break(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        # Double your Strength
        for power_player in newstate.player.powers:
            if power_player.power_name == "Strength":
                power_player.amount = power_player.amount * 2
        # Do not Exhaust

    else:
        # Double your Strength
        for power_player in newstate.player.powers:
            if power_player.power_name == "Strength":
                power_player.amount = power_player.amount * 2

        newstate = addcard(newstate, "Limit Break", 'exhaust_pile')

    return newstate

#metallicize 1 cost At the end of your turn, gain 3 Block.
def Metallicize(gamestate, Upgrade):
    newstate = gamestate

    if Upgrade:
        # gain 4 Blocks at the end of your turn
        New_power = Power("Metallicize", "Metallicize", 4)
        newstate.player.powers.append(New_power)

    else:
        # gain 3 blocks, at the end of your turn
        New_power = Power("Metallicize", "Metallicize", 3)
        newstate.player.powers.append(New_power)

    return newstate

#offering 0 cost Lose 6 HP. Gain 2 energy. Draw 3 cards. Exhaust.
def Offering(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        newstate.player.current_hp = newstate.player.current_hp - 6

        #rupture 1 cost Whenever you lose HP from a card, gain 1 Strength
        for player_power in newstate.player.powers:
            if player_power.power_name == "Rupture":
                newstate = player_gain_strength(newstate, player_power.amount)

        #add Draw 5 Cards
        #Gain 2 energy
        newstate.player.energy = newstate.player.energy + 2
        newstate = draw(newstate, 5)
        newstate = addcard(newstate, "Offering", 'exhaust_pile')
    else:
        newstate.player.current_hp = newstate.player.current_hp - 6

        #rupture 1 cost Whenever you lose HP from a card, gain 1 Strength
        for player_power in newstate.player.powers:
            if player_power.power_name == "Rupture":
                newstate = player_gain_strength(newstate, player_power.amount)

        #add Draw 3 Cards
        #Gain 2 energy
        newstate.player.energy = newstate.player.energy + 2
        newstate = draw(newstate, 3)
        newstate = addcard(newstate, "Offering", 'exhaust_pile')

    return newstate

#perfected strike 2 cost Deal 6 damage. Deals an additional 2 damage for ALL of your cards containing "Strike".
def Perfected_Strike(gamestate, hitmonster, Upgrade):
    newstate = gamestate

    count_Strike = 0
    for card in newstate.hand:
        if "Strike" in card.name:
            count_Strike += 1

    if Upgrade:
        newstate =dealdmg(newstate, 6, hitmonster)
        #add Deal an additional 3 damage for All of your cards containing "Strike"
        newstate = dealdmg(newstate, 3, hitmonster, count_Strike)
    else:
        newstate = dealdmg(newstate, 6, hitmonster)
        #add Deals an additional 2 damage for ALL of your cards containing "Strike".
        newstate = dealdmg(newstate, 2, hitmonster, count_Strike)


    return newstate

#pommel strike 1 cost Deal 9 damage. Draw 1 card(s).
def Pommel_Strike(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        # Deal 10 damage
        newstate =dealdmg(newstate, 10, hitmonster)
        # Add Draw 2 Cards
        newstate = draw(newstate, 2)
    else:
        # Deal 9 damage
        newstate = dealdmg(newstate, 9, hitmonster)
        #add draw 1 card
        newstate = draw(newstate, 1)

    return newstate

#power through 1 cost Add 2 Wounds to your hand. Gain 15 Block.
def Power_Through(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        newstate = addblock(newstate, 20)
        newstate = addcard(newstate, "Wound", 'hand')
        newstate = addcard(newstate, "Wound", 'hand')
    else:
        newstate = addblock(newstate, 15)
        newstate = addcard(newstate, "Wound", 'hand')
        newstate = addcard(newstate, "Wound", 'hand')

    return newstate

#pummel 1 cost Deal 2 damage 4 times. Exhaust.
def Pummel(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        # Deal 2 damage 5 times
        newstate = dealdmg(newstate, 2, hitmonster, 5)
        newstate = addcard(newstate, "Pummel", 'exhaust_pile')
    else:
        # Deal 2 damage 4 times
        newstate = dealdmg(newstate, 2, hitmonster, 4)
        newstate = addcard(newstate, "Pummel", 'exhaust_pile')
    return newstate

#rage 0 cost Whenever you play an Attack this turn, gain 3 Block
def Rage(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        # whenever player play an Attack this turn, gain 5 Block
        New_power = Power("Rage", "Rage", 5)
        newstate.player.powers.append(New_power)
    else:
        # whenever player play an Attack this turn, gain 3 Block
        New_power = Power("Rage", "Rage", 3)
        newstate.player.powers.append(New_power)
    newstate.Rage = True
    return newstate

#rampage 1 cost Deal 5 damage. Every time this card is played, increase its damage by 8 for this combat.
def Rampage(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        #deal 8 damage
        newstate = dealdmg(newstate, 8, hitmonster)
        #Every time this card is played, increase its damage by 8 for this combat.
    else:
        newstate = dealdmg(newstate, 5, hitmonster)
        #Every time this card is played, increase its damage by 8 for this combat.
    return newstate

#reaper 2 cost Deal 4 damage to ALL enemies. Heal for unblocked damage. Exhaust.
def Reaper(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        #deal 5 damage to All enemies
        for x in range(len(newstate.monsters)):
            newstate = dealdmg(newstate, 5, x)
        newstate = addcard(newstate, "Reaper", 'exhaust_pile' )

    else:
        # Deal 4 damage to All enemies
        for x in range(len(newstate.monsters)):
            newstate = dealdmg(newstate, 4, x)
        newstate = addcard(newstate, "Reaper", 'exhaust_pile' )

    return newstate

#reckless charge 0 cost Deal 7 damage. Shuffle a Dazed into your draw pile
def Reckless_Charge(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        # deal 10 damage
        newstate = dealdmg(gamestate, 10, hitmonster)
        newstate = addcard(newstate, "Dazed", 'draw_pile' )

    else:
        # deal 7 damage
        newstate = dealdmg(gamestate, 7, hitmonster)
        newstate = addcard(newstate, "Dazed", 'draw_pile' )

    return newstate

#rupture 1 cost Whenever you lose HP from a card, gain 1 Strength.
def Rupture(gamestate, Upgrade):
    newstate = gamestate
    #whenevr player lose Hp from a cards gain 1 Strength
    New_power = Power("Ruptrue", "Rupture", 1)
    newstate.player.powers.append(New_power)

    return newstate

#searing blow 2 cost Deal 12 damage. Can be upgraded any number of times.
def Searing_Blow(gamestate, hitmonster, Upgrade):
    newstate = gamestate

    if Upgrade:
        # if upgrade n times, deal n(n+7)/2 + 12 Damage (https://slay-the-spire.fandom.com/wiki/Searing_Blow)
        for card in newstate.hand:
            if card.name == "Searing Blow":
                upgrade(card)
                damage = card.upgrades * (card.upgrades + 7) / 2 + 12
                newstate = dealdmg(newstate, damage, hitmonster)
    else:
        for card in newstate.hand:
            if card.name == "Searing Blow":
                damage = card.upgrades * (card.upgrades + 7) / 2 + 12
                newstate = dealdmg(newstate, damage, hitmonster)

    return newstate

#second wind 1 cost Exhaust all non-Attack cards in your hand and gain 5 Block for each.
def Second_Wind(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        #Exhaust all non-Attack Cards in your hand.
        #Gain 7 Block for each
        count_non_attack = 0
        for card in newstate.hand:
            if card.type != CardType.ATTACK:
                count_non_attack += 1
                newstate = addcard(newstate, card.name, 'exhaust_pile')
                newstate.hand.remove(card)
        newstate.player.block = newstate.player.block + (7*count_non_attack)
    else:
        #Exhaust all non-Attack Cards in your hand.
        #Gain 5 Block for each
        count_non_attack = 0
        for card in newstate.hand:
            if card.type != CardType.ATTACK:
                count_non_attack += 1
                newstate = addcard(newstate, card.name, 'exhaust_pile')
                newstate.hand.remove(card)
        newstate.player.block = newstate.player.block + (5*count_non_attack)

    return newstate

#seeing red 1 cost Gain 2 energy. Exhaust.
def Seeing_Red(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        # cost is 0
        # Gain 2 energy/cost
        newstate.player.energy = newstate.player.energy + 2
        newstate = addcard(newstate, "Seeing Red", 'exhaust_pile')
    else:
        #Gain 2 energy/cost
        newstate.player.energy = newstate.player.energy + 2
        newstate = addcard(newstate, "Seeing Red", 'exhaust_pile')

    return newstate

#sentinel 1 cost Gain 5 Block. If this card is Exhausted, gain 2 energy.
def Sentinel(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        newstate = addblock(newstate, 8)
        #add If this card is exhuasted
            #Gain 3 energy/cost
        New_power = Power("Sentinel", "Sentinel", 3)
        newstate.player.powers.append(New_power)
    else:
        #Gain 5 Block
        newstate = addblock(newstate, 5)
        #add If this card is Exhausted
            #Gain 2 energy/cost
        New_power = Power("Sentinel", "Sentinel", 2)
        newstate.player.powers.append(New_power)

    return newstate

#sever soul 2 cost Exhaust all non-Attack cards in your hand. Deal 16 damage.
def Sever_Soul(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        #add exhaust all non-Attack Cards in your hand
        for card in newstate.hand:
            if card.type != CardType.ATTACK:
                newstate = addcard(newstate, card.name, 'exhaust_pile', card)
                newstate.hand.remove(card)
        #Deal 20 Damage
        newstate = dealdmg(newstate, 20, hitmonster)
    else:
        # add exhaust all non-Attack Cards in your hand
        for card in newstate.hand:
            if card.type != CardType.ATTACK:
                newstate = addcard(newstate, card.name, 'exhaust_pile', card)
                newstate.hand.remove(card)
        # Deal 16 damage.
        newstate = dealdmg(newstate, 16, hitmonster)
    return newstate

#shock wave 2 cost Apply 3 Weak and Vulnerable to ALL enemies. Exhaust.
def Shockwave(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
    #add apply 5 Weak and Vulnerable to All enemies
        for x in range(len(newstate.monsters)):
            newstate = dealweak(newstate, 5, x)
            newstate = dealvulnerable(newstate, 5, x)
        newstate = addcard(newstate, "Shockwave", 'exhaust_pile')

    else:
        #add apply 3 Weak and Vulnerable to All enemies
        for x in range(len(newstate.monsters)):
            newstate = dealweak(newstate, 3, x)
            newstate = dealvulnerable(newstate, 3, x)
        newstate = addcard(newstate, "Shockwave", 'exhaust_pile')

    return newstate

#shrug it off 1 cost Gain 8 Block. Draw 1 card.
def Shrug_It_Off(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        #gain 11 block
        newstate = addblock(newstate, 11)
        #add Draw 1 card
        newstate = draw(newstate, 1)
    else:
        #gain 8 Block
        newstate = addblock(newstate, 8)
        #add Draw 1 Card
        newstate = draw(newstate, 1)
    return newstate

#spot weakness 1 cost If an enemy intends to attack, gain 3 Strength.
#NEED Target_Monster
def Spot_Weakness(gamestate, hitmonster,Upgrade):
    newstate = gamestate
    if Upgrade:
        if newstate.monsters[hitmonster].intent == Intent.ATTACK:
            #gain 4 Strength
            newstate = player_gain_strength(newstate, 4)
    else:
        if newstate.monsters[hitmonster].intent == Intent.ATTACK:
            #gain 3 Strength
            newstate = player_gain_strength(newstate, 3)

    return newstate

#strike 1 cost Deal 6 damage.
def Strike(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        # deal 9 damage
        newstate = dealdmg(newstate, 9, hitmonster)
    else:
        # deal 6 damage
        newstate = dealdmg(newstate, 6, hitmonster)

    #newstate = addcard(newstate, "Strike", 'discard_pile')
    return newstate

#sword boomerang 1 cost Deal 3 damage to a random enemy 3 times.
def Sword_Boomerang(gamestate, hitmonster, Upgrade):
    newstate = gamestate

    if Upgrade:
        # a random enemy.
        x = random.randrange(len(newstate.monsters))
        # deal 3 damage, 4 times
        newstate = dealdmg(newstate, 3, x, 4)

    else:
        # a random enemy.
        x = random.randrange(len(newstate.monsters))
        # deal 3 damage, 3 times
        newstate = dealdmg(newstate, 3, x, 3)

    return newstate

#thunderclap 1 cost Deal 4damage and apply 1 Vulnerable to ALL enemies.
def Thunderclap(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        for x in ragne(len(newstate.monsters)):
        #deal 7 demage to All enemies
            newstate = dealdmg(newstate, 7, x)
        #add apply 1 Vulnerable to All enemies
        for x in range(len(newstate.monsters)):
            newstate = dealvulnerable(newstate, 1, x)

    else:
        for x in range(len(newstate.monsters)):
        #deal 4 demage to All enemies
            newstate = dealdmg(newstate, 4, x)
        #add apply 1 Vulnerable to All enemies
        for x in range(len(newstate.monsters)):
            newstate = dealvulnerable(newstate, 1, x)

    return newstate

#true grit 1 cost Gain 7 Block. Exhaust a random card from your hand.
def True_Grit(gamestate, hitmonster, Upgrade):
    newstate = gamestate

    if Upgrade:
        #Gain 9 Block
        newstate = addblock(newstate, 9)
        #Exhaust a random card from your hand
        x = random.randrange(len(hand))
        newstate = addcard(newstate, newstate.hand[x].card.name, 'exhaust_pile', newstate.hand[x])
        newstate.hand.remove(newstate.hand[x])
    else:
        #Gain 7 Block
        newstate = addblock(newstate, 7)
        #Exhaust a random card from your hand
        x = random.randrange(len(hand))
        newstate = addcard(newstate, newstate.hand[x].card.name, 'exhaust_pile', newstate.hand[x])
        newstate.hand.remove(newstate.hand[x])

    return newstate

#twin strike 1 cost Deal 5 damage twice.
def Twin_Strike(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        #Deal 7 damage twice
        newstate = dealdmg(newstate, 7, hitmonster, 2)
    else:
        #Deal 5 Damage twice
        newstate = dealdmg(newstate, 5, hitmonster, 2)

    return newstate

#uppercut 2 cost Deal 13 damage. Apply 1 Weak. Apply 1 Vulnerable.
def Uppercut(gamestate, hitmonster, Upgrade):
    newstate = gamestate
    if Upgrade:
        #deal 13 Damage
        newstate = dealdmg(newstate, 13, hitmonster)
        #apply 2 weak, and 2 Vulnerable
        newstate = dealweak(newstate, 2, hitmonster)
        newstate = dealvulnerable(newstate, 2, hitmonster)

    else:
        #deal 13 Damage
        newstate = dealdmg(newstate, 13, hitmonster)
        #apply 1 weak, and 1 Vulnerable
        newstate = dealweak(newstate, 1, hitmonster)
        newstate = dealvulnerable(newstate, 1, hitmonster)

    return newstate

#warcry 0 cost Draw 1 card. Place a card from your hand on top of your draw pile. Exhaust.
def Warcry(gamestate, Upgrade):
    newstate = gamestate

    if Upgrade:
        #random for now
        cardindex = random.randrange(len(newstate.hand))
        #Draw 2 Card
        newstate = draw(newstate, 2)
        #Place a Card from your hand on top of your draw pile.
        newstate = addcard(newstate, newstate.hand[cardindex].name, 'draw_pile', newstate.hand[cardindex])
        newstate = addcard(newstate, "Warcry", 'exhaust_pile')

    else:
        #random for now
        cardindex = random.randrange(len(newstate.hand))
        #Draw 1 Card
        newstate = draw(newstate, 1)
        #Place a Card from your hand on top of your draw pile.
        newstate = addcard(newstate, newstate.hand[cardindex].name, 'draw_pile', newstate.hand[cardindex])
        newstate = addcard(newstate, "Warcry", 'exhaust_pile')

    return newstate

#whirlwind X cost Deal 5 damage to ALL enemies X times.
def Whirlwind(gamestate, Upgrade):
    newstate = gamestate
    if Upgrade:
        #repeat X times, X is cost, deal 8 damage
        for x in range(len(newstate.monsters)):
            newstate = dealdmg(newstate, 8, x, newstate.player.energy)
    else:
        #repaet X times, X is cost, deal 5 damage
        for x in range(len(newstate.monsters)):
            newstate = dealdmg(newstate, 5, x, newstate.player.energy)

    return newstate

#wildstrike 1 cost Deal 12 damage. Shuffle a Wound into your draw pile.
def Wildstrike(gamestate, hitmonster, Upgrade):
    newstate = gamestate

    if Upgrade:
        #deal 17 damage
        newstate = dealdmg(newstate, 17, hitmonster)
        #Shuffle a Wound into draw pile
        newstate = addcard(newstate, "Wound", 'draw_pile')
    else:
        #deal 12 damage
        newstate = dealdmg(newstate, 12, hitmonster)
        #Shuffle a Wound into draw pile
        newstate = addcard(newstate, "Wound", 'draw_pile')

    return newstate

#Status_Card
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

# unplayable_card cost? for now they are 0 cost
cards = {
    'Anger' : [0, True, Anger, 'A', False, False],
    'Armaments' : [1, False, Armaments, 'S', False, choose_Armaments], #need upgrade function
    'Barricade' : [3, False, Barricade, 'P', False, False], #Barricade needs to be a game state field, do not lose block at turn end
    'Bash' : [2, True, Bash, 'A', False, False],
    'Battle Trance' : [0, False, Battle_Trance, 'S', False, False], # gamestate, You cannot draw additional cards this turn.
    'Berserk' : [0, False, Berserk, 'P', False, False], #somehow figure out energy
    'Blood For Blood' : [4, True, Blood_For_Blood, 'A', False, False],#gamestate, 1 less energy for each time you lose HP in combat
    'Bloodletting' : [0, True, Bloodletting, 'S', False, False],
    'Bludgeon' : [3, True, Bludgeon, 'A', False, False],
    'Body Slam' : [1, True, Body_Slam, 'A', False, False],
    'Brutality' : [0, True, Brutality, 'P', False, False],
    'Burning Pact' : [1, False, Burning_Pact, 'S', False, False], #need draw function
    'Carnage' : [2, True, Carnage, 'A', True, False],
    'Clash' : [0, True, Clash, 'A', False, False], #Clash does not play if not all cards are attacks, SHOULD IGNORE DISCARD, card itself will handle discard
    'Cleave' : [1, True, Cleave, 'A', False, False],
    'Clothesline' : [2, True, Clothesline,'A', False, False],
    'Combust' :[1, True, Combust, 'P', False, False], # gamestate, At the end of your turn
    'Corruption' : [3, False, Corruption, 'P', True, False], # gamestate, Whenever you play a Skill, Exhaust it
    'Dark Embrace' : [2, False, Dark_Embrace,'P', False, False], #gamestate, Whenever a card is Exhausted, draw 1 card.
    'Defend' : [1, False, Defend, 'S', False, False],
    'Disarm' : [3, True, Disarm, 'S', False, False], #exhaust
    'Double Tap' : [1, False, Double_Tap, 'D', False, False], #gamestate, This turn, your next Attack is played twice.
    'Dropkick' : [1, True, Dropkick, 'A', False, False], #draw if conditions are met
    'Dual Wield' : [1, False, Dual_Wield,'S', False, False],
    'Demon Form' : [3, False, Demon_Form, 'P', False, False], # gamestate, at the start of each turn, gain 2 strength
    'Entrench' :[2, False, Entrench, 'S', False, False],
    'Evolve' : [1, False, Evolve, 'P', False, False], # gamestate, Whenever you draw a Status, draw 1 card.
    'Exhume' : [1, False, Exhume, 'S', False, False], #exhaust
    'Feed' :[1, True, Feed, 'A', False, False], #exhaust
    'Feel No Pain' : [1, False, Feel_No_Pain, 'P', False, False],#gamestate, Whenever a card is Exhausted, gain 3 Block.
    'Fiend Fire' : [2, True, Fiend_Fire, 'A', False, False], #exhaust
    'Fire Breathing' : [1, True, Fire_Breathing, 'P', False, False],#gamestate,  Whenever you draw a Status or Curse card,
    'Flame Barrier' : [2, False, Flame_Barrier, 'S', False, False], #gamestate,  Whenever you are attacked this turn
    'Flex' : [0, False, Flex, 'S', False, False], #gamestate, lose 2 strength at end of turn
    'Ghostly Armor' : [1, False, Ghostly_Armor,'S', True, False],
    'Havoc' : [1, False, Havoc, 'S', False, False],
    'Headbutt' : [1, True, Headbutt,'A', False, choose_Headbutt], #need new function to return card from discard pile
    'Heavy Blade' : [2, True, Heavy_Blade, 'A', False, False], #Strength affects heavy blade 3 times
    'Hemokinesis' : [1, True, Hemokinesis, 'A', False, False],
    'Immolate' : [2, False, Immolate, 'A', False, False],
    'Impervious' : [2, False, Impervious, 'S', False, False], #exhaust
    'Infernal Blade' : [1, False, Infernal_Blade,'S', False, False],
    'Inflame' : [1, True, Inflame, 'P', False, False],
    'Intimidate' : [0, False, Intimidate,'S', False, False], # exhaust
    'Iron wave' : [1, True, Iron_wave,'A', False, False],
    'Juggernaut' : [2, True, Juggernaut, 'P', False, False], # gamstate, Whenever you gain Block,
    'Limit Break' : [1, False, Limit_Break, 'S', False, False], #exhaust
    'Metallicize' : [1, False, Metallicize,'P', False, False], #gamestate,At the end of your turn, gain 3 Block.
    'Offering' : [0, False, Offering, 'S', False, False], #need add energy/mana function, exhaust
    'Perfected Strike' : [2, True, Perfected_Strike, 'A', False, False],
    'Pommel Strike' : [1, True, Pommel_Strike, 'A', False, False], #draw
    'Power Through' : [1, False, Power_Through, 'S', False, False], #add 2 wounds to hand
    'Pummel' : [1, True, Pummel, 'A', False, False], #exhaust
    'Rage' : [0, False, Rage, 'S', False, False], # gamestate, Whenever you play an Attack this turn, gain 3 Block
    'Rampage' : [1, True, Rampage, 'A', False, False], #need ability to track unique cards of rampage
    'Reaper' : [2, False, Reaper, 'A', False, False], #exhaust
    'Reckless Charge' : [0, True, Reckless_Charge, 'A', False, False], #shuffle daze in draw pile
    'Rupture' : [1, False, Rupture, 'P', False, False], #gamestate, Whenever you lose HP from a card, gain 1 Strength.
    'Searing Blow' : [2, True, Searing_Blow, 'A', False, False], #can be upgraded nay number of times
    'Seeing Red' : [0, False, Seeing_Red, 'S', False, False], #exhaust
    'Sentinel' : [1, False, Sentinel, 'S', False, False], #check gamestate for exhaust skills when used
    'Sever Soul' : [2, False, Sever_Soul, 'A', False, False],
    'Shockwave' : [2, False, Shockwave, 'S', False, False], # exhaust
    'Shrug It Off' : [1, False, Shrug_It_Off, 'S', False, False], #draw
    'Spot Weakness' : [1, True, Spot_Weakness, 'S', False, False], #check enemy intent, NEED TARGET_MONSTER
    'Strike' : [1, True, Strike, 'A', False, False],
    'Second Wind' : [1, False, Second_Wind, 'S', False, False], # #Exhaust all non-Attack Cards in your hand.
    'Sword Boomerang' : [1, True, Sword_Boomerang, 'A', False, False], #some way to handle probability
    'Thunderclap' : [1, True,Thunderclap, 'A', False, False],
    'True grit' : [1, False, True_Grit, 'S', False, False], #need some way to randomly handle probability
    'Twin Strike' : [1, True, Twin_Strike, 'A', False, False],
    'Uppercut' : [2, True, Uppercut, 'A', False, False],
    'Warcry' : [0, False, Warcry, 'S', False, False],
    'Whirlwind' : ['Whirlwind', False, Whirlwind, 'A', False, False], #COST IS VARIABLE PAY ATTENTION
    'Wild Strike' : [1, True, Wildstrike,'A', False, False], #shuffle wound to draw pile
    'Slimed' : [1, False, Slimed, 'ST', False, False],
    'Burn' : [0, False, Burn, 'ST', False, False],
    'Dazed' : [0, False, Dazed, 'ST', True, False],
    'Wound' : [0, False, Wound, 'ST', False, False],
    'Void' : [0, False, Void, 'ST', True, False],
    }


