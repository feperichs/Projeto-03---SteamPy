from datetime import datetime

class SessaoJogo:
    """Representa uma sessão de jogo do usuário."""
    def __init__(self, jogo, tempo_jogado):
        self.jogo = jogo  # Objeto Jogo
        self.tempo_jogado = tempo_jogado  # Horas
        self.data_sessao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = self._calcular_status(tempo_jogado)

    @staticmethod
    def _calcular_status(tempo_total):
        """Define status baseado no tempo total acumulado do jogo."""
        if tempo_total < 2:
            return "iniciado"
        elif tempo_total < 10:
            return "em andamento"
        elif tempo_total < 20:
            return "muito jogado"
        else:
            return "concluído simbolicamente"

    def __str__(self):
        return f"{self.jogo.titulo} | Sessão: {self.tempo_jogado:.1f}h | Total: {self.jogo.titulo} | Status: {self.status} | Data: {self.data_sessao}"