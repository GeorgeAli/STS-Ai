ironclad_cards = {
    # Normal cards
    "Strike": {"type": "ATTACK", "damage": 6, "block": 0},
    "Defend": {"type": "SKILL", "damage": 0, "block": 5},
    "Bash": {"type": "ATTACK", "damage": 8, "block": 0, "vulnerable": 2},
    "Anger": {"type": "ATTACK", "damage": 6, "block": 0},
    "Armaments": {"type": "SKILL", "damage": 0, "block": 5, "upgrade": True},
    "Body Slam": {"type": "ATTACK", "damage": 0, "block": 0, "based_on_block": True},
    "Clash": {"type": "ATTACK", "damage": 14, "block": 0},
    "Cleave": {"type": "ATTACK", "damage": 8, "block": 0, "aoe": True},
    "Clothesline": {"type": "ATTACK", "damage": 12, "block": 0, "weak": 2},
    "Flex": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "strength": 2,
        "lose_strength": 2,
    },
    "Iron Wave": {"type": "ATTACK", "damage": 5, "block": 5},
    "Pommel Strike": {"type": "ATTACK", "damage": 9, "block": 0, "draw": 1},
    "Shrug It Off": {"type": "SKILL", "damage": 0, "block": 8, "draw": 1},
    "Thunderclap": {
        "type": "ATTACK",
        "damage": 4,
        "block": 0,
        "aoe": True,
        "vulnerable": 1,
    },
    "Twin Strike": {"type": "ATTACK", "damage": 10, "block": 0, "multiple_hits": 2},
    "Uppercut": {
        "type": "ATTACK",
        "damage": 13,
        "block": 0,
        "vulnerable": 1,
        "weak": 1,
    },
    "Whirlwind": {
        "type": "ATTACK",
        "damage": 5,
        "block": 0,
        "whirlwind_handle": True,
    },
    "Battle Trance": {"type": "SKILL", "damage": 0, "block": 0, "draw": 3},
    "Berserk": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "gain_energy": 1,
        "self_vulnerable": 2,
    },
    "Blood for Blood": {
        "type": "ATTACK",
        "damage": 18,
        "block": 0,
        "reduced_cost_on_damage": True,
    },
    "Bloodletting": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "gain_energy": 2,
        "lose_hp": 3,
    },
    "Bludgeon": {"type": "ATTACK", "damage": 32, "block": 0},
    "Brutality": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "draw": 1,
        "lose_hp_per_turn": 1,
    },
    "Burning Pact": {"type": "SKILL", "damage": 0, "block": 0, "draw": 2},
    "Carnage": {"type": "ATTACK", "damage": 20, "block": 0, "ethereal": True},
    "Combust": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "damage_per_turn": 5,
        "aoe": 5,
    },
    "Corruption": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "skills_cost_zero": True
    },
    "Dark Embrace": {"type": "POWER", "damage": 0, "block": 0, "draw_on_exhaust": 1},
    "Disarm": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "reduce_strength": 2,
        "exhaust": True,
    },
    "Double Tap": {"type": "SKILL", "damage": 0, "block": 0, "next_attack_twice": True},
    "Dropkick": {
        "type": "ATTACK",
        "damage": 5,
        "block": 0,
        "draw_if_vulnerable": True,
        "gain_energy_if_vulnerable": True,
    },
    "Dual Wield": {"type": "SKILL", "damage": 0, "block": 0, "create_copy": True},
    "Entrench": {"type": "SKILL", "damage": 0, "block": 0, "double_block": True},
    "Evolve": {"type": "POWER", "damage": 0, "block": 0, "draw_on_status": 1},
    "Exhume": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "retrieve_exhausted_card": True,
    },
    "Feed": {
        "type": "ATTACK",
        "damage": 10,
        "block": 0,
        "gain_max_hp_on_kill": 3,
        "exhaust": True,
    },
    "Feel No Pain": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "gain_block_on_exhaust": 3,
    },
    "Fiend Fire": {
        "type": "ATTACK",
        "damage": 7,
        "block": 0,
        "exhaust_hand": True,
        "multiple_hits": 0,
    },
    "Fire Breathing": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "aoe_damage_on_status_draw": 6,
    },
    "Flame Barrier": {"type": "SKILL", "damage": 0, "block": 12, "damage_on_attack": 4},
    "Ghostly Armor": {"type": "SKILL", "damage": 0, "block": 10, "ethereal": True},
    "Havoc": {"type": "SKILL", "damage": 0, "block": 0, "play_top_card": True},
    "Headbutt": {
        "type": "ATTACK",
        "damage": 9,
        "block": 0,
        "return_card_from_discard": True,
    },
    "Heavy Blade": {
        "type": "ATTACK",
        "damage": 14,
        "block": 0,
        "strength_multiplier": 3,
    },
    "Hemokinesis": {"type": "ATTACK", "damage": 14, "block": 0, "lose_hp": 3},
    "Immolate": {
        "type": "ATTACK",
        "damage": 21,
        "block": 0,
        "aoe": True,
        "burns_to_draw": 1,
    },
    "Impervious": {"type": "SKILL", "damage": 0, "block": 30, "exhaust": True},
    "Infernal Blade": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "create_random_attack": True,
        "exhaust": True,
        "exhaust": True,
    },
    "Inflame": {"type": "POWER", "damage": 0, "block": 0, "strength": 2},
    "Intimidate": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "weak_aoe": 1,
        "exhaust": True,
    },
    "Juggernaut": {"type": "POWER", "damage": 0, "block": 0, "damage_on_block": 5},
    "Limit Break": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "double_strength": True,
        "exhaust": True,
    },
    "Metallicize": {"type": "POWER", "damage": 0, "block": 0, "block_per_turn": 3},
    "Offering": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "gain_energy": 2,
        "draw": 3,
        "lose_hp": 6,
        "exhaust": True,
    },
    "Perfected Strike": {
        "type": "ATTACK",
        "damage": 6,
        "block": 0,
        "bonus_damage_per_strike": 2,
    },
    "Power Through": {
        "type": "SKILL",
        "damage": 0,
        "block": 15,
        "add_wounds_to_hand": 2,
    },
    "Pummel": {
        "type": "ATTACK",
        "damage": 2,
        "block": 0,
        "multiple_hits": 4,
        "exhaust": True,
    },
    "Rage": {"type": "SKILL", "damage": 0, "block": 0, "block_on_ATTACK": 3},
    "Rampage": {
        "type": "ATTACK",
        "damage": 8,
        "block": 0,
        "increase_damage_per_play": 8,
    },
    "Reaper": {
        "type": "ATTACK",
        "damage": 4,
        "block": 0,
        "aoe": True,
        "heal_on_damage": True,
        "exhaust": True,
    },
    "Reckless Charge": {
        "type": "ATTACK",
        "damage": 7,
        "block": 0,
        "add_dazed_to_discard": 1,
    },
    "Rupture": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "gain_strength_on_hp_loss_from_playing_cards": 1,
    },
    "Second Wind": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "exhaust_non_attack": True,
        "block_per_exhaust": 5,
    },
    "Seeing Red": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "gain_energy": 2,
        "exhaust": True,
    },
    "Sentinel": {"type": "SKILL", "damage": 0, "block": 5, "gain_energy_on_exhaust": 2},
    "Sever Soul": {
        "type": "ATTACK",
        "damage": 16,
        "block": 0,
        "exhaust_non_attack": True,
        "block_per_exhaust": 0,
    },
    "Shockwave": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "weak_aoe": 3,
        "vulnerable_aoe": 3,
        "exhaust": True,
    },
    "Spot Weakness": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "gain_strength_if_attack_intent": 3,
    },
    "Sword Boomerang": {
        "type": "ATTACK",
        "damage": 3,
        "block": 0,
        "sword_boomerang_handle": True,
        "hits": 3,
    },
    "Thunderclap": {
        "type": "ATTACK",
        "damage": 4,
        "block": 0,
        "aoe": True,
        "vulnerable": 1,
    },
    "True Grit": {
        "type": "SKILL",
        "damage": 0,
        "block": 7,
        "exhaust_random_card": True,
    },
    "Twin Strike": {"type": "ATTACK", "damage": 10, "block": 0, "hits": 2},
    "Uppercut": {
        "type": "ATTACK",
        "damage": 13,
        "block": 0,
        "vulnerable": 1,
        "weak": 1,
    },
    "Warcry": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "draw": 1,
        "put_card_on_top_of_deck": True,
        "exhaust": True,
    },
    # Upgraded cards
    "Strike+": {"type": "ATTACK", "damage": 9, "block": 0},
    "Defend+": {"type": "SKILL", "damage": 0, "block": 8},
    "Bash+": {"type": "ATTACK", "damage": 10, "block": 0, "vulnerable": 3},
    "Anger+": {"type": "ATTACK", "damage": 8, "block": 0},
    "Armaments+": {"type": "SKILL", "damage": 0, "block": 5, "upgrade_all": True},
    "Body Slam+": {"type": "ATTACK", "damage": 0, "block": 0, "based_on_block": True},
    "Clash+": {"type": "ATTACK", "damage": 18, "block": 0},
    "Cleave+": {"type": "ATTACK", "damage": 11, "block": 0, "aoe": True},
    "Clothesline+": {"type": "ATTACK", "damage": 14, "block": 0, "weak": 3},
    "Flex+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "strength": 4,
        "lose_strength": 4,
    },
    "Iron Wave+": {"type": "ATTACK", "damage": 7, "block": 7},
    "Pommel Strike+": {"type": "ATTACK", "damage": 10, "block": 0, "draw": 2},
    "Shrug It Off+": {"type": "SKILL", "damage": 0, "block": 11, "draw": 1},
    "Thunderclap+": {
        "type": "ATTACK",
        "damage": 7,
        "block": 0,
        "aoe": True,
        "vulnerable": 2,
    },
    "Twin Strike+": {"type": "ATTACK", "damage": 14, "block": 0, "hits": 2},
    "Uppercut+": {
        "type": "ATTACK",
        "damage": 13,
        "block": 0,
        "vulnerable": 2,
        "weak": 2,
    },
    "Whirlwind+": {
        "type": "ATTACK",
        "damage": 8,
        "block": 0,
        "aoe": True,
        "whirlwind_handle": True,
    },
    "Battle Trance+": {"type": "SKILL", "damage": 0, "block": 0, "draw": 4},
    "Berserk+": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "gain_energy": 1,
        "self_vulnerable": 1,
    },
    "Blood for Blood+": {
        "type": "ATTACK",
        "damage": 22,
        "block": 0,
        "reduced_cost_on_damage": True,
    },
    "Bloodletting+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "gain_energy": 3,
        "lose_hp": 3,
    },
    "Bludgeon+": {"type": "ATTACK", "damage": 42, "block": 0},
    "Brutality+": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "draw": 2,
        "lose_hp_per_turn": 1,
    },
    "Burning Pact+": {"type": "SKILL", "damage": 0, "block": 0, "draw": 3},
    "Carnage+": {"type": "ATTACK", "damage": 28, "block": 0, "ethereal": True},
    "Combust+": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "damage_per_turn": 7,
        "aoe": 7,
    },
    "Corruption+": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "skills_cost_zero": True
    },
    "Dark Embrace+": {"type": "POWER", "damage": 0, "block": 0, "draw_on_exhaust": 1},
    "Disarm+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "reduce_strength": 3,
        "exhaust": True,
    },
    "Double Tap+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "next_attack_twice": True,
    },
    "Dropkick+": {
        "type": "ATTACK",
        "damage": 8,
        "block": 0,
        "draw_if_vulnerable": True,
        "gain_energy_if_vulnerable": True,
    },
    "Dual Wield+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "create_two_copies": True,
    },
    "Entrench+": {"type": "SKILL", "damage": 0, "block": 0, "double_block": True},
    "Evolve+": {"type": "POWER", "damage": 0, "block": 0, "draw_on_status": 2},
    "Exhume+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "retrieve_exhausted_card": True,
    },
    "Feed+": {
        "type": "ATTACK",
        "damage": 12,
        "block": 0,
        "gain_max_hp_on_kill": 4,
        "exhaust": True,
    },
    "Feel No Pain+": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "gain_block_on_exhaust": 4,
    },
    "Fiend Fire+": {
        "type": "ATTACK",
        "damage": 7,
        "block": 0,
        "exhaust_hand": True,
        "multiple_hits": 0,
    },
    "Fire Breathing+": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "aoe_damage_on_status_draw": 10,
    },
    "Flame Barrier+": {
        "type": "SKILL",
        "damage": 0,
        "block": 16,
        "damage_on_attack": 6,
    },
    "Ghostly Armor+": {"type": "SKILL", "damage": 0, "block": 13, "ethereal": True},
    "Havoc+": {"type": "SKILL", "damage": 0, "block": 0, "play_top_card": True},
    "Headbutt+": {
        "type": "ATTACK",
        "damage": 12,
        "block": 0,
        "return_card_from_discard": True,
    },
    "Heavy Blade+": {
        "type": "ATTACK",
        "damage": 14,
        "block": 0,
        "strength_multiplier": 5,
    },
    "Hemokinesis+": {"type": "ATTACK", "damage": 20, "block": 0, "lose_hp": 3},
    "Immolate+": {
        "type": "ATTACK",
        "damage": 28,
        "block": 0,
        "aoe": True,
        "burns_to_draw": 1,
    },
    "Impervious+": {"type": "SKILL", "damage": 0, "block": 40, "exhaust": True},
    "Infernal Blade+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "create_random_attack": True,
        "exhaust": True,
    },
    "Inflame+": {"type": "POWER", "damage": 0, "block": 0, "strength": 3},
    "Intimidate+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "weak_aoe": 2,
        "exhaust": True,
    },
    "Juggernaut+": {"type": "POWER", "damage": 0, "block": 0, "damage_on_block": 7},
    "Limit Break+": {"type": "SKILL", "damage": 0, "block": 0, "double_strength": True},
    "Metallicize+": {"type": "POWER", "damage": 0, "block": 0, "block_per_turn": 4},
    "Offering+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "gain_energy": 2,
        "draw": 5,
        "lose_hp": 6,
        "exhaust": True,
    },
    "Perfected Strike+": {
        "type": "ATTACK",
        "damage": 6,
        "block": 0,
        "bonus_damage_per_strike": 3,
    },
    "Power Through+": {
        "type": "SKILL",
        "damage": 0,
        "block": 20,
        "add_wounds_to_hand": 2,
    },
    "Pummel+": {
        "type": "ATTACK",
        "damage": 2,
        "block": 0,
        "multiple_hits": 4,
        "exhaust": True,
    },
    "Rage+": {"type": "SKILL", "damage": 0, "block": 0, "block_on_attack": 5},
    "Rampage+": {
        "type": "ATTACK",
        "damage": 8,
        "block": 0,
        "increase_damage_per_play": 8,
    },
    "Reaper+": {
        "type": "ATTACK",
        "damage": 5,
        "block": 0,
        "aoe": True,
        "heal_on_damage": True,
        "exhaust": True,
    },
    "Reckless Charge+": {
        "type": "ATTACK",
        "damage": 10,
        "block": 0,
        "add_dazed_to_discard": 1,
    },
    "Rupture+": {
        "type": "POWER",
        "damage": 0,
        "block": 0,
        "gain_strength_on_hp_loss_from_playing_cards": 2,
    },
    "Second Wind+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "exhaust_non_attack": True,
        "block_per_exhaust": 7,
    },
    "Seeing Red+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "gain_energy": 2,
        "exhaust": True,
    },
    "Sentinel+": {
        "type": "SKILL",
        "damage": 0,
        "block": 8,
        "gain_energy_on_exhaust": 3,
    },
    "Sever Soul+": {
        "type": "ATTACK",
        "damage": 20,
        "block": 0,
        "exhaust_non_attack": True,
        "block_per_exhaust": 0,
    },
    "Shockwave+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "weak_aoe": 5,
        "vulnerable_aoe": 5,
        "exhaust": True,
    },
    "Spot Weakness+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "gain_strength_if_attack_intent": 4,
    },
    "Sword Boomerang+": {
        "type": "ATTACK",
        "damage": 3,
        "block": 0,
        "sword_boomerang_handle": True,
        "hits": 4,
    },
    "Thunderclap+": {
        "type": "ATTACK",
        "damage": 7,
        "block": 0,
        "aoe": True,
        "vulnerable_aoe": 2,
    },
    "True Grit+": {"type": "SKILL", "damage": 0, "block": 9},
    "Twin Strike+": {"type": "ATTACK", "damage": 14, "block": 0, "hits": 2},
    "Uppercut+": {
        "type": "ATTACK",
        "damage": 13,
        "block": 0,
        "vulnerable": 2,
        "weak": 2,
    },
    "Warcry+": {
        "type": "SKILL",
        "damage": 0,
        "block": 0,
        "draw": 2,
        "put_card_on_top_of_deck": True,
        "exhaust": True,
    },
    "Demon Form+": {"type": "POWER", "damage": 0, "block": 0, "give_power_per_turn": 3},
    "Demon Form": {"type": "POWER", "damage": 0, "block": 0, "give_power_per_turn": 2},
    "Barricade+": {"type": "POWER", "damage": 0, "block": 0, "block_never_expires": True},
    "Barricade": {"type": "POWER", "damage": 0, "block": 0, "block_never_expires": True},
}


