import math
from card_dictionary import get_card_values


class Priority:

    CARD_PRIORITY_LIST = []

    PLAY_PRIORITY_LIST = []

    AOE_CARDS = []

    DEFENSIVE_CARDS = []

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
        self.CARD_PRIORITIES = {
            self.CARD_PRIORITY_LIST[i]: i for i in range(len(self.CARD_PRIORITY_LIST))
        }
        self.PLAY_PRIORITIES = {
            self.PLAY_PRIORITY_LIST[i]: i for i in range(len(self.PLAY_PRIORITY_LIST))
        }
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

    def get_best_card(self, card_list):
        return min(
            card_list,
            key=lambda x: self.CARD_PRIORITIES.get(x.card_id, math.inf)
            - 0.5 * x.upgrades,
        )

    def get_worst_card(self, card_list):
        return max(
            card_list,
            key=lambda x: self.CARD_PRIORITIES.get(x.card_id, math.inf)
            - 0.5 * x.upgrades,
        )

    def get_sorted_cards(self, card_list, reverse=False):
        return sorted(
            card_list,
            key=lambda x: self.CARD_PRIORITIES.get(x.card_id, math.inf)
            - 0.5 * x.upgrades,
            reverse=reverse,
        )

    def get_sorted_cards_to_play(self, card_list, reverse=False):
        return sorted(
            card_list,
            key=lambda x: self.PLAY_PRIORITIES.get(x.card_id, math.inf)
            - 0.5 * x.upgrades,
            reverse=reverse,
        )

    def get_best_card_to_play(self, card_list):
        return min(
            card_list,
            key=lambda x: self.PLAY_PRIORITIES.get(x.card_id, math.inf)
            - 0.5 * x.upgrades,
        )

    def get_worst_card_to_play(self, card_list):
        return max(
            card_list,
            key=lambda x: self.PLAY_PRIORITIES.get(x.card_id, math.inf)
            - 0.5 * x.upgrades,
        )

    def should_skip(self, card):
        return self.CARD_PRIORITIES.get(
            card.card_id, math.inf
        ) > self.CARD_PRIORITIES.get("Skip")

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

    def get_cards_for_action(self, action, cards, max_cards):
        if action in self.GOOD_CARD_ACTIONS:
            sorted_cards = self.get_sorted_cards(cards, reverse=False)
        else:
            sorted_cards = self.get_sorted_cards(cards, reverse=True)
        num_cards = min(max_cards, len(cards))
        return sorted_cards[:num_cards]

    MAP_NODE_PRIORITIES_1 = {"R": 1000, "E": 100, "$": 10, "?": 10, "M": 1, "T": 0}

    MAP_NODE_PRIORITIES_2 = {"R": 100, "E": -1000, "$": 10, "?": 10, "M": 1, "T": 0}

    MAP_NODE_PRIORITIES_3 = {"R": 1000, "E": 10, "$": 100, "?": 100, "M": 1, "T": 0}


