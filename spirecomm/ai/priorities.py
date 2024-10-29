from card_dictionary import ironclad_archetypes


class Priority:
    MAX_COPIES = {}
    BOSS_RELIC_PRIORITY_LIST = []
    MAP_NODE_PRIORITIES_1 = {"R": 300, "E": 500, "$": 100, "?": 200, "M": 700, "T": 0}
    MAP_NODE_PRIORITIES_2 = {"R": 400, "E": 100, "$": 500, "?": 700, "M": 500, "T": 0}
    MAP_NODE_PRIORITIES_3 = {"R": 400, "E": 500, "$": 400, "?": 700, "M": 600, "T": 0}

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

    def get_sorted_cards(self, card_list, game_state, reverse=False):
        return sorted(
            card_list,
            key=lambda card: self.evaluate_card_synergy(
                card, game_state.deck, ironclad_archetypes
            ),
            reverse=reverse,
        )

    def should_skip(self, game, archetype, card):
        # Extract the key from the dictionary
        archetype_key = list(archetype.keys())[0]
        archetype_dict = {archetype_key: ironclad_archetypes[archetype_key]}
        card_synergy = self.evaluate_card_synergy(card, game.deck, archetype_dict)
        return card_synergy < 10

    def needs_more_copies(self, card, num_copies):
        return self.MAX_COPIES.get(card.card_id, 0) > num_copies

    def get_best_boss_relic(self, relic_list):
        return min(
            relic_list,
            key=lambda x: self.BOSS_RELIC_PRIORITIES.get(x.relic_id, float("inf")),
        )

    def get_cards_for_action(self, cards, max_cards, gamestate):
        sorted_cards = self.get_sorted_cards(cards, gamestate, reverse=False)
        num_cards = min(max_cards, len(cards))
        return sorted_cards[:num_cards]

    def evaluate_card_synergy(self, card, deck, archetypes):
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
        if card_name in ["Barricade", "Corruption", "Demon Form", "Fiend Fire", "Immolate", "Impervious","Juggernaut", "Offering", "Reaper"]:
            synergy_score += 100  # Rare cards that are a must take
        if card_name in archetypes[dominant_archetype]["key_cards"]:
            synergy_score += 15  # High priority for key cards
        if card_name in archetypes[dominant_archetype]["support_cards"]:
            synergy_score += 10  # Medium priority for support cards

        # Add some logic for overlapping cards that fit into multiple builds
        for archetype, cards in archetypes.items():
            if card_name in cards["key_cards"] or card_name in cards["support_cards"]:
                if archetype != dominant_archetype:
                    synergy_score += 5  # Lower priority for multi-build cards

        if card_name in ["Defend_R", "Strike_R"]:
            synergy_score -= 50  # Penalty for basic cards

        return synergy_score


class IroncladPriority(Priority):
    MAX_COPIES = {
        "Limit Break": 1,
        "Barricade": 1,
        "Demon Form": 1,
        "Feed": 1,
        "Juggernaut": 1,
        "Offering": 2,
        "Immolate": 1,
        "Bludgeon": 1,
        "Fiend Fire": 1,
        "Reaper": 1,
        "Impervious": 2,
        "Exhume": 1,
        "Whirlwind": 1,
        "Berserk": 1,
        "Double Tap": 0,        
        "Dark Embrace": 1,
        "Brutality": 0,
        "Feel No Pain": 2,
        "Shrug It Off": 2,
        "Metallicize": 0,
        "Disarm": 2,
        "Shockwave": 1,
        "Entrench": 0,
        "Inflame": 1,
        "Battle Trance": 1,
        "Armaments": 1,
        "Uppercut": 1,
        "Carnage": 1,
        "Ghostly Armor": 0,
        "Pummel": 1,
        "Pommel Strike": 2,
        "Dropkick": 0,
        "Flex": 1,
        "Twin Strike": 0,
        "True Grit": 1,
        "Wild Strike": 0,
        "Clothesline": 0,
        "Thunderclap": 0,
        "Anger": 1,
        "Body Slam": 0,
        "Headbutt": 0,
        "Sword Boomerang": 1,
        "Rampage": 1,
        "Blood for Blood": 1,
        "Perfected Strike": -100,  # dont pick this card.
        "Cleave": 1,
        "Sever Soul": 0,
        "Rupture": 0,
        "Evolve": 0,
        "Fire Breathing": 0,
        "Combust": 0,
        "Hemokinesis": 1,
        "Warcry": 0,
        "Intimidate": 0,
        "Second Wind": 1,
        "Burning Pact":0,
        "Seeing Red": 0,
        "Iron Wave": 1,
        "Spot Weakness": 0,
        "Havoc": 0,
        "Searing Blow": 0,
        "Heavy Blade": 0,
        "Bloodletting": 0,
        "Flame Barrier": 1,
        "Dual Wield": 0,
        "Power Through": 1,
        "Sentinel": 0,
        "Rage": 0,
    }

    BOSS_RELIC_PRIORITY_LIST = [
        "Sozu",
        "Philosopher's Stone",
        "Mark of Pain",
        "Calling Bell",
        "Cursed Key",
        "Runic Pyramid",
        "Pandora's Box",
        "Busted Crown",
        "Empty Cage",
        "Astrolabe",
        "Runic Cube",
        "Snecko Eye",
        "Slaver's Collar",
        "Ectoplasm",
        "Fusion Hammer",
        "Tiny House",
        "Sacred Bark",
        "Coffee Dripper",
        "Black Blood",
        "Velvet Choker",
        "Runic Dome",
    ]

    def __init__(self):
        super().__init__()
