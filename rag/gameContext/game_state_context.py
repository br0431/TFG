import json
import re
from pathlib import Path

from game_state import GameState
# Rutas
ROOT = Path(__file__).resolve().parent.parent
CHAMPIONS_DIR = ROOT / "scrapping" / "data" / "champions"
ITEMS_DIR = ROOT / "scrapping" / "data" / "items"
# Patrón de las fases, las fases de la partida siempre siguen un patrón 3-1 hasta la 3-7, 4-1 hasta las 4-7...
PHASE_PATTERN = re.compile(r"^[1-7]-[1-7]$")

def _load_names(directory: Path) -> list[str]:
    """Cargamos todos los nombres de los campeones válidos desde los JSONs del directorio del scrapping"""
    names = []
    for f in directory.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        names.append(data["name"])
    return sorted(names)


def _name_match(value: str, valid: list[str]) -> str | None:
    """
    Comparamos el valor que ha introducido el usuario con los presentes en la lista de nombres válidos ignorando las mayúsculas y las minúsculas
    y se devuelve el nombre oficial si hay coincidencia, en caso de que no haya se devuelve un None.
    """
    value_lower = value.strip().lower()
    for name in valid:
        if name.lower() == value_lower:
            return name
    return None


def _ask_phase() -> str:
    """
    Solicitamos la fase actual hasta que el formato sea el correcto, para eso implementamos un bucle hasta que el usuario introduzca un valor correcto.
    """
    while True:
        raw = input("Fase actual (ej. 3-2): ").strip()
        if PHASE_PATTERN.match(raw):
            return raw
        print(f"  Formato incorrecto. Usa el formato X-Y (ejemplo: 3-2).")


def _ask_level() -> int:
    """
    Al igual que en la anterior función, solicitamos el nivel actual e implementamos bucle hasta que el valor sea correcto.
    """
    while True:
        raw = input("Nivel actual (1-9): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 9:
            return int(raw)
        print("  El nivel debe ser un número entre 1 y 9.")


def _ask_gold() -> int:
    """
    Solicitamos el oro disponible en el momento del jugador, lo único que se valida es que el valor sea positivo también con un bucle.
    """
    while True:
        raw = input("Oro actual: ").strip()
        if raw.isdigit():
            return int(raw)
        print("  Introduce un número válido. El número no puede ser negativo")


def _ask_list(prompt: str, valid: list[str]) -> list[str]:
    """
    Pide al usuario una lista de nombres separados por comas y los valida contra la lista de nombres oficiales que devuelve la función _name_match.
    Si no se reconoce un nombre se omite y se notifica al usuario.
    """
    print(f"{prompt} (separados por comas, ENTER para omitir):")
    raw = input("> ").strip()
    if not raw:
        return []

    selected = []
    unknown = []
    # Para cada entrada separada por comas de lo que escribe el usuario, se comprueba que el nombre sea válido.
    for entry in raw.split(","):
        match = _name_match(entry, valid)
        # Si el nombre es válido se añade a la lista para el contexto.
        if match:
            selected.append(match)
        # Si no es válido se añade a una lista de campeones no reconocidos.
        else:
            unknown.append(entry.strip())

    if unknown:
        print(f"  No reconocidos y omitidos: {', '.join(unknown)}")
    # Devolvemos la lista de campeones seleccionados y validados.
    return selected


def collect_game_state() -> GameState:
    """
    Es la función principal de este script y la única que no es privada.
    Se alimenta de todas las demas funciones y orquesta la recogida de todos los datos que introduce el usuario y que han sido validados.
    Devuelve un GameState con el contexto completo de la partida.
    """

    # Cargamos todos los nombres válidos de los JSONs para poder validar lo introducido por el usuario.
    valid_champions = _load_names(CHAMPIONS_DIR)
    valid_items = _load_names(ITEMS_DIR)

    print("\n=== Situación de partida actual ===\n")
    # Recogemos los datos.
    phase = _ask_phase()
    level = _ask_level()
    gold = _ask_gold()
    champions = _ask_list("Campeones en tablero y en el banquillo", valid_champions)
    items = _ask_list("Ítems disponibles", valid_items)
    # Construimos el objeto GameState con todos los datos recogidos.
    state = GameState(
        phase=phase,
        level=level,
        gold=gold,
        champions=champions,
        items=items,
    )

    print("\n=== Contexto guardado ===")
    print(f"  Fase:      {state.phase}")
    print(f"  Nivel:     {state.level}")
    print(f"  Oro:       {state.gold}")
    print(f"  Campeones: {', '.join(state.champions) or '—'}")
    print(f"  Ítems:     {', '.join(state.items) or '—'}")

    return state


if __name__ == "__main__":
    game_state = collect_game_state()