class IroncladPriority(Priority):
    CARD_PRIORITY_LIST = [
        "Limit Break",
        "Barricade",
        "Demon Form",
        "Feed",
        "Juggernaut",
        "Offering",
        "Immolate",
        "Bludgeon",
        "Fiend Fire",
        "Reaper",
        "Impervious",
        "Exhume",
        "Whirlwind",
        "Berserk",
        "Double Tap",
        "Dark Embrace",
        "Brutality",
        "Feel No Pain",
        "Shrug It Off",
        "Metallicize",
        "Disarm",
        "Shockwave",
        "Entrench",
        "Inflame",
        "Battle Trance",
        "Armaments",
        "Uppercut",
        "Carnage",
        "Ghostly Armor",
        "Pummel",
        "Pommel Strike",
        "Dropkick",
        "Flex",
        "Twin Strike",
        "True Grit",
        "Wild Strike",
        "Clothesline",
        "Thunderclap",        
        "Body Slam",
        "Headbutt",
        "Sword Boomerang",
        "Rampage",
        "Blood for Blood",
        "Cleave",
        "Sever Soul",
        "Rupture",
        "Evolve",
        "Fire Breathing",
        "Combust",
        "Hemokinesis",
        "Warcry",
        "Intimidate",
        "Second Wind",
        "Burning Pact",
        "Seeing Red",
        "Iron Wave",
        "Spot Weakness",
        "Havoc",
        "Searing Blow",
        "Heavy Blade",
        "Skip",
        "Bash",
        "Anger",
        "Strike_R",
        "Defend_R",
        "Wound",
        "Dazed",
        "Burn",
        "Slimed",
        "Clumsy",
        "Normality",
        "Parasite",
        "Pain",
        "Pride",
        "Regret",
        "Shame",
        "Doubt",
        "Injury",
        "Writhe",
        "Curse of the Bell",
    ]

    DEFENSIVE_CARDS = [
        "Shrug It Off",
        "Metallicize",
        "Ghostly Armor",
        "Armaments",
        "True Grit",
        "Second Wind",
        "Impervious",
        "Entrench",
        "Disarm",
        "Intimidate",
    ]

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
        "Immolate": 2,
        "Bludgeon": 1,
        "Fiend Fire": 1,
        "Reaper": 1,
        "Impervious": 2,
        "Exhume": 1,
        "Whirlwind": 2,
        "Berserk": 1,
        "Double Tap": 1,
        "Bludgeon": 1,
        "Dark Embrace": 1,
        "Brutality": 1,
        "Feel No Pain": 2,
        "Shrug It Off": 3,
        "Metallicize": 2,
        "Disarm": 2,
        "Shockwave": 2,
        "Entrench": 1,
        "Inflame": 2,
        "Battle Trance": 2,
        "Armaments": 2,
        "Uppercut": 1,
        "Carnage": 1,
        "Ghostly Armor": 2,
        "Pummel": 1,
        "Pommel Strike": 2,
        "Dropkick": 2,
        "Flex": 2,
        "Twin Strike": 2,
        "True Grit": 2,
        "Wild Strike": 1,
        "Clothesline": 1,
        "Thunderclap": 2,
        "Anger": 2,
        "Body Slam": 1,
        "Headbutt": 2,
        "Sword Boomerang": 2,
        "Rampage": 1,
        "Blood for Blood": 1,
        "Perfected Strike": 1,
        "Cleave": 2,
        "Sever Soul": 1,
        "Rupture": 1,
        "Evolve": 1,
        "Fire Breathing": 1,
        "Combust": 1,
        "Hemokinesis": 1,
        "Warcry": 2,
        "Intimidate": 2,
        "Second Wind": 1,
        "Burning Pact": 1,
        "Seeing Red": 2,
        "Iron Wave": 2,
        "Spot Weakness": 1,
        "Havoc": 2,
        "Searing Blow": 1,
        "Heavy Blade": 1,
        "Perfected Strike": 0,
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
        "Coffee Dripper",
        "Calling Bell",
        "Black Blood",
    ]

    PLAY_PRIORITY_LIST = [
        "Offering",
        "Limit Break",
        "Barricade",
        "Demon Form",
        "Feed",
        "Juggernaut",
        "Immolate",
        "Bludgeon",
        "Fiend Fire",
        "Reaper",
        "Impervious",
        "Exhume",
        "Whirlwind",
        "Berserk",
        "Double Tap",
        "Dark Embrace",
        "Brutality",
        "Feel No Pain",
        "Shrug It Off",
        "Metallicize",
        "Disarm",
        "Shockwave",
        "Entrench",
        "Inflame",
        "Battle Trance",
        "Armaments",
        "Uppercut",
        "Carnage",
        "Ghostly Armor",
        "Pummel",
        "Pommel Strike",
        "Dropkick",
        "Flex",
        "Twin Strike",
        "True Grit",
        "Wild Strike",
        "Clothesline",
        "Thunderclap",
        "Anger",
        "Body Slam",
        "Headbutt",
        "Sword Boomerang",
        "Rampage",
        "Blood for Blood",
        "Perfected Strike",
        "Cleave",
        "Sever Soul",
        "Rupture",
        "Evolve",
        "Fire Breathing",
        "Combust",
        "Hemokinesis",
        "Warcry",
        "Intimidate",
        "Second Wind",
        "Burning Pact",
        "Seeing Red",
        "Iron Wave",
        "Spot Weakness",
        "Havoc",
        "Searing Blow",
        "Heavy Blade",
        "Bash",
        "Strike_R",
        "Defend_R",
        "Strike",
        "Defend_R",
    ]

    def __init__(self):
        super().__init__()
