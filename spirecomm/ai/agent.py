import itertools
from anytree import Node, RenderTree, LevelOrderGroupIter
import copy
from card_dictionary import get_card_values
from spirecomm.spire.game import Game
from spirecomm.spire.character import Intent, PlayerClass
import spirecomm.spire.card
from spirecomm.spire.screen import RestOption
from spirecomm.communication.action import *
from spirecomm.ai.priorities import IroncladPriority


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

    def evaluate_card_playability(self, game_state, card):
        score = 0
        card_values = get_card_values(card.name)

        # Apply buffs and debuffs
        strength = next(
            (
                power.amount
                for power in game_state.player.powers
                if power.power_id == "Strength"
            ),
            0,
        )
        dexterity = next(
            (
                power.amount
                for power in game_state.player.powers
                if power.power_id == "Dexterity"
            ),
            0,
        )
        vulnerable = next(
            (
                power.amount
                for power in game_state.player.powers
                if power.power_id == "Vulnerable"
            ),
            0,
        )
        weak = next(
            (
                power.amount
                for power in game_state.player.powers
                if power.power_id == "Weak"
            ),
            0,
        )

        # Adjust damage and block values
        adjusted_damage = card_values["damage"] + strength
        adjusted_block = card_values["block"] + dexterity

        if "vulnerable" in card_values:
            adjusted_damage = int(
                adjusted_damage * 1.5
            )  # Vulnerable increases damage taken by 50%

        if weak:
            adjusted_damage = int(adjusted_damage * 0.75)  # Weak reduces damage by 25%

        score += adjusted_damage
        score += adjusted_block

        # Check opponent intents
        for monster in game_state.monsters:
            if monster.intent == Intent.ATTACK:
                if card_values["block"] > 0:
                    score += 20 + adjusted_block
            elif monster.intent in [Intent.BUFF, Intent.DEBUFF]:
                if card_values["damage"] > 0:
                    score += 20 + adjusted_damage

        # Prioritize cards with status effects
        status_effects = [
            "vulnerable",
            "weak",
            "strength",
            "draw",
            "gain_energy",
            "lose_hp",
            "reduce_strength",
            "ethereal",
            "multiple_hits",
            "aoe",
            "based_on_block",
            "create_copy",
            "double_block",
            "exhaust",
            "exhaust_hand",
            "exhaust_random_card",
            "exhaust_non_attack",
            "exhaust_top_card",
            "increase_damage_per_play",
            "play_top_discard",
            "put_card_on_top_of_deck",
            "random_targets",
            "strength_multiplier",
            "variable_cost",
            "block_on_attack",
            "damage_on_attack",
            "gain_block_on_exhaust",
            "gain_strength_on_hp_loss",
            "skills_cost_zero",
            "create_random_attack",
            "double_strength",
            "draw_on_exhaust",
            "draw_on_status",
            "damage_per_turn",
            "aoe_damage_on_status_draw",
            "damage_on_block",
            "gain_energy_on_exhaust",
            "lose_hp_per_turn",
        ]

        if any(effect in card_values for effect in status_effects):
            score += 15

        return score


def eval_function(gamestate):
    eval = 0
    player = gamestate.player

    # Basic metrics
    eval += player.current_hp
    if player.current_hp < 1:
        eval -= 200
    eval += gamestate.gold

    # Enemy metrics
    if not gamestate.monsters:
        eval += 200
    else:
        for m in gamestate.monsters:
            if m.current_hp < 0:
                m.current_hp = 0
            eval -= m.current_hp
            eval -= m.move_adjusted_damage * m.move_hits

            for mpower in player.powers:
                eval -= get_power_penalty(mpower)

    for ppower in player.powers:
        eval += get_power_value(ppower)

    eval += player.block

    return eval


def get_power_value(power):
    values = {
        "Strength": 10,
        "Dexterity": 10,
        "Weakened": -10,
        "Vulnerable": -10,
        "Rage": 5,
        "Double Tap": 20,
        "Flame Barrier": 15,
        "Juggernaut": 20,
        "Dark Embrace": 20,
        "Feel No Pain": 10,
        "Sentinel": 5,
        "No Draw": -10,
        "Evolve": 15,
        "Fire Breathing": 10,
        "Combust": 15,
        "Rupture": 10,
        "Flex": 10,
        "Metallicize": 10,
        "Poison": -5,
        "Energized": 20,
        "Barricade": 25,
        "Demon Form": 30,
        "Brutality": 10,
    }
    return values.get(power.power_name, 0)


