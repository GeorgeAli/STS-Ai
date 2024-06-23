#dict of cards
#cost, target, function, type, ethereal
#target true = card can target enemy
#target false = card just gets played
#type = A for Attack,  P for Power, S for Skill
#ethereal = whether the card is exhausted after end of turn
#choose_headbut(), choose_armaments() = False, if not need

#will need new type for status like the card wound

#WILL NEED MORE FIELD IN ARRAY
#Ethereal, exhaust, etc.
#type of card also important
#need ignore discard field

import colorless_card, curse_card, help_function, ironclad_cards, status_card
from ironclad_cards import *
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
    'Spot Weakness' : [1, False, Spot_Weakness, 'S', False, False], #check enemy intent
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
    }
    
    #call the dictionary
    #print(cards['Anger'][0])
    #print(cards['Anger'][1])
    #newstate = cards['Anger'][2](gamestate,hitmonster)
    #print(cards['Anger'][3])
