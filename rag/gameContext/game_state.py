from dataclasses import dataclass, field
from typing import List
#Clase para guardar el estado de la partida que indica el jugador y pasarla como contexto más tarde.
@dataclass
class GameState:
    phase: str # Fase de la partida en la que se encuentra.
    level: int # Nivel en el que está.
    gold: int # Cuánto oro tiene el usuario.
    champions: List[str] = field(default_factory=list) # Lista de campeones que tiene en el momento el usuario. La opción field(default_factory=list) devuelve listas vacías en caso de que el usuario no proporcione nada.
    items: List[str] = field(default_factory=list) # Lista de objetos que tiene en el momento el usuario.