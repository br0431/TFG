"""
bertscore_eval.py - Calcula BERTScore F1 entre respuesta esperada y respuesta del sistema.
Ejecuta la evaluacion sobre los pares de respuestas del Excel de resultados y muestra
el score individual por pregunta, por nivel y la media global.
"""

from bert_score import score as bert_score

# Modelo multilingue para evaluar tanto castellano como ingles.
MODEL = "bert-base-multilingual-cased"

# PARES CASTELLANO

PAIRS_ES = [
    # Nivel 1
    {
        "nivel": 1,
        "pregunta": "Que hace el objeto Filo Infinito?",
        "esperada": "Infinity Edge hace que las habilidades del portador puedan golpear criticamente. Si ya pueden, otorga un 10% de dano de impacto critico adicional.",
        "sistema": "El item Infinity Edge hace que las habilidades del portador puedan golpear criticamente. Si las habilidades ya pueden golpear criticamente, el portador obtiene un 10% de dano de impacto critico en lugar de eso.",
    },
    {
        "nivel": 1,
        "pregunta": "Cuales son las sinergias de Aatrox?",
        "esperada": "Las sinergias de Aatrox son Darkin, World Ender y Slayer.",
        "sistema": "Los traits de Aatrox son Darkin, World Ender y Slayer.",
    },
    {
        "nivel": 1,
        "pregunta": "Con que componentes se construye la Sanguinaria?",
        "esperada": "Bloodthirster se construye con un Bfsword y una Negatroncloak.",
        "sistema": "La Bloodthirster se construye con un Bfsword y una Negatroncloak.",
    },
    {
        "nivel": 1,
        "pregunta": "De que coste es Fiddlesticks?",
        "esperada": "Fiddlesticks es un campeon de coste 5.",
        "sistema": "Fiddlesticks cuesta 5.",
    },
    {
        "nivel": 1,
        "pregunta": "Que bonificaciones da la Mejora Azul?",
        "esperada": "Blue Buff da un 15% de dano de ataque, 15 de poder de habilidad y 5 de regeneracion de mana.",
        "sistema": "La Blue Buff da un 10% de bonus adicional en Ataque y Poder Magico desde todas las fuentes.",
    },
    # Nivel 2
    {
        "nivel": 2,
        "pregunta": "Que objetos son los mejores para Miss Fortune?",
        "esperada": "Los mejores objetos para Miss Fortune son Captain's Brew, Dead Man's Dagger y First Mate's Flintlock.",
        "sistema": "Los mejores items para Miss Fortune son Captain's Brew y Dead Man's Dagger.",
    },
    {
        "nivel": 2,
        "pregunta": "Que composicion incluye a Sona y Poppy?",
        "esperada": "La composicion que incluye a Sona y Poppy es Demacia Lux.",
        "sistema": "La composicion que incluye a Sona y Poppy es la Demacia Lux.",
    },
    {
        "nivel": 2,
        "pregunta": "Que diferencia hay entre Filo Mortal y Filo Infinito?",
        "esperada": "Deathblade otorga dano fisico y amplificacion de dano, mientras que Infinity Edge otorga dano critico y probabilidad de critico.",
        "sistema": "La diferencia entre Deathblade y Infinity Edge es que Deathblade otorga un aumento del 55% en AD (Ataque Fisico) y un aumento del 10% en el dano, mientras que Infinity Edge otorga un aumento del 35% en AD y un aumento del 35% en la probabilidad de critico.",
    },
    {
        "nivel": 2,
        "pregunta": "Que rol tiene el campeon Nautilus y el campeon Graves?",
        "esperada": "Nautilus tiene el rol de Magic Tank y Graves tiene el rol de Attack Fighter.",
        "sistema": "El campeon Nautilus tiene el rol de Magic Tank y el campeon Graves tiene el rol de Attack Fighter.",
    },
    {
        "nivel": 2,
        "pregunta": "El objeto Chaleco de Zarzas es bueno para un tanque?",
        "esperada": "Si, Bramble Vest es un buen objeto para un tanque porque le da armadura.",
        "sistema": "El Bramble Vest es un buen item para un tanque porque le da armadura (+65) y reduce el dano recibido en ataques. Ademas, cuando es golpeado por cualquier ataque, hace dano magico a los enemigos adyacentes.",
    },
    # Nivel 3
    {
        "nivel": 3,
        "pregunta": "Tengo un Espadon y una Lagrima de la Diosa, que objeto me fabrico y a quien se lo pongo?",
        "esperada": "Fabricar la Spear of Shojin y equiparlo a un campeon que dependa del uso del mana.",
        "sistema": "Con los componentes Bfsword y Tearofthegoddess, te fabricas un Spear of Shojin. Puedes equiparlo en cualquier campeon que lo necesite.",
    },
    {
        "nivel": 3,
        "pregunta": "Que composicion me recomiendas si tengo a Garen, Lux y Poppy en mesa?",
        "esperada": "Con Garen, Lux y Poppy en mesa se recomienda jugar la composicion Demacia Lux.",
        "sistema": "Con Garen, Lux y Poppy en el tablero, te recomiendo la composicion Demacia Lux. Esta composicion incluye a Sona y otros campeones como Galio, Xin Zhao y Jarvan IV, que se complementan bien con los campeones que ya tienes. A nivel 9, se agrega Ornn a esta composicion, lo que puede ser util para completarla.",
    },
    {
        "nivel": 3,
        "pregunta": "Tengo Mejora Azul y Guantelete Enjoyado, a que campeon le viene mejor en una composicion de Demacia?",
        "esperada": "Lux es el campeon que mas se beneficia ya que Blue Buff y Jeweled Gauntlet son sus objetos perfectos.",
        "sistema": "Con Blue Buff y Jeweled Gauntlet, te recomiendo equipar a Lux en una composicion de Demacia. Ambos objetos son parte de los mejores items para Lux, segun su ficha.",
    },
    {
        "nivel": 3,
        "pregunta": "Si mi rival lleva mucho dano magico, que objetos son defensivos para este tipo de dano?",
        "esperada": "Los objetos defensivos contra dano magico son los que se fabrican con una Negatron Cloak.",
        "sistema": "No hay informacion en los documentos sobre items defensivos contra dano magico.",
    },
    {
        "nivel": 3,
        "pregunta": "Si quiero que mi tanque tenga mucha vida, es mejor Capa de Fuego Solar o Corazon Resuelto?",
        "esperada": "Ambos son buenos, Steadfast Heart da mas vida base (250) pero Sunfire Cape da mas vida en total gracias a su pasiva.",
        "sistema": "Si quieres que tu tanque tenga mucha vida, te recomiendo el item Steadfast Heart porque le da mas vida (+250) en comparacion con el Sunfire Cape (+150). Ademas, el Steadfast Heart tiene un bonus de durabilidad (+10%) mientras este por encima del 50% de vida.",
    },
]