ironclad_archetypes = {
    "strength": {
        "key_cards": [
            "Inflame",
            "Demon Form",
            "Limit Break",
            "Offering",
            "Reaper"
        ],
        "support_cards": [
            "Feel No Pain",
            "Flex",
            "Whirlwind",
            "Sword Boomerang",
            "Immolate"
        ],
        "important_relics": [
            "Shuriken",
            "Vajra",
            "Paper Frog",
            "Red Skull",
            "Champion Belt"
        ],
    },
    "exhaust": {
        "key_cards": [
            "Feel No Pain",
            "Dark Embrace",
            "Corruption",
            "Second Wind",
            "Fiend Fire",
            "Exhume"
        ],
        "support_cards": [
            "Barricade",
            "Juggernaut",
            "Impervious",
            "True Grit"
        ],
        "important_relics": [
            "Charon's Ashes",
            "Dead Branch"
        ],
    },
}


ironclad_relic_values = {
    "Chemical X": 25,
    "Cauldron": 5,
    "Clockwork Souvenir": 25,
    "Dolly's Mirror": 15,
    "Hand Drill": 25,
    "Lee's Waffle": 30,
    "Medical Kit": 15,
    "Membership Card": 25,
    "Orange Pellets": 20,
    "Orrery": 5,
    "Sling of Courage": 15,
    "Strange Spoon": 10,
    "The Abacus": 20,
    "Toolbox": 10,
}


def get_card_values(card_name):
    return ironclad_cards.get(card_name, {})