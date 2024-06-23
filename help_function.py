import math

def dealdmg(gamestate, damage, monster, attacknum = 1):
    newstate = gamestate

    for pplayer in newstate.player.powers:
        if pplayer.power_name == "Strength":
            damage += p.amount
    for pplayer in newstate.player.powers:
        if pplayer.power_name == "Weakened":
            #round down
            damage = math.floor(damage * 0.75)
    for pmonster in newstate.monsters[monster].powers:
        if pmonster.power_name == "Vulnerable":
            #round down
            damage = math.floor(damage * 1.5)

    #rage 0 cost Whenever you play an Attack this turn, gain 3 Block
    for power_player in newstate.player.powers:
        if power_player.power_name == "Rage":
            newstate = addblock(newstate, power_player.amount)

    #double tap  This turn, your next 1(2) Attack is played twice.
    for power_player in newstate.player.powers:
        if power_player.power_name == "Double Tap":
            attacknum = attacknum+attacknum
            power_player = power_player - 1
            if power_player.amount == 0:
                del player_power

    for x in range(attacknum):
    #need to check block. if block is existed, reduce block. Not the HP
        if newstate.monsters[monster].block > 0 :
            if newstate.monsters[monster].block < damage:
                # remain
                left = damage - newstate.monsters[monster].block

                newstate.monsters[monster].block = 0
                newstate.monsters[monster].current_hp -= left
                if newstate.monsters[monster].current_hp <= 0:
                    del newstate.monsters[monster]

        else:
            newstate.monsters[monster].current_hp -= damage
            if newstate.monsters[monster].current_hp <= 0:
                del newstate.Monsters[monster]
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
        if not monster.is_gone:
            # Attack n times
            for attackmum in range(newstate.monsters[monster].move_hit):
                # lose block first
                if newstate.player.block > 0:
                    if newstate.monsters[monster].block < newstate.monsters[monster].move_adjust_damage:
                        left = newstate.monsters[monster].move_adjust_damage - newstate.monsters[monster].block
                        newstate.player.block = 0
                        newstate.player.current_hp - left
                    else:
                        newstate.player.block -= newstate.monsters[monster].move_adjust_damage
                # lose hp if no block
                else:
                    newstate.player.current_hp -= newstate.monsters[monster].move_adjust_damage

                #flame barrier 2 cost Gain 12 Block. Whenever you are attacked this turn, deal 4 damage to the attacker.
                for player_power in newstate.player.powers:
                    if player_power.power_name == "Flame Barrier":
                        newstate = dealdmg(newstate, player_power.amount, monster)
    # only this turn
    for player_power in newstate.player_power.powers:
        if player_power.power_name == "Flame Barrier":
            del player_power

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
        if player_powers.power_name == "Juggernaut":
            x = randomrange(len(newstate.monsters))
            newstate = dealdmg(newstate, player_power.amount, newstate.monsters[x])
    #add block
    newstate.player.block += block

    return newstate

def addcard(gamestate, name, pile):
    newstate = gamestate
    #newcard = card(name, name, card_type, "", upgrades=0, has_target=False, cost=0, uuid="", misc=0, price=0, is_playable=False, exhausts=False):
    newcard = Card(name = name, upgrades = 0, cost = cards[name][0])
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
    for pmonster in newstate.monsters[monster].power:
        if pmonster.power_name == "Vulnerable":
            pmonster.amount = pmonster.amount + amount
            return newstate
    newvulnerable = Power("Vulnerable", "Vulnerable", amount)
    newvulnerable.just_applied = True
    newstate.monsters[monster].powers.append(newvulnerable)
    return newstate

def dealweak(gamestate, amount, monster):
    newstate = gamestate
    for pmonster in newstate.monsters[monster].power:
        if pmonster.power_name == "Weakened":
            pmonster.amount = pmonster.amount + amount
            return newstate
    newweak = Power("Weakened", "Weakened", amount)
    newweak.just_applied = True
    newstate.monsters[monster].powers.append(newweak)
    return newstate

def player_gain_strength(newstate, amount):
    newstate = gamestate

    for power_player in newstate.player.powers:
        if power_player.power_name == "Strength":
            power_name.amount = power_name.amount + amount

    New_power = Power("Strength", "Strength", amount)
    New_power.just_applied = True
    newstate.player.powers.append(New_power)

    return newstate

def monster_lose_strength(newstate, amount, monster):
    newstate = gamestate

    for power_monster in newstate.monsters[monster].powers:
        if power_monster.power_name == "Strength":
            power_name.amount = power_name.amount - amount

    return newstate


