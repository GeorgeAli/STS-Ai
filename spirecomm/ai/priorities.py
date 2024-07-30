import math
from card_dictionary import get_card_values, ironclad_archetypes


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


def evaluate_card_utility(card, game_state):
    card_values = get_card_values(card.card_id)
    utility_score = 0

    # Consider immediate utility based on the game state
    if "gain_strength_if_attack_intent" in card_values:
        if any(monster.intent.is_attack() for monster in game_state.monsters):
            utility_score += 10
    if (
        "draw_if_vulnerable" in card_values
        or "gain_energy_if_vulnerable" in card_values
    ):
        if any(monster.has_debuff("vulnerable") for monster in game_state.monsters):
            utility_score += 10
    # Add more conditions as needed...

    return utility_score


def evaluate_card_value(card):
    # Base value for the card
    base_value = get_card_values(card.card_id).get("value", 0)
    return base_value


class Priority:
    AOE_CARDS = []
    MAX_COPIES = {}
    BOSS_RELIC_PRIORITY_LIST = []
    MAP_NODE_PRIORITIES_1 = {"R": 1000, "E": 10, "$": 100, "?": 100, "M": 1, "T": 0}
    MAP_NODE_PRIORITIES_2 = {"R": 1000, "E": 100, "$": 10, "?": 10, "M": 1, "T": 0}
    MAP_NODE_PRIORITIES_3 = {"R": 1000, "E": 1, "$": 100, "?": 100, "M": 10, "T": 0}

    GOOD_CARD_ACTIONS = [
        "PutOnDeckAction",
        "ArmamentsAction",
        "DualWieldAction",
        "NightmareAction",
        "RetainCardsAction",
        "SetupAction",
    ]

    BAD_CARD_ACTIONS = [
        "DiscardAction",
        "ExhaustAction",
        "PutOnBottomOfDeckAction",
        "RecycleAction",
        "ForethoughtAction",
        "GamblingChipAction",
    ]

    def __init__(self):
        self.BOSS_RELIC_PRIORITIES = {
            self.BOSS_RELIC_PRIORITY_LIST[i]: i
            for i in range(len(self.BOSS_RELIC_PRIORITY_LIST))
        }
        self.MAP_NODE_PRIORITIES = {
            1: self.MAP_NODE_PRIORITIES_1,
            2: self.MAP_NODE_PRIORITIES_2,
            3: self.MAP_NODE_PRIORITIES_3,
            4: self.MAP_NODE_PRIORITIES_3,
        }

    def get_best_card(self, card_list, game_state):
        return max(card_list, key=lambda card: self.evaluate_card(card, game_state))

    def get_worst_card(self, card_list, game_state):
        return min(card_list, key=lambda card: self.evaluate_card(card, game_state))

    def get_sorted_cards(self, card_list, game_state, reverse=False):
        return sorted(
            card_list,
            key=lambda card: self.evaluate_card(card, game_state),
            reverse=reverse,
        )

    def evaluate_card(self, card, game_state):
        deck = game_state.deck
        archetypes = ironclad_archetypes

        synergy_score = evaluate_card_synergy(card, deck, archetypes)
        utility_score = evaluate_card_utility(card, game_state)
        base_value = evaluate_card_value(card)

        # Combine scores
        total_score = synergy_score + utility_score + base_value
        return total_score

    def should_skip(self, game, archetype, card):
        # Extract the key from the dictionary
        archetype_key = list(archetype.keys())[0]
        archetype_dict = {archetype_key: ironclad_archetypes[archetype_key]}
        card_synergy = evaluate_card_synergy(card, game.deck, archetype_dict)
        return card_synergy < 5

    def needs_more_copies(self, card, num_copies):
        return self.MAX_COPIES.get(card.card_id, 0) > num_copies

    def get_best_boss_relic(self, relic_list):
        return min(
            relic_list, key=lambda x: self.BOSS_RELIC_PRIORITIES.get(x.relic_id, 0)
        )

    def is_card_aoe(self, card):
        return card.card_id in self.AOE_CARDS

    def is_card_defensive(self, card):
        card_values = get_card_values(card.name)
        return card_values["block"] > 0

    def get_cards_for_action(self, action, cards, max_cards, gamestate):
        if action in self.GOOD_CARD_ACTIONS:
            sorted_cards = self.get_sorted_cards(cards, gamestate, reverse=False)
        else:
            sorted_cards = self.get_sorted_cards(cards, gamestate, reverse=True)
        num_cards = min(max_cards, len(cards))
        return sorted_cards[:num_cards]


class IroncladPriority(Priority):

    AOE_CARDS = [
        "Whirlwind",
        "Immolate",
        "Cleave",
        "Thunderclap",
        "Shockwave",
    ]

    MAX_COPIES = {
        "Limit Break": 1,
        "Barricade": 1,
        "Demon Form": 1,
        "Feed": 1,
        "Juggernaut": 1,
        "Offering": 2,
        "Immolate": 1,
        "Bludgeon": 0,
        "Fiend Fire": 1,
        "Reaper": 1,
        "Impervious": 2,
        "Exhume": 1,
        "Whirlwind": 1,
        "Berserk": 1,
        "Double Tap": 1,
        "Bludgeon": 1,
        "Dark Embrace": 1,
        "Brutality": 0,
        "Feel No Pain": 2,
        "Shrug It Off": 2,
        "Metallicize": 1,
        "Disarm": 2,
        "Shockwave": 1,
        "Entrench": 0,
        "Inflame": 2,
        "Battle Trance": 1,
        "Armaments": 1,
        "Uppercut": 0,
        "Carnage": 1,
        "Ghostly Armor": 0,
        "Pummel": 1,
        "Pommel Strike": 2,
        "Dropkick": 1,
        "Flex": 1,
        "Twin Strike": 1,
        "True Grit": 1,
        "Wild Strike": 1,
        "Clothesline": 0,
        "Thunderclap": 1,
        "Anger": 0,
        "Body Slam": 0,
        "Headbutt": 0,
        "Sword Boomerang": 2,
        "Rampage": 1,
        "Blood for Blood": -1,
        "Perfected Strike": -1,
        "Cleave": 1,
        "Sever Soul": 0,
        "Rupture": 0,
        "Evolve": 1,
        "Fire Breathing": 1,
        "Combust": 1,
        "Hemokinesis": 1,
        "Warcry": 0,
        "Intimidate": 1,
        "Second Wind": 0,
        "Burning Pact": 0,
        "Seeing Red": 0,
        "Iron Wave": 1,
        "Spot Weakness": 0,
        "Havoc": 0,
        "Searing Blow": 0,
        "Heavy Blade": 0,
    }

    BOSS_RELIC_PRIORITY_LIST = [
        "Mark of Pain",
        "Sozu",
        "Ectoplasm",
        "Runic Dome",
        "Snecko Eye",
        "Fusion Hammer",
        "Tiny House",
        "Busted Crown",
        "Velvet Choker",
        "Cursed Key",
        "Sacred Bark",
        "Runic Cube",
        "Astrolabe",
        "Empty Cage",
        "Pandora's Box",
        "Ring of the Serpent",
        "Calling Bell",
        "Coffee Dripper",
        "Black Blood",
    ]

    def __init__(self):
        super().__init__()
