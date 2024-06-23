#This is colorless_card

from help_function import *
import random

"""
    List of card needs to add end of turn
    
    #The Bomb : cost 2, At the end of 3 turns, deal 40(50) damage to ALL enemies.
    #Omega : cost 3 , At the end of your turn deal 50(60) damage to ALL enemies.
    
    List of card needs to add start of turn
    
    #magnetism : cost 2(1), At the start of each turn, add a random colorless card to your hand.
    #Mayhem : cost 2(1), At the start of your turn, play the top card of your draw pile.
    
    List of card needs to work:
    
"""
#Bandage Up : cost 0, Heal 4(6)HP exhaust
def Bandage_UP(gamestate, hitmonster, upgrade):
    newstate = gamestate
    if upgrade:
        newstate = healing(newstate, 6)
    else:
        newstate = healing(newstate, 4)
    newstate = addcard(newstate, "Bandage Up", 'exhaust_pile')
    return newstate
  
#Blind : cost 0, Apply 2 weak (to ALL enemies)
def Blind(newstate, hitmonster, upgrade):
    newstate = gamestate
    if upgrade:
        for monster in range(len(newstate.monsters)):
            dealweak(newstate, 2, monster)
    else:
        dealweak(newstate, 2, histmonster)
        
    return newstate
#modify here : THIS TURN

#Dard shackles : cost 0, Enemy loses 9(15) Strength for the rest of this turn. Exhaust.
def Dard_Shackles(newstate, hitmonster, upgrade):
    newstate = gamestate
    if upgrade:
        monster_lose_strength(newstate, 15, hitmonster)
    else:
        monster_lose_strength(newstate, 9, hitmonster)
        
    newstate = addcard(newstate, "Dard Shackles", 'exhaust_pile')
    return newstate

#Deep Breath : cost 0 , Shuffle your discard pile into your draw pile. Draw 1(2) card(s).
def Deep_Breath(newstate, hitmonster, upgrade):
    newstate = gamestate
    for card in newstate.discard_pile:
        newstate = addcard(newstate, card.name ,'draw_pile')
    
    #delete all discard_pile
    del newstate.discard_pile
    
    if upgrade:
        newstate = draw(newstate, 2)
    else:
        newstate = draw(newstate, 1)
        
    return newstate

