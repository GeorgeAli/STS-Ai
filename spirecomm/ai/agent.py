import random
import sys
from anytree import Node, RenderTree, LevelOrderGroupIter
import copy
from card_dictionary import *
from spirecomm.spire.game import Game
from spirecomm.spire.character import Intent, PlayerClass
import spirecomm.spire.card
from spirecomm.spire.screen import RestOption
from spirecomm.communication.action import *
from spirecomm.ai.priorities import *


class SimGame:
    def __init__(self):
        self.in_combat = False
        self.player = None
        self.monsters = []
        self.draw_pile = []
        self.discard_pile = []
        self.exhaust_pile = []
        self.hand = []
        self.limbo = []
        self.card_in_play = None
        self.turn = 0
        self.cards_discarded_this_turn = 0
        self.gold = 0
        # --------- Additional
        self.decision = []


# percolates the max evaluation value up to the root of the tree
# @param r: the root node of the tree
def tree_search(r):
    if not r.children:  # if node is a leaf
        return
    max = -1001
    for children in LevelOrderGroupIter(r, maxlevel=2):
        for node in children:
            if node in r.children:
                tree_search(node)
                if node.name.grade > max:
                    max = node.name.grade
    r.name.grade = max  # set current node's eval to max of children


# assigns evaluation values to the leaves of the tree only
# @param r: the root node of the tree
def eval_tree(r):
    for children in LevelOrderGroupIter(r):
        for node in children:
            if not node.children:
                node.name.grade = eval_function(node.name)