def draw(gamestate, amount):
    newstate = gamestate
    #check deck
    #if not enough cards add discards_pile to deck, and reset discard_pile
    can_draw = True # it is for "Battle Trance", which is cannot draw card for this turn

    for power_player in newstate.player.powers:
         if power_player.power_name == "No Draw":
             can_draw = False

    if can_draw:
        if len(newstate.deck_pile) < amount :

            left = amount - len(newstate.deck_pile)

            for x in range(len(newstate.deck_pile)):
                #max hand
                if len(newstate.hand_pile) != 10:
                    # chosen_card randomly
                    chosen_card = randomrange(len(newstate.deck_pile[chosen_card]))
                    # add chosen_card to hand_pile
                    newstate.hand_pile.append(newstate.deck_pile[chosen_card])
                    #evolve 1 cost Whenever you draw a Status, draw 1 card to fucntion called draw
                    for player_power in newstate.player.powers:
                            if player_power.power_name == "Evolve":
                                if newstate.deck_pile[chosen_card].type == CardType.STATUS:
                                    newstate = draw(newstate, 1)

                    #fire breathing 1 cost Whenever you draw a Status or Curse card, deal 6(10) damage to all enemies.
                            if player_power.power_name == "Fire Breathing":
                                if newstate.deck_pile[chosen_card].type == CardType.STATUS:
                                    newstate = draw(newstate, 1)
                                if newstate.deck_pile[chosen_card].type == CardType.CURSE:
                                    newstate = draw(newstate, 1)
                    # remove chosen_card from deck_pile
                    newstate.deck_pile.pop(chosen_card)

            # add discard_pile to deck_pile
            newstate.deck_pile = newstate.discard_pile
            # reset the discard_pile
            newstate.discard_pile.clear()

            for x in range(left):
                #max hand
                if len(newstate.hand_pile) != 10:
                    # chosen_card randomly
                    chosen_card = randomrange(len(newstate.deck_pile))
                    # add chosen_card to hand_pile

                    newstate.hand_pile.append(newstate.deck_pile[chosen_card])
                    #evolve 1 cost Whenever you draw a Status, draw 1 card to fucntion called draw
                    for player_power in newstate.player.powers:
                        if player_power.power_name == "Evolve":
                            if newstate.deck_pile[chosen_card].type == CardType.STATUS:
                                newstate = draw(newstate, 1)

                    #fire breathing 1 cost Whenever you draw a Status or Curse card, deal 6(10) damage to all enemies.
                            if player_power.power_name == "Fire Breathing":
                                if newstate.deck_pile[chosen_card].type == CardType.STATUS:
                                    newstate = draw(newstate, 1)
                                if newstate.deck_pile[chosen_card].type == CardType.CURSE:
                                    newstate = draw(newstate, 1)

                    # remove chosen_card from deck_pile
                    newstate.deck_pile.pop(chosen_card)
        else:
            for x in range(amount):
                #max hand
                if len(newstate.hand_pile) != 10:
                    # chosen_card randomly
                    chosen_card = randomrange(len(newstate.deck_pile))
                    # add chosen_card to hand_pile
                    newstate.hand_pile.append(newstate.deck_pile[chosen_card])
                    # remove chosen_card from deck_pile
                    newstate.deck_pile.pop(chosen_card)

    return newstate

def upgrade(card):
    if card.name == "Searing Blow":
        card.upgrades += 1
    elif card.upgrades > 1:
        card.upgrades = 1
    return card

# def changestrength(gamestate, amount, character):
#     newstate = gamestate
#     character


# Effect at end of turn
def end_of_turn(gamestate):
    newstate = gamestate

    # Take demage from the monsters
    newstate = player_take_damage(newstate)

    #check
    #Pride : Innate, Ate the end of turn, put a copy of this card on top of your draw pile. Exhuast
	#Innate : Start each combat with this card in your hand
    Pride = False
    for card in newstate.hand:
        if card.name == "Pride":
              Pride = True

    #combust At the end of your turn, lose 1 HP and deal 5 damage to ALL enemies
    for power_player in newstate.player.powers:
        if power_player.power_name == "Combust":
            newstate.player.current_hp -= power_player.power.damage
            #deal power_player.amount dmage to All
            for monster in range(len(newstate.monsters)):
                newstate = dealdmg(newstate, power_player.amount, monster)

            #rupture 1 cost Whenever you lose HP from a card, gain 1 Strength
            for player_power in newstate.player.powers:
                if player_power.power_name == "Rupture":
                    newstate = player_gain_strength(newstate, player_power.amount)

    #flex At the end of your turn, lose 2(4) Strength.
    for power_player in newstate.player.powers:
        if power_player.power_name == "Flex":
            newstate = player_gain_strength(newstate, power_player.amount)

    #metallicize At the end of your turn, gain 3(4) Block.
    for power_player in newstate.player.powers:
        if power_player.power_name == "Metallicize":
            newstate = addblock(newstate, power_player.amount)

    #deal poison damage, reduces poison stack
    #monster
    for monster in range(len(newstate.monster)):
        for pmonster in newstate.monsters[monster].powers:
            if pmonster.power_name == "Poison":
                if newstate.monsters[monster].block > 0:
                    if newstate.monsters[monster].block < pmonster.amount:
                        left = pmonster.amount - newstate.monsters[monster].block
                        newstate.monsters[monster].block = 0
                        newstate.monsters[monster].current_hp - left
                    else:
                        newstate.pmonster.block -= pmonster.amount
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

    for power_monster in newstate.monsters.powers:

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
        x = cards[card.name]
        if x[4] == True:
            gamestate = addcard(gamestate, card.name, 'exhaust_pile')
            del card

    return newstate

def start_of_turn(gamestate):
    newstate = gamestate

    #reset energy/mana
    for player_power in newstate.player.powers:
        if player_power.power_name == "Energized":
            newstate.player.energy = newstate.player.energy + player_power.amount
        else:
            newstate.player.energy = 3

    #at the start of your turn, Block no longer expires
    # else do reset the block
    for player_power in newstate.player.powers:
        if player_power.power_name == "Barricade":
            # keep the block
            newstate.player.block = newstate.player.block
        else:
            newstate.player.block = 0

    #demon form 3 cost At the start of each turn, gain 2 Strength.
    for player_power in newstate.player.powers:
        if player_power.power_name == "Demon Form":
            newstate = player_gain_strength(newstate, player_power.amount)

    #brutality 0 cost (Innate.) At the start of your turn, lose 1 HP and draw 1 card.
    #Warning : Even if player has block, lose hp
    for player_power in newstate.player.powers:
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
