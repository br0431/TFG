def get_decisions(phase: str, level: int, gold: int, hp: int, champions: list, items: list) -> dict:
    """
    Recibe el estado de partida del jugador y devuelve:
      - rules: lista de acciones recomendadas (reglas hardcodeadas basadas en mi conocimiento sobre el juego)
      - prompt: prompt enriquecido listo para pasarle al RAG
    """
    actions = []
    # variables para guardar cada parte de una fase y poder tratarlas de forma independiente y de forma compacta.
    stage, round_num = map(int, phase.split('-'))

    # REGLAS CENTRADAS EN LA FASE HARDCODEADAS

    if stage == 2:
        if round_num <= 3:
            actions.append("If you've won the first two rounds and are unsure if you can win the third, level up. If you can't make interest, try a pre-level.")
        if round_num >= 4:
            actions.append("Focus on economy and try to make interest.")

    if stage == 3:
        if round_num == 1:
            actions.append("Evaluate whether you can maintain your winning streak. If not, do not waste any gold and wait for 3-2 to level up to level 6.")
        if round_num == 2:
            actions.append("Level up to level 6.")
            if hp < 40:
                actions.append("Low health: Roll down to stabilize the board with solid units before continuing to make interest.")
            else:
                actions.append("If your board holds up, keep the gold for interest and prepare for the 4-2. Upgrade any units that if you are able to.")
        if round_num >= 5:
            actions.append("Start preparing your economy for the Phase 4-2 rolldown. Aim to reach 50+ gold to level up to 8 and roll.")

    if stage == 4:
        if round_num == 1:
            actions.append("Don't level up or roll yet. Save your gold for the rolldown at 4-2.")
        if round_num == 2:
            actions.append("Level up to level 8.")
            actions.append("Roll down until you find all your key composition units.")
            if gold < 20:
                actions.append("Low gold for the rolldown: prioritize the most important units, don't go for everything at once.")
        if round_num >= 3:
            if hp < 30:
                actions.append("Critical low HP: spend the necessary gold to stabilize the board even if you lose interest.")
            else:
                actions.append("If the board is stable, accumulate gold to advance to level 9 in the next phase.")

    if stage >= 5:
        actions.append("Consider upgrading to level 9 to complete the composition with the higher-cost units. You can also aim for a 3 star 4 cost unit.")
        if gold >= 30:
            actions.append("Do a final rolldown by finding the 4 and 5 cost units you are missing.")

    # REGLAS CENTRADAS EN ORO HARDCODEADAS

    if gold >= 50 and stage <4:
        actions.append(f"You have {gold} gold: good passive interest. Use it only if the board urgently needs it or if you can upgrade a unit. If not, wait for stage 4 to push level and build your final board.")
    elif gold < 50:
        actions.append("Right now you are not making the highest interest. If you are not in a delicate stage (3-2,4-2 or stage 5) focus on making 50 gold.")
    elif gold < 10 and stage >= 4:
        actions.append("Your gold is very low for this stage of the game. If you have more than 50 health, try to conserve some resources; otherwise, roll through every round until you stabilize.")

    # REGLAS CENTRADAS EN VIDA HARDCODEADAS

    if hp < 20:
        actions.append("Critical life (<20 HP): You need to stabilize NOW. Prioritize winning the next round over any economic strategy.")

    # PROMPT PARA EL RAG

    # unión de los elementos de una lista como un string para pasarselo al LLM.
    champ_str = ", ".join(champions) if champions else "none indicated"
    item_str  = ", ".join(items) if items else "none indicated"
    rules_str = "; ".join(actions)

    prompt = (
        f"The player is at stage {phase}, level {level}, "
        f"with {gold} gold and {hp} HP. "
        f"Current board/bench: {champ_str}. "
        f"Available items: {item_str}. "
        f"Tactical situation: {rules_str}. "
        f"What composition should they play with what they have? "
        f"What units should they look for and which ones are expendable?"
    )

    return {
        'rules': actions,
        'prompt': prompt
    }