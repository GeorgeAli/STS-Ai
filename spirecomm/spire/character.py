from enum import Enum
from spirecomm.spire.power import Power


class Intent(Enum):
    ATTACK = 1
    ATTACK_BUFF = 2
    ATTACK_DEBUFF = 3
    ATTACK_DEFEND = 4
    BUFF = 5
    DEBUFF = 6
    STRONG_DEBUFF = 7
    DEBUG = 8
    DEFEND = 9
    DEFEND_DEBUFF = 10
    DEFEND_BUFF = 11
    ESCAPE = 12
    MAGIC = 13
    NONE = 14
    SLEEP = 15
    STUN = 16
    UNKNOWN = 17

    def is_attack(self):
        return self in [
            Intent.ATTACK,
            Intent.ATTACK_BUFF,
            Intent.ATTACK_DEBUFF,
            Intent.ATTACK_DEFEND,
        ]


class PlayerClass(Enum):
    IRONCLAD = 1
    # THE_SILENT = 2
    # DEFECT = 3


class Orb:

    def __init__(self, name, orb_id, evoke_amount, passive_amount):
        self.name = name
        self.orb_id = orb_id
        self.evoke_amount = evoke_amount
        self.passive_amount = passive_amount

    @classmethod
    def from_json(cls, json_object):
        name = json_object.get("name")
        orb_id = json_object.get("id")
        evoke_amount = json_object.get("evoke_amount")
        passive_amount = json_object.get("passive_amount")
        orb = Orb(name, orb_id, evoke_amount, passive_amount)
        return orb


class Character:

    def __init__(self, max_hp, current_hp=None, block=0):
        self.max_hp = max_hp
        self.current_hp = current_hp
        if self.current_hp is None:
            self.current_hp = self.max_hp
        self.block = block
        self.powers = []


class Player(Character):

    def __init__(self, max_hp, current_hp=None, block=0, energy=0):
        super().__init__(max_hp, current_hp, block)
        self.energy = energy
        self.hand = []
        self.draw_pile = []
        self.discard_pile = []
        self.exhaust_pile = []
        self.powers = []
        self.ethereal = []
        self.orbs = []

    @classmethod
    def from_json(cls, json_object):
        player = cls(
            json_object.get("max_hp", 0),
            json_object.get("current_hp", 0),
            json_object.get("block", 0),
            json_object.get("energy", 0),
        )
        player.powers = [
            Power.from_json(json_power) for json_power in json_object.get("powers", [])
        ]
        player.orbs = [Orb.from_json(orb) for orb in json_object.get("orbs", [])]
        return player

    def draw(self, number_of_cards):
        for _ in range(number_of_cards):
            if not self.draw_pile and self.discard_pile:
                self.draw_pile = self.discard_pile[:]
                self.discard_pile = []
            if self.draw_pile:
                self.hand.append(self.draw_pile.pop(0))

    def shuffle_discard_into_draw(self):
        self.draw_pile = self.discard_pile[:]
        self.discard_pile.clear()
        # Shuffle the draw pile
        import random

        random.shuffle(self.draw_pile)

    def gain_energy(self, amount):
        self.energy += amount

    def add_buff(self, buff_name, amount):
        found_buff = next(
            (buff for buff in self.powers if buff.power_name == buff_name), None
        )
        if found_buff:
            found_buff.amount += amount
        else:
            new_buff = Power(power_id=buff_name, name=buff_name, amount=amount)
            self.powers.append(new_buff)


class Buff:
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount


class Monster(Character):
    def __init__(
        self,
        name,
        monster_id,
        max_hp,
        current_hp,
        block,
        intent,
        half_dead,
        is_gone,
        move_id=-1,
        last_move_id=None,
        second_last_move_id=None,
        move_base_damage=0,
        move_adjusted_damage=0,
        move_hits=0,
        debuffs=None,
    ):
        super().__init__(max_hp, current_hp, block)
        self.name = name
        self.monster_id = monster_id
        self.intent = intent
        self.half_dead = half_dead
        self.is_gone = is_gone
        self.move_id = move_id
        self.last_move_id = last_move_id
        self.second_last_move_id = second_last_move_id
        self.move_base_damage = move_base_damage
        self.move_adjusted_damage = move_adjusted_damage
        self.move_hits = move_hits
        self.monster_index = 0
        self.debuffs = debuffs or {}
        self.powers = []

    @classmethod
    def from_json(cls, json_object):
        name = json_object["name"]
        monster_id = json_object["id"]
        max_hp = json_object["max_hp"]
        current_hp = json_object["current_hp"]
        block = json_object["block"]
        intent = Intent[json_object["intent"]]
        half_dead = json_object["half_dead"]
        is_gone = json_object["is_gone"]
        move_id = json_object.get("move_id", -1)
        last_move_id = json_object.get("last_move_id", None)
        second_last_move_id = json_object.get("second_last_move_id", None)
        move_base_damage = json_object.get("move_base_damage", 0)
        move_adjusted_damage = json_object.get("move_adjusted_damage", 0)
        move_hits = json_object.get("move_hits", 0)
        debuffs = {
            debuff["id"]: debuff["amount"] for debuff in json_object.get("debuffs", [])
        }

        monster = cls(
            name,
            monster_id,
            max_hp,
            current_hp,
            block,
            intent,
            half_dead,
            is_gone,
            move_id,
            last_move_id,
            second_last_move_id,
            move_base_damage,
            move_adjusted_damage,
            move_hits,
            debuffs,
        )
        monster.powers = [
            Power.from_json(json_power) for json_power in json_object.get("powers", [])
        ]
        return monster

    def add_debuff(self, debuff_name, amount):
        if debuff_name in self.debuffs:
            self.debuffs[debuff_name] += amount
        else:
            self.debuffs[debuff_name] = amount
            
    def add_buff(self, buff_name, amount):
        found_buff = next(
            (buff for buff in self.powers if buff.power_name == buff_name), None
        )
        if found_buff:
            found_buff.amount += amount
        else:
            new_buff = Power(power_id=buff_name, name=buff_name, amount=amount)
            self.powers.append(new_buff)

    def has_debuff(self, debuff_name):
        for debuff in self.debuffs:
            if debuff.power_id == debuff_name:
                return True
        return False

    def __eq__(self, other):
        if (
            self.name == other.name
            and self.current_hp == other.current_hp
            and self.max_hp == other.max_hp
            and self.block == other.block
        ):
            if len(self.powers) == len(other.powers):
                for i in range(len(self.powers)):
                    if self.powers[i] != other.powers[i]:
                        return False
                return True
        return False