def get_power_penalty(power):
    penalties = {
        "Strength": -10,
        "Weakened": 5,
        "Vulnerable": 5,
        "Rage": -5,
        "Double Tap": -20,
        "Flame Barrier": -15,
        "Dexterity": -10,
        "Juggernaut": -20,
        "Dark Embrace": -20,
        "Feel No Pain": -10,
        "Sentinel": -5,
        "No Draw": 10,
        "Evolve": -15,
        "Fire Breathing": -10,
        "Combust": -15,
        "Rupture": -10,
        "Flex": -10,
        "Metallicize": -10,
        "Poison": 5,
        "Energized": -20,
        "Barricade": -25,
        "Demon Form": -30,
        "Brutality": -10,
    }
    return penalties.get(power.power_name, 0)


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
        if isinstance(target, list):
            for t in target:
                next_state.monsters[t].current_hp -= damage
        else:
            next_state.monsters[target].current_hp -= damage

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
        next_state.player.add_buff("strength", strength)

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


def minimax(node, depth, is_maximizing, alpha=float("-inf"), beta=float("inf")):
    if depth == 0 or not node.children:
        node.name.grade = eval_function(node.name)
        return node.name.grade

    if is_maximizing:
        max_eval = float("-inf")
        for child in node.children:
            eval = minimax(child, depth - 1, False, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        node.name.grade = max_eval
        return max_eval
    else:
        min_eval = float("inf")
        for child in node.children:
            eval = minimax(child, depth - 1, True, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        node.name.grade = min_eval
        return min_eval


def build_tree(gamestate, depth=3):
    if (
        depth == 0
        or not gamestate.name.monsters
        or gamestate.name.player.current_hp <= 0
    ):
        return

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
                card = c.name
                card_values = get_card_values(card)
                if card_values is None:
                    continue

                if not card_values.get("multi_target"):
                    index = card_values["effect"](gamestate, 0, c.upgrades)
                    p = c
                    next_state = copy.deepcopy(gamestate.name)
                    next_state.hand.remove(c)
                    next_state.player.energy -= p.cost
                    for i in index:
                        next_state = get_next_game_state(p, next_state, i)
                        child = Node(next_state, parent=gamestate)
                        build_tree(child, depth - 1)

                elif card_values.get("multi_target"):
                    p = c
                    next_state = copy.deepcopy(gamestate.name)
                    next_state.hand.remove(c)
                    next_state.player.energy -= p.cost
                    for monsterindex in range(len(next_state.monsters)):
                        if not next_state.monsters[monsterindex].is_gone:
                            next_state = get_next_game_state(
                                p, next_state, monsterindex
                            )
                            child = Node(next_state, parent=gamestate)
                            build_tree(child, depth - 1)

                else:
                    p = c
                    next_state = copy.deepcopy(gamestate.name)
                    next_state.hand.remove(c)
                    next_state.player.energy -= p.cost
                    next_state = get_next_game_state(p, next_state, -1)
                    child = Node(next_state, parent=gamestate)
                    build_tree(child, depth - 1)

    next_state = get_next_game_state("End_Turn", copy.deepcopy(gamestate.name), -1)
    child = Node(next_state, parent=gamestate)
    build_tree(child, depth - 1)


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


ironclad_archetypes = {
    "strength": {
        "key_cards": [
            "Flex",
            "Limit Break",
            "Spot Weakness",
            "Inflame",
            "Demon Form",
            "Heavy Blade",
            "Whirlwind",
        ],
        "support_cards": [
            "Pommel Strike",
            "Clothesline",
            "Anger",
            "Uppercut",
            "Berserk",
        ],
    },
    "block": {
        "key_cards": ["Barricade", "Entrench", "Body Slam", "Juggernaut", "Impervious"],
        "support_cards": [
            "Shrug It Off",
            "Iron Wave",
            "True Grit",
            "Feel No Pain",
            "Ghostly Armor",
            "Power Through",
        ],
    },
    "exhaust": {
        "key_cards": [
            "Feel No Pain",
            "Dark Embrace",
            "Evolve",
            "Corruption",
            "Second Wind",
        ],
        "support_cards": [
            "Infernal Blade",
            "Fiend Fire",
            "Shrug It Off",
            "True Grit",
            "Warcry",
        ],
    },
    "dot": {
        "key_cards": ["Rupture", "Combust", "Hemokinesis", "Bloodletting", "Brutality"],
        "support_cards": [
            "Reaper",
            "Blood for Blood",
            "Whirlwind",
            "Anger",
            "Carnage",
            "Immolate",
        ],
    },
    "energy": {
        "key_cards": [
            "Double Tap",
            "Offering",
            "Battle Trance",
            "Berserk",
            "Infernal Blade",
        ],
        "support_cards": [
            "Anger",
            "Pommel Strike",
            "Rampage",
            "Headbutt",
            "Wild Strike",
        ],
    },
}

ironclad_relic_values = {
    "Bag of Marbles": 10,
    "Champion Belt": 10,
    "Charon's Ashes": 15,
    "Paper Frog": 20,
    "Self-Forming Clay": 15,
    "Stone Calendar": 10,
    "Calipers": 20,
    "Incense Burner": 15,
    "Magic Flower": 10,
    "Nunchaku": 10,
    "Oddly Smooth Stone": 10,
    "Red Skull": 15,
    "Shuriken": 20,
    "Singing Bowl": 10,
    "Strawberry": 10,
    "Thread and Needle": 15,
    "Toy Ornithopter": 10,
    "Vajra": 20,
    "Whetstone": 10,
}


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

    return synergy_score


def evaluate_card_in_shop(card, deck, archetypes):
    return evaluate_card_synergy(card, deck, archetypes) + get_card_values(
        card.card_id
    ).get("value", 0)


def evaluate_relic_in_shop(relic):
    return ironclad_relic_values.get(relic.relic_id, 0)


def evaluate_card_removal(card, deck, archetypes):
    if card.card_id in ["Strike_R", "Defend_R"]:
        return 15  # High priority to remove basic cards
    return -evaluate_card_synergy(
        card, deck, archetypes
    )  # Remove cards that do not fit the archetype


def evaluate_kill_potential(game_state, card, target_monster):
    simulated_state = getstate(game_state)
    target_index = game_state.monsters.index(target_monster)
    next_state = get_next_game_state(card, simulated_state, target_index)
    return next_state.monsters[target_index].current_hp <= 0


def can_kill_any_monster(game_state):
    for card in game_state.hand:
        if card.is_playable:
            for idx, monster in enumerate(game_state.monsters):
                if monster.current_hp > 0 and evaluate_kill_potential(
                    game_state, card, idx
                ):
                    return PlayCardAction(card=card, target_monster=monster)
    return None


def evaluate_lethal_combinations(game_state):
    playable_cards = [card for card in game_state.hand if card.is_playable]
    max_combination_length = (
        4  # Limiting the length of combinations to make it more efficient
    )

    for r in range(1, max_combination_length + 1):
        for card_combination in itertools.combinations(playable_cards, r):
            simulated_state = getstate(game_state)
            for card in card_combination:
                target = None
                if card.has_target:
                    target = (
                        get_lowest_hp_target(simulated_state)
                        if get_card_values(card.name).get("damage", 0) > 0
                        else get_highest_hp_target(simulated_state)
                    )
                if target is None and card.has_target:
                    continue  # Skip this combination if a target is required but not available
                simulated_state = get_next_game_state(card, simulated_state, target)
            if all(monster.current_hp <= 0 for monster in simulated_state.monsters):
                return card_combination
    return None


def get_incoming_damage(game_state):
    incoming_damage = 0
    for monster in game_state.monsters:
        if not monster.is_gone and not monster.half_dead:
            if monster.move_adjusted_damage is not None:
                incoming_damage += monster.move_adjusted_damage * monster.move_hits
            elif monster.intent == Intent.NONE:
                incoming_damage += 5 * game_state.act
    return incoming_damage


def simulate_defense_value(game_state):
    total_block = sum(get_card_values(card.name)["block"] for card in game_state.hand)
    return total_block


def get_lowest_hp_target(game_state):
    valid_targets = [
        monster
        for monster in game_state.monsters
        if monster.current_hp > 0 and not monster.half_dead and not monster.is_gone
    ]
    if not valid_targets:
        return None
    return min(valid_targets, key=lambda x: x.current_hp)


def get_highest_hp_target(game_state):
    valid_targets = [
        monster
        for monster in game_state.monsters
        if monster.current_hp > 0 and not monster.half_dead and not monster.is_gone
    ]
    if not valid_targets:
        return None
    return max(valid_targets, key=lambda x: x.current_hp)


def prioritize_cards(cards, priority_obj):
    return priority_obj.get_sorted_cards_to_play(cards)


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
        raise Exception(error)

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
        if not available_monsters:
            return None
        return min(available_monsters, key=lambda x: x.current_hp)

    def get_high_hp_target(self):
        available_monsters = [
            monster
            for monster in self.game.monsters
            if monster.current_hp > 0 and not monster.half_dead and not monster.is_gone
        ]
        if not available_monsters:
            return None
        return max(available_monsters, key=lambda x: x.current_hp)

    def evaluate_card_playability(self, game_state, card):
        score = 0
        card_values = get_card_values(card.name)

        # Apply buffs and debuffs
        strength = next(
            (
                power.amount
                for power in game_state.player.powers
                if power.power_id == "Strength"
            ),
            0,
        )
        dexterity = next(
            (
                power.amount
                for power in game_state.player.powers
                if power.power_id == "Dexterity"
            ),
            0,
        )
        vulnerable = next(
            (
                power.amount
                for power in game_state.player.powers
                if power.power_id == "Vulnerable"
            ),
            0,
        )
        weak = next(
            (
                power.amount
                for power in game_state.player.powers
                if power.power_id == "Weak"
            ),
            0,
        )

        # Adjust damage and block values
        adjusted_damage = card_values.get("damage", 0) + strength
        adjusted_block = card_values.get("block", 0) + dexterity

        if vulnerable:
            adjusted_damage = int(
                adjusted_damage * 1.5
            )  # Vulnerable increases damage taken by 50%

        if weak:
            adjusted_damage = int(adjusted_damage * 0.75)  # Weak reduces damage by 25%

        score += adjusted_damage
        score += adjusted_block

        # Check opponent intents
        for monster in game_state.monsters:
            if monster.intent == Intent.ATTACK:
                if card_values.get("block", 0) > 0:
                    score += 20 + adjusted_block
            elif monster.intent in [Intent.BUFF, Intent.DEBUFF]:
                if card_values.get("damage", 0) > 0:
                    score += 20 + adjusted_damage

        # Prioritize cards with status effects
        status_effects = [
            "vulnerable",
            "weak",
            "strength",
            "draw",
            "gain_energy",
            "lose_hp",
            "reduce_strength",
            "ethereal",
            "multiple_hits",
            "aoe",
            "based_on_block",
            "create_copy",
            "double_block",
            "exhaust",
            "exhaust_hand",
            "exhaust_random_card",
            "exhaust_non_attack",
            "exhaust_top_card",
            "increase_damage_per_play",
            "play_top_discard",
            "put_card_on_top_of_deck",
            "random_targets",
            "strength_multiplier",
            "variable_cost",
            "block_on_attack",
            "damage_on_attack",
            "gain_block_on_exhaust",
            "gain_strength_on_hp_loss",
            "skills_cost_zero",
            "create_random_attack",
            "double_strength",
            "draw_on_exhaust",
            "draw_on_status",
            "damage_per_turn",
            "aoe_damage_on_status_draw",
            "damage_on_block",
            "gain_energy_on_exhaust",
            "lose_hp_per_turn",
        ]

        if any(effect in card_values for effect in status_effects):
            score += 15

        return score

    def get_play_card_action(self):
        def get_playable_cards():
            return [card for card in self.game.hand if card.is_playable]

        def evaluate_lethal():
            lethal_combination = evaluate_lethal_combinations(self.game)
            if lethal_combination:
                target = (
                    self.get_low_hp_target()
                    if lethal_combination[0].has_target
                    else None
                )
                if target is None and lethal_combination[0].has_target:
                    return None  # No valid target for lethal combination
                return PlayCardAction(card=lethal_combination[0], target_monster=target)
            return None

        playable_cards = get_playable_cards()
        if not playable_cards:
            return EndTurnAction()

        # Check for lethal
        lethal_action = evaluate_lethal()
        if lethal_action:
            return lethal_action

        incoming_damage = self.get_incoming_damage()
        defense_value = sum(
            get_card_values(card.name).get("block", 0)
            for card in self.game.hand
            if card.is_playable
        )

        # If incoming damage is high and we can't kill, prioritize defense
        if incoming_damage > 0 and defense_value >= incoming_damage:
            defensive_cards = [
                card
                for card in playable_cards
                if get_card_values(card.name).get("block", 0) > 0
            ]
            if defensive_cards:
                best_defensive_card = max(
                    defensive_cards,
                    key=lambda card: self.evaluate_card_playability(self.game, card),
                )
                if best_defensive_card.has_target:
                    target = self.get_low_hp_target()
                    if target is None:
                        return EndTurnAction()  # No valid target for the defensive card
                    return PlayCardAction(
                        card=best_defensive_card, target_monster=target
                    )
                return PlayCardAction(card=best_defensive_card)

        # If we can't fully block the incoming damage, prioritize attacks
        attack_cards = [
            card
            for card in playable_cards
            if get_card_values(card.name).get("damage", 0) > 0
        ]
        if attack_cards:
            best_attack_card = max(
                attack_cards,
                key=lambda card: self.evaluate_card_playability(self.game, card),
            )
            if best_attack_card.has_target:
                target = self.get_low_hp_target()
                if target is None:
                    return EndTurnAction()  # No valid target for the attack card
                else:
                    return PlayCardAction(card=best_attack_card, target_monster=target)
            else:
                return PlayCardAction(card=best_attack_card)

        # Use zero-cost cards if available
        zero_cost_cards = [
            card
            for card in playable_cards
            if get_card_values(card.name).get("cost", 1) == 0
        ]
        if zero_cost_cards:
            best_zero_cost_card = max(
                zero_cost_cards,
                key=lambda card: self.evaluate_card_playability(self.game, card),
            )
            if best_zero_cost_card.has_target:
                target = (
                    self.get_low_hp_target()
                    if get_card_values(best_zero_cost_card.name).get("damage", 0) > 0
                    else self.get_high_hp_target()
                )
                if target is None:
                    return EndTurnAction()  # No valid target for the zero-cost card
                else:
                    return PlayCardAction(
                        card=best_zero_cost_card, target_monster=target
                    )
            else:
                return PlayCardAction(card=best_zero_cost_card)

        # Use non-zero cost cards based on priority
        best_card = max(
            playable_cards,
            key=lambda card: self.evaluate_card_playability(self.game, card),
        )
        if best_card.has_target:
            target = (
                self.get_low_hp_target()
                if get_card_values(best_card.name).get("damage", 0) > 0
                else self.get_high_hp_target()
            )
            if target is None:
                return EndTurnAction()  # No valid target for the non-zero cost card
            return PlayCardAction(card=best_card, target_monster=target)
        else:
            return PlayCardAction(card=best_card)

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
                #return self.choose_upgrade()
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

    def choose_upgrade(self):
        upgradeable_cards = [card for card in self.game.deck if not card.upgrades]
        if not upgradeable_cards:
            return RestAction(RestOption.REST)

        # Prioritize upgrading key cards from the dominant archetype
        archetype_scores = {arch: 0 for arch in ironclad_archetypes}
        for deck_card in self.game.deck:
            for archetype, cards in ironclad_archetypes.items():
                if (
                    deck_card.card_id in cards["key_cards"]
                    or deck_card.card_id in cards["support_cards"]
                ):
                    archetype_scores[archetype] += 1
        dominant_archetype = max(archetype_scores, key=archetype_scores.get)

        best_card_to_upgrade = max(
            upgradeable_cards,
            key=lambda card: evaluate_card_synergy(
                card, self.game.deck, ironclad_archetypes
            ),
        )
        return RestAction(RestOption.SMITH, best_card_to_upgrade)

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
            # Evaluate each card based on synergy with the current deck
            best_card = max(
                pickable_cards,
                key=lambda card: evaluate_card_synergy(
                    card, self.game.deck, ironclad_archetypes
                ),
            )
            return CardRewardAction(best_card)
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
