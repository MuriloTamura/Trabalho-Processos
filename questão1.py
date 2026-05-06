import json
import random
import math
from collections import deque
from copy import deepcopy

# ─────────────────────────────────────────────
#  CONFIG (JSON do enunciado + processos extras)
# ─────────────────────────────────────────────
CONFIG = {
    "spec_version": "1.0",
    "challenge_id": "rr_srtf_preemptivo_demo",
    "metadata": {
        "context_switch_cost": 1,
        "throughput_window_T": 100,
        "algorithms": ["RR", "SRTF"],
        "rr_quantums": [1, 2, 4, 8, 16]
    },
    "workload": {
        "time_unit": "ticks",
        "processes": [
            {"pid": "P01", "arrival_time": 0,  "burst_time": 5},
            {"pid": "P02", "arrival_time": 1,  "burst_time": 17},
            {"pid": "P03", "arrival_time": 2,  "burst_time": 3},
            {"pid": "P04", "arrival_time": 4,  "burst_time": 22},
            {"pid": "P05", "arrival_time": 6,  "burst_time": 7},
            # processos extras com burst time longo (T3-T4 range)
            {"pid": "P06", "arrival_time": 0,  "burst_time": 45},
            {"pid": "P07", "arrival_time": 3,  "burst_time": 38},
            {"pid": "P08", "arrival_time": 5,  "burst_time": 52},
        ]
    }
}

SEED = 42
CTX  = CONFIG["metadata"]["context_switch_cost"]
T_WIN = CONFIG["metadata"]["throughput_window_T"]
PROCS = CONFIG["workload"]["processes"]

# ─────────────────────────────────────────────
#  ESTRUTURAS AUXILIARES
# ─────────────────────────────────────────────
class Process:
    def __init__(self, pid, arrival, burst):
        self.pid          = pid
        self.arrival      = arrival
        self.burst        = burst
        self.remaining    = burst
        self.start_time   = None   # primeira execução
        self.finish_time  = None
        self.response_time = None
        self.turnaround   = None

def make_processes():
    return [Process(p["pid"], p["arrival_time"], p["burst_time"]) for p in PROCS]

def compute_metrics(procs, timeline, T=T_WIN):
    finished = [p for p in procs if p.finish_time is not None]
    resp  = [p.response_time for p in finished]
    turn  = [p.turnaround    for p in finished]
    n = len(finished)

    avg_resp = sum(resp)/n if n else 0
    std_resp = math.sqrt(sum((r - avg_resp)**2 for r in resp)/n) if n else 0
    avg_turn = sum(turn)/n if n else 0
    std_turn = math.sqrt(sum((t - avg_turn)**2 for t in turn)/n) if n else 0

    # throughput: processos concluídos até T
    completed_in_T = sum(1 for p in finished if p.finish_time <= T)
    throughput = completed_in_T / T

    return {
        "avg_response": avg_resp, "std_response": std_resp,
        "avg_turnaround": avg_turn, "std_turnaround": std_turn,
        "throughput": throughput,
        "completed_in_T": completed_in_T,
        "n_finished": n
    }

