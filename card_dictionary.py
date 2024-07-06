ironclad_cards = {
    # Normal cards
    "Strike": {"type": "attack", "damage": 6, "block": 0},
    "Defend": {"type": "skill", "damage": 0, "block": 5},
    "Bash": {"type": "attack", "damage": 8, "block": 0, "vulnerable": 2},
    "Anger": {"type": "attack", "damage": 6, "block": 0},
    "Armaments": {"type": "skill", "damage": 0, "block": 5, "upgrade": True},
    "Body Slam": {"type": "attack", "damage": 0, "block": 0, "based_on_block": True},
    "Clash": {"type": "attack", "damage": 14, "block": 0},
    "Cleave": {"type": "attack", "damage": 8, "block": 0, "aoe": True},
    "Clothesline": {"type": "attack", "damage": 12, "block": 0, "weak": 2},
    "Flex": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "strength": 2,
        "lose_strength": 2,
    },
    "Iron Wave": {"type": "attack", "damage": 5, "block": 5},
    "Pommel Strike": {"type": "attack", "damage": 9, "block": 0, "draw": 1},
    "Shrug It Off": {"type": "skill", "damage": 0, "block": 8, "draw": 1},
    "Thunderclap": {
        "type": "attack",
        "damage": 4,
        "block": 0,
        "aoe": True,
        "vulnerable": 1,
    },
    "Twin Strike": {"type": "attack", "damage": 10, "block": 0, "hits": 2},
    "Uppercut": {
        "type": "attack",
        "damage": 13,
        "block": 0,
        "vulnerable": 1,
        "weak": 1,
    },
    "Whirlwind": {
        "type": "attack",
        "damage": 5,
        "block": 0,
        "aoe": True,
        "variable_cost": True,
    },
    "Battle Trance": {"type": "skill", "damage": 0, "block": 0, "draw": 3},
    "Berserk": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "gain_energy": 1,
        "vulnerable": 1,
    },
    "Blood for Blood": {
        "type": "attack",
        "damage": 18,
        "block": 0,
        "reduced_cost_on_damage": True,
    },
    "Bloodletting": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "gain_energy": 1,
        "lose_hp": 3,
    },
    "Bludgeon": {"type": "attack", "damage": 32, "block": 0},
    "Brutality": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "draw": 1,
        "lose_hp_per_turn": 1,
    },
    "Burning Pact": {"type": "skill", "damage": 0, "block": 0, "draw": 2},
    "Carnage": {"type": "attack", "damage": 20, "block": 0, "ethereal": True},
    "Combust": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "damage_per_turn": 5,
        "aoe_damage": 5,
    },
    "Corruption": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "skills_cost_zero": True,
        "exhaust_skills": True,
    },
    "Dark Embrace": {"type": "power", "damage": 0, "block": 0, "draw_on_exhaust": 1},
    "Disarm": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "reduce_strength": 2,
        "exhaust": True,
    },
    "Double Tap": {"type": "skill", "damage": 0, "block": 0, "next_attack_twice": True},
    "Dropkick": {
        "type": "attack",
        "damage": 5,
        "block": 0,
        "draw_if_vulnerable": True,
        "gain_energy_if_vulnerable": True,
    },
    "Dual Wield": {"type": "skill", "damage": 0, "block": 0, "create_copy": True},
    "Entrench": {"type": "skill", "damage": 0, "block": 0, "double_block": True},
    "Evolve": {"type": "power", "damage": 0, "block": 0, "draw_on_status": 1},
    "Exhume": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "retrieve_exhausted_card": True,
    },
    "Feed": {
        "type": "attack",
        "damage": 10,
        "block": 0,
        "gain_max_hp_on_kill": 3,
        "exhaust": True,
    },
    "Feel No Pain": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "gain_block_on_exhaust": 3,
    },
    "Fiend Fire": {
        "type": "attack",
        "damage": 7,
        "block": 0,
        "exhaust_hand": True,
        "multiple_hits": True,
    },
    "Fire Breathing": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "aoe_damage_on_status_draw": 6,
    },
    "Flame Barrier": {"type": "skill", "damage": 0, "block": 12, "damage_on_attack": 4},
    "Ghostly Armor": {"type": "skill", "damage": 0, "block": 10, "ethereal": True},
    "Havoc": {"type": "skill", "damage": 0, "block": 0, "play_top_discard": True},
    "Headbutt": {
        "type": "attack",
        "damage": 9,
        "block": 0,
        "return_card_from_discard": True,
    },
    "Heavy Blade": {
        "type": "attack",
        "damage": 14,
        "block": 0,
        "strength_multiplier": 3,
    },
    "Hemokinesis": {"type": "attack", "damage": 14, "block": 0, "lose_hp": 3},
    "Immolate": {
        "type": "attack",
        "damage": 21,
        "block": 0,
        "aoe": True,
        "burns_to_draw": 1,
    },
    "Impervious": {"type": "skill", "damage": 0, "block": 30, "exhaust": True},
    "Infernal Blade": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "create_random_attack": True,
        "exhaust": True,
    },
    "Inflame": {"type": "power", "damage": 0, "block": 0, "strength": 2},
    "Intimidate": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "weak_aoe": 1,
        "exhaust": True,
    },
    "Juggernaut": {"type": "power", "damage": 0, "block": 0, "damage_on_block": 5},
    "Limit Break": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "double_strength": True,
        "exhaust": True,
    },
    "Metallicize": {"type": "power", "damage": 0, "block": 0, "block_per_turn": 3},
    "Offering": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "gain_energy": 2,
        "draw": 3,
        "lose_hp": 6,
        "exhaust": True,
    },
    "Perfected Strike": {
        "type": "attack",
        "damage": 6,
        "block": 0,
        "bonus_damage_per_strike": 2,
    },
    "Power Through": {
        "type": "skill",
        "damage": 0,
        "block": 15,
        "add_wounds_to_hand": 2,
    },
    "Pummel": {
        "type": "attack",
        "damage": 2,
        "block": 0,
        "multiple_hits": 4,
        "exhaust": True,
    },
    "Rage": {"type": "skill", "damage": 0, "block": 0, "block_on_attack": 3},
    "Rampage": {
        "type": "attack",
        "damage": 8,
        "block": 0,
        "increase_damage_per_play": 8,
    },
    "Reaper": {
        "type": "attack",
        "damage": 4,
        "block": 0,
        "aoe": True,
        "heal_on_damage": True,
        "exhaust": True,
    },
    "Reckless Charge": {
        "type": "attack",
        "damage": 7,
        "block": 0,
        "add_dazed_to_discard": 1,
    },
    "Rupture": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "gain_strength_on_hp_loss": 1,
    },
    "Second Wind": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "exhaust_non_attack": True,
        "block_per_exhaust": 5,
    },
    "Seeing Red": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "gain_energy": 2,
        "exhaust": True,
    },
    "Sentinel": {"type": "skill", "damage": 0, "block": 5, "gain_energy_on_exhaust": 2},
    "Sever Soul": {
        "type": "attack",
        "damage": 16,
        "block": 0,
        "exhaust_non_attack": True,
    },
    "Shockwave": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "weak_aoe": 3,
        "vulnerable_aoe": 3,
        "exhaust": True,
    },
    "Spot Weakness": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "gain_strength_if_attack_intent": 3,
    },
    "Sword Boomerang": {
        "type": "attack",
        "damage": 3,
        "block": 0,
        "random_targets": True,
        "hits": 3,
    },
    "Thunderclap": {
        "type": "attack",
        "damage": 4,
        "block": 0,
        "aoe": True,
        "vulnerable": 1,
    },
    "True Grit": {
        "type": "skill",
        "damage": 0,
        "block": 7,
        "exhaust_random_card": True,
    },
    "Twin Strike": {"type": "attack", "damage": 10, "block": 0, "hits": 2},
    "Uppercut": {
        "type": "attack",
        "damage": 13,
        "block": 0,
        "vulnerable": 1,
        "weak": 1,
    },
    "Warcry": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "draw": 1,
        "put_card_on_top_of_deck": True,
        "exhaust": True,
    },
    "Whirlwind": {
        "type": "attack",
        "damage": 5,
        "block": 0,
        "aoe": True,
        "variable_cost": True,
    },
    # Upgraded cards
    "Strike+": {"type": "attack", "damage": 9, "block": 0},
    "Defend+": {"type": "skill", "damage": 0, "block": 8},
    "Bash+": {"type": "attack", "damage": 10, "block": 0, "vulnerable": 3},
    "Anger+": {"type": "attack", "damage": 8, "block": 0},
    "Armaments+": {"type": "skill", "damage": 0, "block": 5, "upgrade_all": True},
    "Body Slam+": {"type": "attack", "damage": 0, "block": 0, "based_on_block": True},
    "Clash+": {"type": "attack", "damage": 18, "block": 0},
    "Cleave+": {"type": "attack", "damage": 11, "block": 0, "aoe": True},
    "Clothesline+": {"type": "attack", "damage": 14, "block": 0, "weak": 3},
    "Flex+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "strength": 4,
        "lose_strength": 4,
    },
    "Iron Wave+": {"type": "attack", "damage": 7, "block": 7},
    "Pommel Strike+": {"type": "attack", "damage": 10, "block": 0, "draw": 2},
    "Shrug It Off+": {"type": "skill", "damage": 0, "block": 11, "draw": 1},
    "Thunderclap+": {
        "type": "attack",
        "damage": 7,
        "block": 0,
        "aoe": True,
        "vulnerable": 2,
    },
    "Twin Strike+": {"type": "attack", "damage": 14, "block": 0, "hits": 2},
    "Uppercut+": {
        "type": "attack",
        "damage": 13,
        "block": 0,
        "vulnerable": 2,
        "weak": 2,
    },
    "Whirlwind+": {
        "type": "attack",
        "damage": 8,
        "block": 0,
        "aoe": True,
        "variable_cost": True,
    },
    "Battle Trance+": {"type": "skill", "damage": 0, "block": 0, "draw": 4},
    "Berserk+": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "gain_energy": 1,
        "vulnerable": 0,
    },
    "Blood for Blood+": {
        "type": "attack",
        "damage": 22,
        "block": 0,
        "reduced_cost_on_damage": True,
    },
    "Bloodletting+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "gain_energy": 2,
        "lose_hp": 3,
    },
    "Bludgeon+": {"type": "attack", "damage": 42, "block": 0},
    "Brutality+": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "draw": 2,
        "lose_hp_per_turn": 1,
    },
    "Burning Pact+": {"type": "skill", "damage": 0, "block": 0, "draw": 3},
    "Carnage+": {"type": "attack", "damage": 28, "block": 0, "ethereal": True},
    "Combust+": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "damage_per_turn": 7,
        "aoe_damage": 7,
    },
    "Corruption+": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "skills_cost_zero": True,
        "exhaust_skills": True,
    },
    "Dark Embrace+": {"type": "power", "damage": 0, "block": 0, "draw_on_exhaust": 1},
    "Disarm+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "reduce_strength": 3,
        "exhaust": True,
    },
    "Double Tap+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "next_attack_twice": True,
    },
    "Dropkick+": {
        "type": "attack",
        "damage": 8,
        "block": 0,
        "draw_if_vulnerable": True,
        "gain_energy_if_vulnerable": True,
    },
    "Dual Wield+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "create_two_copies": True,
    },
    "Entrench+": {"type": "skill", "damage": 0, "block": 0, "double_block": True},
    "Evolve+": {"type": "power", "damage": 0, "block": 0, "draw_on_status": 2},
    "Exhume+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "retrieve_exhausted_card": True,
    },
    "Feed+": {
        "type": "attack",
        "damage": 12,
        "block": 0,
        "gain_max_hp_on_kill": 4,
        "exhaust": True,
    },
    "Feel No Pain+": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "gain_block_on_exhaust": 4,
    },
    "Fiend Fire+": {
        "type": "attack",
        "damage": 7,
        "block": 0,
        "exhaust_hand": True,
        "multiple_hits": True,
    },
    "Fire Breathing+": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "aoe_damage_on_status_draw": 10,
    },
    "Flame Barrier+": {
        "type": "skill",
        "damage": 0,
        "block": 16,
        "damage_on_attack": 6,
    },
    "Ghostly Armor+": {"type": "skill", "damage": 0, "block": 13, "ethereal": True},
    "Havoc+": {"type": "skill", "damage": 0, "block": 0, "play_top_discard": True},
    "Headbutt+": {
        "type": "attack",
        "damage": 12,
        "block": 0,
        "return_card_from_discard": True,
    },
    "Heavy Blade+": {
        "type": "attack",
        "damage": 14,
        "block": 0,
        "strength_multiplier": 5,
    },
    "Hemokinesis+": {"type": "attack", "damage": 20, "block": 0, "lose_hp": 3},
    "Immolate+": {
        "type": "attack",
        "damage": 28,
        "block": 0,
        "aoe": True,
        "burns_to_draw": 1,
    },
    "Impervious+": {"type": "skill", "damage": 0, "block": 40, "exhaust": True},
    "Infernal Blade+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "create_random_attack": True,
        "exhaust": True,
    },
    "Inflame+": {"type": "power", "damage": 0, "block": 0, "strength": 3},
    "Intimidate+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "weak_aoe": 2,
        "exhaust": True,
    },
    "Juggernaut+": {"type": "power", "damage": 0, "block": 0, "damage_on_block": 7},
    "Limit Break+": {"type": "skill", "damage": 0, "block": 0, "double_strength": True},
    "Metallicize+": {"type": "power", "damage": 0, "block": 0, "block_per_turn": 4},
    "Offering+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "gain_energy": 2,
        "draw": 5,
        "lose_hp": 6,
        "exhaust": True,
    },
    "Perfected Strike+": {
        "type": "attack",
        "damage": 6,
        "block": 0,
        "bonus_damage_per_strike": 3,
    },
    "Power Through+": {
        "type": "skill",
        "damage": 0,
        "block": 20,
        "add_wounds_to_hand": 2,
    },
    "Pummel+": {
        "type": "attack",
        "damage": 2,
        "block": 0,
        "multiple_hits": 4,
        "exhaust": True,
    },
    "Rage+": {"type": "skill", "damage": 0, "block": 0, "block_on_attack": 5},
    "Rampage+": {
        "type": "attack",
        "damage": 8,
        "block": 0,
        "increase_damage_per_play": 8,
    },
    "Reaper+": {
        "type": "attack",
        "damage": 5,
        "block": 0,
        "aoe": True,
        "heal_on_damage": True,
        "exhaust": True,
    },
    "Reckless Charge+": {
        "type": "attack",
        "damage": 10,
        "block": 0,
        "add_dazed_to_discard": 1,
    },
    "Rupture+": {
        "type": "power",
        "damage": 0,
        "block": 0,
        "gain_strength_on_hp_loss": 2,
    },
    "Second Wind+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "exhaust_non_attack": True,
        "block_per_exhaust": 7,
    },
    "Seeing Red+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "gain_energy": 2,
        "exhaust": True,
    },
    "Sentinel+": {
        "type": "skill",
        "damage": 0,
        "block": 8,
        "gain_energy_on_exhaust": 3,
    },
    "Sever Soul+": {
        "type": "attack",
        "damage": 20,
        "block": 0,
        "exhaust_non_attack": True,
    },
    "Shockwave+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "weak_aoe": 5,
        "vulnerable_aoe": 5,
        "exhaust": True,
    },
    "Spot Weakness+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "gain_strength_if_attack_intent": 4,
    },
    "Sword Boomerang+": {
        "type": "attack",
        "damage": 3,
        "block": 0,
        "random_targets": True,
        "hits": 4,
    },
    "Thunderclap+": {
        "type": "attack",
        "damage": 7,
        "block": 0,
        "aoe": True,
        "vulnerable": 2,
    },
    "True Grit+": {
        "type": "skill",
        "damage": 0,
        "block": 9,
        "exhaust_random_card": True,
    },
    "Twin Strike+": {"type": "attack", "damage": 14, "block": 0, "hits": 2},
    "Uppercut+": {
        "type": "attack",
        "damage": 13,
        "block": 0,
        "vulnerable": 2,
        "weak": 2,
    },
    "Warcry+": {
        "type": "skill",
        "damage": 0,
        "block": 0,
        "draw": 2,
        "put_card_on_top_of_deck": True,
        "exhaust": True,
    },
    "Whirlwind+": {
        "type": "attack",
        "damage": 8,
        "block": 0,
        "aoe": True,
        "variable_cost": True,
    },
}


def get_card_values(card_name):
    return ironclad_cards.get(card_name, {})