#Discovery : cost 1, Choose 1 of 3 random cards to add to your hand. It costs 0 this turn. Exhaust. (Don't Exhaust.)
def Discovery(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Dramatic Entrance : cost 0 , Innate. Deal 6(8) damage to ALL enemies. Exhaust.
def Dramatic_Entrance(newstate, hitmonster, upgrade):
    newstate = gamestate
    
    if upgrade:
        for monster in range(len(newstate.monsters)):
            newstate = dealdmg(newstate, 8, monster)
    else:
        for monster in range(len(newstate.monsters)):
            newstate = dealdmg(newstate, 6, monster)
    
    newstate = addcard(newstate,"Dramatic Entrance" ,'exhaust_pile')
    
    return newstate

#Enlightenment : cost 0 , Reduce the cost of cards in your hand to 1 this turn(combat)
def Enlightenment(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Finesse : cost 0 Gain 2(4)  Block. Draw 1 card.
def Finesse(newstate, hitmonster, upgrade):
    newstate = gamestate

    if upgrade:
        newstate = addblock(newstate, 4)
    else:
        newstate = addblock(newstate, 2)
    
    newstate = addcard(newstate, 1)
    
    return newstate

#Flash of Steel : cost 0, Deal 3(6) damage. Draw 1 card.
def Flash_of_Steel(newstate, hitmonster, upgrade):
    newstate = gamestate
    if upgrade:
        newstate = dealdmg(newstate, 6, hitmonster)
    else:
        newstate = dealdmg(newstate, 3, hitmonster)
        
    newstate = addcard(newstate, 1)
    
    return newstate

#Forethought : cost, Place a card(any number of cards) from your hand on the bottom of your draw pile. It (They) costs 0 until played.
def Forthought(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Good instincts : cost 0, Gain 5(8) Block.
def Good_instincts(newstate, hitmonster, upgrade):
    newstate = gamestate
    
    if upgrade:
        newstate = addblock(newstate, 8)
    else:
        newstate = addblock(newstate, 5)
        
    return newstate

#impatience : cost 0, If you have no Attack cards in your hand, draw 2(3) cards.
def impatience(newstate, hitmonster, upgrade):
    newstate = gamestate
    
    is_no_Attack = True
    
    for card in newstate.hand:
        if card.type == CardType.ATTACK:
            is_no_Attack = False
    
    if is_no_Attack :
        if upgrade:
            newstate = draw(newstate, 3)
        else:
            newstate = draw(newstate, 2)
    
    return newstate

#Jack Of All Trades : cost 0, Add 1(2) random Colorless card(s) to your hand.
def Jack_Of_All_Trades(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Madness : cost 1(0), A random card in your hand costs 0 for the rest of combat. Exhaust.
def Madness(newstate, hitmonster, upgrade):
    newstate = gamestate

    x = randomrange(lend(newstate.hand))
    newstate = newstate.hand[x].cost = 0

    newstate = addcard(newstate, "Madness", 'exhaust_pile')
    return newstate

#Mind Blast : cost 2(1), Innate. Deal damage equal to the number of cards in your draw pile.
def Mind_Blast(newstate, hitmonster, upgrade):
    newstate = gamestate

    newstate = dealdmg(newstate, len(newstate.draw_pile), hitmonster)

    return newstate

#Panacea : cost 0, Gain 1(2)  Artifact.Exhaust.
def Panacea(newstate, hitmonster, upgrade):
    newstate = gamestate
    
    newstate = addcard(newstate, "Panacea", 'exhaust_pile')
    
    return newstate

#Panic Button : cost 0, Gain 30(40) Block. You cannot gain IBlock from cards for the next 2 turns. Exhaust.

def Panic_Button(newstate, hitmonster, upgrade):
    newstate = gamestate
    if upgrade:
        newstate = addblock(newstate, 40)
    else:
        newstate = addblock(newstate, 30)
    return newstate

#Purity : cost 0, Choose and exhaust 3(5) cards in your hand. Exhaust.
def Purity(newstate, hitmonster, upgrade):
    newstate = gamestate
    
    newstate = addcard(newstate, "Purity", 'exhaust_pile')
    return newstate

#Swift Strike : cost 0, Deal 6(9) damage.
def Swift_Strike(newstate, hitmonster, upgrade):
    newstate = gamestate
    
    if upgrade:
        newstate = dealdmg(newstate, 6, hitmonster)
    else:
        newstate = dealdmg(newstate, 9, hitmonster)
        
    return newstate

#Trip : cost 0, Apply 2 Vulnerable (to ALL enemies).
def Trip(newstate, hitmonster, upgrade):
    newstate = gamestate
  
    if upgrade:
        for monster in range(len(newstate.monsters)):
            newstate = dealvulnerable(newstate, 2, monster)
    else:
        newstate = dealvulnerable(newstate, 2, hitmonster)

    return newstate

#Apotheosis : cost 2(1), Upgrade ALL of your cards for the rest of combat. Exhaust.
def Apotheosis(newstate, hitmonster, upgrade):
    newstate = gamestate
    
    # upgrade all for the rest of combat
    for card in newstate.hand:
        newstate = upgrade(card)
    
    for card in newstate.draw_pile:
        newstate = upgrade(card)
    
    for card in newstate.exhaust_pile:
        newstate = upgrade(card)
        
    for card in newstate.discard_pile:
        newstate = upgrade(card)
        
    return newstate

#Chrysalis : cost 2, Add 3(5) random Skills into your Draw Pile. They cost 0 this combat. Exhaust.
def Chrysalis(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Hand of Greed : cost 2 , Deal 20(25) damage. If this kills a non-minion enemy, gain 20(25) Gold.
def Hand_of_Greed(newstate, hitmonster, upgrade):
    newstate = gamestate
    if upgrade:
        newstate = dealdmg(newstate, 25, hitmonster)
        # if this kills a non-minion enemy, gain 25 Gold
    else:
        newstate = dealdmg(newstate, 20, hitmonster)
        # if this kills a non-minion enemy, gain 20 Gold

    return newstate

#magnetism : cost 2(1), At the start of each turn, add a random colorless card to your hand.
def Magnetism(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Master Of Strategy : cost 0, Draw 3(4) cards. Exhaust.
def Master_Of_Strategy(newstate, hitmonster, upgrade):
    newstate = gamestate

    if upgrade:
        newstate = draw(newstate, 4)
    else:
        newstate = draw(newstate, 3)
        
    return newstate

#Mayhem : cost 2(1), At the start of your turn, play the top card of your draw pile.
def Mayhem(newstate, hitmonster, upgrade):
    newstate = gamestate
    
    return newstate

#Metamorphosis: cost 2, Add 3(5) random Attacks into your Draw Pile. They cost 0 this combat. Exhaust.
def Metamorphosis(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Panache : cost 0, Every time you play 5 cards in a single turn, deal 10(14) damage to ALL enemies.
def Panache(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Sadistic Nature : cost 0, Whenever you apply a Debuff to an enemy, they take 3(4) damage.
def Sadistic_Nature(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Secret Technique : cost 0, Choose a Skill from your draw pile and place it into your hand. Exhaust. (Don't Exhaust)
def Secret_Technique(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Secret Weapon : cost 0, Choose an Attack from your draw pile and place it into your hand. Exhaust. (Don't Exhaust)
def Secret_Weapon(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#The Bomb : cost 2, At the end of 3 turns, deal 40(50) damage to ALL enemies.
def The_Bomb(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Thinking Ahead : cost 0, Draw 2 cards. Place a card from your hand on top of your draw pile. Exhaust.(Don't Exhaust)
def Thinking_Ahead(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Transmutation :cost X, Add X random (Upgraded) colorless cards into your hand. They cost 0 this turn. Exhaust.
def Transutation(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Violence : cost 0 , Place 3(4) random Attack cards from your draw pile into your hand. Exhaust.
def Violence(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Apparition : cost 1, Gain 1 Icon Intangible Intangible. Exhaust. Ethereal. (no longer Ethereal.)(Obtained from event: Council of Ghosts).
def Apparition(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Beta : cost 2(1), Shuffle an Omega into your draw pile. Exhaust. (Obtained from Alpha).
def Beta(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Bite : cost 1, Deal 7(8) damage. Heal 2(3) HP. (Obtained from event: Vampires(?)).
def Bite(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Expunger : cost 1, Deal 9(15) damage X times. (Obtained from Conjure Blade).
def Expunger(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#insight : cost 0, Icon Retain Retain. Draw 2(3) cards. Exhaust. (Obtained from Evaluate, Pray and Study).
def Insight(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#J.A.X. : cost 0, Lose 3 HP.Gain 2(3) Icon Strength Strength. (Obtained from event: Augmenter)
def JAX(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Miracle : cost 0, Icon Retain Retain. Gain (2) Energy. Exhaust. (Obtained from Collect, Deus Ex Machina, PureWater-0 Pure Water, and Holy water Holy Water).
def Miracle(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Omega : cost 3 , At the end of your turn deal 50(60) damage to ALL enemies. (Obtained from Beta).
def Omega(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Ritual Dagger : cost 1, Deal 15 damage. If this kills an enemy then permanently increase this card's damage by 3(5) (Obtained during event: The Nest)
def Ritual_Dagger(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Safety : cost 1 , Icon Retain Retain. Gain 12(16) Icon Block Block. Exhaust. (Obtained from Deceive Reality).
def Safety(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Shiv : cost 0, Deal 4(6) damage. Exhaust. (Obtained from the Blade Dance, Cloak and Dagger, Infinite Blades, Storm of Steel, and NinjaScroll Ninja Scroll).
def Shiv(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Smite : cost 1 , Icon Retain Retain. Deal 12(16) damage. Exhaust. (Obtained from Carve Reality and Battle Hymn).
def Smite(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate

#Through Violence : cost 0, Icon Retain Retain. Deal 20(30) damage. Exhaust. (Obtained from Reach Heaven).
def Through_Violence(newstate, hitmonster, upgrade):
    newstate = gamestate
    return newstate



