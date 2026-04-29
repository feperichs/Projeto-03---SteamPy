class FilaBacklog:
    """Fila (FIFO) para o backlog de jogos a jogar."""
    def __init__(self):
        self._fila = []

    def enqueue(self, jogo):
        """Adiciona jogo ao final da fila."""
        self._fila.append(jogo)

    def dequeue(self):
        """Remove e retorna o primeiro jogo da fila."""
        if self._fila:
            return self._fila.pop(0)
        return None

    def is_empty(self):
        return len(self._fila) == 0

    def mostrar(self):
        """Exibe a fila na ordem correta (do primeiro ao último)."""
        if self.is_empty():
            print("Backlog vazio.")
            return
        print("\n--- BACKLOG (Próximo a jogar primeiro) ---")
        for i, jogo in enumerate(self._fila, 1):
            print(f"{i}. {jogo}")
        print("------------------------------------------")

    def tamanho(self):
        return len(self._fila)

    def to_list(self):
        """Retorna a lista interna para salvamento."""
        return self._fila.copy()