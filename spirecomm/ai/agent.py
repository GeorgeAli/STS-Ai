import itertools
from math import log
from anytree import LevelOrderGroupIter
import copy
import random
from card_dictionary import get_card_values, ironclad_archetypes, ironclad_relic_values
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


def apply_card_effects(next_state, card_values, play, target=None):
    # Apply damage
    if "damage" in card_values and target is not None:
        damage = card_values["damage"]
        if "strength_multiplier" in card_values:
            strength = next(
                (
                    power.amount
                    for power in next_state.player.powers
                    if power.power_id == "Strength"
                ),
                0,
            )
            damage += strength * card_values["strength_multiplier"]

        # Handle "Curl Up" power
        if isinstance(target, list):
            for t in target:
                monster = next_state.monsters[t]
                if any(power.power_id == "Curl Up" for power in monster.powers):
                    block_from_curl_up = next(
                        (
                            power.amount
                            for power in monster.powers
                            if power.power_id == "Curl Up"
                        ),
                        0,
                    )
                    monster.current_hp -= damage
                    monster.block += block_from_curl_up
                    # Remove "Curl Up" power after it triggers
                    monster.powers = [
                        power for power in monster.powers if power.power_id != "Curl Up"
                    ]
                else:
                    monster.current_hp -= damage
        else:
            monster = next_state.monsters[target]
            if any(power.power_id == "Curl Up" for power in monster.powers):
                block_from_curl_up = next(
                    (
                        power.amount
                        for power in monster.powers
                        if power.power_id == "Curl Up"
                    ),
                    0,
                )
                monster.current_hp -= damage
                monster.block += block_from_curl_up
                # Remove "Curl Up" power after it triggers
                monster.powers = [
                    power for power in monster.powers if power.power_id != "Curl Up"
                ]
            else:
                monster.current_hp -= damage

    # Apply block
    if "block" in card_values:
        block = card_values["block"]
        next_state.player.block += block

    # Apply vulnerable
    if "vulnerable" in card_values and target is not None:
        if isinstance(target, list):
            for t in target:
                next_state.monsters[t].add_debuff(
                    "vulnerable", card_values["vulnerable"]
                )
        else:
            next_state.monsters[target].add_debuff(
                "vulnerable", card_values["vulnerable"]
            )

    # Apply weak
    if "weak" in card_values and target is not None:
        if isinstance(target, list):
            for t in target:
                next_state.monsters[t].add_debuff("weak", card_values["weak"])
        else:
            next_state.monsters[target].add_debuff("weak", card_values["weak"])

    # Apply strength
    if "strength" in card_values:
        strength = card_values["strength"]
        next_state.player.add_buff("Strength", strength)

    # Apply draw
    if "draw" in card_values:
        draw = card_values["draw"]
        next_state.player.draw(draw)

    # Apply gain_energy
    if "gain_energy" in card_values:
        energy = card_values["gain_energy"]
        next_state.player.gain_energy(energy)

    # Apply lose_hp
    if "lose_hp" in card_values:
        lose_hp = card_values["lose_hp"]
        next_state.player.current_hp -= lose_hp

    # Apply ethereal
    if "ethereal" in card_values:
        next_state.player.ethereal.append(play)

    # Apply exhaust
    if "exhaust" in card_values:
        play.exhausts = True


