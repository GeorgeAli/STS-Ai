import itertools
import copy
from card_dictionary import get_card_values, ironclad_archetypes, ironclad_relic_values
from spirecomm.spire.card import Card, CardType
from spirecomm.spire.game import Game
from spirecomm.spire.character import PlayerClass
from spirecomm.spire.screen import RestOption
from spirecomm.communication.action import *
from spirecomm.ai.priorities import IroncladPriority
import logging
import time


logging.basicConfig(filename="best_simulated_states.log", level=logging.INFO)


class GameStateCache:
    """This is the cache that is used for the already explored combinations in the expectimax algorithm"""

    def __init__(self):
        self.cache = {}

    def get_state(self, key):
        """Retrieve both the cached state and the target for the first card, if applicable."""
        state, target, eval = self.cache.get(key, (None, None, None))
        return copy.deepcopy(state), target, eval

    def store_state(self, key, state, target, eval):
        """Store both the state and the target for the first card in the cache."""
        if state is not None:
            self.cache[key] = (copy.deepcopy(state), target, eval)
        else:
            logging.warning(f"Attempted to store None state for key {key}")


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
        self.decision = []
        self.grade = None
        self.played_cards = []
        self.played_a_potion = False


class SimpleAgent:
    def __init__(self, chosen_class=PlayerClass.IRONCLAD):
        self.game = Game()
        self.errors = 0
        self.choose_good_card = False
        self.skipped_cards = False
        self.visited_shop = False
        self.chosen_class = chosen_class
        self.priorities = IroncladPriority()
        self.change_class(chosen_class)
        self.initial_depth = 10
        self.feed_effect_used = False
        self.map_route = []
        self.player_current_hp = 80
        self.player_max_hp = 80

    def change_class(self, new_class):
        """This can theoritically be used to cycle between classes, only ironclad works.."""
        self.chosen_class = PlayerClass.IRONCLAD
        self.priorities = IroncladPriority()

    def handle_error(self, error):
        """A function that handles all errors that might appear"""
        error_message = f"An unexpected error occurred: {str(error)}"
        card_info = f"Card: {getattr(error, 'card', None)}"
        if isinstance(card_info, dict):
            card_name = card_info.get("name", "Unknown")
            card_id = card_info.get("card_id", "Unknown")
            card_info = f"Card: {card_name} (ID: {card_id})"
        else:
            card_info = "Card: Unknown"
        error_message += f" {card_info}"

        target_info = f"Target: {getattr(error, 'target', 'Unknown')}"
        error_message += f" {target_info}"

        logging.info(error_message)
        raise Exception(error_message)

    def get_next_action_in_game(self, game_state):
        """This gets called from the coordinator and is used for everything in the game"""

        logging.info(f"FLOOR: {self.game.floor} ")
        self.game = game_state

        # HP values are set for the map generation
        if game_state.player is not None:
            self.player_current_hp = game_state.player.current_hp
            self.player_max_hp = game_state.player.max_hp

        if self.game.choice_available:
            return self.handle_screen()
        if self.game.proceed_available:
            return ProceedAction()
        if self.game.play_available:
            self.played_a_potion = False
            potions_count = len(self.game.get_real_potions())

            for relic in self.game.relics:
                if (
                    (
                        relic.name == "White Beast Statue"
                        or (potions_count == 3 and relic.name != "Potion Belt")
                        or potions_count == 5
                    )
                    and potions_count > 0
                    and self.played_a_potion == False
                ):
                    potion_action = self.use_next_potion()
                    if potion_action is not None:
                        self.played_a_potion = True
                        return potion_action

            if self.game.room_type == "MonsterRoomBoss":
                potion_action = self.use_next_potion()
                if potion_action is not None:
                    return potion_action

            ((card, target), best_game_state, best_eval) = self.get_play_card_action()

            # We died, maybe try to play some potions
            if best_eval == -1000000:
                if potions_count > 0:
                    potion_action = self.use_next_potion()
                    if potion_action is not None:
                        return potion_action
            else:
                if best_game_state is not None and best_game_state.player.energy == 0:
                    potion_action = self.play_all_static_potions(best_game_state)
                    if potion_action is not None:
                        return potion_action

            if not card:
                return EndTurnAction()

            # Log the action state
            # self.log_simulated_state(best_game_state, target)

            return PlayCardAction(card=card, target_monster=target)
        if self.game.end_available:
            return EndTurnAction()
        if self.game.cancel_available:
            return CancelAction()

    def get_next_action_out_of_game(self):
        """Starts a new game"""
        return StartGameAction(self.chosen_class)

    def get_incoming_damage(self, game_state):
        """Calculates the damage the agent is receiving this turn. Also accounts for every possible thing that might add or reduce damage"""

        has_intangible = False
        has_torii = False
        has_trod = False
        incoming_damage = 0
        incoming_damage -= game_state.player.block

        for relic in game_state.relics:
            if relic.name == "Orichalcum" and game_state.player.block == 0:
                incoming_damage -= 6
            if relic.name == "Torii":
                has_torii = True
            if relic.name == "Tungsten Rod":
                has_trod = True

        for power in game_state.player.powers:
            if power.power_id in ["Plated Armor", "Metallicize"]:
                incoming_damage -= power.amount
            if power.power_id == "Intangible":
                has_intangible = True
            if power.power_id == "Constricted":
                if has_intangible:
                    if not has_trod:
                        incoming_damage += 1
                else:
                    incoming_damage += power.amount

        for monster in game_state.monsters:
            if monster.current_hp > 0 and not monster.is_gone:
                if (
                    monster.move_adjusted_damage is not None
                    and monster.move_adjusted_damage > 0
                ):
                    if has_intangible:
                        if not has_trod:
                            incoming_damage += 1 * monster.move_hits
                    else:
                        if monster.move_adjusted_damage <= 5 and has_torii:
                            monster.move_adjusted_damage = 1
                        if has_trod:
                            monster.move_adjusted_damage -= 1

                        incoming_damage += (
                            monster.move_adjusted_damage * monster.move_hits
                        )

        for card in game_state.hand:
            if card.name == "Burn":
                burn_damage = 2
                if has_intangible or has_torii:
                    burn_damage = 1
                if has_trod:
                    burn_damage -= 1
                incoming_damage += burn_damage
            if card.name == "Burn+":
                burn_damage = 4
                if has_intangible or has_torii:
                    burn_damage = 1
                if has_trod:
                    burn_damage -= 1
                incoming_damage += burn_damage
            if card.name == "Decay":
                decay_damage = 2
                if has_intangible or has_torii:
                    decay_damage = 1
                if has_trod:
                    decay_damage -= 1
                incoming_damage += decay_damage

        if game_state.instances_of_damage > 0:
            if has_intangible:
                if not has_trod:
                    incoming_damage += 1 * game_state.instances_of_damage
            else:
                incoming_damage += 3 * game_state.instances_of_damage
        return incoming_damage

    def get_best_target(self, game_state):
        """Finds the best target out of all the enemies in the field"""
        # Filter out all alive monsters
        alive_monsters = [
            monster
            for monster in game_state.monsters
            if monster.current_hp > 0 and monster.is_gone == False
        ]

        # Check for a special targets
        wizard_target = next(
            (monster for monster in alive_monsters if monster.name == "Gremlin Wizard"),
            None,
        )

        sentry_target = next(
            (monster for monster in alive_monsters if monster.name == "Sentry"),
            None,
        )

        torch_head_target = next(
            (monster for monster in alive_monsters if monster.name == "Torch Head"),
            None,
        )

        donu_target = next(
            (monster for monster in alive_monsters if monster.name == "Donu"),
            None,
        )

        centurion_target = next(
            (monster for monster in alive_monsters if monster.name == "Centurion"),
            None,
        )

        if sentry_target or alive_monsters.count == 1 or centurion_target:
            return alive_monsters[0]

        if torch_head_target:
            if len(alive_monsters) == 1 or len(alive_monsters) == 3:
                return alive_monsters[0]
            return alive_monsters[1]

        if wizard_target:
            return wizard_target

        if donu_target:
            return donu_target

        # Filter to find monsters that are actively attacking
        attacking_monsters = [
            monster for monster in alive_monsters if monster.move_adjusted_damage > 0
        ]

        # Attack the monster with the lowest HP among those that are attacking
        if attacking_monsters:
            return min(attacking_monsters, key=lambda m: m.current_hp + m.block)

        if alive_monsters:
            return min(alive_monsters, key=lambda m: m.current_hp + m.block)

        return None

    def get_all_targets(self, game_state):
        """Experimental method to return all targets in case i want to migrate to a solution where the agent simulates all states against all enemies (Very computationally expensive)"""
        # Filter out all alive monsters
        alive_monsters = [
            monster
            for monster in game_state.monsters
            if monster.current_hp > 0 and monster.is_gone == False
        ]

        # Check for a special targets
        wizard_target = next(
            (monster for monster in alive_monsters if monster.name == "Gremlin Wizard"),
            None,
        )

        sentry_target = next(
            (monster for monster in alive_monsters if monster.name == "Sentry"),
            None,
        )

        torch_head_target = next(
            (monster for monster in alive_monsters if monster.name == "Torch Head"),
            None,
        )

        donu_target = next(
            (monster for monster in alive_monsters if monster.name == "Donu"),
            None,
        )

        centurion_target = next(
            (monster for monster in alive_monsters if monster.name == "Centurion"),
            None,
        )

        if sentry_target or alive_monsters.count == 1 or centurion_target:
            return [alive_monsters[0]]

        if torch_head_target:
            if len(alive_monsters) == 1:
                return alive_monsters[0]
            return [alive_monsters[1]]

        if wizard_target:
            return [wizard_target]

        if donu_target:
            return [donu_target]

        return alive_monsters

    def init_playable_cards(self, game_state):
        """Narrows down the possible actions by removing cards from hand. The result from this is used to simulate all states"""

        def is_pure_block_card(card):
            card_values = get_card_values(card.name)
            if not ("block" in card_values and "damage" in card_values):
                return False
            return (
                card_values["block"] > 0
                and card.type.name == "SKILL"
                and card.card_id
                not in ["Armaments", "Flame Barrier", "Sentinel", "True Grit"]
                and not "draw" in card_values
                and card_values["damage"] == 0
            )

        playable_cards = []

        incoming_damage = self.get_incoming_damage(game_state)

        # First, get all playable cards once
        all_playable_cards = [card for card in game_state.hand if card.is_playable]

        # Prepare to adjust playable cards based on monster powers
        for monster in game_state.monsters:
            if (
                monster.monster_id == "GremlinNob"
                and game_state.turn > 1
                and game_state.player.current_hp
                + game_state.player.block
                - incoming_damage
                > 0
            ):
                playable_cards = [
                    card for card in all_playable_cards if card.type.name != "SKILL"
                ]
                return playable_cards

        playable_cards = all_playable_cards

        for power in game_state.player.powers:
            if power.power_id not in ["Barricade", "Juggernaut"]:
                if incoming_damage <= 0:
                    playable_cards = [
                        card
                        for card in all_playable_cards
                        if not is_pure_block_card(card)
                    ]

        # Ensure priority cards are played first if available
        for card in playable_cards:
            if card.card_id == "Limit Break":
                current_strength = next(
                    (
                        buff.amount
                        for buff in game_state.player.powers
                        if buff.power_id == "Strength"
                    ),
                    0,
                )
                if current_strength <= 0:
                    playable_cards.remove(card)
            if card.card_id == "Exhume":
                if len(game_state.exhaust_pile) <= 0:
                    playable_cards.remove(card)
            if card.card_id == "Bloodletting":

                card_values = get_card_values(card.name)
                energy_given = card_values["gain_energy"]

                temp_game_state = copy.deepcopy(game_state)
                temp_playable_cards = copy.deepcopy(playable_cards)

                temp_playable_cards.remove(card)
                temp_game_state.player.energy += energy_given

                for temp_card in temp_playable_cards:
                    for power in temp_game_state.player.powers:
                        if (
                            power.power_name == "Corruption"
                            and temp_card.type.name == "SKILL"
                        ):
                            temp_card.exhausts = True
                            temp_card.cost = 0
                    if temp_card.cost == -1:
                        temp_card.cost = temp_game_state.player.energy
                    if temp_card.cost == -2:
                        temp_card.cost = 0
                    temp_game_state.player.energy -= temp_card.cost
                    if temp_game_state.player.energy < 0:
                        temp_game_state.player.energy += temp_card.cost
                        continue
                    temp_playable_cards.remove(temp_card)
                if (
                    temp_game_state.player.energy > energy_given
                    or len(temp_playable_cards) == 0
                ):
                    playable_cards.remove(card)
        return playable_cards

    def expectimax(self):
        """This is where everything happens, the return of the algorithm is the action the agent is going to take.
        There is a notable computational expense here. This function calculates the best possible combination of cards up to the available energy but only returns the first card.
        This is done because the game is so unpredictable with card combinations, relics, draws, powers, enemy abilites, the randomness of the game that cant be replicated without cheating and so much more,
        that the best action is to simulate the best combo, find it and return its first card. 9/10 the resulting 2-3 itterations will return the exact same combo but i found out that it is worth the effort.
        """

        def get_partial_combination_key(partial_combo):
            return tuple((card.card_id, card.cost) for card in partial_combo)

        best_action = (None, None)
        best_game_state = None
        duplication_power = False

        # We init the cache
        cache = GameStateCache()

        # Copying the gamestate is important because we are going to perform a lot of simulations that will alter the original gamestate if not copied
        starting_state = copy.deepcopy(self.game)

        # This is a safety messure, all it does it check if the resulting eval is better than the eval we started with. If not do nothing
        starting_state.player.current_hp -= max(
            0, self.get_incoming_damage(starting_state)
        )
        max_eval = self.evaluate_state(starting_state)

        # These are all our cards
        playable_cards = self.init_playable_cards(self.game)

        available_energy = self.game.player.energy

        # This run for ALL possible compinations
        for r in range(1, len(playable_cards) + 1):
            for combo in itertools.permutations(playable_cards, r):
                total_cost = 0
                first_card_target = None
                is_first_card = True

                # Calculate the cost of the combo and skip if it exceeds energy
                for card in combo:
                    for power in self.game.player.powers:
                        if (
                            power.power_name == "Corruption"
                            and card.type.name == "SKILL"
                        ):
                            card.exhausts = True
                            card.cost = 0
                        if power.power_id == "DuplicationPower":
                            duplication_power = True
                    if card.cost == -1:
                        card.cost = available_energy
                    if card.cost == -2:
                        card.cost = 0
                    total_cost += card.cost

                if total_cost > available_energy:
                    continue

                # Again we copy the original game_state
                current_state = copy.deepcopy(self.game)

                # This is the position the loop is going to simulate if it finds a combo that is partially cached. For example:
                # Lets assume we have this combo of 3 cards:
                # [Strike, Strike, Defend]
                # If we have alreay played and cached the combo [Strike, Strike], the cache is going to return its game_state, its eval and the target of the first card.
                # Then we will simulate on top of that the play of Defend and return the eval.
                # !!!NOTE!!!
                # The combinations [Strike,Strike,Defend] and [Strike,Defend,Strike] are not and should not be treated as the same.
                skip_to_position = 0

                for i, card in enumerate(combo):
                    partial_combo_key = get_partial_combination_key(combo[: i + 1])

                    cached_state, cached_target, cached_eval = cache.get_state(
                        partial_combo_key
                    )
                    if cached_state:
                        current_state = cached_state
                        eval = cached_eval
                        if is_first_card and i == 0:
                            first_card_target = cached_target
                            is_first_card = False
                        skip_to_position = i + 1
                    else:
                        break

                # Start simulating from the first uncached position in the combo
                for i in range(skip_to_position, len(combo)):
                    card = combo[i]
                    target = None

                    # If card requires target, evaluate with all targets
                    if card.has_target or card.card_id in ["Sword Boomerang"]:

                        # Find the best target
                        target = self.get_best_target(current_state)

                        # We have to store the first card's target here as well
                        if is_first_card:
                            first_card_target = target
                            is_first_card = False

                    # Simulate the game_state
                    current_state = self.simulate_card_play(current_state, card, target)

                    # This is a power that lets us play the same card twice
                    if duplication_power:
                        current_state = self.simulate_card_play(
                            current_state, card, target
                        )
                        duplication_power = False

                    # Evaluate the simulated_state
                    eval = self.evaluate_state(current_state)

                    # Store the new state and target in the cache
                    partial_combo_key = get_partial_combination_key(combo[: i + 1])
                    cache.store_state(
                        partial_combo_key,
                        current_state,
                        target,
                        eval,
                    )

                # Update best action if this evaluation is higher
                if eval >= max_eval:
                    max_eval = eval
                    best_action = (combo[0], first_card_target)
                    best_game_state = copy.deepcopy(self.game)
                    best_game_state = self.simulate_card_play(
                        best_game_state, combo[0], first_card_target
                    )

        return max_eval, best_action, best_game_state

    def get_play_card_action(self):
        """ Calls expectimax and returns EndTurn if no better action was found or if an error occured"""

        best_eval, best_action, best_game_state = self.expectimax()

        if best_action:
            return (
                best_action,
                best_game_state,
                best_eval,
            )  # Return the best card action to perform
        else:
            return EndTurnAction()

    def simulate_card_play(self, simulated_state, card, target=None):
        """Attempts a modest simulation of the game_state when playing a card. Optimizing the agent to make better decisions means making the simulation as accurate as possible.
        This is so complicated that there are bound to be unfound bugs possibly bypassed because of the single card play 
        """

        def apply_exhaust_effects(game_state, card):
            """Applies effects of powers when exhausting a card
            Relics are random and cant be possibly predicted without cheating and drawing from the draw pile is also random so keep that in mind
            """
            card_values = get_card_values(card.name)
            for power in game_state.player.powers:
                if power.power_name == "Dark Embrace":
                    game_state.player.draw(power.amount)
                if power.power_name == "Feel No Pain":
                    game_state.player.block += power.amount
            if "gain_energy_on_exhaust" in card_values:
                game_state.player.energy += card_values["gain_energy_on_exhaust"]
            game_state.exhaust_pile.append(card)

        def deal_damage(card, game_state, target):
            """Deals damage to a target, accounts for everything unless i have forgotten them or not seen them in my tests"""
            card_values = get_card_values(card.name)

            if card_values.get("damage", 0) <= 0 or target is None:
                return 0

            damage = card_values["damage"]

            current_strength = next(
                (
                    buff.amount
                    for buff in game_state.player.powers
                    if buff.power_id == "Strength"
                ),
                0,
            )

            # Adjust damage based on strength and weakened status
            damage += current_strength

            if "strength_multiplier" in card_values:
                damage += max(1, current_strength) * card_values["strength_multiplier"]

            # Check for Paper Frog relic, which increases the vulnerability effect to 75%
            for relic in game_state.relics:
                if relic.relic_id == "Akabeko" and game_state.turn == 0:
                    damage += 8
                if relic.relic_id == "Pen Nib" and relic.counter == 10:
                    damage *= 2
                if target.has_debuff("Vulnerable"):
                    if relic.relic_id == "Paper Phrog":
                        damage = int(damage * 1.75)
                    else:
                        damage = int(damage * 1.50)

            if game_state.player.has_debuff("Weakened") == True:
                damage = int(damage * 0.75)  # Reduce damage by 25% if weakened

            game_state.damage_dealt += damage
            for power in target.powers:
                if power.power_id in ["Sharp Hide", "Thorns"]:
                    game_state.instances_of_damage += 1

            target.block -= damage

            if target.block <= 0:
                damage = abs(target.block)
                target.block = 0
            else:
                return 0

            target.current_hp -= damage

            if target.current_hp <= 0:
                damage += target.current_hp
                if target.monster_id == "FungiBeast":
                    game_state.player.add_buff("Vulnerable", target.powers[0].amount)
            return damage

        def handle_enemy_powers(monster, card, damage, simulated_state):
            """How the each enemy will interact with the play of a card.
            Most enemies have a unique effect and a way to beat them so we mustaaccount for that and base our strategies around it
            """
            card_effects = get_card_values(card.name)

            for power in monster.powers:
                if power.power_id == "Curl Up" and damage > 0:
                    monster.block += power.amount
                    monster.powers = [
                        p for p in monster.powers if p.power_id != "Curl Up"
                    ]
                if power.power_id == "Anger" and card.type.name == "SKILL":
                    monster.add_buff("Strength", power.amount)
                if power.power_id == "Angry" and damage > 0:
                    monster.add_buff("Strength", power.amount)
                if power.power_id == "Artifact":
                    debuffs = ["Vulnerable", "Weakened"]  # List of debuffs
                    for debuff in debuffs:
                        if monster.has_debuff(debuff) and debuff in card_effects:
                            if power.amount > 0:
                                monster.remove_buff(debuff, card_effects[debuff])
                if power.power_id == "Malleable":
                    monster.block += power.amount
                    power.amount += (
                        1  # Malleable increases the amount of block each time
                    )
                if power.power_id == "Buffer" and damage > 0:
                    monster.powers = [
                        p for p in monster.powers if p.power_id != "Buffer"
                    ]
                    damage = 0
                if power.power_id == "Invincible":
                    if damage > monster.max_hp * 0.15:
                        damage = monster.max_hp * 0.15  # Cap damage to 15% of max HP
                if power.power_id == "Mode Shift":
                    monster.current_hp = power.amount
                if power.power_id == "Plated Armor" and damage > 0:
                    if monster.block <= 0:
                        power.amount -= (
                            1  # Reduce Plated Armor by 1 for each unblocked attack
                        )
                        if power.amount <= 0:
                            monster.powers = [
                                p
                                for p in monster.powers
                                if p.power_id != "Plated Armor"
                            ]
                if power.power_id == "Flight":
                    if power.amount <= 0:
                        monster.move_adjusted_damage = 0
                    else:
                        damage /= 2
                if power.power_id == "Split":
                    monster.current_hp = monster.current_hp - int(monster.max_hp / 2)

            return monster, simulated_state, damage

        try:
            damage = 0
            block = 0
            current_dexterity = 0
            no_extra_damage = False
            simulated_state_target = None
            has_torii = False
            has_trod = False
            has_intagible = False
            is_frail = False

            if target is not None:
                for each_monster in simulated_state.monsters:
                    if each_monster == target:
                        simulated_state_target = each_monster
                        break

            if card in simulated_state.hand:
                if card.cost > simulated_state.player.energy:
                    return simulated_state
                simulated_state.hand.remove(card)
                simulated_state.played_cards.append(card)
            else:
                return simulated_state

            card_values = get_card_values(card.name)

            # Find player's dexterity and Frail status
            for buff in simulated_state.player.powers:
                if buff.power_id == "Dexterity":
                    current_dexterity = buff.amount
                if buff.power_id == "Frail":
                    is_frail = True
                if buff.power_id == "Intangible":
                    has_intagible = True

            for relic in simulated_state.relics:
                if relic.name == "Torii":
                    has_torii = True
                if relic.name == "Tungsten Rod":
                    has_trod = True

            if "block" in card_values:
                block = card_values["block"]

                # Adjust block based on dexterity and frail status
                if block != 0:
                    block += current_dexterity
                    if is_frail:
                        block = int(block * 0.75)  # Frail reduces block by 25%
                    simulated_state.player.block += block

            # Other effects (vulnerable, weak, strength, etc.)
            if "self_vulnerable" in card_values:
                simulated_state.player.add_buff(
                    "Vulnerable", card_values["self_vulnerable"]
                )
                simulated_state.player.add_buff("Berserk", card_values["gain_energy"])
            if "weak" in card_values and simulated_state_target is not None:
                simulated_state_target.add_buff("Weakened", card_values["weak"])
            if "strength" in card_values:
                simulated_state.player.add_buff("Strength", card_values["strength"])
            if "draw" in card_values:
                simulated_state.player.draw(card_values["draw"])
                simulated_state.cards_drawn_this_turn += 1
            if "draw_on_status" in card_values:
                simulated_state.player.add_buff("Evolve", card_values["draw_on_status"])
            if "gain_energy" in card_values:
                simulated_state.player.gain_energy(card_values["gain_energy"])
            if "lose_hp" in card_values:
                lose_hp = card_values["lose_hp"]
                if has_intagible:
                    lose_hp = 1
                if has_torii and lose_hp <= 5:
                    lose_hp = 1
                if has_trod:
                    lose_hp -= 1
                simulated_state.player.current_hp -= lose_hp
            if "exhaust" in card_values:
                apply_exhaust_effects(simulated_state, card)
            if "aoe" in card_values:
                for aoe_monster in simulated_state.monsters:
                    no_extra_damage = True
                    if aoe_monster.current_hp > 0 and not aoe_monster.is_gone:
                        damage = deal_damage(card, simulated_state, aoe_monster)
                        if "heal_on_damage" in card_values:
                            simulated_state.player.current_hp = max(
                                damage + simulated_state.player.current_hp,
                                simulated_state.player.max_hp,
                            )
            if "exhaust_non_attack" in card_values:
                block = 0
                for each_card in simulated_state.hand:
                    if each_card.type.name != "ATTACK" and each_card.uuid != card.uuid:
                        block += card_values["block_per_exhaust"] + current_dexterity
                        if is_frail:
                            block = int(block * 0.75)  # Frail reduces block by 25%
                        simulated_state.player.block += block
                        apply_exhaust_effects(simulated_state, each_card)
            if "based_on_block" in card_values:
                card_values["damage"] = simulated_state.player.block
                damage = deal_damage(card, simulated_state, aoe_monster)
                no_extra_damage = True
            if "play_top_card" in card_values:
                if simulated_state.draw_pile:
                    top_card = simulated_state.draw_pile.pop()
                    simulated_state = self.simulate_card_play(
                        simulated_state, top_card, simulated_state_target
                    )
            if "create_copy" in card_values:
                simulated_state.hand.append(copy.deepcopy(card))
            if "gain_block_on_exhaust" in card_values:
                simulated_state.player.add_buff(
                    "Feel No Pain", card_values["gain_block_on_exhaust"]
                )
            if "gain_strength_on_hp_loss" in card_values:
                simulated_state.player.add_buff(
                    "Rupture",
                    card_values["gain_strength_on_hp_loss_from_playing_cards"],
                )
            if "exhaust_hand" in card_values:
                simulated_state.exhaust_pile.extend(simulated_state.hand)
                if "multiple_hits" in card_values:
                    card_values["multiple_hits"] = len(simulated_state.hand) - 1
                for each_card in simulated_state.hand:
                    if card.uuid != each_card.uuid:
                        apply_exhaust_effects(simulated_state, each_card)
                simulated_state.hand.clear()
            if "multiple_hits" in card_values and simulated_state_target is not None:
                hits = card_values["multiple_hits"]
                no_extra_damage = True
                for _ in range(hits):
                    if (
                        simulated_state_target.current_hp > 0
                        and not simulated_state_target.is_gone
                    ):
                        damage = deal_damage(
                            card, simulated_state, simulated_state_target
                        )
            if "block_on_attack" in card_values:
                block = card_values["block_on_attack"]
                simulated_state.player.block += block
            if "double_strength" in card_values:
                for buff in simulated_state.player.powers:
                    if buff.power_name == "Strength":
                        buff.amount *= 2
            if "damage_on_block" in card_values:
                simulated_state.player.add_buff(
                    "Juggernaut", card_values["damage_on_block"]
                )
            if "damage_on_attack" in card_values and simulated_state_target is not None:
                simulated_state.player.add_buff(
                    "Flame Barrier", card_values["damage_on_attack"]
                )
            if "double_block" in card_values:
                simulated_state.player.block *= 2
            if "draw_on_exhaust" in card_values:
                simulated_state.player.add_buff(
                    "Dark Embrace", card_values["draw_on_exhaust"]
                )
            if "give_power_per_turn" in card_values:
                simulated_state.player.add_buff(
                    "Demon Form", card_values["give_power_per_turn"]
                )
            if "block_never_expires" in card_values:
                simulated_state.player.add_buff(
                    "Barricade", card_values["block_never_expires"]
                )
            if "lose_hp_per_turn" in card_values:
                simulated_state.player.add_buff(
                    "Brutality", card_values["lose_hp_per_turn"]
                )
            if "skills_cost_zero" in card_values:
                simulated_state.player.add_buff(
                    "Corruption", card_values["skills_cost_zero"]
                )
            if "reduce_strength" in card_values and simulated_state_target is not None:
                simulated_state_target.add_buff(
                    "Strength", -card_values["reduce_strength"]
                )
            if "burns_to_draw" in card_values:
                burn_card = Card(
                    card_id="Burn",
                    name="Burn",
                    card_type=CardType(4),
                    rarity="COMMON",
                    cost=-1,
                    is_playable=False,
                )
                simulated_state.draw_pile.append(burn_card)
            if "add_wounds_to_hand" in card_values:
                wound_card = Card(
                    card_id="Wound",
                    name="Wound",
                    card_type=CardType(4),
                    rarity="COMMON",
                    cost=-2,
                    is_playable=False,
                )
                simulated_state.hand.append(wound_card)
                simulated_state.hand.append(wound_card)
            if "sword_boomerang_handle" in card_values:
                for i in range(card_values["hits"]):
                    damage = deal_damage(card, simulated_state, simulated_state_target)
                no_extra_damage = True
            if "weak_aoe" in card_values:
                for monster in simulated_state.monsters:
                    monster.add_buff("Weakened", card_values["weak_aoe"])
            if "vulnerable_aoe" in card_values:
                for monster in simulated_state.monsters:
                    monster.add_buff("Vulnerable", card_values["vulnerable_aoe"])
            if "whirlwind_handle" in card_values:
                while simulated_state.player.energy > 0:
                    simulated_state.player.energy -= 1
                    for aoe_monster in simulated_state.monsters:
                        if aoe_monster.current_hp > 0 and aoe_monster.is_gone == False:
                            damage = deal_damage(card, simulated_state, aoe_monster)
                no_extra_damage = True
            if (
                "gain_max_hp_on_kill" in card_values
                and simulated_state_target is not None
            ):
                feed_heal = card_values["gain_max_hp_on_kill"]
                no_extra_damage = True
                damage = deal_damage(card, simulated_state, simulated_state_target)

                # Check if Feed will kill the target
                if simulated_state_target.current_hp <= 0:
                    # Simulate the kill and the HP gain
                    simulated_state.player.max_hp += feed_heal
                    simulated_state.player.current_hp += feed_heal
                    self.feed_effect_used = True
                else:
                    self.feed_effect_used = False

            for power in simulated_state.player.powers:
                if power.power_name == "Juggernaut" and block > 0:
                    # This is wrong it needs to be random but we cant simulate the game's randomness
                    for each_monster in simulated_state.monsters:
                        each_monster.current_hp = (
                            each_monster.current_hp + each_monster.block - power.amount
                        )
                        break
                if power.power_name == "Evolve":
                    for each_card in simulated_state.hand:
                        if each_card.type.name == "STATUS":
                            simulated_state.player.draw(power.amount)
                if power.power_name == "Flame Barrier":
                    for attacking_monsters in simulated_state.monsters:
                        if attacking_monsters.move_adjusted_damage > 0:
                            damage += power.amount
                            attacking_monsters.block -= power.amount

                            if attacking_monsters.block < 0:
                                attacking_monsters.block = 0
                            else:
                                attacking_monsters.current_hp -= power.amount
                    no_extra_damage = True
                    simulated_state.damage_dealt += damage
                if power.power_name == "Rupture":
                    for temp_power in simulated_state.player.powers:
                        if temp_power.power_name == "Brutality":
                            simulated_state.player.add_buff("Strength", power.amount)
                    if "lose_hp" in card_values:
                        simulated_state.player.add_buff("Strength", power.amount)
                if power.power_name == "Brutality":
                    if not has_trod:
                        simulated_state.player.current_hp -= 1

            if simulated_state_target is not None:
                simulated_state_target, simulated_state, damage = handle_enemy_powers(
                    simulated_state_target, card, damage, simulated_state
                )

            if (
                no_extra_damage == False
                and simulated_state_target is not None
                and simulated_state_target.current_hp > 0
                and not simulated_state_target.is_gone
            ):
                # Calc damage to deal to target
                damage = deal_damage(card, simulated_state, simulated_state_target)

            simulated_state.player.energy -= max(0, card.cost)

            # vulnerable from cards like bash, Thunderclap and Uppercut gets added after the attack, not before
            if "vulnerable" in card_values and simulated_state_target is not None:
                simulated_state_target.add_buff("Vulnerable", card_values["vulnerable"])

            return simulated_state
        except Exception as e:
            logging.info(f"Error simulating card play: {e}")
            raise

    def evaluate_state(self, game_state):
        """Evaluation function of our agent, takes as input a gamestate and returns an integer that represents how good or bad the gamestate is"""

        eval = 0
        all_monsters_dead = True
        killed_special_monster = False
        total_monster_hp = 0

        eval += game_state.cards_drawn_this_turn * 10

        # Player Positive buffs
        strength = next(
            (
                buff.amount
                for buff in game_state.player.powers
                if buff.power_id == "Strength"
            ),
            0,
        )
        dexterity = next(
            (
                buff.amount
                for buff in game_state.player.powers
                if buff.power_id == "Dexterity"
            ),
            0,
        )
        vulnerable = next(
            (
                debuff.amount
                for debuff in game_state.player.powers
                if debuff.power_id == "Vulnerable"
            ),
            0,
        )

        eval += strength * 700
        eval += dexterity * 200
        eval -= vulnerable * 75

        for monster in game_state.monsters:
            if monster.current_hp <= 0 or monster.is_gone == True:
                eval += 1000  # Reward for killing an enemy
                if monster.name in ["Reptomancer", "The Collector", "Gremlin Leader"]:
                    killed_special_monster = True
            else:

                total_monster_hp += monster.current_hp

                # Monster buffs
                for debuff in monster.powers:
                    if debuff.power_id == "Vulnerable":
                        eval += 100 * debuff.amount
                    if debuff.power_id == "Weakened":
                        eval += 100 * debuff.amount
                    if debuff.power_id == "Strength":
                        eval -= 100 * debuff.amount

                all_monsters_dead = False

        eval += game_state.damage_dealt * 9

        eval -= total_monster_hp

        incoming_damage = self.get_incoming_damage(game_state)

        # Winning the fight
        if all_monsters_dead == True or killed_special_monster:
            eval += 30000
        else:
            game_state.player.current_hp -= max(0, incoming_damage)

            if game_state.player.current_hp <= 0:
                return -1000000  # Strongly penalize if the player is dead

            eval += game_state.player.current_hp * 12

        if incoming_damage > 0:
            eval -= incoming_damage * 20
        elif incoming_damage < -10:
            eval -= (abs(incoming_damage) - 10) * 3

        # Reward for exhausting Curses but penalize exhausting good cards
        for card in game_state.exhaust_pile:
            if card.type.name in ["STATUS", "CURSE"]:
                eval += 20
            else:
                if card.card_id not in ["Defend_R", "Attack_R"]:
                    eval -= 5
                if card.card_id == "Feed" and not self.feed_effect_used:
                    eval -= 6000
                elif card.card_id == "Feed" and self.feed_effect_used:
                    eval += 10000

        # Penalty for status and curse cards in hand, discard pile, and draw pile
        count_status_curse_cards = sum(
            1
            for card in game_state.hand + game_state.discard_pile + game_state.draw_pile
            if card.type.name in ["STATUS", "CURSE"]
        )
        eval -= 30 * count_status_curse_cards

        for power in game_state.player.powers:
            if power.power_name in [
                "Demon Form",
                "Corruption",
                "Juggernaut",
                "Dark Embrace",
                "Feel No Pain",
                "Barricade",
                "Berserk",
            ]:
                if incoming_damage <= 5:
                    eval += 200
                else:
                    eval += 100
                if game_state.room_type == "MonsterRoomBoss":
                    eval += 200
                elif game_state.room_type == "MonsterRoomElite":
                    eval += 100
        return eval

    def play_all_static_potions(self, gamestate):
        """Static potions are all potions that have either a permanent effect or a semi-permanent one that lasts throught the battle. This handles when to play these potions"""

        for potion in gamestate.get_static_potions():
            if potion.can_use:
                incoming_damage = self.get_incoming_damage(gamestate)
                target = self.get_best_target(gamestate)

                if potion.name in [
                    "Blood Potion",
                    "Regen Potion",
                ] and gamestate.player.current_hp >= (
                    gamestate.player.max_hp - (gamestate.player.max_hp * 20) / 100
                ):
                    continue

                if (
                    potion.name
                    in ["Essence of Steel", "Dexterity Potion", "Strength Potion"]
                    and gamestate.room_type != "MonsterRoomElite"
                ):
                    continue
                if (
                    potion.name in ["Ghost In A Jar", "Fire Potion", "Block Potion"]
                    and incoming_damage <= 15
                ):
                    continue

                if potion.requires_target and target is not None:

                    if (
                        potion.name == "Explosive Potion"
                        and incoming_damage <= 13
                        and target.current_hp > 10
                    ):
                        continue

                    return PotionAction(
                        True,
                        potion=potion,
                        target_monster=target,
                    )
                else:
                    return PotionAction(True, potion=potion)
        return None

    def use_next_potion(self):
        """Uses all the potions in order"""

        all_potions = self.game.get_real_potions()
        for potion in all_potions:
            if potion.can_use:
                if potion.name == "Entropic Brew" and len(all_potions) != 1:
                    continue
                if potion.name == "Smoke Bomb":
                    time.sleep(5)
                if potion.requires_target:
                    return PotionAction(
                        True,
                        potion=potion,
                        target_monster=self.get_best_target(self.game),
                    )
                else:
                    return PotionAction(True, potion=potion)

        return None

    def handle_screen(self):
        """One of the bearbone function of the agent, this handles everything my might appear on the screnn, from clicking paths on the map to discarding cards to buying from shops"""

        def get_archetype(deck):
            """Returns the dominant archetype of the current deck"""

            archetype_counts = {arch: 0 for arch in ironclad_archetypes.keys()}
            for card in deck:
                for archetype, cards in ironclad_archetypes.items():
                    if card.card_id in cards["key_cards"]:
                        archetype_counts[archetype] += 1
            dominant_archetype = max(archetype_counts, key=archetype_counts.get)
            return {dominant_archetype: ironclad_archetypes[dominant_archetype]}

        def best_option_from_action(option):
            """Helper function to find the best option from the input or return the first available"""

            number_of_options = len(self.game.screen.options) - 1
            if option > number_of_options:
                return ChooseAction(number_of_options)
            else:
                return ChooseAction(option)

        def choose_rest_option(game_state):
            """Handles the entire resting screen, from smithing to resting to lifting (relic exclusive) etc"""

            rest_options = game_state.screen.rest_options
            if len(rest_options) > 0 and not game_state.screen.has_rested:
                if (
                    RestOption.REST in rest_options
                    and game_state.current_hp < game_state.max_hp / 3
                ):
                    return RestAction(RestOption.REST)
                elif RestOption.DIG in rest_options:
                    return RestAction(RestOption.DIG)
                elif RestOption.SMITH in rest_options:
                    non_basic_cards = [
                        card
                        for card in game_state.deck
                        if card.card_id not in ["Strike_R", "Defend_R"]
                    ]
                    if non_basic_cards:
                        return RestAction(RestOption.SMITH)
                    elif RestOption.REST in rest_options:
                        return RestAction(RestOption.REST)
                    else:
                        return ChooseAction(0)
                elif RestOption.LIFT in rest_options:
                    return RestAction(RestOption.LIFT)
                elif (
                    RestOption.REST in rest_options
                    and game_state.current_hp < game_state.max_hp
                ):
                    return RestAction(RestOption.REST)
                else:
                    return ChooseAction(0)
            else:
                return ProceedAction()

        def handle_grid_select(game_state, priorities):
            """Returns the best card to bbe picked from a grid of cards"""

            if not game_state.choice_available:
                return ProceedAction()
            if game_state.screen.for_upgrade:
                available_cards = [
                    card for card in game_state.screen.cards if not card.upgrades
                ]
                if not available_cards:
                    return ProceedAction()
                archetype = get_archetype(game_state.deck)
                best_card = max(
                    available_cards,
                    key=lambda card: priorities.evaluate_card_synergy(
                        card, game_state.deck, archetype
                    ),
                )
                return CardSelectAction([best_card])
            num_cards = game_state.screen.num_cards
            return CardSelectAction(game_state.screen.cards[:num_cards])

        def choose_card_reward(game_state, priorities):
            """Used for deck building, picks the best card to add to deck"""

            def count_copies_in_deck(card):
                count = 0
                for deck_card in game_state.deck:
                    if deck_card.card_id == card.card_id:
                        count += 1
                return count

            reward_cards = game_state.screen.cards
            if game_state.screen.can_skip and not game_state.in_combat:
                pickable_cards = [
                    card
                    for card in reward_cards
                    if priorities.needs_more_copies(card, count_copies_in_deck(card))
                ]
            else:
                pickable_cards = reward_cards

            if len(pickable_cards) > 0:
                best_card = max(
                    pickable_cards,
                    key=lambda card: priorities.evaluate_card_synergy(
                        card, game_state.deck, get_archetype(game_state.deck)
                    ),
                )
                return (False, CardRewardAction(best_card))
            elif game_state.screen.can_bowl:
                return (False, CardRewardAction(bowl=True))
            else:
                return (True, CancelAction())

        def make_map_choice(game_state, priorities, map_route):
            """This is how the agent picks the next path on the map"""

            def generate_map_route(priorities, map_route, game_state):
                # Select map strategy based on current HP at each node exploration
                map_route_strategy = priorities.MAP_NODE_PRIORITIES_Balanced

                if self.player_current_hp >= 0.65 * self.player_max_hp:
                    map_route_strategy = priorities.MAP_NODE_PRIORITIES_Risky
                elif self.player_current_hp <= 0.3 * self.player_max_hp:
                    map_route_strategy = priorities.MAP_NODE_PRIORITIES_Safe

                # Retrieve rewards for the current act based on strategy
                node_rewards = map_route_strategy.get(game_state.act)

                # Pathfinding algorithm for dynamically determining the best path
                best_rewards = {
                    0: {
                        node.x: node_rewards[node.symbol]
                        for node in game_state.map.nodes[0].values()
                    }
                }
                best_parents = {
                    0: {node.x: 0 for node in game_state.map.nodes[0].values()}
                }

                min_reward = min(node_rewards.values())
                map_height = max(game_state.map.nodes.keys())

                for y in range(0, map_height):
                    best_rewards[y + 1] = {
                        node.x: min_reward * 20
                        for node in game_state.map.nodes[y + 1].values()
                    }
                    best_parents[y + 1] = {
                        node.x: -1 for node in game_state.map.nodes[y + 1].values()
                    }
                    for x in best_rewards[y]:
                        node = game_state.map.get_node(x, y)
                        best_node_reward = best_rewards[y][x]
                        for child in node.children:
                            test_child_reward = (
                                best_node_reward + node_rewards[child.symbol]
                            )
                            if test_child_reward > best_rewards[y + 1][child.x]:
                                best_rewards[y + 1][child.x] = test_child_reward
                                best_parents[y + 1][child.x] = node.x

                # Construct best path from rewards and parents maps
                best_path = [0] * (map_height + 1)
                best_path[map_height] = max(
                    best_rewards[map_height].keys(),
                    key=lambda x: best_rewards[map_height][x],
                )
                for y in range(map_height, 0, -1):
                    best_path[y - 1] = best_parents[y][best_path[y]]
                map_route[:] = best_path

            # Dynamically re-generate route at every node
            generate_map_route(priorities, map_route, game_state)

            if game_state.screen.boss_available:
                return ChooseMapBossAction()

            current_y = game_state.screen.current_node.y
            next_y = current_y + 1

            # Add boundary check to prevent IndexError
            if next_y >= len(map_route):
                logging.warning("Reached the end of the map_route, no next node.")
                return ChooseAction(0)  # Or handle as appropriate for your game

            # Choose next node based on dynamically generated map route
            chosen_x = map_route[next_y]
            for choice in game_state.screen.next_nodes:
                if choice.x == chosen_x:
                    return ChooseMapNodeAction(choice)

            return ChooseAction(0)

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
            elif self.game.screen.event_id == "The Cleric":
                if self.game.current_hp <= self.game.max_hp / 1.5:
                    option = 0
                elif self.game.gold > 50:
                    option = 1
                else:
                    option = 2
            elif self.game.screen.event_id in ["Big Fish"]:
                if self.game.current_hp <= self.game.max_hp / 2.5:
                    option = 0
                else:
                    option = 1
            elif self.game.screen.event_id == "Shining Light":
                if self.game.current_hp - 30 > 0:
                    option = 0
                else:
                    option = 1
            else:
                option = 0
            return best_option_from_action(option)
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
            return choose_rest_option(self.game)
        elif self.game.screen_type == ScreenType.CARD_REWARD:
            (self.skipped_cards, action) = choose_card_reward(
                self.game, self.priorities
            )
            return action
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
            return make_map_choice(self.game, self.priorities, self.map_route)
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
            for relic in self.game.screen.relics:
                if (
                    self.game.gold >= relic.price
                    and relic.relic_id in ironclad_relic_values
                ):
                    return BuyRelicAction(relic)
            for card in self.game.screen.cards:
                archetype = get_archetype(self.game.deck)
                if self.game.gold >= card.price and not self.priorities.should_skip(
                    self.game, archetype, card
                ):
                    return BuyCardAction(card)
            return CancelAction()
        elif self.game.screen_type == ScreenType.GRID:
            return handle_grid_select(self.game, self.priorities)
        elif self.game.screen_type == ScreenType.HAND_SELECT:
            if not self.game.choice_available:
                return ProceedAction()
            num_cards = min(self.game.screen.num_cards, 3)
            return CardSelectAction(
                self.priorities.get_cards_for_action(
                    self.game.screen.cards,
                    num_cards,
                    self.game,
                )
            )
        else:
            return ProceedAction()

    def log_simulated_state(self, simulated_state, target=None):
        """This is a helper function that simply logs the game_state object"""

        # Log general game state information
        logging.info(f"  Choice Available: {simulated_state.choice_available}")
        logging.info(f"  Choice List: {simulated_state.choice_list}")
        logging.info(f"  Played Cards: {simulated_state.played_cards}")

        # Log player information
        logging.info("Player Information:")
        player = simulated_state.player
        if player:
            logging.info(f"  HP: {player.current_hp}/{player.max_hp}")
            logging.info(f"  Block: {player.block}")
            logging.info(f"  Energy: {player.energy}")
            logging.info(f"  Strength: {getattr(player, 'strength', 0)}")
            logging.info(f"  Dexterity: {getattr(player, 'dexterity', 0)}")

        # Log deck, hand, and piles
        logging.info(f"Deck Size: {len(simulated_state.deck)}")
        logging.info(
            f"Hand: {', '.join(f'{card.name} (ID: {card.card_id})' for card in simulated_state.hand)}"
        )
        logging.info(
            f"Draw Pile: {', '.join(f'{card.name} (ID: {card.card_id})' for card in simulated_state.draw_pile)}"
        )
        logging.info(
            f"Discard Pile: {', '.join(f'{card.name} (ID: {card.card_id})' for card in simulated_state.discard_pile)}"
        )
        logging.info(
            f"Exhaust Pile: {', '.join(f'{card.name} (ID: {card.card_id})' for card in simulated_state.exhaust_pile)}"
        )
        if simulated_state.card_in_play:
            logging.info(
                f"Card In Play: {simulated_state.card_in_play.name} (ID: {simulated_state.card_in_play.card_id})"
            )

        # Log monster information
        logging.info("Monsters:")
        for monster in simulated_state.monsters:
            target_marker = (
                " <- Target" if target is not None and monster == target else ""
            )
            logging.info(
                f"  {monster.name}: HP: {monster.current_hp}/{monster.max_hp}, Block: {monster.block}{target_marker}"
            )
            logging.info(f"  Status: {'Alive' if monster.current_hp > 0 else 'Dead'}")

        # Log turn information
        logging.info(f"Turn: {simulated_state.turn}")
        logging.info(
            f"Cards Discarded This Turn: {simulated_state.cards_discarded_this_turn}"
        )

        # Log relics
        logging.info(
            f"Relics: {', '.join(f'{r.name} (ID: {r.relic_id})' for r in simulated_state.relics)}"
        )

        # Final separator for clarity
        logging.info("===================================================\n")
        logging.info("===================================================\n")