# ─────────────────────────────────────────────
#  ROUND ROBIN
# ─────────────────────────────────────────────
def simulate_rr(quantum):
    rng = random.Random(SEED)
    procs = make_processes()
    ready = deque()
    timeline = []       # lista de (tick, pid | "CTX" | "IDLE")
    t = 0
    last_pid = None
    proc_map = {p.pid: p for p in procs}
    arrived  = set()

    def enqueue_arrivals():
        newcomers = [p for p in procs if p.arrival <= t and p.pid not in arrived and p.remaining > 0]
        # embaralha chegadas simultâneas (seed fixa)
        if len(newcomers) > 1:
            rng.shuffle(newcomers)
        for p in newcomers:
            arrived.add(p.pid)
            ready.append(p)

    enqueue_arrivals()

    while any(p.remaining > 0 for p in procs):
        enqueue_arrivals()

        if not ready:
            timeline.append((t, "IDLE"))
            t += 1
            enqueue_arrivals()
            continue

        # pega próximo processo
        current = ready.popleft()

        # custo de troca de contexto (se mudou de processo)
        if last_pid is not None and last_pid != current.pid:
            timeline.append((t, "CTX"))
            t += 1
            enqueue_arrivals()

        if current.remaining <= 0:
            continue

        # registra primeira execução
        if current.start_time is None:
            current.start_time   = t
            current.response_time = t - current.arrival

        # executa até quantum ou fim
        run = min(quantum, current.remaining)
        for _ in range(run):
            timeline.append((t, current.pid))
            t += 1
            current.remaining -= 1
            enqueue_arrivals()
            if current.remaining == 0:
                break

        last_pid = current.pid

        if current.remaining == 0:
            current.finish_time = t
            current.turnaround  = t - current.arrival
        else:
            # recoloca no final da fila, mas primeiro adiciona recém-chegados
            ready.append(current)

    return procs, timeline

# ─────────────────────────────────────────────
#  SRTF  (Shortest Remaining Time First - preemptivo)
# ─────────────────────────────────────────────
def simulate_srtf():
    rng = random.Random(SEED)
    procs = make_processes()
    timeline = []
    t = 0
    last_pid = None

    def get_ready():
        return [p for p in procs if p.arrival <= t and p.remaining > 0]

    while any(p.remaining > 0 for p in procs):
        ready = get_ready()
        if not ready:
            timeline.append((t, "IDLE"))
            t += 1
            last_pid = None
            continue

        # escolhe menor remaining; empate → aleatório (seed fixa)
        min_rem = min(p.remaining for p in ready)
        candidates = [p for p in ready if p.remaining == min_rem]
        current = rng.choice(candidates) if len(candidates) > 1 else candidates[0]

        # custo de troca de contexto
        if last_pid is not None and last_pid != current.pid:
            timeline.append((t, "CTX"))
            t += 1
            # após CTX, o processo escolhido assume (não reavalia)
            # mas se chegou algo mais curto, reavalia no próximo tick

        # registra primeira execução
        if current.start_time is None:
            current.start_time    = t
            current.response_time = t - current.arrival

        timeline.append((t, current.pid))
        current.remaining -= 1
        last_pid = current.pid
        t += 1

        if current.remaining == 0:
            current.finish_time = t
            current.turnaround  = t - current.arrival

    return procs, timeline

# ─────────────────────────────────────────────
#  FORMATAÇÃO DE SAÍDA
# ─────────────────────────────────────────────
SEP = "─" * 70

def fmt_timeline(timeline, max_show=80):
    """Comprime a timeline para display."""
    seq = []
    i = 0
    while i < len(timeline):
        tick, label = timeline[i]
        j = i
        while j < len(timeline) and timeline[j][1] == label:
            j += 1
        count = j - i
        if count > 1:
            seq.append(f"{label}×{count}")
        else:
            seq.append(label)
        i = j
    full = " → ".join(seq)
    if len(full) > 300:
        full = full[:300] + " …"
    return full

def print_results(label, procs, timeline, metrics):
    print(f"\n{'═'*70}")
    print(f"  {label}")
    print(f"{'═'*70}")

    # tabela de processos
    print(f"\n{'PID':>5} {'Arr':>5} {'Burst':>6} {'Start':>6} {'Finish':>7} {'Resp':>5} {'Turn':>5}")
    print(SEP)
    for p in sorted(procs, key=lambda x: x.pid):
        s  = p.start_time  if p.start_time  is not None else "-"
        f  = p.finish_time if p.finish_time is not None else "-"
        r  = p.response_time if p.response_time is not None else "-"
        tu = p.turnaround    if p.turnaround    is not None else "-"
        print(f"{p.pid:>5} {p.arrival:>5} {p.burst:>6} {str(s):>6} {str(f):>7} {str(r):>5} {str(tu):>5}")

    print(f"\n  Resp  médio : {metrics['avg_response']:.2f} ± {metrics['std_response']:.2f}")
    print(f"  Turn  médio : {metrics['avg_turnaround']:.2f} ± {metrics['std_turnaround']:.2f}")
    print(f"  Vazão (T={T_WIN}): {metrics['completed_in_T']} proc / {T_WIN} ticks = {metrics['throughput']:.4f} proc/tick")

    print(f"\n  Sequência de execução:")
    print(f"  {fmt_timeline(timeline)}")