# PARES INGLÉS

PAIRS_EN = [
    # Nivel 1
    {
        "nivel": 1,
        "pregunta": "What does the item Infinity Edge do?",
        "esperada": "Infinity Edge allows the holder's abilities to critically strike. If they can already critically strike, it grants 10% additional Critical Strike Damage.",
        "sistema": "Infinity Edge gives the holder's abilities a 35% chance to critically strike. If their abilities can already critically strike, it instead grants 10% Critical Strike Damage.",
    },
    {
        "nivel": 1,
        "pregunta": "What are Aatrox's traits?",
        "esperada": "Aatrox's traits are Darkin, World Ender, and Slayer.",
        "sistema": "Aatrox has the following traits: Darkin, World Ender, Slayer.",
    },
    {
        "nivel": 1,
        "pregunta": "What components is Bloodthirster built from?",
        "esperada": "Bloodthirster is built from a Bfsword and a Negatroncloak.",
        "sistema": "Bloodthirster is built from a Bfsword and a Negatroncloak.",
    },
    {
        "nivel": 1,
        "pregunta": "What cost is Fiddlesticks?",
        "esperada": "Fiddlesticks is a 5 cost champion.",
        "sistema": "Fiddlesticks costs 5.",
    },
    {
        "nivel": 1,
        "pregunta": "What bonuses does Blue Buff give?",
        "esperada": "Blue Buff gives 15% Attack Damage, 15 Ability Power, and 5 Mana Regeneration.",
        "sistema": "Blue buff gives a bonus to gain 10% additional Attack Damage and Ability Power from all sources.",
    },
    # Nivel 2
    {
        "nivel": 2,
        "pregunta": "What are the best items for Miss Fortune?",
        "esperada": "The best items for Miss Fortune are Captain's Brew, Dead Man's Dagger, and First Mate's Flintlock.",
        "sistema": "Captain's Brew and Dead Man's Dagger are the best items for Miss Fortune.",
    },
    {
        "nivel": 2,
        "pregunta": "What composition includes Sona and Poppy?",
        "esperada": "The composition that includes Sona and Poppy is Demacia Lux.",
        "sistema": "The composition that includes Sona is Demacia Lux.",
    },
    {
        "nivel": 2,
        "pregunta": "What's the difference between Deathblade and Infinity Edge?",
        "esperada": "Deathblade grants Attack Damage and damage amplification, while Infinity Edge grants Critical Strike Damage and Critical Strike Chance.",
        "sistema": "Infinity Edge gives a bonus to Critical Chance and, if the holder's abilities can already critically strike, a bonus to Critical Strike Damage. Deathblade gives a bonus to Attack Damage and increases damage amplification by 10%.",
    },
    {
        "nivel": 2,
        "pregunta": "What role does Nautilus and Graves have?",
        "esperada": "Nautilus has the role of Magic Tank and Graves has the role of Attack Fighter.",
        "sistema": "Nautilus is a Magic Tank. Graves is an Attack Fighter.",
    },
    {
        "nivel": 2,
        "pregunta": "Is Bramble Vest good for a tank?",
        "esperada": "Yes, Bramble Vest is a good item for a tank because it provides armor.",
        "sistema": "Bramble Vest is not typically considered a tank item. It provides some armor and health, but its primary effect deals magic damage to adjacent enemies when struck by an attack. For a tank, items like Warmog's Armor or the ones listed as best for Braum (such as Dragon's Claw) might be more suitable.",
    },
    # Nivel 3
    {
        "nivel": 3,
        "pregunta": "I have a Bfsword and a Tearofthegoddess, what item should I craft and who should hold it?",
        "esperada": "Craft the Spear of Shojin and equip it to a champion that relies on the use of mana.",
        "sistema": "You have a Bfsword and a Tear of the Goddess. I would recommend crafting the Spear of Shojin, as it requires both components. The holder should be a champion that benefits from the additional AD and AP provided by this item.",
    },
    {
        "nivel": 3,
        "pregunta": "What composition do you recommend if I have Garen, Lux and Poppy on board?",
        "esperada": "With Garen, Lux and Poppy on board the recommended composition is Demacia Lux.",
        "sistema": "Based on the champions you have on board (Garen, Lux, and Poppy), I would recommend a composition that synergizes with Demacia Lux. This comp is well-suited for Lux's abilities, and Garen can provide a strong frontline presence while Poppy offers crowd control. In this composition, Lux can take advantage of her abilities to deal magical damage from a distance, while Garen and Poppy work together to lock down enemies and protect Lux.",
    },
    {
        "nivel": 3,
        "pregunta": "I have Blue Buff and Jeweled Gauntlet, which champion benefits the most in a Demacia comp?",
        "esperada": "Lux benefits the most because Blue Buff and Jeweled Gauntlet are her best in slot items.",
        "sistema": "Based on the items you have (Blue Buff and Jeweled Gauntlet), I would recommend Lux as the champion who benefits the most in a Demacia comp. This is because Blue Buff is one of Lux's best items, and she synergizes well with other champions in the Demacia Lux composition.",
    },
    {
        "nivel": 3,
        "pregunta": "If my opponent is dealing heavy magic damage, what items are defensive against that type of damage?",
        "esperada": "Defensive items against magic damage are those built from a Negatron Cloak.",
        "sistema": "If your opponent is dealing heavy magic damage, I would recommend using items that provide Magic Resistance (MR) or have a bonus that counters magical damage. Protector's Vow has a high MR value, but it also provides a shield at 40% Health, which can be beneficial in various situations. Evenshroud offers additional MR and a Sunder effect that reduces enemy armor, making it harder for them to deal physical damage. However, if you're looking specifically for items that counter magic damage, I couldn't find any information on such items in the provided documents.",
    },
    {
        "nivel": 3,
        "pregunta": "If I want my tank to have high health, is Sunfire Cape or Steadfast Heart better?",
        "esperada": "Both are good, Steadfast Heart gives more base health (250) but Sunfire Cape gives more total health thanks to its passive.",
        "sistema": "Based on the provided information, if you want your tank to have high health, I would recommend Steadfast Heart. It provides more health (+250) compared to Sunfire Cape (+150).",
    },
]