# return a ballpark evaluation number for given game state
def eval_function(gamestate):
    # eval out of 1000 or so, can be more or less
    eval = 0
    # hp
    eval += gamestate.player.current_hp
    if gamestate.player.current_hp < 1:
        eval -= 200
    eval += gamestate.gold
    if gamestate.monsters == []:
        eval += 200
    else:
        for m in gamestate.monsters:
            if m.current_hp < 0:
                m.current_hp = 0
            eval -= m.current_hp
            eval -= m.move_adjusted_damage * m.move_hits
            for mpower in gamestate.player.powers:
                if mpower.power_name == "Strength":
                    eval -= mpower.amount
                if mpower.power_name == "Weakened":
                    eval += mpower.amount
                if mpower.power_name == "Vulnerable":
                    eval += mpower.amount
                if mpower.power_name == "Rage":
                    eval -= mpower.amount
                if mpower.power_name == "Double Tap":
                    eval -= mpower.amount * 25
                if mpower.power_name == "Flame Barrier":
                    eval -= mpower.amount
                if mpower.power_name == "Dexterity":
                    eval -= mpower.amount
                if mpower.power_name == "Juggernaut":
                    eval -= mpower.amount
                if mpower.power_name == "Dark Embrace":
                    eval -= mpower.amount
                if mpower.power_name == "Feel No Pain":
                    eval -= mpower.amount
                if mpower.power_name == "Sentinel":
                    eval -= mpower.amount
                if mpower.power_name == "No Draw":
                    eval += mpower.amount
                if mpower.power_name == "Evolve":
                    eval -= mpower.amount
                if mpower.power_name == "Fire Breathing":
                    eval -= mpower.amount
                if mpower.power_name == "Combust":
                    eval -= mpower.amount
                if mpower.power_name == "Rupture":
                    eval -= mpower.amount
                if mpower.power_name == "Flex":
                    eval -= mpower.amount
                if mpower.power_name == "Metallicize":
                    # number of block in the end
                    eval -= (mpower.amount * (mpower.amount + 1)) / 2
                if mpower.power_name == "Poison":
                    # number of damage in the end
                    eval += (mpower.amount * (mpower.amount + 1)) / 2
                if mpower.power_name == "Energized":
                    eval -= 100
                if mpower.power_name == "Barricade":
                    eval -= gamestate.player.block * 2
                if mpower.power_name == "Demon Form":
                    eval -= mpower.amount * 100
                if mpower.power_name == "Brutality":
                    eval -= mpower.amount * 25
                if mpower.power_name == "Rupture":
                    eval -= mpower.amount * 25
            # have to do monster powers

    # have to do player powers
    for ppower in gamestate.player.powers:
        if ppower.power_name == "Strength":
            eval += ppower.amount
        if ppower.power_name == "Weakened":
            eval -= ppower.amount
        if ppower.power_name == "Vulnerable":
            eval -= ppower.amount
        if ppower.power_name == "Rage":
            eval += ppower.amount
        if ppower.power_name == "Double Tap":
            eval += ppower.amount * 25
        if ppower.power_name == "Flame Barrier":
            eval += ppower.amount
        if ppower.power_name == "Dexterity":
            eval += ppower.amount
        if ppower.power_name == "Juggernaut":
            eval += ppower.amount
        if ppower.power_name == "Dark Embrace":
            eval += ppower.amount
        if ppower.power_name == "Feel No Pain":
            eval += ppower.amount
        if ppower.power_name == "Sentinel":
            eval += ppower.amount
        if ppower.power_name == "No Draw":
            eval -= ppower.amount
        if ppower.power_name == "Evolve":
            eval += ppower.amount
        if ppower.power_name == "Fire Breathing":
            eval += ppower.amount
        if ppower.power_name == "Combust":
            eval += ppower.amount
        if ppower.power_name == "Rupture":
            eval += ppower.amount
        if ppower.power_name == "Flex":
            eval += ppower.amount
        if ppower.power_name == "Metallicize":
            # number of block in the end
            eval += (ppower.amount * (ppower.amount + 1)) / 2
        if ppower.power_name == "Poison":
            # number of damage in the end
            eval -= (ppower.amount * (ppower.amount + 1)) / 2
        if ppower.power_name == "Energized":
            eval += 100
        if ppower.power_name == "Barricade":
            eval += gamestate.player.block * 2
        if ppower.power_name == "Demon Form":
            eval += ppower.amount * 100
        if ppower.power_name == "Brutality":
            eval += ppower.amount * 25
        if ppower.power_name == "Rupture":
            eval += ppower.amount * 25
    # have to do potions

    # print all the powers for troubleshooting later
    original_stdout = sys.stdout  # Save a reference to the original standard output

    with open("powers .txt", "w") as f:
        sys.stdout = f  # Change the standard output to the file we created.
        powerout = ["Player Powers"]
        for p in gamestate.player.powers:
            powerout = []
            powerout.append("power_id = " + p.power_id)
            powerout.append("power_name = " + p.power_name)
            powerout.append("amount = ")
            powerout.append(p.amount)
            powerout.append("damage = " + str(p.damage))
            powerout.append("misc = " + str(p.misc))
            powerout.append("just_applied" + str(p.just_applied))
            powerout.append("card")
            powerout.append(p.card)
        print(powerout)

        # Monster powers
        mpowerout = ["Monster Powers"]
        for m in gamestate.monsters:
            for p in m.powers:
                mpowerout = []
                mpowerout.append("power_id = " + p.power_id)
                mpowerout.append("power_name = " + p.power_name)
                mpowerout.append("amount = ")
                mpowerout.append(p.amount)
                mpowerout.append("damage = " + str(p.damage))
                mpowerout.append("misc = " + str(p.misc))
                mpowerout.append("just_applied" + str(p.just_applied))
                mpowerout.append("card")
                mpowerout.append(p.card)
        print(mpowerout)
        sys.stdout = original_stdout  # Reset the standard output to its original value
    return eval