def print_comparison_table(results):
    """Tabela comparativa de todas as configurações."""
    print(f"\n\n{'═'*70}")
    print("  TABELA COMPARATIVA")
    print(f"{'═'*70}")
    print(f"{'Algoritmo':>16} {'Resp Méd':>10} {'Resp Std':>10} {'Turn Méd':>10} {'Turn Std':>10} {'Vazão':>8}")
    print(SEP)
    for label, metrics in results:
        print(f"{label:>16} {metrics['avg_response']:>10.2f} {metrics['std_response']:>10.2f} "
              f"{metrics['avg_turnaround']:>10.2f} {metrics['std_turnaround']:>10.2f} "
              f"{metrics['throughput']:>8.4f}")

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    print(f"\n{'═'*70}")
    print("  SIMULADOR DE ESCALONAMENTO – RR vs SRTF")
    print(f"  Context-switch cost: {CTX} tick(s) | Throughput window T={T_WIN}")
    print(f"  Seed aleatória: {SEED}")
    print(f"{'═'*70}")

    print("\n  PROCESSOS DO WORKLOAD:")
    print(f"{'PID':>5} {'Arrival':>8} {'Burst':>6}")
    print(SEP)
    for p in PROCS:
        print(f"  {p['pid']:>4}  {p['arrival_time']:>6}  {p['burst_time']:>6}")

    all_results = []

    # ── RR com diferentes quantums ──
    for q in CONFIG["metadata"]["rr_quantums"]:
        procs, tl = simulate_rr(q)
        m = compute_metrics(procs, tl)
        label = f"RR  (Q={q:>2})"
        print_results(label, procs, tl, m)
        all_results.append((label, m))

    # ── SRTF ──
    procs, tl = simulate_srtf()
    m = compute_metrics(procs, tl)
    label = "SRTF"
    print_results(label, procs, tl, m)
    all_results.append((label, m))

    # ── Comparativo ──
    print_comparison_table(all_results)

    # ── Análise textual ──
    print(f"\n\n{'═'*70}")
    print("  ANÁLISE: VANTAGENS E DESVANTAGENS")
    print(f"{'═'*70}")
    analysis = """
  ROUND ROBIN (RR)
  ┌ Vantagens:
  │  • Justo: todos os processos recebem CPU periodicamente
  │  • Tempo de resposta previsível – bom para sistemas interativos
  │  • Sem inanição: nenhum processo espera indefinidamente
  └ Desvantagens:
     • Quantum pequeno → muitas trocas de contexto → overhead elevado
     • Quantum grande → degenera para FCFS, resposta piora
     • Ignora o tamanho do burst → penaliza processos curtos

  SRTF  (Shortest Remaining Time First – preemptivo)
  ┌ Vantagens:
  │  • Minimiza o tempo médio de retorno (ótimo teórico)
  │  • Processos curtos terminam rapidamente (alta vazão para curtos)
  └ Desvantagens:
     • Inanição: processos longos podem esperar muito
     • Requer conhecimento prévio do burst time (impossível na prática)
     • Overhead de preempção frequente quando chegam processos curtos

  COMPORTAMENTO COM DOIS GRUPOS DE BURST TIME
  • Processos curtos (P01-P05, burst 3-22): SRTF os favorece muito;
    RR com Q grande os prejudica ao deixar processos longos monopolizar.
  • Processos longos (P06-P08, burst 38-52): RR garante progresso
    contínuo; SRTF os posterga enquanto houver processos curtos prontos.
"""
    print(analysis)

if __name__ == "__main__":
    main()
