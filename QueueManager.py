import numpy as np
import random
from PathFinding import a_star_search


class QueueManager:
    """
    Logika kolejek do kas.

    - jedna wspólna kolejka (10 punktów) dla dwóch kas
    - gdy agent skończy ścieżkę zakupową (Agent.finished_path == True),
      jest kierowany do wolnej kasy albo na koniec kolejki
    - gdy kasa się zwolni, pierwszy agent z kolejki idzie do tej kasy,
      a pozostali przesuwają się o jedno miejsce
    - po zakończeniu obsługi przy kasie agent kieruje się do wyjścia
    """

    def __init__(self, env, config):
        self.env = env
        self.config = config
        ag_conf = config["agent_generation"]

        # PUNKTY OBSŁUGI KAS 
        self.cashiers = []

        payment_points = config["environment"]["cash_payment"]

        for pt in payment_points:
            self.cashiers.append({
                "service_point": np.array(pt, dtype=np.float32),
                "agent": None,
                "service_time": 0.0
            })

        # KOLEJKA

        start_x, start_y = 13.25, 11.5
        self.queue_slots = [
            np.array((start_x, start_y - 0.75 * i), dtype=np.float32)
            for i in range(10)
        ]
        self.queue = []

        # FAZY AGENTÓW
        self.agent_phase = {}

    # Pomocnicze: planowanie ścieżek A*

    def _plan_path(self, agent, target_pos, wait_at_end=0.0):
        """Planuje nową ścieżkę A* dla agenta do podanego punktu.
        Ostatni punkt może mieć czas czekania wait_at_end.
        """
        start = tuple(agent.position)
        end = tuple(target_pos)

        segment = a_star_search(self.env.grid_map, start, end)

        if segment is None or len(segment) == 0:
            segment = [start, end]

        agent.path = []
        for i, p in enumerate(segment):
            w = wait_at_end if i == len(segment) - 1 else 0.0
            agent.path.append({'pos': p, 'wait': w})

        agent.path_index = 0
        agent.goal = np.array(agent.path[0]['pos'], dtype=np.float32)
        agent.finished_path = False


    # Główna logika kolejek

    def update(self, dt):
        """
        Aktualizuje stany agentów względem kolejek / kas / wyjścia.
        Wywoływana raz na krok symulacji z Simulation.update().
        """

        #agenci którzy skończyli zakupy
        for agent in self.env.agents:
            if not agent.active or getattr(agent, "exited", False):
                continue

            phase = self.agent_phase.get(agent, "shopping")

            if phase == "shopping" and getattr(agent, "finished_path", False):
                # zakończona ścieżka zakupowa- przydziel do kasy / kolejki
                self._assign_after_shopping(agent)

        #  Obsłuż agentów, którzy właśnie dotarli do celu kolejki/kasy/wyjścia
        for agent, phase in list(self.agent_phase.items()):
            if getattr(agent, "exited", False):
                continue

            if phase in ("to_queue_slot", "to_cashier", "to_exit") and getattr(agent, "finished_path", False):
                self._on_reached_destination(agent, phase)

        #  Wolne kasy pobierają agentów z kolejki
        for idx, cashier in enumerate(self.cashiers):
            if cashier["agent"] is None and self.queue:
                ag = self.queue.pop(0)
                self._start_go_to_cashier(ag, idx)
                self._rebuild_queue_paths()


    # po zakończeniu zakupów

    def _assign_after_shopping(self, agent):
        """
        Wywoływane, gdy agent skończy ścieżkę zakupową.
        Jeśli jakaś kasa jest wolna -> od razu do kasy.
        W przeciwnym razie -> na koniec kolejki.
        """
        # szukamy wolnej kasy
        free_idx = None
        for idx, cashier in enumerate(self.cashiers):
            if cashier["agent"] is None:
                free_idx = idx
                break

        if free_idx is not None:
            # od razu do kasy
            self._start_go_to_cashier(agent, free_idx)
        else:
            # do kolejki
            if agent not in self.queue:
                self.queue.append(agent)
            self.agent_phase[agent] = "to_queue_slot"
            self._rebuild_queue_paths()

    # Etapy: przejścia między stanami
    def _cashier_index_of(self, agent):
        for i, cashier in enumerate(self.cashiers):
            if cashier["agent"] is agent:
                return i
        return None

    def _on_reached_destination(self, agent, phase):
        """Reakcja na zakończenie ścieżki zależnie od fazy."""
        if phase == "to_queue_slot":
            # agent stoi w kolejce – trzymamy go przy jego slocie
            self.agent_phase[agent] = "in_queue"

            # wyznacz slot na podstawie miejsca agenta w kolejce
            if agent in self.queue:
                idx = self.queue.index(agent)
                slot_index = min(idx, len(self.queue_slots) - 1)
                slot_pos = self.queue_slots[slot_index]
            else:
                # awaryjnie: jakby nie był w self.queue, trzymaj go tam, gdzie jest
                slot_pos = agent.position.copy()

            # stały goal na slot
            agent.path = None
            agent.path_index = 0
            agent.finished_path = False
            agent.goal = np.array(slot_pos, dtype=np.float32)

            # lekkie wygaszenie prędkości
            agent.velocity *= 0.3

        elif phase == "to_cashier":
            # Agent zakocnczyl ścieżkę do kasy + czekanie (bo wait_at_end już zadziałał)
            idx = self._cashier_index_of(agent)
            if idx is not None:
                self.cashiers[idx]["agent"] = None  # zwolnij kasę

            # start sekwencji wyjścia
            self._start_exit_for(agent)



        elif phase == "to_exit":

            # Czy agent przeszedł już pierwszy punkt wyjścia
            if hasattr(agent, "exit_sequence"):
                agent.exit_index += 1

                # drugi pkt wyjscia
                if agent.exit_index < len(agent.exit_sequence):
                    # planujemy ścieżkę do kolejnego punktu
                    next_target = agent.exit_sequence[agent.exit_index]
                    self._plan_path(agent, next_target)
                    return  # nie kończymy jeszcze, agent idzie dalej

            # Jeśli nie ma kolejnych punktów — agent wychodzi ze sklepu
            self.agent_phase[agent] = "exited"
            agent.exited = True
            agent.active = False
            agent.goal = None
            agent.velocity *= 0.0


    def _start_go_to_cashier(self, agent, cashier_idx):
        """Przydziela agentowi ścieżkę do danej kasy + czas czekania na końcu."""
        cashier = self.cashiers[cashier_idx]
        service_point = cashier["service_point"]

        service_time = random.uniform(6.0, 10.0)
        cashier["agent"] = agent
        cashier["service_time"] = service_time

        # ostatni punkt ścieżki ma wait = service_time
        self._plan_path(agent, service_point, wait_at_end=service_time)
        self.agent_phase[agent] = "to_cashier"

        # Agent na pewno nie jest już w kolejce
        if agent in self.queue:
            self.queue.remove(agent)


    def _start_exit_for(self, agent):
        """
        Po zakończeniu stania przy kasie agent idzie do wyjścia
        (punkty zdefiniowane w Config.py -> agent_generation.exit_sequence).
        """

        ag_conf = self.config["agent_generation"]
        exit_sequence = ag_conf["exit_sequence"]

        agent.is_waiting = False
        agent.wait_timer = 0.0
        agent.finished_path = False  # nowa ścieżka, więc resetujemy flagę

        # wyczyść starą ścieżkę, na wszelki wypadek
        agent.path = None
        agent.path_index = 0
        agent.goal = None

        # zapamiętaj sekwencję wyjścia
        agent.exit_sequence = exit_sequence
        agent.exit_index = 0

        # zaplanuj ścieżkę do pierwszego punktu wyjścia
        self._plan_path(agent, exit_sequence[0])
        self.agent_phase[agent] = "to_exit"



    def _rebuild_queue_paths(self):
        """
        Przebudowuje ścieżki dla agentów stojących w kolejce:
        agent o indexie i w self.queue idzie do slotu queue_slots[i].
        Jeśli agentów jest więcej niż slotów, dodatkowi kierują się
        do ostatniego slotu.
        """
        for idx, agent in enumerate(self.queue):
            if getattr(agent, "exited", False):
                continue
            # ograniczamy indeks slotu do dostępnego zakresu
            slot_index = min(idx, len(self.queue_slots) - 1)
            target = self.queue_slots[slot_index]
            self._plan_path(agent, target)
            self.agent_phase[agent] = "to_queue_slot"