# returns the next game state after updating a copy of current state
# @param decision: the decision chosen for the next game state
# decision is either the card to be played or the end turn function
# @param state: the current state to be copied and modified
def get_next_game_state(play, state, target):

    # copy current state
    next_state = copy.deepcopy(state)

    # end turn
    decisionlist = []
    if isinstance(play, str):
        next_state = end_of_turn(next_state)
        next_state = start_of_turn(next_state)
        next_state.decision.append("End_Turn")
        return next_state

    # special cards
    elif isinstance(target, list):
        card = play.name
        next_state = cards[card](next_state, target, play.upgrades)
        if play.exhausts == True:
            next_state = addcard(next_state, play.name, "exhaust_pile", play)
        else:
            next_state = addcard(next_state, play.name, "discard_pile", play)
        decisionlist.append(play)
        indexlist = []
        if target[0] == -1:
            indexlist.append("No Monster Target")
            indexlist.append(next_state.player.hand[target[1]])
        elif target[1] == -1:
            indexlist.append(next_state.monsters[target[0]])
            indexlist.append("No Card Target")
        else:
            indexlist.append(next_state.monsters[target[0]])
            indexlist.append(next_state.player.hand[target[1]])
        decisionlist.append(indexlist)
        # this makes len(decision[x]) == 3 so we can discriminate for special
        decisionlist.append("special")

    # cards requiring no target
    elif target == -1:
        card = play.name
        next_state = cards[card][2](next_state, Upgrade=play.upgrades)
        if play.exhausts == True:
            next_state = addcard(next_state, play.name, "exhaust_pile", play)
        else:
            next_state = addcard(next_state, play.name, "discard_pile", play)
        decisionlist.append(play)

    # cards requiring target
    else:
        card = play.name
        next_state = cards[card][2](
            next_state, hitmonster=target, Upgrade=play.upgrades
        )
        if play.exhausts == True:
            next_state = addcard(next_state, play.name, "exhaust_pile", play)
        else:
            next_state = addcard(next_state, play.name, "discard_pile", play)
        decisionlist.append(play)
        decisionlist.append(target)

    next_state.decision.append(decisionlist)
    return next_state


def getstate(gamestate):
    n = SimGame()
    n.player = gamestate.player
    n.monsters = gamestate.monsters
    n.draw_pile = gamestate.draw_pile
    n.discard_pile = gamestate.discard_pile
    n.exhaust_pile = gamestate.exhaust_pile
    n.hand = gamestate.hand
    n.limbo = gamestate.limbo
    n.card_in_play = gamestate.card_in_play
    n.turn = gamestate.turn
    n.cards_discarded_this_turn = gamestate.cards_discarded_this_turn
    n.gold = gamestate.gold
    n.decision = []
    return n


def build_tree(gamestate):
    # bad code
    # if not (gamestate.name.monsters or gamestate.name.player.current_hp <= 0 or three_end_turns(gamestate.name.decision)):
    if (
        (not gamestate.name.monsters)
        or (gamestate.name.player.current_hp <= 0)
        or (three_end_turns(gamestate.name.decision))
    ):
        return

    # original_stdout = sys.stdout
    # with open('cards.txt', 'a') as f:
    #     sys.stdout = f
    #     print(gamestate.name.hand)
    #     print(gamestate.name.draw_pile)
    #     print(gamestate.name.discard_pile)
    #     print(gamestate.name.player.energy)
    #     print(" ")
    # sys.stdout = original_stdout

    for c in gamestate.name.hand:
        if c.name not in [
            "Ascender's Bane",
            "Clumsy",
            "Curse of the Bell",
            "Doubt",
            "Injury",
            "Necronomicurse",
            "Normality",
            "Pain",
            "Parasite",
            "Regret",
            "Shame",
            "Writhe",
            "Burn",
            "Dazed",
            "Void",
            "Wound",
        ]:
            if gamestate.name.player.energy >= c.cost:
                # get_next_game_state needs to append the decision to gamestate.decision

                # checks if needs target
                card = c.name
                if card not in cards:
                    return

                # special cards
                if not cards[card][5] == False:
                    index = cards[card][5](gamestate, 0, c.upgrades)
                    p = c
                    next_state = gamestate.name
                    next_state.hand.remove(c)
                    next_state.player.energy -= p.cost
                    for i in index:
                        next_state = get_next_game_state(p, next_state, i)
                        child = Node(next_state, parent=gamestate)
                        build_tree(child)

                elif cards[card][1] == True:
                    p = c
                    next_state = gamestate.name
                    next_state.hand.remove(c)
                    next_state.player.energy -= p.cost
                    for monsterindex in range(len(next_state.monsters)):
                        if not next_state.monsters[monsterindex].is_gone:
                            next_state = get_next_game_state(
                                p, next_state, monsterindex
                            )
                            child = Node(next_state, parent=gamestate)
                            build_tree(child)

                # don't need target
                else:
                    p = c
                    next_state = gamestate.name
                    next_state.hand.remove(c)
                    next_state.player.energy -= p.cost
                    next_state = get_next_game_state(p, next_state, -1)
                    child = Node(next_state, parent=gamestate)
                    build_tree(child)

    # end turn
    next_state = get_next_game_state("End_Turn", gamestate.name, -1)
    child = Node(next_state, parent=gamestate)
    build_tree(child)


