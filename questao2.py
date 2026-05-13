import random
import threading
import time
from collections import deque
from datetime import datetime

PROGRAMMER_COUNT = 5
THINKING_TIME_RANGE = (1.0, 3.0)
COMPILATION_TIME_RANGE = (2.0, 4.0)
RANDOM_SEED = 42


class ResourceManager:
    """Controla os recursos de forma justa e sem deadlock."""

    def __init__(self, compiler_slots=1, database_slots=2):
        self.free_compilers = compiler_slots
        self.free_database_slots = database_slots
        self.condition = threading.Condition()
        self.waiting_queue = deque()

    def acquire(self, programmer_id):
        with self.condition:
            self.waiting_queue.append(programmer_id)

            while True:
                is_turn = self.waiting_queue[0] == programmer_id
                has_resources = self.free_compilers > 0 and self.free_database_slots > 0

                if is_turn and has_resources:
                    self.waiting_queue.popleft()
                    self.free_compilers -= 1
                    self.free_database_slots -= 1
                    return

                self.condition.wait()

    def release(self):
        with self.condition:
            self.free_compilers += 1
            self.free_database_slots += 1
            self.condition.notify_all()

    def snapshot(self):
        with self.condition:
            return {
                "free_compilers": self.free_compilers,
                "free_database_slots": self.free_database_slots,
                "queue": list(self.waiting_queue),
            }


resource_manager = ResourceManager()
state_lock = threading.Lock()
programmer_states = {f"P{i + 1}": "Inicializando" for i in range(PROGRAMMER_COUNT)}


def get_timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def print_all_states():
    snapshot = resource_manager.snapshot()
    print("-" * 70)
    print(
        f"Compilador livre: {snapshot['free_compilers']}/1 | "
        f"BD livre: {snapshot['free_database_slots']}/2"
    )
    print(f"Fila justa: {snapshot['queue'] or 'vazia'}")
    for pid, state in programmer_states.items():
        print(f"  {pid}: {state}")
    print("-" * 70 + "\n")


def update_state(programmer_id, state):
    with state_lock:
        programmer_states[programmer_id] = state
        print(f"[{get_timestamp()}] {programmer_id}: {state}")
        print_all_states()


def programmer_work(programmer_id):
    cycle = 1
    rng = random.Random(RANDOM_SEED + int(programmer_id[1:]))

    while True:
        update_state(programmer_id, f"Pensando (ciclo {cycle})")
        time.sleep(rng.uniform(*THINKING_TIME_RANGE))

        update_state(programmer_id, f"Entrou na fila de compilacao (ciclo {cycle})")
        resource_manager.acquire(programmer_id)

        update_state(programmer_id, f"Compilando com acesso ao BD (ciclo {cycle})")
        time.sleep(rng.uniform(*COMPILATION_TIME_RANGE))

        update_state(programmer_id, f"Compilacao concluida (ciclo {cycle})")
        resource_manager.release()
        update_state(programmer_id, f"Liberou compilador e BD (ciclo {cycle})")

        cycle += 1


def main():
    print("\n" + "=" * 70)
    print("SIMULACAO DA QUESTAO 2")
    print("5 programadores | 1 compilador exclusivo | 2 acessos ao BD")
    print("Politica: fila FIFO para evitar deadlock e inanicao")
    print("=" * 70 + "\n")

    threads = []
    for index in range(PROGRAMMER_COUNT):
        programmer_id = f"P{index + 1}"
        thread = threading.Thread(
            target=programmer_work,
            args=(programmer_id,),
            daemon=True,
        )
        threads.append(thread)
        thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulacao encerrada pelo usuario.")


if __name__ == "__main__":
    main()
