from asyncio.windows_events import NULL
import itertools
import copy
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

        logging.info(f"Floor: {game_state.floor}")
        self.game = game_state

        if self.game.choice_available:
            self.played_a_potion = False
            return self.handle_screen()
        if self.game.proceed_available:
            self.played_a_potion = False
            return ProceedAction()
        if self.game.play_available:
            for relic in self.game.relics:
                if (
                    relic.name == "White Beast Statue"
                    and len(self.game.get_real_potions()) > 0
                    and self.played_a_potion == False
                ):
                    potion_action = self.use_next_potion()
                    if potion_action is not None:
                        self.played_a_potion = True
                        return potion_action

            if (self.game.room_type == "MonsterRoomBoss") and len(
                self.game.get_real_potions()
            ) > 0:
                potion_action = self.use_next_potion()
                if potion_action is not None:
                    return potion_action

            ((card, target), best_game_state) = self.get_play_card_action()

            if not card:
                return EndTurnAction()

            # Log the action state
            self.log_simulated_state(best_game_state, target)

            return PlayCardAction(card=card, target_monster=target)
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
                6
                for relic in game_state.relics
                if relic.name == "Orichalcum" and game_state.player.block == 0
            ),
            0,
        )

        for power in game_state.player.powers:
            if power.power_id in ["Plated Armor", "Metallicize"]:
                incoming_damage -= power.amount

        for monster in game_state.monsters:
            if monster.current_hp > 0 and not monster.is_gone:
                if (
                    monster.move_adjusted_damage is not None
                    and monster.move_adjusted_damage > 0
                ):
                    incoming_damage += monster.move_adjusted_damage * monster.move_hits

        for card in game_state.hand:
            if card.name == "Burn":
                incoming_damage += 2
            if card.name == "Burn+":
                incoming_damage += 4
            if card.name == "Decay":
                incoming_damage += 2

        return incoming_damage

    def get_best_target(self, game_state):
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

        if sentry_target or alive_monsters.count == 1:
            return alive_monsters[0]

        if wizard_target:
            return wizard_target

        # Filter to find monsters that are actively attacking
        attacking_monsters = [
            monster for monster in alive_monsters if monster.move_adjusted_damage > 0
        ]

        # From attacking monsters, filter out those that have high block, unless their attack is significantly high
        effective_attackers = [
            monster
            for monster in attacking_monsters
            if monster.block < 6
            or monster.move_adjusted_damage > 20
            and monster.current_hp < 13
        ]

        # If there are effective attackers, target the one with the lowest HP to maximize the chance of eliminating a threat
        if effective_attackers:
            return min(effective_attackers, key=lambda m: m.current_hp + m.block)

        # If no effective attackers are found, default to attacking the monster with the lowest HP among those that are attacking
        if attacking_monsters:
            return min(attacking_monsters, key=lambda m: m.current_hp + m.block)

        if alive_monsters:
            return min(alive_monsters, key=lambda m: m.current_hp + m.block)

        return None

    def init_playable_cards(self, game_state):

        def is_pure_block_card(card):
            card_values = get_card_values(card.name)
            return card_values.get("block", 0) > 0 and card_values.get("damage", 0) == 0

        playable_cards = []

        incoming_damage = self.get_incoming_damage(game_state)

        # First, get all playable cards once
        all_playable_cards = [card for card in game_state.hand if card.is_playable]

        # Prepare to adjust playable cards based on monster powers
        for monster in game_state.monsters:
            for power in monster.powers:
                if (
                    monster.name == "Gremlin Nob"
                    or monster.monster_id == "GremlinNob"
                    or power.power_name == "Enrage"
                ):
                    playable_cards = [
                        card for card in all_playable_cards if card.type != "SKILL"
                    ]
                    return playable_cards

        if incoming_damage <= 2:
            playable_cards = [
                card for card in all_playable_cards if not is_pure_block_card(card)
            ]
        else:
            playable_cards = all_playable_cards

        # Ensure priority cards are played first if available
        for card in playable_cards:
            if card.card_id in ["Limit Break"]:
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

        return playable_cards

    def expectimax(self):
        max_eval = float("-inf")
        best_action = (None, None)
        best_game_state = None

        # Get all playable cards
        playable_cards = self.init_playable_cards(self.game)

        # Get the player's available energy
        available_energy = self.game.player.energy

        # Generate all possible combinations of playable cards
        for r in range(1, len(playable_cards) + 1):
            for combo in itertools.permutations(playable_cards, r):
                total_cost = 0
                first_card_target = None
                is_first_card = True

                for card in combo:
                    if card.cost == -1:
                        card.cost = available_energy
                    total_cost += card.cost

                # Skip the combination if it exceeds available energy
                if total_cost > available_energy:
                    continue

                simulated_state = copy.deepcopy(self.game)

                # Now simulate the rest of the combination on top of the simulated state
                for card in combo:
                    if card.has_target or card.card_id in ["Sword Boomerang"]:
                        target_monster = self.get_best_target(simulated_state)
                        simulated_state = self.simulate_card_play(
                            simulated_state, card, target_monster
                        )
                        if is_first_card:
                            first_card_target = target_monster
                            is_first_card = False
                    else:
                        simulated_state = self.simulate_card_play(
                            simulated_state, card, None
                        )

                # Evaluate the final game state
                eval = self.evaluate_state(simulated_state)

                # Update best action and state if a better evaluation is found
                if eval >= max_eval:
                    max_eval = eval
                    best_action = (
                        combo[0],
                        first_card_target,
                    )
                    best_game_state = simulated_state

        return max_eval, best_action, best_game_state

    def get_play_card_action(self):
        best_eval, best_action, best_game_state = self.expectimax()

        if best_action:
            logging.info(f"Best Eval picked: {best_eval}")
            logging.info(f"Best Action picked: {best_action}")
            return (
                best_action,
                best_game_state,
            )  # Return the best card action to perform
        else:
            return EndTurnAction()

    def simulate_card_play(self, simulated_state, card, target=None):

        def apply_exhaust_effects(game_state):
            for power in game_state.player.powers:
                if power.power_name == "Dark Embrace":
                    game_state.player.draw(power.amount)
                if power.power_name == "Feel No Pain":
                    game_state.player.block += power.amount

        def calculate_damage(card, game_state, target):

            card_values = get_card_values(card.name)

            if card_values.get("damage", 0) <= 0 or target is None:
                return 0

            damage = card_values["damage"]
            damage -= target.block

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

            if damage <= 0:
                return 0

            # Adjust damage based on strength and weakened status
            damage += current_strength
            if is_weakened:
                damage = int(damage * 0.75)  # Reduce damage by 25% if weakened

            if "strength_multiplier" in card_values:
                damage += max(1, current_strength) * card_values["strength_multiplier"]

            # Check if the enemy is vulnerable
            if target.has_debuff("Vulnerable") == True:
                damage = int(damage * 1.5)  # Vulnerable increases damage by 50%
                # Check for Paper Frog relic, which increases the vulnerability effect to 75%
                for relic in game_state.relics:
                    if relic.relic_id == "Paper Phrog":
                        damage = int(damage * 1.75)
                    if relic.relic_id == "Pen Nib" and relic.counter == 10:
                        damage *= 2
                    if relic.relic_id == "Akabeko" and game_state.turn == 0:
                        damage += 8

            return damage

        def handle_enemy_powers(monster, card, damage, simulated_state):

            card_effects = get_card_values(card.name)

            for power in monster.powers:
                if power.power_id == "Curl Up" and damage > 0:
                    block_from_curl_up = power.amount
                    monster.block += block_from_curl_up
                    monster.powers = [
                        p for p in monster.powers if p.power_id != "Curl Up"
                    ]
                if power.power_id == "Anger" and card.type == "SKILL":
                    monster.add_buff("Strength", power.amount)
                if power.power_id == "Angry" and damage > 0:
                    monster.add_buff("Strength", power.amount)
                if power.power_id == "Artifact":
                    debuffs = ["vulnerable", "weak", "lose_strength"]  # List of debuffs
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
                if power.power_id == "Thorns":
                    if damage > 0:
                        if simulated_state.player.block == 0:
                            simulated_state.player.current_hp -= power.amount
                        else:
                            simulated_state.player.block -= power.amount
                if power.power_id == "Malleable":
                    monster.block += power.amount
                    power.amount += (
                        1  # Malleable increases the amount of block each time
                    )
                if power.power_id == "Buffer":
                    if damage > 0:
                        monster.powers = [
                            p for p in monster.powers if p.power_id != "Buffer"
                        ]
                        monster.current_hp = max(
                            monster.current_hp + damage, monster.max_hp
                        )
                if power.power_id == "Growth":
                    monster.add_buff("Strength", power.amount)
                    monster.add_buff("Dexterity", power.amount)
                if power.power_id == "Invincible":
                    if damage > monster.max_hp * 0.15:
                        damage = monster.max_hp * 0.15  # Cap damage to 15% of max HP
                if power.power_id == "Metallicize":
                    monster.block += power.amount  # Gains block at the end of each turn
                if power.power_id == "Plated Armor":
                    monster.block += power.amount  # Gains block at the end of each turn
                if power.power_id == "Mode Shift":
                    if power.amount <= 0:
                        monster.move_adjusted_damage = 0
                if power.power_id == "Plated Armor":
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
                if power.power_id == "Regenerate":
                    monster.current_hp = max(
                        monster.current_hp + power.amount, monster.max_hp
                    )  # Heals each turn
                if power.power_id == "Ritual":
                    monster.add_buff("Strength", power.amount)
                if power.power_id == "Flight":
                    if power.amount <= 0:
                        monster.move_adjusted_damage = 0
                        monster.current_hp = monster.current_hp
                    else:
                        monster.current_hp = monster.current_hp * 2
                if power.power_id == "Sharp Hide":
                    if simulated_state.player.block == 0:
                        simulated_state.player.current_hp -= power.amount
                    else:
                        simulated_state.player.block -= power.amount

            return monster, simulated_state

        def handle_feed_card(simulated_state, card, target_monster, card_values):

            if card.card_id != "Feed":
                return simulated_state  # Only proceed if the card is 'Feed'

            feed_heal = card_values["gain_max_hp_on_kill"]

            damage = calculate_damage(card, simulated_state, target_monster)
            target_monster.current_hp -= abs(damage)

            # Check if Feed will kill the target
            if target_monster.current_hp <= 0:
                # Simulate the kill and the HP gain
                simulated_state.player.max_hp += feed_heal
                simulated_state.player.current_hp += feed_heal
                self.feed_effect_used = True
            else:
                self.feed_effect_used = False
            simulated_state.exhaust_pile.append(card)  # Feed is exhausted after use
            apply_exhaust_effects(simulated_state)
            return simulated_state

        try:
            damage = 0
            block = 0
            no_extra_damage = False
            simulated_state_target = None

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
                logging.info(f"Card {card.card_id} not found in simulated hand.")
                return simulated_state

            card_values = get_card_values(card.name)

            # Special handling for the 'Feed' card
            if card.card_id == "Feed":
                return handle_feed_card(
                    simulated_state, card, simulated_state_target, card_values
                )

            # Calculate player's current dexterity
            current_dexterity = next(
                (
                    buff.amount
                    for buff in simulated_state.player.powers
                    if buff.power_id == "Dexterity"
                ),
                0,
            )

            is_frail = any(
                debuff.power_id == "Frail" for debuff in simulated_state.player.powers
            )

            if card_values.get("block", 0) > 0:
                block = card_values["block"]

                # Adjust block based on dexterity and frail status
                if block == 0:
                    simulated_state.player.block = 0
                else:
                    block += current_dexterity
                    if is_frail:
                        block = int(block * 0.75)  # Frail reduces block by 25%
                    simulated_state.player.block += block

            for power in simulated_state.player.powers:
                if power.power_name == "Brutality":
                    simulated_state.current_hp -= 1
                    simulated_state.player.draw(1)
                if power.power_name == "Juggernaut" and block > 0:
                    # This is wrong it needs to be random but we cant simulate the game's randomness
                    for each_monster in simulated_state.monsters:
                        each_monster.current_hp = (
                            each_monster.current_hp + each_monster.block - power.amount
                        )
                        break
                if power.power_name == "Corruption":
                    if card.type == "SKILL":
                        card.exhausts = True
                        card.cost = 0
                if power.power_name == "Evolve":
                    for card in simulated_state.hand:
                        if card.type == "STATUS":
                            simulated_state.player.draw(power.amount)
                if power.power_name == "Flame Barrier":
                    for attacking_monsters in simulated_state.monsters:
                        if attacking_monsters.move_adjusted_damage > 0:
                            damage += power.amount
                            attacking_monsters.block -= damage

                            if attacking_monsters.block < 0:
                                attacking_monsters.current_hp += (
                                    attacking_monsters.block
                                )
                                attacking_monsters.block = 0
                if power.power_name == "Rupture":
                    for temp_power in simulated_state.player.powers:
                        if temp_power.power_name == "Brutality":
                            simulated_state.player.add_buff("Strength", power.amount)
                    if "lose_hp" in card_values:
                        simulated_state.player.add_buff("Strength", power.amount)

            # Other effects (vulnerable, weak, strength, etc.)
            if "vulnerable" in card_values and simulated_state_target is not None:
                simulated_state_target.add_buff("Vulnerable", card_values["vulnerable"])
            if "weak" in card_values and simulated_state_target is not None:
                simulated_state_target.add_buff("Weak", card_values["weak"])
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
                simulated_state.player.current_hp -= card_values["lose_hp"]
            if "ethereal" in card_values:
                simulated_state.player.ethereal.append(card)
            if "exhaust" in card_values:
                simulated_state.exhaust_pile.append(card)
                apply_exhaust_effects(simulated_state)
            if "aoe" in card_values:
                for aoe_monster in simulated_state.monsters:
                    no_extra_damage = True
                    if aoe_monster.current_hp > 0 and not aoe_monster.is_gone:
                        damage += calculate_damage(card, simulated_state, aoe_monster)
                        aoe_monster.current_hp -= damage
            if "exhaust_non_attack" in card_values:
                block = 0
                for card in simulated_state.hand:
                    if card.type != "ATTACK":
                        simulated_state.hand.remove(card)
                        simulated_state.exhaust_pile.append(card)
                        block += card_values["block_per_exhaust"]
                        if block > 0:
                            block += current_dexterity
                            if is_frail:
                                block = int(block * 0.75)  # Frail reduces block by 25%
                            simulated_state.player.block += block
                        apply_exhaust_effects(simulated_state)
            if "play_top_discard" in card_values:
                if simulated_state.discard_pile:
                    top_card = simulated_state.discard_pile.pop()
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
            if "multiple_hits" in card_values:
                hits = card_values["multiple_hits"]
                for _ in range(hits):
                    if simulated_state_target is not None:
                        if (
                            simulated_state_target.current_hp > 0
                            and not simulated_state_target.is_gone
                        ):
                            no_extra_damage = True
                            damage += calculate_damage(
                                card, simulated_state, simulated_state_target
                            )
                            simulated_state_target.current_hp -= damage
            if "exhaust_hand" in card_values:
                simulated_state.exhaust_pile.extend(simulated_state.hand)
                if "multiple_hits" in card_values:
                    card_values["multiple_hits"] = len(simulated_state.hand)
                for card in simulated_state.hand:
                    apply_exhaust_effects(simulated_state)
                simulated_state.hand.clear()
            if "heal_on_damage" in card_values:
                simulated_state.player.current_hp = max(
                    card_values["damage"] + simulated_state.player.current_hp,
                    simulated_state.player.max_hp,
                )
            if "block_on_attack" in card_values:
                block = card_values["block_on_attack"]
                simulated_state.player.block += block
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
                    card_type="STATUS",
                    rarity="COMMON",
                    cost=-1,
                    is_playable=False,
                )
                simulated_state.draw_pile.append(burn_card)
            if "add_wounds_to_hand" in card_values:
                wound_card = Card(
                    card_id="Wound",
                    name="Wound",
                    card_type="STATUS",
                    rarity="COMMON",
                    cost=-2,
                    is_playable=False,
                )
                simulated_state.hand.append(wound_card)
                simulated_state.hand.append(wound_card)
            if "sword_boomerang_handle" in card_values:
                damage += (
                    calculate_damage(card, simulated_state, simulated_state_target)
                    * card_values["hits"]
                )
                no_extra_damage = True
            if "weak_aoe" in card_values:
                for monster in simulated_state.monsters:
                    monster.add_buff("Weak", card_values["weak_aoe"])
            if "vulnerable_aoe" in card_values:
                for monster in simulated_state.monsters:
                    monster.add_buff("Vulnerable", card_values["vulnerable_aoe"])
            if "whirlwind_handle" in card_values:
                energy = simulated_state.player.energy
                while energy > 0:
                    energy -= 1
                    for aoe_monster in simulated_state.monsters:
                        if aoe_monster.current_hp > 0 and aoe_monster.is_gone == False:
                            damage += calculate_damage(
                                card, simulated_state, aoe_monster
                            )
                            aoe_monster.current_hp -= damage
                simulated_state.player.energy = 0
                no_extra_damage = True

            if (
                no_extra_damage == False
                and simulated_state_target is not None
                and simulated_state_target.current_hp > 0
                and not simulated_state_target.is_gone
            ):
                # Calc damage to deal to target
                damage += calculate_damage(
                    card, simulated_state, simulated_state_target
                )
                simulated_state_target.current_hp -= damage
                simulated_state_target, simulated_state = handle_enemy_powers(
                    simulated_state_target, card, damage, simulated_state
                )

            simulated_state.damage_dealt += damage

            simulated_state.player.energy -= max(0, card.cost)

            return simulated_state
        except Exception as e:
            logging.info(f"Error simulating card play: {e}")
            raise

    def evaluate_state(self, game_state):

        eval = 0
        all_monsters_dead = True
        fighting_gremlin = False

        points = game_state.cards_drawn_this_turn * 20
        eval += points
        # logging.info(
        #     f"Adding {points} points for cards drawn this turn ({game_state.cards_drawn_this_turn} cards)"
        # )

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

        eval += strength * 600
        eval += dexterity * 200
        eval -= vulnerable * 500

        for monster in game_state.monsters:
            if monster.current_hp <= 0 or monster.is_gone == True:
                eval += 700  # Reward for killing an enemy
                # logging.info(
                #     f"Adding 700 points for defeating monster ({monster.name})"
                # )
            else:
                if monster.name == "Gremlin Nob" or monster.monster_id == "GremlinNob":
                    fighting_gremlin = True

                # Monster Positive buffs
                monster_strength = next(
                    (
                        buff.amount
                        for buff in monster.powers
                        if buff.power_id == "Strength"
                    ),
                    0,
                )

                # Monster Negative debuffs
                monster_weakened = next(
                    (
                        debuff.amount
                        for debuff in monster.powers
                        if debuff.power_id == "Weakened"
                    ),
                    0,
                )
                monster_vulnerable = next(
                    (
                        debuff.amount
                        for debuff in monster.powers
                        if debuff.power_id == "Vulnerable"
                    ),
                    0,
                )

                points = monster_strength * 150
                eval -= points
                # logging.info(
                #     f"Subtracting {points} points for monster's Strength ({monster_strength})"
                # )

                points = monster_weakened * 225
                eval += points
                # logging.info(
                #     f"Adding {points} points for monster being Weakened ({monster_weakened})"
                # )

                points = monster_vulnerable * 450
                eval += points
                # logging.info(
                #     f"Adding {points} points for monster being Vulnerable ({monster_vulnerable})"
                # )

                damage_dealt = game_state.damage_dealt * 4
                eval += damage_dealt
                # logging.info(f"Adding {damage_dealt} points for damage dealt")

                all_monsters_dead = False

        incoming_damage = self.get_incoming_damage(game_state)

        # Winning the fight
        if all_monsters_dead == True:
            return float("inf")
        else:
            game_state.player.current_hp -= max(0, incoming_damage)

            if game_state.player.current_hp <= 0:
                return float("-inf")  # Strongly penalize if the player is dead

            points = game_state.player.current_hp * 50
            eval += points
            # logging.info(
            #     f"Adding {points} points for player's current HP ({game_state.player.current_hp} HP)"
            # )

        if incoming_damage > 2 and not fighting_gremlin:
            points = incoming_damage * 3
            eval -= points
            # logging.info(
            #     f"Subtracting {points} points for incoming damage ({incoming_damage} damage)"
            # )
        elif incoming_damage < -10 and not fighting_gremlin:
            points = (abs(incoming_damage) - 10) * 2
            eval -= points
            # logging.info(
            #     f"Subtracting {points} points for overblocking ({incoming_damage})"
            # )

        # Reward for exhausting Curses but penalize exhausting good cards
        for card in game_state.exhaust_pile:
            if card.type in ["STATUS", "CURSE"]:
                eval += 10
            else:
                if card.card_id == "Feed" and not self.feed_effect_used:
                    eval -= 6000
                elif card.card_id == "Feed" and self.feed_effect_used:
                    eval += 10000

        # Penalty for status and curse cards in hand, discard pile, and draw pile
        count_status_curse_cards = sum(
            1
            for card in game_state.hand + game_state.discard_pile + game_state.draw_pile
            if card.type in ["STATUS", "CURSE"]
        )
        eval -= 40 * count_status_curse_cards

        for power in self.game.player.powers:
            if power.power_name in [
                "Demon Form",
                "Corruption",
                "Juggernaut",
                "Dark Embrace",
                "Feel No Pain",
                "Barricade",
            ]:
                eval += 500

        for card in game_state.played_cards:
            if fighting_gremlin and card.type == "SKILL":
                eval -= 2000

        # logging.info(f"total eval: {eval}, card: {card.name}")
        return eval

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

        def get_archetype(deck):
            archetype_counts = {arch: 0 for arch in ironclad_archetypes.keys()}
            for card in deck:
                for archetype, cards in ironclad_archetypes.items():
                    if card.card_id in cards["key_cards"]:
                        archetype_counts[archetype] += 1
            dominant_archetype = max(archetype_counts, key=archetype_counts.get)
            return {dominant_archetype: ironclad_archetypes[dominant_archetype]}

        def best_option_from_action(option):
            number_of_options = len(self.game.screen.options) - 1
            if option > number_of_options:
                return ChooseAction(number_of_options)
            else:
                return ChooseAction(option)

        def choose_rest_option(game_state):
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

            def generate_map_route(priorities, map_route):
                node_rewards = priorities.MAP_NODE_PRIORITIES.get(game_state.act)
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
                best_path = [0] * (map_height + 1)
                best_path[map_height] = max(
                    best_rewards[map_height].keys(),
                    key=lambda x: best_rewards[map_height][x],
                )
                for y in range(map_height, 0, -1):
                    best_path[y - 1] = best_parents[y][best_path[y]]
                map_route[:] = best_path

            if (
                len(game_state.screen.next_nodes) > 0
                and game_state.screen.next_nodes[0].y == 0
            ):
                generate_map_route(priorities, map_route)
                game_state.screen.current_node.y = -1
            if game_state.screen.boss_available:
                return ChooseMapBossAction()
            chosen_x = map_route[game_state.screen.current_node.y + 1]
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
            num_cards = min(self.game.screen.num_cards, 5)
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