# Get next game state
def get_next_game_state(play, state, target):
    next_state = copy.deepcopy(state)
    decisionlist = []

    card_name = play.name
    card_values = get_card_values(card_name)

    if isinstance(target, list):
        apply_card_effects(next_state, card_values, play, target)
        if play.exhausts:
            next_state.exhaust_pile.append(play)
        else:
            next_state.discard_pile.append(play)
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
        decisionlist.append("special")
    elif isinstance(target, int):
        if target == -1:
            apply_card_effects(next_state, card_values, play)
        else:
            apply_card_effects(next_state, card_values, play, target)
        if play.exhausts:
            next_state.exhaust_pile.append(play)
        else:
            next_state.discard_pile.append(play)
        decisionlist.append(play)
        if target != -1:
            decisionlist.append(next_state.monsters[target])
    elif target is not None:
        target_index = next_state.monsters.index(target)
        apply_card_effects(next_state, card_values, play, target_index)
        if play.exhausts:
            next_state.exhaust_pile.append(play)
        else:
            next_state.discard_pile.append(play)
        decisionlist.append(play)
        decisionlist.append(target)

    if isinstance(next_state, SimGame):
        next_state.decision.append(decisionlist)
    return next_state


def evaluate_card_synergy(card, deck, archetypes):
    synergy_score = 0
    card_name = card.card_id

    # Determine which archetype the current deck is leaning towards
    archetype_scores = {arch: 0 for arch in archetypes}
    for deck_card in deck:
        for archetype, cards in archetypes.items():
            if (
                deck_card.card_id in cards["key_cards"]
                or deck_card.card_id in cards["support_cards"]
            ):
                archetype_scores[archetype] += 1

    dominant_archetype = max(archetype_scores, key=archetype_scores.get)

    # Calculate synergy score based on the dominant archetype
    if card_name in archetypes[dominant_archetype]["key_cards"]:
        synergy_score += 15  # High priority for key cards
    elif card_name in archetypes[dominant_archetype]["support_cards"]:
        synergy_score += 10  # Medium priority for support cards

    # Add some logic for overlapping cards that fit into multiple builds
    for archetype, cards in archetypes.items():
        if card_name in cards["key_cards"] or card_name in cards["support_cards"]:
            if archetype != dominant_archetype:
                synergy_score += 5  # Lower priority for multi-build cards

    # Penalize basic cards like Defend and Strike
    if card_name in ["Defend_R", "Strike_R"]:
        synergy_score -= 10  # Penalty for basic cards
    return synergy_score


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

    def get_incoming_damage(self, game_state):
        incoming_damage = 0
        incoming_damage -= game_state.player.block

        incoming_damage -= next(
            (
                buff.amount
                for buff in game_state.player.powers
                if buff.power_id == "Metallicize"
            ),
            0,
        )

        for monster in game_state.monsters:
            if not monster.is_gone:
                if (
                    monster.move_adjusted_damage is not None
                    and monster.move_adjusted_damage > 0
                ):
                    incoming_damage += monster.move_adjusted_damage

        return incoming_damage

    def get_best_target(self, game_state, card):

        if card.has_target:
            # Get a list of all potential targets with current_hp > 0
            potential_targets = [
                monster for monster in game_state.monsters if monster.current_hp > 0
            ]

            if not potential_targets:
                return None

            # Prioritize targets with the lowest block and current HP
            target = min(potential_targets, key=lambda m: (m.block, m.current_hp))
            return target

        # If card does not require a target or no damage is involved
        return None

    def get_highest_priority_target(self, game_state):
        attacking_monsters = [
            monster for monster in game_state.monsters if monster.current_hp > 0
        ]
        if attacking_monsters:
            return min(attacking_monsters, key=lambda m: m.current_hp)
        return min(
            (monster for monster in game_state.monsters if monster.current_hp > 0),
            key=lambda m: m.current_hp,
            default=None,
        )

    def has_thorns(self, monster):
        return any(power.power_id == "Thorns" for power in monster.powers)

    def handle_special_enemies(self):
        def is_gremlin_nob(monster):
            return monster.name == "Gremlin Nob"

        def is_lagavulin(monster):
            return monster.name == "Lagavulin"

        for monster in self.game.monsters:
            if self.has_thorns(monster):
                if any(
                    card
                    for card in self.game.hand
                    if card.type == "attack" and card.is_playable
                ):
                    non_thorns_target = next(
                        (
                            m
                            for m in self.game.monsters
                            if not self.has_thorns(m) and m.current_hp > 0
                        ),
                        None,
                    )
                    if non_thorns_target:
                        return non_thorns_target

        if any(is_gremlin_nob(monster) for monster in self.game.monsters):
            return "gremlin_nob"

        if any(is_lagavulin(monster) for monster in self.game.monsters):
            return "lagavulin"

        return None

    def use_all_energy(self, cards):
        energy_used = 0
        for card in cards:
            if card.cost == "X":
                energy_used += self.game.player.energy
            else:
                energy_used += card.cost
        return energy_used >= self.game.player.energy

    def get_play_card_action(self, fallback=0):
        # Filter out block cards if no monsters are attacking
        incoming_damage = self.get_incoming_damage(self.game)
        if fallback == 1:
            playable_cards = [card for card in self.game.hand if card.is_playable]
        elif incoming_damage < 4 and self.game.player.current_hp >= (
            incoming_damage - 4
        ):
            playable_cards = [
                card
                for card in self.game.hand
                if card.is_playable
                and not self.is_pure_block_card(card)
                and not card.card_id in ["Slimed", "Burn", "Wound", "Dazed"]
            ]
        else:
            playable_cards = [
                card
                for card in self.game.hand
                if card.is_playable
                and card.card_id not in ["Slimed", "Burn", "Wound", "Dazed"]
            ]

        available_targets = [
            monster for monster in self.game.monsters if monster.current_hp > 0
        ]

        if not playable_cards:
            fallback += 1
            return self.get_play_card_action(fallback)

        if not available_targets:
            playable_cards = [card for card in playable_cards if not card.has_target]

        # Ensure priority cards are played first if available
        for card in playable_cards:
            if card.name in ["Flex", "Flex+", "Inflame", "Inflame+"]:
                if card.has_target:
                    target = self.get_best_target(self.game, card)
                else:
                    target = None
                return PlayCardAction(card=card, target_monster=target)

        best_action = None
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
                    target = None  # Reset target for each combination

                    for card in card_combination:
                        # Determine if a target is needed and find the best one
                        if card.has_target:
                            target = self.get_best_target(simulated_state, card)
                            if target is None:
                                valid_combination = False
                                break

                        # Simulate card play
                        simulated_state = self.simulate_card_play(
                            simulated_state, card, target
                        )

                    if valid_combination:
                        value = self.minimax(simulated_state, 10, False)
                        if value > best_value or (
                            value == best_value
                            and self.use_all_energy(card_combination)
                        ):
                            best_value = value
                            best_action = PlayCardAction(
                                card=card_combination[0], target_monster=target
                            )

        # If no optimal action is found, fallback and run get_play_card again
        if not best_action:
            fallback += 1
            return self.get_play_card_action(fallback)

        # If somehow no action was chosen, end turn as a last resort
        return best_action if best_action else EndTurnAction()

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
        try:
            simulated_state = copy.deepcopy(game_state)

            if card in simulated_state.hand:
                simulated_state.hand.remove(card)
                simulated_state.played_cards.append(card)
            else:
                raise ValueError(f"Card {card.card_id} not found in simulated hand.")

            card_values = get_card_values(card.name)
            target_index = None

            if card.has_target and target is not None:
                target_index = self.find_monster_index(game_state, target)

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

            # Apply card effects (damage, block, etc.)
            if card_values.get("damage", 0) > 0 and target_index is not None:
                damage = card_values["damage"]

                # Adjust damage based on strength and weakened status
                damage += current_strength
                if is_weakened:
                    damage = int(damage * 0.75)  # Reduce damage by 25% if weakened

                if "strength_multiplier" in card_values:
                    damage += current_strength * card_values["strength_multiplier"]

                monster = simulated_state.monsters[target_index]
                if any(power.power_id == "Curl Up" for power in monster.powers):
                    block_from_curl_up = next(
                        (
                            power.amount
                            for power in monster.powers
                            if power.power_id == "Curl Up"
                        ),
                        0,
                    )
                    monster.current_hp -= damage
                    monster.block += block_from_curl_up
                    monster.powers = [
                        power for power in monster.powers if power.power_id != "Curl Up"
                    ]
                else:
                    monster.current_hp -= damage

            if card_values.get("block", 0) > 0:
                block = card_values["block"]

                # Adjust block based on dexterity
                block += current_dexterity
                simulated_state.player.block += block

            # Other effects (vulnerable, weak, strength, etc.)
            if "vulnerable" in card_values and target_index is not None:
                simulated_state.monsters[target_index].add_debuff(
                    "vulnerable", card_values["vulnerable"]
                )
            if "weak" in card_values and target_index is not None:
                simulated_state.monsters[target_index].add_debuff(
                    "weak", card_values["weak"]
                )
            if "strength" in card_values:
                strength = card_values["strength"]
                simulated_state.player.add_buff("Strength", strength)
            if "draw" in card_values:
                draw = card_values["draw"]
                simulated_state.player.draw(draw)
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
            if card_values.get("aoe", False):
                for monster in simulated_state.monsters:
                    if monster.current_hp > 0:
                        monster.current_hp -= card_values["damage"]
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
                block = card_values["gain_block_on_exhaust"]
                simulated_state.player.block += block
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
                simulated_state.hand.clear()
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
                draw = card_values["draw_on_exhaust"]
                simulated_state.player.draw(draw)

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
            raise ValueError("Target cannot be None when finding monster index.")

        if isinstance(target, int):
            if 0 <= target < len(game_state.monsters):
                return target
            else:
                logging.info(f"Target index {target} is out of range.")
                raise ValueError(f"Target index {target} is out of range.")

        if hasattr(target, "name"):
            for index, monster in enumerate(game_state.monsters):
                if monster.name == target.name and monster.current_hp > 0:
                    return index
        else:
            logging.info(f"Invalid target: {target}")
            raise ValueError(f"Invalid target: {target}")

        logging.info("Target not found among monsters.")
        raise ValueError("Target not found among monsters.")

    def minimax(
        self,
        game_state,
        depth,
        maximizing_player,
        alpha=float("-inf"),
        beta=float("inf"),
    ):
        if depth == 0 or self.is_terminal(game_state):
            return self.evaluate_state(game_state)

        if maximizing_player:
            max_eval = float("-inf")
            for card in game_state.hand:
                if card.is_playable:
                    for target in self.get_possible_targets(game_state, card):
                        simulated_state = self.simulate_card_play(
                            game_state, card, target
                        )
                        eval = self.minimax(
                            simulated_state, depth - 1, False, alpha, beta
                        )
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break  # Beta cut-off
            return max_eval
        else:
            min_eval = float("inf")
            for card in game_state.hand:
                if card.is_playable:
                    for target in self.get_possible_targets(game_state, card):
                        simulated_state = self.simulate_card_play(
                            game_state, card, target
                        )
                        eval = self.minimax(
                            simulated_state, depth - 1, True, alpha, beta
                        )
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break  # Alpha cut-off
            return min_eval

    def is_terminal(self, game_state):
        return game_state.player.current_hp <= 0 or all(
            monster.current_hp <= 0 for monster in game_state.monsters
        )

    def evaluate_state(self, game_state):
        eval = 0
        tolerable_damage_threshold = 4  # Allowable damage without heavy penalty

        # Player health and survival
        eval += game_state.player.current_hp
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
        eval += strength * 100  # Value strength highly
        eval += dexterity * 10  # Value dexterity highly

        # Negative debuffs: Weakened, Vulnerable, Frail
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
        eval -= weakened * 5
        eval -= vulnerable * 5
        eval -= frail * 5

        # Monster health
        for monster in game_state.monsters:
            if "Vulnerable" in [debuff.power_id for debuff in monster.powers]:
                eval += 20  # Reward for exploiting vulnerability

        # Card effects: reward draw, block, damage
        for card in game_state.played_cards:
            card_values = get_card_values(card.name)
            if "draw" in card_values:
                eval += 5 * card_values["draw"]
            if "block" in card_values:
                eval += 30 * card_values["block"]
            if "damage" in card_values:
                eval += 30 * card_values["damage"]
            if card.name in ("Defend", "Strike", "Defend+", "Strike+"):
                eval -= 200

        # Assess incoming damage and apply a penalty for over-blocking or unnecessary block
        incoming_damage = self.get_incoming_damage(game_state)

        if incoming_damage > tolerable_damage_threshold:
            eval -= incoming_damage * 40
        elif incoming_damage < -tolerable_damage_threshold:
            eval += (incoming_damage) * 40  # Harsher penalty for excess block

        # Dying, prioritize block
        if incoming_damage >= game_state.player.current_hp:
            eval += game_state.player.block * 100

        # Penalty for status cards like Slimed, Burn, etc.
        if any(
            card.card_id in ["Slimed", "Burn", "Wound", "Dazed", "Dende"]
            for card in game_state.played_cards
        ):
            eval -= 20  # Apply a penalty for playing status cards

        logging.info(f"Eval: {eval}")

        return eval

    def use_next_potion(self):
        for potion in self.game.get_real_potions():
            if potion.can_use:
                if potion.requires_target:
                    return PotionAction(
                        True,
                        potion=potion,
                        target_monster=self.get_highest_priority_target(self.game),
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
                    self.game.current_action,
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
                key=lambda card: evaluate_card_synergy(card, self.game.deck, archetype),
            )
            return CardSelectAction([best_card])
        num_cards = self.game.screen.num_cards
        return CardSelectAction(self.game.screen.cards[:num_cards])

    def should_buy_relic(self, relic):
        return (
            relic.relic_id in ironclad_relic_values
            and ironclad_relic_values[relic.relic_id] >= 15
        )

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
                key=lambda card: evaluate_card_synergy(
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
        archetype = self.get_archetype()
        best_card = max(
            upgradeable_cards,
            key=lambda card: self.evaluate_card_upgrade(card, archetype),
        )
        return best_card

    def evaluate_card_upgrade(self, card, archetype):
        # Evaluate the benefit of upgrading a card based on its archetype synergy
        card_values = get_card_values(card.name)
        synergy_score = evaluate_card_synergy(card, self.game.deck, ironclad_archetypes)

        upgrade_benefits = {
            "damage": 5,
            "block": 5,
            "draw": 10,
            "gain_energy": 10,
            "strength": 10,
            "vulnerable": 7,
            "weak": 7,
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

    def log_simulated_state(self, simulated_state, card, target_index=None):
        logging.info(f"Simulated playing {card.card_id} ({card.name}):")

        # Log general game state information
        logging.info("General Game State:")
        logging.info(f"  Current Action: {simulated_state.current_action}")
        logging.info(f"  Current HP: {simulated_state.current_hp}")
        logging.info(f"  Max HP: {simulated_state.max_hp}")
        logging.info(f"  Floor: {simulated_state.floor}")
        logging.info(f"  Act: {simulated_state.act}")
        logging.info(f"  Gold: {simulated_state.gold}")
        logging.info(f"  Ascension Level: {simulated_state.ascension_level}")
        logging.info(f"  Room Phase: {simulated_state.room_phase}")
        logging.info(f"  Room Type: {simulated_state.room_type}")
        logging.info(f"  Screen Up: {simulated_state.screen_up}")
        logging.info(f"  Screen Type: {simulated_state.screen_type}")
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
        logging.info(
            f"Limbo: {', '.join(f'{card.name} (ID: {card.card_id})' for card in simulated_state.limbo)}"
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
        logging.info("===================================================")