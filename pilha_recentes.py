class PilhaRecentes:
    """Pilha (LIFO) com limite de 20 jogos recentes."""
    LIMITE = 20

    def __init__(self):
        self._pilha = []

    def push(self, jogo):
        """Empilha jogo no topo. Se já estiver na pilha, move para o topo."""
        # Remove se já existir (para evitar duplicatas ao retomar)
        try:
            idx = self._pilha.index(jogo)
            self._pilha.pop(idx)
        except ValueError:
            pass
        self._pilha.append(jogo)
        # Mantém o limite
        if len(self._pilha) > self.LIMITE:
            self._pilha.pop(0)

    def pop(self):
        """Remove e retorna o topo da pilha."""
        if self._pilha:
            return self._pilha.pop()
        return None

    def topo(self):
        """Retorna o topo sem remover."""
        if self._pilha:
            return self._pilha[-1]
        return None

    def is_empty(self):
        return len(self._pilha) == 0

    def mostrar(self):
        """Exibe do mais recente para o mais antigo."""
        if self.is_empty():
            print("Nenhum jogo recente.")
            return
        print("\n--- JOGOS RECENTES (Mais recente primeiro) ---")
        for i, jogo in enumerate(reversed(self._pilha), 1):
            print(f"{i}. {jogo}")
        print("----------------------------------------------")

    def tamanho(self):
        return len(self._pilha)

    def to_list(self):
        """Retorna a lista do mais antigo para o mais recente (ordem interna)."""
        return self._pilha.copy()