import json


entrada = {
    "spec_version": "1.0",
    "challenge_id": "vet_room_protocol_demo",
    "metadata": {
        "room_count": 1,
        "allowed_states": ["EMPTY", "DOGS", "CATS"],
        "sign_change_latency": 0,
        "tie_breaker": ["arrival_time", "id"]
    },
    "room": {
        "initial_sign_state": "EMPTY"
    },
    "workload": {
        "time_unit": "ticks",
        "animals": [
            {"id": "D01", "species": "DOG", "arrival_time": 0, "rest_duration": 5},
            {"id": "C01", "species": "CAT", "arrival_time": 1, "rest_duration": 4},
            {"id": "D02", "species": "DOG", "arrival_time": 2, "rest_duration": 6},
            {"id": "C02", "species": "CAT", "arrival_time": 3, "rest_duration": 2},
            {"id": "D03", "species": "DOG", "arrival_time": 4, "rest_duration": 3}
        ]
    }
}


def nome_estado(especie):
    if especie == "DOG":
        return "DOGS"
    if especie == "CAT":
        return "CATS"
    return "EMPTY"


def simular(dados, modo_justo=False):
    animais = sorted(
        dados["workload"]["animals"],
        key=lambda a: (a["arrival_time"], a["id"])
    )

    tempo = 0
    indice = 0
    sala = []
    espera = []
    estado = None
    finalizados = 0
    eventos = []
    resultado = {}

    while finalizados < len(animais):
        mudou = False

        saindo = [item for item in sala if item["saida"] <= tempo]
        for item in saindo:
            animal = item["animal"]
            eventos.append(f"t={tempo:02d} | {animal['id']} saiu da sala")
            finalizados += 1
            mudou = True

        sala = [item for item in sala if item["saida"] > tempo]

        if not sala and estado is not None:
            estado = None
            eventos.append(f"t={tempo:02d} | placa -> EMPTY")

        while indice < len(animais) and animais[indice]["arrival_time"] <= tempo:
            animal = animais[indice]
            espera.append(animal)
            eventos.append(f"t={tempo:02d} | {animal['id']} chegou ({animal['species']})")
            indice += 1
            mudou = True

        espera.sort(key=lambda a: (a["arrival_time"], a["id"]))

        especie_para_entrar = None

        if estado is None and espera:
            especie_para_entrar = espera[0]["species"]
            estado = especie_para_entrar
            eventos.append(f"t={tempo:02d} | placa -> {nome_estado(estado)}")

        elif estado is not None:
            existe_mesma_especie = any(a["species"] == estado for a in espera)
            existe_especie_oposta = any(a["species"] != estado for a in espera)

            if not modo_justo and existe_mesma_especie:
                especie_para_entrar = estado

            if modo_justo and existe_mesma_especie and not existe_especie_oposta:
                especie_para_entrar = estado

        if especie_para_entrar is not None:
            entrando = [a for a in espera if a["species"] == especie_para_entrar]
            espera = [a for a in espera if a["species"] != especie_para_entrar]

            for animal in entrando:
                saida = tempo + animal["rest_duration"]
                sala.append({"animal": animal, "saida": saida})

                resultado[animal["id"]] = {
                    "chegada": animal["arrival_time"],
                    "entrada": tempo,
                    "saida": saida,
                    "espera": tempo - animal["arrival_time"]
                }

                eventos.append(
                    f"t={tempo:02d} | {animal['id']} entrou | sai em t={saida:02d}"
                )

            mudou = True

        if not mudou:
            proximos_tempos = []

            if indice < len(animais):
                proximos_tempos.append(animais[indice]["arrival_time"])

            if sala:
                proximos_tempos.append(min(item["saida"] for item in sala))

            tempo = min(t for t in proximos_tempos if t > tempo)
        else:
            continue

    return eventos, resultado


def imprimir(titulo, eventos, resultado):
    print("\n" + titulo)
    print("-" * len(titulo))

    for evento in eventos:
        print(evento)

    print("\nResumo:")
    for animal_id, dados in sorted(resultado.items()):
        print(
            f"{animal_id}: chegou={dados['chegada']}, "
            f"entrou={dados['entrada']}, saiu={dados['saida']}, "
            f"esperou={dados['espera']}"
        )


eventos_injusto, resultado_injusto = simular(entrada, modo_justo=False)
eventos_justo, resultado_justo = simular(entrada, modo_justo=True)

imprimir("Solução com possibilidade de inanição", eventos_injusto, resultado_injusto)
imprimir("Solução sem possibilidade de inanição", eventos_justo, resultado_justo)
