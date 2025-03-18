import json
import math
from enum import Enum
from typing import NamedTuple, Tuple, List
from src.utils import clamp


class Type(str, Enum):
    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    ELECTRIC = "electric"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DARK = "dark"
    DRAGON = "dragon"
    STEEL = "steel"
    FAIRY = "fairy"
    NONE = "none"


class Stats(NamedTuple):
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int


class StatusEffect(Enum):
    POISON = ("poison", 1.5)
    BURN = ("burn", 1.5)
    PARALYSIS = ("paralysis", 1.5)
    SLEEP = ("sleep", 2)
    FREEZE = ("freeze", 2)
    NONE = ("none", 1)

    def __init__(self, status_name: str, modifier: float):
        self.status_name = status_name
        self.modifier = modifier

    @classmethod
    def from_string(cls, name: str):
        mapping = {effect.value[0]: effect for effect in cls}
        return mapping.get(name.lower(), cls.NONE)

class Pokemon:
    def __init__(
        self,
        name: str,
        type: Tuple[Type, Type],
        current_hp_percentage: float,
        status_effect: StatusEffect,
        level: int,
        stats: Stats,
        catch_rate: int,
        weight: float,
    ):

        self._name = name  # Underscored variables denote "private"
        self._type = type
        self._stats = stats
        self._catch_rate = catch_rate
        self._weight = weight

        self.status_effect = status_effect
        self.level = level

        self.set_current_hp(current_hp_percentage)

    @property  # Property annotation for read-only attributes
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def stats(self):
        return self._stats
    
    @property
    def catch_rate(self):
        return self._catch_rate

    @property
    def weight(self):
        return self._weight

    @property
    def max_hp(self):
        base_hp = self._stats.hp
        level = self.level

        # Real max hp formula includes EVs and IVs, this is a simplification
        return math.floor(0.01 * (2 * base_hp) + level + 10)

    def set_current_hp(self, hp_percentage: float):
        self.current_hp = math.floor(clamp(0, hp_percentage, 1)  * self.max_hp)
    
    def set_status_effect(self, effect: StatusEffect):
        self.status_effect = effect

    def damage(self, percentage: float):
        self.current_hp -= max(0, self.max_hp * (clamp(0, percentage, 1)))

    def level_up(self):
        self.level += 1
        self.set_current_hp(1)

    def __str__(self):
        return (
            f"{self.name} (Level {self.level})\n"
            f"Type: {self.type[0].name}" + (f" / {self.type[1].name}" if self.type[1] else "") + "\n"
            f"HP: {self.current_hp}/{self.max_hp}\n"
            f"Status: {self.status_effect.name}\n"
            f"Stats: {self.stats}\n"
            f"Catch Rate: {self.catch_rate}, Weight: {self.weight}kg"
        )


class PokemonFactory:
    def __init__(self, src_file="pokemon.json"):
        self._src_file = src_file
        with open(self._src_file, "r") as c:
            self.pokemon_db = json.load(c)

    def create(
        self, name: str, level: int, status: StatusEffect, hp_percentage: float
    ) -> Pokemon:
        if hp_percentage < 0 or hp_percentage > 1:
            raise ValueError("hp has to be value between 0 and 1")
        if name.lower() not in self.pokemon_db:
            raise ValueError("Not a valid pokemon")
        poke = self.pokemon_db[name]

        t1, t2 = poke["type"]
        type = (Type(t1.lower()), Type(t2.lower()))
        stats = Stats(*poke["stats"])

        new_pokemon = Pokemon(
            name, type, hp_percentage, status, level, stats, poke["catch_rate"], poke["weight"]
        )
        return new_pokemon
    
    def create_many(
            self, pokemon_list: List[str], level=1, status: StatusEffect = StatusEffect.NONE, hp_percentage = 1
    ) -> List[Pokemon]:
        to_return = []
        for pokemon_name in pokemon_list:
            if pokemon_name.lower() not in self.pokemon_db:
                raise ValueError("Not a valid pokemon")
            poke = self.pokemon_db[pokemon_name]
            
            t1, t2 = poke["type"]
            type = (Type(t1.lower()), Type(t2.lower()))
            stats = Stats(*poke["stats"])

            to_return.append(Pokemon(
                pokemon_name, type, hp_percentage, status, level, stats, poke["catch_rate"], poke["weight"]
            ))
        return to_return
        

    def create_all(self, level=1) -> list[Pokemon]:
        pokemons = []
        for name in self.pokemon_db:
            poke = self.pokemon_db[name]
            t1, t2 = poke["type"]
            type = (Type(t1.lower()), Type(t2.lower()))
            stats = Stats(*poke["stats"])
            pokemons.append(Pokemon(
                name, type, 1, StatusEffect.NONE, level, stats, poke["catch_rate"], poke["weight"]
            ))
        return pokemons