def compute_bertscore(pairs, lang):
    """Calcula BERTScore F1 para una lista de pares."""
    refs = [p["esperada"] for p in pairs]
    cands = [p["sistema"] for p in pairs]

    _, _, f1 = bert_score(
        cands=cands,
        refs=refs,
        model_type=MODEL,
        lang=lang,
        verbose=False,
    )

    return f1.tolist()


def print_results(pairs, scores, label):
    """Muestra los resultados por pregunta, por nivel y media global."""

    print(f"\n{'=' * 70}")
    print(f"  {label}")
    print(f"{'=' * 70}")

    current_level = None
    level_scores = {}

    for pair, f1 in zip(pairs, scores):
        nivel = pair["nivel"]

        if nivel != current_level:
            current_level = nivel
            level_labels = {1: "Consulta directa", 2: "Relacional", 3: "Razonamiento complejo"}
            print(f"\n  -- Nivel {nivel} - {level_labels[nivel]} --")

        print(f"    {pair['pregunta'][:65]}")
        print(f"    BERTScore F1: {f1:.4f}")
        print()

        if nivel not in level_scores:
            level_scores[nivel] = []
        level_scores[nivel].append(f1)

    # Media por nivel
    print(f"  -- Medias por nivel --")
    for nivel in sorted(level_scores):
        avg = sum(level_scores[nivel]) / len(level_scores[nivel])
        print(f"    Nivel {nivel}: {avg:.4f}")

    # Media global
    avg_global = sum(scores) / len(scores)
    print(f"\n  Media global: {avg_global:.4f}")
    print(f"  Rango: {min(scores):.4f} - {max(scores):.4f}")

    return avg_global


def main():
    print("Calculando BERTScore F1...")
    print(f"Modelo: {MODEL}\n")

    print("Procesando pares en castellano...")
    scores_es = compute_bertscore(PAIRS_ES, "es")
    avg_es = print_results(PAIRS_ES, scores_es, "CASTELLANO")

    print("\nProcesando pares en ingles...")
    scores_en = compute_bertscore(PAIRS_EN, "en")
    avg_en = print_results(PAIRS_EN, scores_en, "ENGLISH")

    # Resumen final
    print(f"\n{'=' * 70}")
    print(f"  RESUMEN FINAL")
    print(f"{'=' * 70}")
    print(f"  Castellano - Media F1: {avg_es:.4f}")
    print(f"  English    - Media F1: {avg_en:.4f}")
    avg_total = (avg_es + avg_en) / 2
    print(f"  Global     - Media F1: {avg_total:.4f}")


if __name__ == "__main__":
    main()