# returns True if three end turns are in decision
def three_end_turns(decision):
    count = 0
    for x in decision:
        if x == "End_Turn":
            count += 1
            if count > 2:
                return True
    return False


# #returns first element in decision list of max leaf
# def max_leaf_decision(r):
#     for children in LevelOrderGroupIter(r, maxlevel=2):
#         for node in children:
#             if node in r.children:
#                 if node.name.grade == r.name.grade:
#                     if not node.children:
#                         return node.name.decision[0]
#                     else:
#                         max_leaf_decision(node)


class impleAgent:

    def __init__(self, chosen_class=PlayerClass.THE_SILENT):
        self.game = Game()
        self.errors = 0
        self.choose_good_card = False
        self.skipped_cards = False
        self.visited_shop = False
        self.map_route = []
        self.chosen_class = chosen_class
        self.priorities = Priority()
        self.change_class(chosen_class)

    def max_leaf_decision(self, r):
        for children in LevelOrderGroupIter(r, maxlevel=2):
            for node in children:
                if node in r.children:
                    if node.name.grade == r.name.grade:
                        if not node.children:
                            return node.name.decision[0]
                        else:
                            return self.max_leaf_decision(node)

    def change_class(self, new_class):
        self.chosen_class = new_class
        if self.chosen_class == PlayerClass.THE_SILENT:
            self.priorities = SilentPriority()
        elif self.chosen_class == PlayerClass.IRONCLAD:
            self.priorities = IroncladPriority()
        elif self.chosen_class == PlayerClass.DEFECT:
            self.priorities = DefectPowerPriority()
        else:
            self.priorities = random.choice(list(PlayerClass))

    def handle_error(self, error):
        raise Exception(error)

    def get_next_action_in_game(self, game_state):
        self.game = game_state
        # time.sleep(0.07)
        if self.game.choice_available:
            return self.handle_screen()
        if self.game.proceed_available:
            return ProceedAction()
        if self.game.play_available:
            if (
                self.game.room_type == "MonsterRoomBoss"
                and len(self.game.get_real_potions()) > 0
            ):
                potion_action = self.use_next_potion()
                if potion_action is not None:
                    return potion_action
            return self.get_play_card_action()

        if self.game.end_available:
            return EndTurnAction()
        if self.game.cancel_available:
            return CancelAction()

    def get_next_action_out_of_game(self):
        return StartGameAction(self.chosen_class)

    def is_monster_attacking(self):
        for monster in self.game.monsters:
            if monster.intent.is_attack() or monster.intent == Intent.NONE:
                return True
        return False

    def get_incoming_damage(self):
        incoming_damage = 0
        for monster in self.game.monsters:
            if not monster.is_gone and not monster.half_dead:
                if monster.move_adjusted_damage is not None:
                    incoming_damage += monster.move_adjusted_damage * monster.move_hits
                elif monster.intent == Intent.NONE:
                    incoming_damage += 5 * self.game.act
        return incoming_damage

    def get_low_hp_target(self):
        available_monsters = [
            monster
            for monster in self.game.monsters
            if monster.current_hp > 0 and not monster.half_dead and not monster.is_gone
        ]
        best_monster = min(available_monsters, key=lambda x: x.current_hp)
        return best_monster

    def get_high_hp_target(self):
        available_monsters = [
            monster
            for monster in self.game.monsters
            if monster.current_hp > 0 and not monster.half_dead and not monster.is_gone
        ]
        best_monster = max(available_monsters, key=lambda x: x.current_hp)
        return best_monster

    def many_monsters_alive(self):
        available_monsters = [
            monster
            for monster in self.game.monsters
            if monster.current_hp > 0 and not monster.half_dead and not monster.is_gone
        ]
        return len(available_monsters) > 1

    def get_play_card_action(self):
        # test a card like strike, card 1 may not be strike so watch out
        # return [self.game.hand[1], self.game.monsters[0]]

        # test end turn
        # return "End_Turn"
        d = 0

        # make SimGame object containing current real gamestate
        n = getstate(copy.deepcopy(self.game))
        # root node containing current real gamestate
        root = Node(n, parent=None)
        build_tree(root)
        eval_tree(root)
        tree_search(root)
        original_stdout = sys.stdout
        with open("tree.txt", "w", encoding="utf8") as f:
            sys.stdout = f
            for pre, fill, node in RenderTree(root):
                print(
                    "%s%s%s"
                    % (pre, "decision" + str(node.name.decision), node.name.grade)
                )
                # for c in node.name.hand:
                #     print(pre, c.name + ' ' + c.uuid)
        sys.stdout = original_stdout

        d = self.max_leaf_decision(root)
        root = None
        # delete tree

        # if we can't make the tree for some reason
        if d == None:
            playable_cards = [card for card in self.game.hand if card.is_playable]
            zero_cost_cards = [card for card in playable_cards if card.cost == 0]
            zero_cost_attacks = [
                card
                for card in zero_cost_cards
                if card.type == spirecomm.spire.card.CardType.ATTACK
            ]
            zero_cost_non_attacks = [
                card
                for card in zero_cost_cards
                if card.type != spirecomm.spire.card.CardType.ATTACK
            ]
            nonzero_cost_cards = [card for card in playable_cards if card.cost != 0]
            aoe_cards = [
                card for card in playable_cards if self.priorities.is_card_aoe(card)
            ]
            if self.game.player.block > self.get_incoming_damage() - (
                self.game.act + 4
            ):
                offensive_cards = [
                    card
                    for card in nonzero_cost_cards
                    if not self.priorities.is_card_defensive(card)
                ]
                if len(offensive_cards) > 0:
                    nonzero_cost_cards = offensive_cards
                else:
                    nonzero_cost_cards = [
                        card for card in nonzero_cost_cards if not card.exhausts
                    ]
            if len(playable_cards) == 0:
                return EndTurnAction()
            if len(zero_cost_non_attacks) > 0:
                card_to_play = self.priorities.get_best_card_to_play(
                    zero_cost_non_attacks
                )
            elif len(nonzero_cost_cards) > 0:
                card_to_play = self.priorities.get_best_card_to_play(nonzero_cost_cards)
                if (
                    len(aoe_cards) > 0
                    and self.many_monsters_alive()
                    and card_to_play.type == spirecomm.spire.card.CardType.ATTACK
                ):
                    card_to_play = self.priorities.get_best_card_to_play(aoe_cards)
            elif len(zero_cost_attacks) > 0:
                card_to_play = self.priorities.get_best_card_to_play(zero_cost_attacks)
            else:
                # This shouldn't happen!
                return EndTurnAction()
            if card_to_play.has_target:
                available_monsters = [
                    monster
                    for monster in self.game.monsters
                    if monster.current_hp > 0
                    and not monster.half_dead
                    and not monster.is_gone
                ]
                if len(available_monsters) == 0:
                    return EndTurnAction()
                if card_to_play.type == spirecomm.spire.card.CardType.ATTACK:
                    target = self.get_low_hp_target()
                else:
                    target = self.get_high_hp_target()
                return PlayCardAction(card=card_to_play, target_monster=target)
            else:
                return PlayCardAction(card=card_to_play)

        if isinstance(d, str):
            return EndTurnAction()

        with open("PCA.txt", "w") as f:
            sys.stdout = f
            print(d)
            print(len(d))
            for m in range(len(self.game.monsters)):
                print("index" + str(m))
                print(self.game.monsters[m].name)
            print(" ")
        sys.stdout = original_stdout

        # simple play the card in d[0]
        if len(d) == 1:
            for c in self.game.hand:
                if c.uuid == d[0].uuid:
                    d[0] = c
            return PlayCardAction(d[0])

        # if card needs a target(s)
        # format d[0] card, d[1] target index
        if (len(d) == 2) and (isinstance(d[1], int)):
            for c in self.game.hand:
                if c.uuid == d[0].uuid:
                    d[0] = c
            return PlayCardAction(card=d[0], target_monster=self.game.monsters[d[1]])

        # else format is d[0] is the card to play
        # d[1] is the second Action to do
        # d[1][0] is the monster target index, can have 'No Monster Target'
        # d[1][1] is the card to be selected, can have 'No Card Target'
        else:
            for c in self.game.hand:
                if c.uuid == d[0].uuid:
                    d[0] = c
            # converting monster index to object
            if isinstance(d[1][0], int):
                d[1][0] = self.game.monsters[d[1][0]]
            # convert sim card object to real card
            if not (d[1][1] == "No Card Target"):
                for c in (
                    self.game.hand
                    + self.game.draw_pile
                    + self.game.discard_pile
                    + self.game.exhaust_pile
                ):
                    if c.uuid == d[1][1].uuid:
                        d[1][1] = c
                return DoubleAction(d)

    def use_next_potion(self):
        for potion in self.game.get_real_potions():
            if potion.can_use:
                if potion.requires_target:
                    return PotionAction(
                        True, potion=potion, target_monster=self.get_low_hp_target()
                    )
                else:
                    return PotionAction(True, potion=potion)

    def handle_screen(self):
        if self.game.screen_type == ScreenType.EVENT:
            if self.game.screen.event_id in [
                "Vampires",
                "Masked Bandits",
                "Knowing Skull",
                "Ghosts",
                "Liars Game",
                "Golden Idol",
                "Drug Dealer",
                "The Library",
            ]:
                return ChooseAction(len(self.game.screen.options) - 1)
            else:
                return ChooseAction(0)
        elif self.game.screen_type == ScreenType.CHEST:
            return OpenChestAction()
        elif self.game.screen_type == ScreenType.SHOP_ROOM:
            if not self.visited_shop:
                self.visited_shop = True
                return ChooseShopkeeperAction()
            else:
                self.visited_shop = False
                return ProceedAction()
        elif self.game.screen_type == ScreenType.REST:
            return self.choose_rest_option()
        elif self.game.screen_type == ScreenType.CARD_REWARD:
            return self.choose_card_reward()
        elif self.game.screen_type == ScreenType.COMBAT_REWARD:
            for reward_item in self.game.screen.rewards:
                if (
                    reward_item.reward_type == RewardType.POTION
                    and self.game.are_potions_full()
                ):
                    continue
                elif reward_item.reward_type == RewardType.CARD and self.skipped_cards:
                    continue
                else:
                    return CombatRewardAction(reward_item)
            self.skipped_cards = False
            return ProceedAction()
        elif self.game.screen_type == ScreenType.MAP:
            return self.make_map_choice()
        elif self.game.screen_type == ScreenType.BOSS_REWARD:
            relics = self.game.screen.relics
            best_boss_relic = self.priorities.get_best_boss_relic(relics)
            return BossRewardAction(best_boss_relic)
        elif self.game.screen_type == ScreenType.SHOP_SCREEN:
            if (
                self.game.screen.purge_available
                and self.game.gold >= self.game.screen.purge_cost
            ):
                return ChooseAction(name="purge")
            for card in self.game.screen.cards:
                if self.game.gold >= card.price and not self.priorities.should_skip(
                    card
                ):
                    return BuyCardAction(card)
            for relic in self.game.screen.relics:
                if self.game.gold >= relic.price:
                    return BuyRelicAction(relic)
            return CancelAction()
        elif self.game.screen_type == ScreenType.GRID:
            if not self.game.choice_available:
                return ProceedAction()
            if self.game.screen.for_upgrade or self.choose_good_card:
                available_cards = self.priorities.get_sorted_cards(
                    self.game.screen.cards
                )
            else:
                available_cards = self.priorities.get_sorted_cards(
                    self.game.screen.cards, reverse=True
                )
            num_cards = self.game.screen.num_cards
            return CardSelectAction(available_cards[:num_cards])
        elif self.game.screen_type == ScreenType.HAND_SELECT:
            if not self.game.choice_available:
                return ProceedAction()
            # Usually, we don't want to choose the whole hand for a hand select. 3 seems like a good compromise.
            num_cards = min(self.game.screen.num_cards, 3)
            return CardSelectAction(
                self.priorities.get_cards_for_action(
                    self.game.current_action, self.game.screen.cards, num_cards
                )
            )
        else:
            return ProceedAction()

    def choose_rest_option(self):
        rest_options = self.game.screen.rest_options
        if len(rest_options) > 0 and not self.game.screen.has_rested:
            if (
                RestOption.REST in rest_options
                and self.game.current_hp < self.game.max_hp / 2
            ):
                return RestAction(RestOption.REST)
            elif (
                RestOption.REST in rest_options
                and self.game.act != 1
                and self.game.floor % 17 == 15
                and self.game.current_hp < self.game.max_hp * 0.9
            ):
                return RestAction(RestOption.REST)
            elif RestOption.SMITH in rest_options:
                return RestAction(RestOption.SMITH)
            elif RestOption.LIFT in rest_options:
                return RestAction(RestOption.LIFT)
            elif RestOption.DIG in rest_options:
                return RestAction(RestOption.DIG)
            elif (
                RestOption.REST in rest_options
                and self.game.current_hp < self.game.max_hp
            ):
                return RestAction(RestOption.REST)
            else:
                return ChooseAction(0)
        else:
            return ProceedAction()

    def count_copies_in_deck(self, card):
        count = 0
        for deck_card in self.game.deck:
            if deck_card.card_id == card.card_id:
                count += 1
        return count

    def choose_card_reward(self):
        reward_cards = self.game.screen.cards
        if self.game.screen.can_skip and not self.game.in_combat:
            pickable_cards = [
                card
                for card in reward_cards
                if self.priorities.needs_more_copies(
                    card, self.count_copies_in_deck(card)
                )
            ]
        else:
            pickable_cards = reward_cards
        if len(pickable_cards) > 0:
            potential_pick = self.priorities.get_best_card(pickable_cards)
            return CardRewardAction(potential_pick)
        elif self.game.screen.can_bowl:
            return CardRewardAction(bowl=True)
        else:
            self.skipped_cards = True
            return CancelAction()

    def generate_map_route(self):
        node_rewards = self.priorities.MAP_NODE_PRIORITIES.get(self.game.act)
        best_rewards = {
            0: {
                node.x: node_rewards[node.symbol]
                for node in self.game.map.nodes[0].values()
            }
        }
        best_parents = {0: {node.x: 0 for node in self.game.map.nodes[0].values()}}
        min_reward = min(node_rewards.values())
        map_height = max(self.game.map.nodes.keys())
        for y in range(0, map_height):
            best_rewards[y + 1] = {
                node.x: min_reward * 20 for node in self.game.map.nodes[y + 1].values()
            }
            best_parents[y + 1] = {
                node.x: -1 for node in self.game.map.nodes[y + 1].values()
            }
            for x in best_rewards[y]:
                node = self.game.map.get_node(x, y)
                best_node_reward = best_rewards[y][x]
                for child in node.children:
                    test_child_reward = best_node_reward + node_rewards[child.symbol]
                    if test_child_reward > best_rewards[y + 1][child.x]:
                        best_rewards[y + 1][child.x] = test_child_reward
                        best_parents[y + 1][child.x] = node.x
        best_path = [0] * (map_height + 1)
        best_path[map_height] = max(
            best_rewards[map_height].keys(), key=lambda x: best_rewards[map_height][x]
        )
        for y in range(map_height, 0, -1):
            best_path[y - 1] = best_parents[y][best_path[y]]
        self.map_route = best_path

    def make_map_choice(self):
        if (
            len(self.game.screen.next_nodes) > 0
            and self.game.screen.next_nodes[0].y == 0
        ):
            self.generate_map_route()
            self.game.screen.current_node.y = -1
        if self.game.screen.boss_available:
            return ChooseMapBossAction()
        chosen_x = self.map_route[self.game.screen.current_node.y + 1]
        for choice in self.game.screen.next_nodes:
            if choice.x == chosen_x:
                return ChooseMapNodeAction(choice)
        # This should never happen
        return ChooseAction(0)
