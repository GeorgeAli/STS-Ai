import itertools
from anytree import LevelOrderGroupIter
import copy
import random
from card_dictionary import get_card_values, ironclad_archetypes, ironclad_relic_values
from spirecomm.spire.card import Card
from spirecomm.spire.game import Game
from spirecomm.spire.character import PlayerClass
from spirecomm.spire.screen import RestOption
from spirecomm.communication.action import *
from spirecomm.ai.priorities import IroncladPriority
import logging


logging.basicConfig(filename="best_simulated_states.log", level=logging.INFO)


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


class SimpleAgent:
    def __init__(self, chosen_class=PlayerClass.IRONCLAD):
        self.game = Game()
        self.errors = 0
        self.choose_good_card = False
        self.skipped_cards = False
        self.visited_shop = False
        self.map_route = []
        self.chosen_class = chosen_class
        self.priorities = IroncladPriority()
        self.change_class(chosen_class)
        self.action_queue = []

    def change_class(self, new_class):
        self.chosen_class = PlayerClass.IRONCLAD
        self.priorities = IroncladPriority()

    def handle_error(self, error):
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
        self.game = game_state

        if self.game.choice_available:
            self.action_queue.clear()
            return self.handle_screen()
        if self.game.proceed_available:
            self.action_queue.clear()
            return ProceedAction()
        if self.game.play_available:
            if (
                self.game.room_type == "MonsterRoomBoss"
                and len(self.game.get_real_potions()) > 0
            ):
                potion_action = self.use_next_potion()
                if potion_action is not None:
                    return potion_action

            if not self.action_queue:  # Initialize the action queue if it's empty
                self.action_queue = self.get_play_card_action()

            if self.action_queue:
                action = self.action_queue.pop(0)

                # Log the action state
                self.log_simulated_state(
                    self.game, self.find_monster_index(self.game, action.target_monster)
                )

                return action
        if self.game.end_available:
            self.action_queue.clear()
            return EndTurnAction()
        if self.game.cancel_available:
            self.action_queue.clear()
            return CancelAction()

    def get_next_action_out_of_game(self):
        return StartGameAction(self.chosen_class)

    def get_incoming_damage(self, game_state):
        incoming_damage = 0
        incoming_damage -= game_state.player.block

        incoming_damage -= next(
            (
                6
                for relic in game_state.relics
                if relic.name == "Orichalcum" and game_state.player.block == 0
            ),
            0,
        )

        incoming_damage -= next(
            (
                buff.amount
                for buff in game_state.player.powers
                if buff.power_id == "Metallicize"
            ),
            0,
        )

        incoming_damage -= next(
            (
                buff.amount
                for buff in game_state.player.powers
                if buff.power_id == "Plated Armor"
            ),
            0,
        )

        for monster in game_state.monsters:
            if not monster.is_gone:
                if (
                    monster.move_adjusted_damage is not None
                    and monster.move_adjusted_damage > 0
                ):
                    incoming_damage += monster.move_adjusted_damage * monster.move_hits

        for card in game_state.hand:
            if card.name == "Burn":
                incoming_damage += 2
            elif card.name == "Burn+":
                incoming_damage += 4

        return incoming_damage

    def get_best_target(self, game_state):
        # Filter out all alive monsters
        alive_monsters = [
            monster for monster in game_state.monsters if monster.current_hp > 0
        ]

        wizard_target = next(
            (monster for monster in alive_monsters if monster.name == "Gremlin Wizard"),
            None,
        )

        if wizard_target:
            return wizard_target

        # Further filter to find monsters that are attacking
        attacking_monsters = [
            monster for monster in alive_monsters if monster.move_adjusted_damage > 0
        ]

        # If there are attacking monsters, return the one with the lowest HP
        if attacking_monsters:
            return min(attacking_monsters, key=lambda m: (m.current_hp, m.block))

        # If no attacking monsters are found, return the monster with the lowest HP among all alive monsters
        if alive_monsters:
            return min(alive_monsters, key=lambda m: (m.block, m.current_hp))

    def get_play_card_action(self, fallback=0):
        # Filter out block cards if no monsters are attacking
        incoming_damage = self.get_incoming_damage(self.game)

        logging.info(f"incoming d is: {incoming_damage}")

        if fallback > 1:
            return [EndTurnAction()]

        # Determine playable cards based on the current state and fallback level
        playable_cards = []
        if (
            incoming_damage < 4
            and self.game.player.current_hp >= (incoming_damage - 3)
            and fallback == 0
        ):
            playable_cards = [
                card
                for card in self.game.hand
                if card.is_playable and not self.is_pure_block_card(card)
            ]
        else:
            for monster in self.game.monsters:
                for power in monster.powers:
                    if power.power_name == "Enrage":
                        playable_cards = [
                            card
                            for card in self.game.hand
                            if card.is_playable and card.type not in ["SKILL"]
                        ]
                        break

            playable_cards = [card for card in self.game.hand if card.is_playable]

        if not playable_cards:
            fallback += 1
            return self.get_play_card_action(fallback)

        # Ensure priority cards are played first if available
        for card in playable_cards:
            if card.card_id in ["Flex"]:
                return [PlayCardAction(card=card, target_monster=None)]
            if card.card_id in ["Limit Break"] and fallback < 3:
                current_strength = next(
                    (
                        buff.amount
                        for buff in self.game.player.powers
                        if buff.power_id == "Strength"
                    ),
                    0,
                )
                if current_strength <= 0:
                    playable_cards.remove(card)

        best_action_combination = []
        best_value = float("-inf")

        # Explore all possible combinations of card plays up to the available energy
        for r in range(1, len(playable_cards) + 1):
            for card_combination in itertools.combinations(playable_cards, r):
                energy_used = sum(
                    card.cost if card.cost != "X" else self.game.player.energy
                    for card in card_combination
                )
                if energy_used <= self.game.player.energy:
                    simulated_state = copy.deepcopy(self.game)
                    valid_combination = True
                    targets = []  # Reset targets for each combination
                    target = None

                    for card in card_combination:
                        # Determine if a target is needed and find the best one
                        if card.has_target:
                            target = self.get_best_target(simulated_state)
                            if target is None:
                                valid_combination = False
                                break
                            targets.append(target)
                        else:
                            targets.append(None)

                        # Simulate card play
                        simulated_state = self.simulate_card_play(
                            simulated_state, card, target
                        )

                    if valid_combination:
                        value = self.evaluate_state(simulated_state)
                        if value > best_value:
                            best_value = value
                            best_action_combination = [
                                PlayCardAction(card=card, target_monster=target)
                                for card, target in zip(card_combination, targets)
                            ]

        # If no optimal action is found, fallback and run get_play_card again
        if not best_action_combination:
            fallback += 1
            return self.get_play_card_action(fallback)

        logging.info(f"Eval chosen: {best_value}")

        return best_action_combination

    def is_pure_block_card(self, card):
        card_values = get_card_values(card.name)
        return card_values.get("block", 0) > 0 and card_values.get("damage", 0) == 0

    def get_possible_targets(self, game_state, card):
        if card.has_target:
            return [
                monster for monster in game_state.monsters if monster.current_hp > 0
            ]
        else:
            return [None]

    def simulate_card_play(self, game_state, card, target=None):

        def handle_enemy_powers(monster, card, damage, simulated_state):

            card_effects = get_card_values(card.name)

            for power in monster.powers:
                if power.power_id == "Curl Up" and damage > 0:
                    block_from_curl_up = power.amount
                    monster.block += block_from_curl_up
                    monster.powers = [
                        p for p in monster.powers if p.power_id != "Curl Up"
                    ]
                elif power.power_id == "Angry":
                    monster.add_buff("Strength", power.amount)
                elif power.power_id == "Enrage" and card.type == "SKILL":
                    monster.add_buff("Strength", power.amount)
                elif power.power_id == "Artifact":
                    debuffs = ["Vulnerable", "Weak", "Lose Strength"]  # List of debuffs
                    for debuff in debuffs:
                        if debuff in card_effects:
                            power.amount -= 1
                            if power.amount <= 0:
                                monster.powers = [
                                    p
                                    for p in monster.powers
                                    if p.power_id != "Artifact"
                                ]
                            break  # Stop after one debuff attempt to apply
                elif power.power_id == "Thorns":
                    if damage > 0:
                        simulated_state.player.current_hp -= power.amount
                elif power.power_id == "Malleable":
                    monster.block += power.amount
                    power.amount += (
                        1  # Malleable increases the amount of block each time
                    )
                elif power.power_id == "Buffer":
                    if damage > 0:
                        monster.powers = [
                            p for p in monster.powers if p.power_id != "Buffer"
                        ]
                        monster.current_hp = max(
                            monster.current_hp + damage, monster.max_hp
                        )
                elif power.power_id == "Growth":
                    monster.add_buff("Strength", power.amount)
                    monster.add_buff("Dexterity", power.amount)
                elif power.power_id == "Invincible":
                    if damage > monster.max_hp * 0.15:
                        damage = monster.max_hp * 0.15  # Cap damage to 15% of max HP
                elif power.power_id == "Metallicize":
                    monster.block += power.amount  # Gains block at the end of each turn
                elif power.power_id == "Plated Armor":
                    monster.block += power.amount  # Gains block at the end of each turn
                elif power.power_id == "Mode Shift":
                    if power.amount <= 0:
                        monster.move_adjusted_damage = 0
                elif power.power_id == "Plated Armor":
                    monster.block += power.amount  # Adds block each turn
                    if damage > 0:
                        power.amount -= (
                            1  # Reduce Plated Armor by 1 for each unblocked attack
                        )
                        if power.amount <= 0:
                            monster.powers = [
                                p
                                for p in monster.powers
                                if p.power_id != "Plated Armor"
                            ]
                elif power.power_id == "Regenerate":
                    monster.current_hp = max(
                        monster.current_hp + power.amount, monster.max_hp
                    )  # Heals each turn
                elif power.power_id == "Ritual":
                    monster.add_buff("Strength", power.amount)
                elif power.power_id == "Mode Shift":
                    monster.current_hp = power.amount
                elif power.power_id == "Flight":
                    if power.amount <= 0:
                        monster.move_adjusted_damage = 0
                        monster.current_hp = monster.current_hp
                    else:
                        monster.current_hp = monster.current_hp * 2
                elif power.power_id == "Sharp Hide":
                    if damage > 0:
                        simulated_state.player.current_hp -= power.amount
                        monster.current_hp = monster.current_hp

            return monster, simulated_state

        def handle_feed_card(game_state, card, target):
            """
            Special logic for handling the 'Feed' card to maximize its benefit.
            """
            if card.card_id != "Feed":
                return game_state  # Only proceed if the card is 'Feed'

            target_monster = game_state.monsters[target]
            feed_damage = get_card_values(card.name).get("damage", 0)
            feed_heal = get_card_values(card.name).get("gain_max_hp_on_kill", 0)

            # Calculate potential damage with strength and weakened adjustments
            current_strength = next(
                (
                    buff.amount
                    for buff in game_state.player.powers
                    if buff.power_id == "Strength"
                ),
                0,
            )
            is_weakened = any(
                debuff.power_id == "Weakened" for debuff in game_state.player.powers
            )

            if is_weakened:
                feed_damage = int(feed_damage * 0.75)  # Weakened reduces damage by 25%
            feed_damage += current_strength  # Add strength to damage

            # Check if Feed will kill the target
            if target_monster.current_hp <= feed_damage:
                # Simulate the kill and the HP gain
                game_state.player.max_hp += feed_heal
                game_state.player.current_hp += feed_heal

                # Remove the target monster from the game state
                game_state.monsters.remove(target_monster)
                game_state.exhaust_pile.append(card)  # Feed is exhausted after use
            else:
                # If Feed does not kill, apply damage normally
                target_monster.current_hp -= feed_damage

            return game_state

        is_vulnerable = False
        has_dark_emrace = False

        try:
            simulated_state = copy.deepcopy(game_state)

            random.seed(simulated_state.seed)

            if card in simulated_state.hand:
                simulated_state.hand.remove(card)
                simulated_state.played_cards.append(card)
            else:
                raise ValueError(f"Card {card.card_id} not found in simulated hand.")

            card_values = get_card_values(card.name)
            target_index = None

            if card.has_target and target is not None:
                target_index = self.find_monster_index(game_state, target)

            # Special handling for the 'Feed' card
            if card.card_id == "Feed":
                simulated_state = handle_feed_card(simulated_state, card, target_index)

            # Add strength to monsters if Philosopher's Stone
            for relic in simulated_state.relics:
                if relic.name == "Philosopher's Stone":
                    for each_monster in simulated_state.monsters:
                        each_monster.add_buff("Strength", 1)

            # Calculate player's current strength and dexterity
            current_strength = next(
                (
                    buff.amount
                    for buff in simulated_state.player.powers
                    if buff.power_id == "Strength"
                ),
                0,
            )
            current_dexterity = next(
                (
                    buff.amount
                    for buff in simulated_state.player.powers
                    if buff.power_id == "Dexterity"
                ),
                0,
            )

            # Check for player's debuffs like Weakened
            is_weakened = any(
                debuff.power_id == "Weakened"
                for debuff in simulated_state.player.powers
            )

            is_frail = any(
                debuff.power_id == "Frail" for debuff in simulated_state.player.powers
            )

            if card_values.get("damage", 0) > 0 and target_index is not None:
                damage = card_values["damage"]

                # Adjust damage based on strength and weakened status
                damage += current_strength
                if is_weakened:
                    damage = int(damage * 0.75)  # Reduce damage by 25% if weakened

                if "strength_multiplier" in card_values:
                    damage += current_strength * card_values["strength_multiplier"]

                monster = simulated_state.monsters[target_index]

                # Check if the enemy is vulnerable
                is_vulnerable = any(
                    debuff.power_id == "Vulnerable" for debuff in monster.powers
                )

                if is_vulnerable is not None:
                    damage = int(damage * 1.5)  # Vulnerable increases damage by 50%
                    # Check for Paper Frog relic, which increases the vulnerability effect to 75%
                    if any(
                        relic.relic_id == "Paper Phrog"
                        for relic in simulated_state.relics
                    ):
                        damage = int(damage * 1.75)

                damage -= monster.block

                if damage > 0:
                    monster.current_hp -= damage
                    monster.current_hp -= damage
                    monster.block = 0
                else:
                    damage = 0

                monster, simulated_state = handle_enemy_powers(
                    monster, card, damage, simulated_state
                )

            for power in simulated_state.player.powers:
                if power.power_name == "Brutality":
                    simulated_state.current_hp -= 1
                    simulated_state.player.draw(1)
                if power.power_name == "Dark Embrace":
                    has_dark_emrace = True
                if power.power_name == "Corruption":
                    if card.type == "SKILL":
                        card.exhausts = True
                        card.cost = 0
                if power.power_name == "Evolve":
                    for card in simulated_state.hand:
                        if card.type == "STATUS":
                            simulated_state.player.draw(power.amount)
                if power.power_name == "Feel No Pain":
                    if card.exhausts == True:
                        simulated_state.player.block += power.amount

            if card_values.get("block", 0) > 0:
                block = card_values["block"]

                # Adjust block based on dexterity and frail status
                block += current_dexterity
                if is_frail:
                    block = int(block * 0.75)  # Frail reduces block by 25%
                simulated_state.player.block += block

            # Other effects (vulnerable, weak, strength, etc.)
            if "vulnerable" in card_values and target_index is not None:
                simulated_state.monsters[target_index].add_debuff(
                    "Vulnerable", card_values["vulnerable"]
                )
            if "weak" in card_values and target_index is not None:
                simulated_state.monsters[target_index].add_debuff(
                    "Weak", card_values["weak"]
                )
            if "strength" in card_values:
                strength = card_values["strength"]
                simulated_state.player.add_buff("Strength", strength)
            if "draw" in card_values:
                draw = card_values["draw"]
                simulated_state.player.draw(draw)
            if "draw_on_status" in card_values:
                simulated_state.player.add_buff("Evolve", card_values["draw_on_status"])
            if "gain_energy" in card_values:
                energy = card_values["gain_energy"]
                simulated_state.player.gain_energy(energy)
            if "lose_hp" in card_values:
                lose_hp = card_values["lose_hp"]
                simulated_state.player.current_hp -= lose_hp
            if "ethereal" in card_values:
                simulated_state.player.ethereal.append(card)
            if "exhaust" in card_values:
                simulated_state.exhaust_pile.append(card)
                if has_dark_emrace:
                    simulated_state.player.draw(power.amount)
            if "aoe" in card_values:
                for aoe_monster in simulated_state.monsters:
                    if aoe_monster == monster:
                        continue
                    if aoe_monster.current_hp > 0:
                        if is_vulnerable is not None:
                            aoe_monster.current_hp -= int(
                                card_values["damage"] * 1.5
                            )  # Vulnerable increases damage by 50%
                            # Check for Paper Phrog relic, which increases the vulnerability effect to 75%
                            if any(
                                relic.relic_id == "Paper Phrog"
                                for relic in simulated_state.relics
                            ):
                                aoe_monster.current_hp -= int(
                                    card_values["damage"] * 1.75
                                )  # Vulnerable increases damage by 75%
            if "based_on_block" in card_values and target_index is not None:
                damage = simulated_state.player.block
                simulated_state.monsters[target_index].current_hp -= damage
            if "play_top_discard" in card_values:
                if simulated_state.discard_pile:
                    top_card = simulated_state.discard_pile.pop()
                    simulated_state = self.simulate_card_play(
                        simulated_state, top_card, target_index
                    )
            if "create_copy" in card_values:
                simulated_state.hand.append(copy.deepcopy(card))
            if "gain_block_on_exhaust" in card_values:
                simulated_state.player.add_buff(
                    "Feel No Pain", card_values["gain_block_on_exhaust"]
                )
            if "gain_strength_on_hp_loss" in card_values:
                strength = card_values["gain_strength_on_hp_loss"]
                simulated_state.player.add_buff("Strength", strength)
            if "multiple_hits" in card_values:
                hits = card_values["multiple_hits"]
                damage = card_values["damage"]
                for _ in range(hits):
                    if target_index is not None:
                        simulated_state.monsters[target_index].current_hp -= damage
            if "exhaust_hand" in card_values:
                simulated_state.exhaust_pile.extend(simulated_state.hand)
                if has_dark_emrace:
                    for card in simulated_state.hand:
                        simulated_state.player.draw(power.amount)
                simulated_state.hand.clear()
            if "heal_on_damage" in card_values:
                simulated_state.player.current_hp = max(
                    card_values["damage"] + simulated_state.player.current_hp,
                    simulated_state.player.max_hp,
                )
            if "random_targets" in card_values:
                targets = simulated_state.monsters[:]
                for _ in range(card_values["hits"]):
                    if targets:
                        target = random.choice(targets)
                        target.current_hp -= card_values["damage"]
            if "block_on_attack" in card_values:
                block = card_values["block_on_attack"]
                simulated_state.player.block += block
            if "damage_on_attack" in card_values and target_index is not None:
                damage = card_values["damage_on_attack"]
                simulated_state.monsters[target_index].current_hp -= damage
            if "double_block" in card_values:
                simulated_state.player.block *= 2
            if "draw_on_exhaust" in card_values:
                simulated_state.player.add_buff(
                    "Dark Embrace", card_values["draw_on_exhaust"]
                )
            if "lose_hp_per_turn" in card_values:
                simulated_state.player.add_buff(
                    "Brutality", card_values["lose_hp_per_turn"]
                )
            if "skills_cost_zero" in card_values:
                simulated_state.player.add_buff(
                    "Corruption", card_values["skills_cost_zero"]
                )
            if "exhaust_random_card" in card_values:
                if simulated_state.hand:
                    random_card_to_exhaust = random.choice(simulated_state.hand)
                    simulated_state.hand.remove(random_card_to_exhaust)
                    simulated_state.exhaust_pile.append(random_card_to_exhaust)
                    if has_dark_emrace:
                        simulated_state.player.draw(power.amount)
            if "reduce_strength" in card_values:
                simulated_state.monsters[target_index].add_buff(
                    "Strength", -card_values["reduce_strength"]
                )
            if "burns_to_draw" in card_values:
                burn_card = Card(
                    card_id="Burn",
                    name="Burn",
                    type="Status",
                    cost=-1,
                    is_playable=False,
                )
                simulated_state.draw_pile.append(burn_card)
            if "weak_aoe" in card_values:
                for monster in simulated_state.monsters:
                    monster.add_debuff("Weak", card_values["weak_aoe"])
            if "vulnerable_aoe" in card_values:
                for monster in simulated_state.monsters:
                    monster.add_debuff("Vulnerable", card_values["vulnerable_aoe"])

            return simulated_state
        except Exception as e:
            logging.info(f"Error simulating card play: {e}")
            logging.info(f"Card: {card}")
            logging.info(f"Target: {target}")
            e.card = card
            e.target = target
            raise

    # self.log_simulated_state(simulated_state, card, target_index)
    def find_monster_index(self, game_state, target):
        if target is None:
            logging.info("Target is None when attempting to find monster index.")
            return None

        if isinstance(target, int):
            if 0 <= target < len(game_state.monsters):
                return target
            else:
                logging.info(f"Target index {target} is out of range.")
                return None

        if hasattr(target, "name"):
            for index, monster in enumerate(game_state.monsters):
                if monster.name == target.name and monster.current_hp > 0:
                    return index
        else:
            logging.info(f"Invalid target: {target}")
            return None

        logging.info("Target not found among monsters.")
        return None

    def evaluate_state(self, game_state):
        eval = 0
        tolerable_damage_threshold = 4

        # Player health and survival
        eval -= (game_state.max_hp - game_state.player.current_hp) * 10
        if game_state.player.current_hp <= 0:
            return float("-inf")  # Strongly penalize if the player is dead

        # Positive buffs: Strength and Dexterity
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

        # Negative debuffs
        weakened = next(
            (
                debuff.amount
                for debuff in game_state.player.powers
                if debuff.power_id == "Weakened"
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
        frail = next(
            (
                debuff.amount
                for debuff in game_state.player.powers
                if debuff.power_id == "Frail"
            ),
            0,
        )

        eval += strength * 50
        eval += dexterity * 20
        eval -= weakened * 5
        eval -= vulnerable * 5
        eval -= frail * 5

        all_monsters_dead = True
        for monster in game_state.monsters:
            if monster.current_hp <= 0:
                eval += 5000  # Reward for killing an enemy
            else:
                eval += (monster.max_hp - monster.current_hp) / 10
                all_monsters_dead = False

        # Reward for exhausting Strikes and Defends
        for card in game_state.exhaust_pile:
            if card.card_id in ["Strike_R", "Defend_R"]:
                eval += 150
            elif card.type in ["STATUS", "CURSE"]:
                eval += 300

        # Assess incoming damage
        incoming_damage = self.get_incoming_damage(game_state)
        if incoming_damage > tolerable_damage_threshold:
            eval -= incoming_damage * 15
        elif incoming_damage < -tolerable_damage_threshold:
            eval += (incoming_damage) * 15

        eval += game_state.player.block * 3

        # Penalty for playing status cards or basic cards over better options
        playing_bad_cards = sum(
            1
            for card in game_state.played_cards
            if card.name in ["Strike", "Defend", "Slimed"]
        )
        eval -= 100 * playing_bad_cards

        # Penalty for status and curse cards in hand, discard pile, and draw pile
        count_status_curse_cards = sum(
            1
            for card in game_state.hand + game_state.discard_pile + game_state.draw_pile
            if card.type in ["STATUS", "CURSE"]
        )
        eval -= 50 * count_status_curse_cards

        for power in self.game.player.powers:
            if power.power_name in ["Hex"]:
                for card in game_state.played_cards:
                    if card.type in ["SKILL"]:
                        eval -= 300

        # Bonus for winning the fight
        if all_monsters_dead:
            eval += 10000  # Significant bonus for winning the fight

        logging.info(f"Total Eval: {int(eval)}")

        return int(eval)

    def use_next_potion(self):
        for potion in self.game.get_real_potions():
            if potion.can_use:
                if potion.requires_target:
                    return PotionAction(
                        True,
                        potion=potion,
                        target_monster=self.get_best_target(self.game),
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
            for relic in self.game.screen.relics:
                if self.game.gold >= relic.price and self.should_buy_relic(relic):
                    return BuyRelicAction(relic)
            for card in self.game.screen.cards:
                archetype = self.get_archetype()
                if self.game.gold >= card.price and not self.priorities.should_skip(
                    self.game, archetype, card
                ):
                    return BuyCardAction(card)
            return CancelAction()
        elif self.game.screen_type == ScreenType.GRID:
            return self.handle_grid_select()
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

    def handle_grid_select(self):
        if not self.game.choice_available:
            return ProceedAction()
        if self.game.screen.for_upgrade:
            available_cards = [
                card for card in self.game.screen.cards if not card.upgrades
            ]
            if not available_cards:
                return ProceedAction()
            archetype = self.get_archetype()
            best_card = max(
                available_cards,
                key=lambda card: self.priorities.evaluate_card_synergy(
                    card, self.game.deck, archetype
                ),
            )
            return CardSelectAction([best_card])
        num_cards = self.game.screen.num_cards
        return CardSelectAction(self.game.screen.cards[:num_cards])

    def should_buy_relic(self, relic):
        return relic.relic_id in ironclad_relic_values

    def get_archetype(self):
        archetype_counts = {arch: 0 for arch in ironclad_archetypes.keys()}
        for card in self.game.deck:
            for archetype, cards in ironclad_archetypes.items():
                if card.card_id in cards["key_cards"]:
                    archetype_counts[archetype] += 1
        dominant_archetype = max(archetype_counts, key=archetype_counts.get)
        return {dominant_archetype: ironclad_archetypes[dominant_archetype]}

    def choose_rest_option(self):
        rest_options = self.game.screen.rest_options
        if len(rest_options) > 0 and not self.game.screen.has_rested:
            if (
                RestOption.REST in rest_options
                and self.game.current_hp < self.game.max_hp / 3
            ):
                return RestAction(RestOption.REST)
            elif RestOption.SMITH in rest_options:
                non_basic_cards = [
                    card
                    for card in self.game.deck
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

        def get_archetype(deck):
            archetype_counts = {arch: 0 for arch in ironclad_archetypes.keys()}
            for card in deck:
                for archetype, cards in ironclad_archetypes.items():
                    if card.card_id in cards["key_cards"]:
                        archetype_counts[archetype] += 1

            return max(archetype_counts, key=archetype_counts.get)

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
            archetype = get_archetype(self.game.deck)
            best_card = max(
                pickable_cards,
                key=lambda card: self.priorities.evaluate_card_synergy(
                    card, self.game.deck, {archetype: ironclad_archetypes[archetype]}
                ),
            )
            return CardRewardAction(best_card)
        elif self.game.screen.can_bowl:
            return CardRewardAction(bowl=True)
        else:
            self.skipped_cards = True
            return CancelAction()

    def choose_card_to_upgrade(self):
        upgradeable_cards = [card for card in self.game.deck if card.upgrades > 0]
        if not upgradeable_cards:
            return None

        # Evaluate each card based on synergy with the current archetype
        best_card = max(
            upgradeable_cards,
            key=lambda card: self.evaluate_card_upgrade(card),
        )
        return best_card

    def evaluate_card_upgrade(self, card):
        # Evaluate the benefit of upgrading a card based on its archetype synergy
        card_values = get_card_values(card.name)
        synergy_score = self.priorities.evaluate_card_synergy(
            card, self.game.deck, ironclad_archetypes
        )

        upgrade_benefits = {
            "damage": 5,
            "block": 7,
            "draw": 5,
            "gain_energy": 5,
            "strength": 15,
            "vulnerable": 10,
            "weak": 10,
            "exhaust": 2,
        }

        benefit_score = 0
        for key, value in upgrade_benefits.items():
            if key in card_values:
                benefit_score += value

        return synergy_score + benefit_score

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
        return ChooseAction(0)

    def max_leaf_decision(self, r):
        for children in LevelOrderGroupIter(r, maxlevel=2):
            for node in children:
                if node in r.children:
                    if node.name.grade == r.name.grade:
                        if not node.children:
                            return node.name.decision[0]
                        else:
                            return self.max_leaf_decision(node)

    def log_simulated_state(self, simulated_state, target_index=None):

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
        for i, monster in enumerate(simulated_state.monsters):
            target_marker = " <- Target" if i == target_index else ""
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