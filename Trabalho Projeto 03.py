"""
SteamPy - Plataforma de organização, consumo e análise de jogos digitais
Projeto para a disciplina de Programação de Computadores
Universidade Cruzeiro do Sul - Prof. Alcides Teixeira Barboza Junior
"""

import csv
import os
import json
from datetime import datetime
from collections import deque, Counter


# =============================================================================
# CLASSE JOGO
# =============================================================================

class Jogo:
    """Representa um jogo do catálogo."""

    def __init__(self, id, titulo, console, genero, publisher, developer,
                 critic_score, total_sales, na_sales, jp_sales, pal_sales,
                 other_sales, release_date):
        self.id = id
        self.titulo = titulo
        self.console = console
        self.genero = genero
        self.publisher = publisher
        self.developer = developer
        self.critic_score = critic_score      # float ou None
        self.total_sales = total_sales        # float (milhões)
        self.na_sales = na_sales
        self.jp_sales = jp_sales
        self.pal_sales = pal_sales
        self.other_sales = other_sales
        self.release_date = release_date

    def __str__(self):
        nota = f"{self.critic_score:.1f}" if self.critic_score else "N/A"
        vendas = f"{self.total_sales:.2f}M" if self.total_sales else "N/A"
        return (f"[{self.id:>5}] {self.titulo[:45]:<45} | "
                f"{self.console:<8} | {self.genero:<15} | "
                f"Nota: {nota:>4} | Vendas: {vendas:>8}")

    def resumo(self):
        nota = f"{self.critic_score:.1f}" if self.critic_score else "N/A"
        vendas = f"{self.total_sales:.2f}M" if self.total_sales else "N/A"
        return (f"\n  Título    : {self.titulo}"
                f"\n  Console   : {self.console}"
                f"\n  Gênero    : {self.genero}"
                f"\n  Publisher : {self.publisher}"
                f"\n  Developer : {self.developer}"
                f"\n  Nota      : {nota}"
                f"\n  Vendas    : {vendas}"
                f"\n  Lançamento: {self.release_date}")


# =============================================================================
# CLASSE FILA BACKLOG
# =============================================================================

class FilaBacklog:
    """Fila FIFO que representa o backlog de jogos do usuário."""

    def __init__(self):
        self._fila = deque()

    def enqueue(self, jogo):
        """Adiciona jogo ao final da fila."""
        self._fila.append(jogo)

    def dequeue(self):
        """Remove e retorna o jogo do início da fila."""
        if self.is_empty():
            return None
        return self._fila.popleft()

    def is_empty(self):
        return len(self._fila) == 0

    def mostrar(self):
        if self.is_empty():
            print("  Backlog vazio.")
            return
        for i, jogo in enumerate(self._fila, 1):
            print(f"  {i:>3}. {jogo.titulo} [{jogo.console}]")

    def tamanho(self):
        return len(self._fila)

    def contem_id(self, jogo_id):
        return any(j.id == jogo_id for j in self._fila)

    def to_list(self):
        return list(self._fila)


# =============================================================================
# CLASSE PILHA RECENTES
# =============================================================================

class PilhaRecentes:
    """Pilha LIFO que representa os jogos recentes jogados."""

    LIMITE = 20

    def __init__(self):
        self._pilha = []

    def push(self, jogo):
        """Empilha o jogo; remove duplicata e respeita limite."""
        # Remove se já existe (evita duplicatas, coloca no topo)
        self._pilha = [j for j in self._pilha if j.id != jogo.id]
        self._pilha.append(jogo)
        # Respeita o limite máximo
        if len(self._pilha) > self.LIMITE:
            self._pilha.pop(0)

    def pop(self):
        """Desempilha o jogo do topo."""
        if self.is_empty():
            return None
        return self._pilha.pop()

    def topo(self):
        """Retorna o jogo do topo sem remover."""
        if self.is_empty():
            return None
        return self._pilha[-1]

    def is_empty(self):
        return len(self._pilha) == 0

    def mostrar(self):
        if self.is_empty():
            print("  Nenhum jogo recente.")
            return
        for i, jogo in enumerate(reversed(self._pilha), 1):
            print(f"  {i:>3}. {jogo.titulo} [{jogo.console}]")

    def tamanho(self):
        return len(self._pilha)

    def to_list(self):
        return list(reversed(self._pilha))


# =============================================================================
# CLASSE SESSAO JOGO
# =============================================================================

class SessaoJogo:
    """Representa uma sessão de jogo registrada pelo usuário."""

    def __init__(self, jogo, tempo_jogado, tempo_total, data_sessao=None,
                 percentual_simulado=0.0, status="iniciado"):
        self.jogo = jogo
        self.tempo_jogado = tempo_jogado        # horas nesta sessão
        self.tempo_total = tempo_total          # horas acumuladas
        self.data_sessao = data_sessao or datetime.now().strftime("%d/%m/%Y %H:%M")
        self.percentual_simulado = percentual_simulado
        self.status = status

    @staticmethod
    def calcular_status(tempo_total):
        if tempo_total < 2:
            return "iniciado"
        elif tempo_total < 10:
            return "em andamento"
        elif tempo_total < 20:
            return "muito jogado"
        else:
            return "concluído simbolicamente"

    def __str__(self):
        return (f"  [{self.data_sessao}] {self.jogo.titulo:<40} | "
                f"Sessão: {self.tempo_jogado:>5.1f}h | "
                f"Total: {self.tempo_total:>6.1f}h | "
                f"Status: {self.status}")


# =============================================================================
# CLASSE PRINCIPAL STEAMPY
# =============================================================================

class SteamPy:
    """Classe principal do sistema SteamPy."""

    ARQUIVO_BACKLOG   = "backlog.txt"
    ARQUIVO_HISTORICO = "historico_jogo.txt"
    ARQUIVO_RECENTES  = "recentes.txt"

    def __init__(self):
        self.catalogo: list[Jogo] = []                  # lista principal
        self.indice: dict[int, Jogo] = {}               # dict id → Jogo
        self.backlog = FilaBacklog()
        self.recentes = PilhaRecentes()
        self.historico: list[SessaoJogo] = []           # todas as sessões
        self.tempo_por_jogo: dict[int, float] = {}      # id → horas totais
        self.recomendacoes: list[Jogo] = []

    # -------------------------------------------------------------------------
    # PARTE 1 – CARREGAMENTO DO CATÁLOGO
    # -------------------------------------------------------------------------

    def carregar_jogos(self, nome_arquivo="dataset.csv"):
        """Lê o dataset CSV e popula catálogo e índice."""
        if not os.path.exists(nome_arquivo):
            print(f"  [ERRO] Arquivo '{nome_arquivo}' não encontrado.")
            return 0

        self.catalogo.clear()
        self.indice.clear()
        total_ok = 0
        total_erro = 0

        with open(nome_arquivo, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                try:
                    def safe_float(val):
                        try:
                            return float(val) if val and val.strip() not in ("", "N/A", "nan") else None
                        except ValueError:
                            return None

                    jogo = Jogo(
                        id=i,
                        titulo=row.get("title", "").strip(),
                        console=row.get("console", "").strip(),
                        genero=row.get("genre", "").strip(),
                        publisher=row.get("publisher", "").strip(),
                        developer=row.get("developer", "").strip(),
                        critic_score=safe_float(row.get("critic_score")),
                        total_sales=safe_float(row.get("total_sales")),
                        na_sales=safe_float(row.get("na_sales")),
                        jp_sales=safe_float(row.get("jp_sales")),
                        pal_sales=safe_float(row.get("pal_sales")),
                        other_sales=safe_float(row.get("other_sales")),
                        release_date=row.get("release_date", "").strip(),
                    )

                    if not jogo.titulo:
                        total_erro += 1
                        continue

                    self.catalogo.append(jogo)
                    self.indice[jogo.id] = jogo
                    total_ok += 1

                except Exception:
                    total_erro += 1

        print(f"  Catálogo carregado: {total_ok} jogos | {total_erro} linha(s) ignorada(s).")
        return total_ok

    # -------------------------------------------------------------------------
    # PARTE 2 – BUSCA, FILTROS E ORDENAÇÃO
    # -------------------------------------------------------------------------

    def listar_jogos(self, lista=None, limite=50):
        jogos = lista if lista is not None else self.catalogo
        if not jogos:
            print("  Nenhum jogo para exibir.")
            return
        print(f"\n  {'ID':>5}  {'Título':<45}  {'Console':<8}  {'Gênero':<15}  {'Nota':>4}  {'Vendas':>8}")
        print("  " + "-" * 100)
        for j in jogos[:limite]:
            print(" ", j)
        if len(jogos) > limite:
            print(f"\n  ... exibindo {limite} de {len(jogos)} resultados.")

    def buscar_jogo_por_nome(self, termo):
        """Busca parcial por título (case-insensitive)."""
        termo_lower = termo.lower()
        return [j for j in self.catalogo if termo_lower in j.titulo.lower()]

    def filtrar_por_genero(self, genero):
        g = genero.lower()
        return [j for j in self.catalogo if j.genero.lower() == g]

    def filtrar_por_console(self, console):
        c = console.lower()
        return [j for j in self.catalogo if j.console.lower() == c]

    def filtrar_por_nota(self, nota_minima):
        return [j for j in self.catalogo
                if j.critic_score is not None and j.critic_score >= nota_minima]

    def filtrar_por_vendas(self, vendas_minimas):
        return [j for j in self.catalogo
                if j.total_sales is not None and j.total_sales >= vendas_minimas]

    def filtrar_por_publisher(self, publisher):
        p = publisher.lower()
        return [j for j in self.catalogo if j.publisher.lower() == p]

    def ordenar_jogos(self, criterio, lista=None):
        """Ordena pelo critério escolhido. Retorna nova lista."""
        jogos = list(lista) if lista is not None else list(self.catalogo)
        criterios = {
            "titulo":    lambda j: j.titulo.lower(),
            "nota":      lambda j: j.critic_score if j.critic_score else -1,
            "vendas":    lambda j: j.total_sales if j.total_sales else -1,
            "data":      lambda j: j.release_date or "",
            "console":   lambda j: j.console.lower(),
            "genero":    lambda j: j.genero.lower(),
        }
        reverse = criterio in ("nota", "vendas")
        key = criterios.get(criterio)
        if not key:
            print(f"  Critério '{criterio}' inválido.")
            return jogos
        return sorted(jogos, key=key, reverse=reverse)

    # -------------------------------------------------------------------------
    # PARTE 3 – BACKLOG (FILA)
    # -------------------------------------------------------------------------

    def adicionar_ao_backlog(self, jogo):
        if self.backlog.contem_id(jogo.id):
            print(f"  '{jogo.titulo}' já está no backlog.")
            return
        self.backlog.enqueue(jogo)
        print(f"  '{jogo.titulo}' adicionado ao backlog.")

    def mostrar_backlog(self):
        print(f"\n  === BACKLOG ({self.backlog.tamanho()} jogo(s)) ===")
        self.backlog.mostrar()

    def jogar_proximo(self):
        """Remove o próximo jogo do backlog e inicia uma sessão."""
        jogo = self.backlog.dequeue()
        if not jogo:
            print("  Backlog vazio!")
            return
        print(f"\n  Iniciando: {jogo.titulo} [{jogo.console}]")
        self._iniciar_sessao(jogo)

    def salvar_backlog(self):
        with open(self.ARQUIVO_BACKLOG, "w", encoding="utf-8") as f:
            f.write("id;titulo;console\n")
            for j in self.backlog.to_list():
                f.write(f"{j.id};{j.titulo};{j.console}\n")
        print(f"  Backlog salvo em '{self.ARQUIVO_BACKLOG}'.")

    def carregar_backlog(self):
        if not os.path.exists(self.ARQUIVO_BACKLOG):
            return
        with open(self.ARQUIVO_BACKLOG, encoding="utf-8") as f:
            linhas = f.readlines()[1:]  # pula cabeçalho
        for linha in linhas:
            partes = linha.strip().split(";")
            if len(partes) < 1:
                continue
            try:
                jogo_id = int(partes[0])
                if jogo_id in self.indice:
                    self.backlog.enqueue(self.indice[jogo_id])
            except (ValueError, IndexError):
                continue
        if self.backlog.tamanho() > 0:
            print(f"  Backlog carregado: {self.backlog.tamanho()} jogo(s).")

    # -------------------------------------------------------------------------
    # PARTE 4 – RECENTES (PILHA)
    # -------------------------------------------------------------------------

    def mostrar_recentes(self):
        print(f"\n  === JOGOS RECENTES ({self.recentes.tamanho()} jogo(s)) ===")
        self.recentes.mostrar()

    def retomar_ultimo_jogo(self):
        jogo = self.recentes.topo()
        if not jogo:
            print("  Nenhum jogo recente para retomar.")
            return
        print(f"\n  Retomando: {jogo.titulo} [{jogo.console}]")
        self._iniciar_sessao(jogo)

    def salvar_recentes(self):
        with open(self.ARQUIVO_RECENTES, "w", encoding="utf-8") as f:
            f.write("id;titulo;console\n")
            for j in self.recentes.to_list():
                f.write(f"{j.id};{j.titulo};{j.console}\n")

    def carregar_recentes(self):
        if not os.path.exists(self.ARQUIVO_RECENTES):
            return
        with open(self.ARQUIVO_RECENTES, encoding="utf-8") as f:
            linhas = f.readlines()[1:]
        # Carrega na ordem correta (mais antigo primeiro para o push recriar a pilha)
        for linha in reversed(linhas):
            partes = linha.strip().split(";")
            try:
                jogo_id = int(partes[0])
                if jogo_id in self.indice:
                    self.recentes.push(self.indice[jogo_id])
            except (ValueError, IndexError):
                continue

    # -------------------------------------------------------------------------
    # PARTE 5 – SIMULAÇÃO DE TEMPO DE JOGO
    # -------------------------------------------------------------------------

    def _iniciar_sessao(self, jogo):
        """Fluxo de registro de tempo de jogo."""
        tempo_anterior = self.tempo_por_jogo.get(jogo.id, 0.0)
        print(f"  Tempo já registrado para '{jogo.titulo}': {tempo_anterior:.1f}h")
        while True:
            entrada = input("  Informe o tempo jogado nesta sessão (ex: 2.5 para 2h30min): ").strip()
            try:
                tempo_sessao = float(entrada)
                if tempo_sessao < 0:
                    print("  Valor inválido.")
                    continue
                break
            except ValueError:
                print("  Digite um número válido.")

        tempo_total = tempo_anterior + tempo_sessao
        self.tempo_por_jogo[jogo.id] = tempo_total
        status = SessaoJogo.calcular_status(tempo_total)

        sessao = SessaoJogo(jogo, tempo_sessao, tempo_total, status=status)
        self.historico.append(sessao)
        self.recentes.push(jogo)

        print(f"\n  Sessão registrada!")
        print(f"  Tempo nesta sessão : {tempo_sessao:.1f}h")
        print(f"  Tempo total        : {tempo_total:.1f}h")
        print(f"  Status             : {status}")

        self.salvar_historico()
        self.salvar_recentes()

    def registrar_sessao(self, jogo=None, tempo=None):
        """Menu para registrar tempo em qualquer jogo."""
        if jogo is None:
            termo = input("  Digite parte do nome do jogo: ").strip()
            resultados = self.buscar_jogo_por_nome(termo)
            if not resultados:
                print("  Nenhum jogo encontrado.")
                return
            self.listar_jogos(resultados[:20])
            try:
                escolha = int(input("  Digite o ID do jogo: "))
                jogo = self.indice.get(escolha)
                if not jogo:
                    print("  ID inválido.")
                    return
            except ValueError:
                print("  Entrada inválida.")
                return

        self.recentes.push(jogo)
        self._iniciar_sessao(jogo)

    # -------------------------------------------------------------------------
    # PARTE 6 – HISTÓRICO COMPLETO
    # -------------------------------------------------------------------------

    def mostrar_historico(self):
        if not self.historico:
            print("  Nenhuma sessão registrada.")
            return
        print(f"\n  === HISTÓRICO DE SESSÕES ({len(self.historico)} sessão(ões)) ===")
        for s in self.historico:
            print(s)

    def salvar_historico(self):
        with open(self.ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
            f.write("titulo;tempo_sessao;tempo_total;status;data\n")
            for s in self.historico:
                f.write(f"{s.jogo.titulo};{s.tempo_jogado};{s.tempo_total};"
                        f"{s.status};{s.data_sessao}\n")

    def carregar_historico(self):
        if not os.path.exists(self.ARQUIVO_HISTORICO):
            return
        with open(self.ARQUIVO_HISTORICO, encoding="utf-8") as f:
            linhas = f.readlines()[1:]
        for linha in linhas:
            partes = linha.strip().split(";")
            if len(partes) < 4:
                continue
            try:
                titulo = partes[0]
                tempo_sessao = float(partes[1])
                tempo_total = float(partes[2])
                status = partes[3]
                data = partes[4] if len(partes) > 4 else ""
                # Busca o jogo pelo título
                jogo = next((j for j in self.catalogo
                             if j.titulo == titulo), None)
                if jogo:
                    self.tempo_por_jogo[jogo.id] = tempo_total
                    sessao = SessaoJogo(jogo, tempo_sessao, tempo_total,
                                       data_sessao=data, status=status)
                    self.historico.append(sessao)
            except (ValueError, IndexError):
                continue

    # -------------------------------------------------------------------------
    # PARTE 7 – RECOMENDAÇÃO
    # -------------------------------------------------------------------------

    def recomendar_jogos(self, quantidade=10):
        """Recomenda jogos com base em gênero, console e nota preferidos."""
        if not self.historico:
            print("  Sem histórico suficiente para recomendações.")
            print("  Exibindo jogos mais bem avaliados do catálogo:")
            top = self.ordenar_jogos("nota")[:quantidade]
            self.listar_jogos(top)
            self.recomendacoes = top
            return top

        # Analisa perfil do usuário
        generos = Counter(s.jogo.genero for s in self.historico if s.jogo.genero)
        consoles = Counter(s.jogo.console for s in self.historico if s.jogo.console)
        notas_jogadas = [s.jogo.critic_score for s in self.historico
                         if s.jogo.critic_score is not None]
        nota_media = sum(notas_jogadas) / len(notas_jogadas) if notas_jogadas else 7.0

        genero_fav = generos.most_common(1)[0][0] if generos else None
        console_fav = consoles.most_common(1)[0][0] if consoles else None

        print(f"\n  Critérios usados:")
        print(f"    Gênero favorito : {genero_fav}")
        print(f"    Console favorito: {console_fav}")
        print(f"    Nota mínima     : {nota_media:.1f}")

        # IDs já jogados ou no backlog
        ids_jogados = {s.jogo.id for s in self.historico
                       if self.tempo_por_jogo.get(s.jogo.id, 0) >= 10}
        ids_backlog = {j.id for j in self.backlog.to_list()}
        excluidos = ids_jogados | ids_backlog

        def pontuacao(jogo):
            pts = 0
            if jogo.genero == genero_fav:
                pts += 3
            if jogo.console == console_fav:
                pts += 2
            if jogo.critic_score and jogo.critic_score >= nota_media:
                pts += 2
            if jogo.total_sales and jogo.total_sales >= 1.0:
                pts += 1
            return pts

        candidatos = [j for j in self.catalogo if j.id not in excluidos]
        candidatos.sort(key=pontuacao, reverse=True)
        self.recomendacoes = candidatos[:quantidade]
        return self.recomendacoes

    # -------------------------------------------------------------------------
    # PARTE 8 – RANKING PESSOAL
    # -------------------------------------------------------------------------

    def gerar_ranking_pessoal(self):
        if not self.historico:
            print("  Nenhum jogo jogado ainda.")
            return

        print("\n  ╔══════════════════════════════════════════════════╗")
        print("  ║              RANKING PESSOAL                    ║")
        print("  ╚══════════════════════════════════════════════════╝")

        # 1. Jogos mais jogados (por tempo total)
        print("\n  ▶ TOP 10 JOGOS MAIS JOGADOS (por tempo)")
        print("  " + "-" * 60)
        jogados = {}
        for s in self.historico:
            jogados[s.jogo] = self.tempo_por_jogo.get(s.jogo.id, 0)
        top_jogos = sorted(jogados.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (jogo, hrs) in enumerate(top_jogos, 1):
            print(f"  {i:>3}. {jogo.titulo:<45} {hrs:>6.1f}h")

        # 2. Gêneros mais jogados
        print("\n  ▶ GÊNEROS MAIS JOGADOS")
        print("  " + "-" * 60)
        generos: dict[str, float] = {}
        for s in self.historico:
            g = s.jogo.genero or "Desconhecido"
            generos[g] = generos.get(g, 0) + s.tempo_jogado
        for i, (g, hrs) in enumerate(
                sorted(generos.items(), key=lambda x: x[1], reverse=True)[:8], 1):
            print(f"  {i:>3}. {g:<25} {hrs:>6.1f}h")

        # 3. Consoles mais jogados
        print("\n  ▶ CONSOLES MAIS JOGADOS")
        print("  " + "-" * 60)
        consoles: dict[str, float] = {}
        for s in self.historico:
            c = s.jogo.console or "Desconhecido"
            consoles[c] = consoles.get(c, 0) + s.tempo_jogado
        for i, (c, hrs) in enumerate(
                sorted(consoles.items(), key=lambda x: x[1], reverse=True)[:8], 1):
            print(f"  {i:>3}. {c:<25} {hrs:>6.1f}h")

        # 4. Top jogos por nota (dentro do histórico)
        print("\n  ▶ TOP 10 JOGOS POR NOTA (já jogados)")
        print("  " + "-" * 60)
        vistos = {}
        for s in self.historico:
            if s.jogo.id not in vistos and s.jogo.critic_score is not None:
                vistos[s.jogo.id] = s.jogo
        top_nota = sorted(vistos.values(),
                          key=lambda j: j.critic_score, reverse=True)[:10]
        for i, j in enumerate(top_nota, 1):
            print(f"  {i:>3}. {j.titulo:<45} nota: {j.critic_score:.1f}")

    # -------------------------------------------------------------------------
    # PARTE 9 – DASHBOARD
    # -------------------------------------------------------------------------

    def exibir_dashboard(self):
        # Contagens de status
        status_count: dict[str, int] = {}
        notas_jogadas = []
        for jogo_id, total_hrs in self.tempo_por_jogo.items():
            s = SessaoJogo.calcular_status(total_hrs)
            status_count[s] = status_count.get(s, 0) + 1
        for s in self.historico:
            if s.jogo.critic_score is not None:
                notas_jogadas.append(s.jogo.critic_score)

        tempo_total = sum(self.tempo_por_jogo.values())
        media_horas = tempo_total / len(self.historico) if self.historico else 0

        # Jogo mais jogado
        jogo_mais_jogado = max(self.tempo_por_jogo.items(),
                                key=lambda x: x[1], default=(None, 0))
        jogo_mj_obj = self.indice.get(jogo_mais_jogado[0]) if jogo_mais_jogado[0] else None

        # Gênero e console favorito
        generos = Counter(s.jogo.genero for s in self.historico if s.jogo.genero)
        consoles = Counter(s.jogo.console for s in self.historico if s.jogo.console)
        genero_fav = generos.most_common(1)[0][0] if generos else "N/A"
        console_fav = consoles.most_common(1)[0][0] if consoles else "N/A"
        nota_media = sum(notas_jogadas) / len(notas_jogadas) if notas_jogadas else 0

        # Jogo mais popular e melhor nota já jogados
        jogados_ids = list(self.tempo_por_jogo.keys())
        jogados_objs = [self.indice[i] for i in jogados_ids if i in self.indice]
        jogo_popular = max(
            (j for j in jogados_objs if j.total_sales),
            key=lambda j: j.total_sales, default=None
        )
        jogo_melhor_nota = max(
            (j for j in jogados_objs if j.critic_score),
            key=lambda j: j.critic_score, default=None
        )

        print("\n  ╔══════════════════════════════════════════════════════════╗")
        print("  ║                 🎮  DASHBOARD  STEAMPY                  ║")
        print("  ╚══════════════════════════════════════════════════════════╝")
        print(f"\n  {'─'*60}")
        print(f"  {'BIBLIOTECA & ATIVIDADE':^60}")
        print(f"  {'─'*60}")
        print(f"  {'Total de jogos no catálogo':<40}: {len(self.catalogo):>8}")
        print(f"  {'Total no backlog':<40}: {self.backlog.tamanho():>8}")
        print(f"  {'Total de jogos recentes':<40}: {self.recentes.tamanho():>8}")
        print(f"  {'Total de sessões jogadas':<40}: {len(self.historico):>8}")
        print(f"  {'Tempo total jogado':<40}: {tempo_total:>7.1f}h")
        print(f"  {'Média de horas por sessão':<40}: {media_horas:>7.1f}h")

        print(f"\n  {'─'*60}")
        print(f"  {'PERFIL DO JOGADOR':^60}")
        print(f"  {'─'*60}")
        print(f"  {'Jogo mais jogado':<40}: {jogo_mj_obj.titulo[:30] if jogo_mj_obj else 'N/A'}")
        print(f"  {'Gênero favorito':<40}: {genero_fav}")
        print(f"  {'Console favorito':<40}: {console_fav}")
        print(f"  {'Nota média dos jogos jogados':<40}: {nota_media:>7.1f}")

        print(f"\n  {'─'*60}")
        print(f"  {'STATUS DOS JOGOS':^60}")
        print(f"  {'─'*60}")
        print(f"  {'Jogos iniciados':<40}: {status_count.get('iniciado', 0):>8}")
        print(f"  {'Jogos em andamento':<40}: {status_count.get('em andamento', 0):>8}")
        print(f"  {'Jogos muito jogados':<40}: {status_count.get('muito jogado', 0):>8}")
        print(f"  {'Jogos concluídos simbolicamente':<40}: {status_count.get('concluído simbolicamente', 0):>8}")

        print(f"\n  {'─'*60}")
        print(f"  {'DESTAQUES':^60}")
        print(f"  {'─'*60}")
        print(f"  {'Jogo mais popular já jogado':<40}: {jogo_popular.titulo[:30] if jogo_popular else 'N/A'}")
        print(f"  {'Jogo com melhor nota já jogado':<40}: {jogo_melhor_nota.titulo[:30] if jogo_melhor_nota else 'N/A'}")
        print(f"  {'Recomendações disponíveis':<40}: {len(self.recomendacoes):>8}")
        print(f"  {'─'*60}\n")

    # -------------------------------------------------------------------------
    # INICIALIZAÇÃO (carrega tudo ao iniciar)
    # -------------------------------------------------------------------------

    def inicializar(self, arquivo_dataset="dataset.csv"):
        print("\n  Inicializando SteamPy...")
        n = self.carregar_jogos(arquivo_dataset)
        if n > 0:
            self.carregar_backlog()
            self.carregar_historico()
            self.carregar_recentes()
        print("  Sistema pronto!\n")


# =============================================================================
# MENU INTERATIVO
# =============================================================================

def _separador(titulo=""):
    if titulo:
        print(f"\n  {'═'*10} {titulo.upper()} {'═'*(max(0, 40-len(titulo)))}")
    else:
        print()


def _input_int(prompt, minimo=None, maximo=None):
    while True:
        try:
            v = int(input(prompt))
            if minimo is not None and v < minimo:
                print(f"  Valor mínimo: {minimo}")
                continue
            if maximo is not None and v > maximo:
                print(f"  Valor máximo: {maximo}")
                continue
            return v
        except ValueError:
            print("  Digite um número inteiro válido.")


def _input_float(prompt, minimo=0.0):
    while True:
        try:
            v = float(input(prompt))
            if v < minimo:
                print(f"  Valor mínimo: {minimo}")
                continue
            return v
        except ValueError:
            print("  Digite um número válido (ex: 8.5).")


def _escolher_jogo(sistema: SteamPy, prompt="Digite parte do nome do jogo: "):
    """Auxiliar para buscar e selecionar um jogo do catálogo."""
    termo = input(f"  {prompt}").strip()
    if not termo:
        return None
    resultados = sistema.buscar_jogo_por_nome(termo)
    if not resultados:
        print("  Nenhum jogo encontrado.")
        return None
    sistema.listar_jogos(resultados[:20])
    try:
        escolha = int(input("  Digite o ID do jogo desejado: "))
        return sistema.indice.get(escolha)
    except ValueError:
        print("  Entrada inválida.")
        return None


def menu():
    sistema = SteamPy()

    print("╔══════════════════════════════════════════════╗")
    print("║          🎮  SteamPy  v1.0                  ║")
    print("║   Plataforma de Gerenciamento de Jogos       ║")
    print("╚══════════════════════════════════════════════╝")

    # Tenta carregar dataset padrão ao iniciar
    if os.path.exists("dataset.csv"):
        sistema.inicializar("dataset.csv")
    else:
        print("  dataset.csv não encontrado. Use a opção 1 para carregar manualmente.\n")

    opcoes = {
        1:  "Carregar catálogo",
        2:  "Listar jogos",
        3:  "Buscar jogo por nome",
        4:  "Filtrar por gênero",
        5:  "Filtrar por console",
        6:  "Filtrar por nota mínima",
        7:  "Filtrar por vendas mínimas",
        8:  "Filtrar por publisher",
        9:  "Ordenar catálogo",
        10: "Adicionar jogo ao backlog",
        11: "Ver backlog",
        12: "Jogar próximo do backlog",
        13: "Ver jogos recentes",
        14: "Retomar último jogo",
        15: "Registrar tempo de jogo (jogo livre)",
        16: "Ver histórico completo",
        17: "Ver recomendações",
        18: "Ver ranking pessoal",
        19: "Ver dashboard",
        20: "Salvar backlog",
        0:  "Sair",
    }

    while True:
        print("\n╔══════════════════════════════════════════════╗")
        print("║                  MENU PRINCIPAL              ║")
        print("╠══════════════════════════════════════════════╣")
        for num, desc in opcoes.items():
            print(f"║  {num:>2}. {desc:<42}║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Catálogo: {len(sistema.catalogo)} jogos  |  "
              f"Backlog: {sistema.backlog.tamanho()}  |  "
              f"Sessões: {len(sistema.historico)}")

        try:
            opcao = int(input("\n  Escolha uma opção: "))
        except ValueError:
            print("  Opção inválida.")
            continue

        # ── 1. Carregar catálogo ──────────────────────────────────────────────
        if opcao == 1:
            _separador("Carregar catálogo")
            arq = input("  Nome do arquivo CSV [dataset.csv]: ").strip() or "dataset.csv"
            sistema.inicializar(arq)

        # ── 2. Listar jogos ───────────────────────────────────────────────────
        elif opcao == 2:
            _separador("Listar jogos")
            if not sistema.catalogo:
                print("  Catálogo vazio.")
            else:
                limite = _input_int("  Quantos jogos exibir? [50]: ") \
                    if input("  Personalizar limite? (s/n): ").strip().lower() == "s" \
                    else 50
                sistema.listar_jogos(limite=limite)

        # ── 3. Buscar por nome ────────────────────────────────────────────────
        elif opcao == 3:
            _separador("Buscar por nome")
            termo = input("  Digite parte do título: ").strip()
            resultados = sistema.buscar_jogo_por_nome(termo)
            print(f"\n  {len(resultados)} resultado(s) encontrado(s):")
            sistema.listar_jogos(resultados)

        # ── 4. Filtrar por gênero ─────────────────────────────────────────────
        elif opcao == 4:
            _separador("Filtrar por gênero")
            # Mostra gêneros disponíveis
            generos = sorted(set(j.genero for j in sistema.catalogo if j.genero))
            print("  Gêneros disponíveis: " + ", ".join(generos[:20]))
            g = input("  Digite o gênero: ").strip()
            r = sistema.filtrar_por_genero(g)
            print(f"\n  {len(r)} jogo(s) encontrado(s):")
            sistema.listar_jogos(r)

        # ── 5. Filtrar por console ────────────────────────────────────────────
        elif opcao == 5:
            _separador("Filtrar por console")
            consoles = sorted(set(j.console for j in sistema.catalogo if j.console))
            print("  Consoles disponíveis: " + ", ".join(consoles[:30]))
            c = input("  Digite o console: ").strip()
            r = sistema.filtrar_por_console(c)
            print(f"\n  {len(r)} jogo(s) encontrado(s):")
            sistema.listar_jogos(r)

        # ── 6. Filtrar por nota ───────────────────────────────────────────────
        elif opcao == 6:
            _separador("Filtrar por nota mínima")
            nota = _input_float("  Nota mínima (0-10): ", minimo=0.0)
            r = sistema.filtrar_por_nota(nota)
            print(f"\n  {len(r)} jogo(s) com nota >= {nota}:")
            sistema.listar_jogos(r)

        # ── 7. Filtrar por vendas ─────────────────────────────────────────────
        elif opcao == 7:
            _separador("Filtrar por vendas mínimas")
            vendas = _input_float("  Vendas mínimas (em milhões, ex: 1.5): ", minimo=0.0)
            r = sistema.filtrar_por_vendas(vendas)
            print(f"\n  {len(r)} jogo(s) com vendas >= {vendas}M:")
            sistema.listar_jogos(r)

        # ── 8. Filtrar por publisher ──────────────────────────────────────────
        elif opcao == 8:
            _separador("Filtrar por publisher")
            pub = input("  Digite o nome da publisher: ").strip()
            r = sistema.filtrar_por_publisher(pub)
            print(f"\n  {len(r)} jogo(s) encontrado(s):")
            sistema.listar_jogos(r)

        # ── 9. Ordenar catálogo ───────────────────────────────────────────────
        elif opcao == 9:
            _separador("Ordenar catálogo")
            print("  Critérios: titulo | nota | vendas | data | console | genero")
            criterio = input("  Escolha o critério: ").strip().lower()
            r = sistema.ordenar_jogos(criterio)
            print(f"\n  Catálogo ordenado por '{criterio}':")
            sistema.listar_jogos(r)

        # ── 10. Adicionar ao backlog ──────────────────────────────────────────
        elif opcao == 10:
            _separador("Adicionar ao backlog")
            jogo = _escolher_jogo(sistema)
            if jogo:
                sistema.adicionar_ao_backlog(jogo)

        # ── 11. Ver backlog ───────────────────────────────────────────────────
        elif opcao == 11:
            sistema.mostrar_backlog()

        # ── 12. Jogar próximo do backlog ──────────────────────────────────────
        elif opcao == 12:
            _separador("Jogar próximo do backlog")
            sistema.jogar_proximo()

        # ── 13. Ver recentes ──────────────────────────────────────────────────
        elif opcao == 13:
            sistema.mostrar_recentes()

        # ── 14. Retomar último jogo ───────────────────────────────────────────
        elif opcao == 14:
            _separador("Retomar último jogo")
            sistema.retomar_ultimo_jogo()

        # ── 15. Registrar tempo (jogo livre) ──────────────────────────────────
        elif opcao == 15:
            _separador("Registrar tempo de jogo")
            sistema.registrar_sessao()

        # ── 16. Ver histórico ─────────────────────────────────────────────────
        elif opcao == 16:
            sistema.mostrar_historico()

        # ── 17. Recomendações ─────────────────────────────────────────────────
        elif opcao == 17:
            _separador("Recomendações")
            qtd = 10
            rec = sistema.recomendar_jogos(qtd)
            if rec:
                print(f"\n  🎯 Jogos recomendados para você:")
                sistema.listar_jogos(rec)

        # ── 18. Ranking pessoal ───────────────────────────────────────────────
        elif opcao == 18:
            sistema.gerar_ranking_pessoal()

        # ── 19. Dashboard ─────────────────────────────────────────────────────
        elif opcao == 19:
            sistema.exibir_dashboard()

        # ── 20. Salvar backlog ────────────────────────────────────────────────
        elif opcao == 20:
            sistema.salvar_backlog()

        # ── 0. Sair ───────────────────────────────────────────────────────────
        elif opcao == 0:
            print("\n  Salvando dados...")
            sistema.salvar_backlog()
            sistema.salvar_historico()
            sistema.salvar_recentes()
            print("  Até logo! 👾")
            break

        else:
            print("  Opção inválida.")

        input("\n  Pressione Enter para continuar...")


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    menu()