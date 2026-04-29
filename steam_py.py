import csv
import os
from jogo import Jogo
from fila_backlog import FilaBacklog
from pilha_recentes import PilhaRecentes
from sessao_jogo import SessaoJogo


class SteamPy:
    """Sistema principal de gerenciamento de jogos."""
    def __init__(self):
        self.catalogo = []          # Lista de objetos Jogo
        self.catalogo_dict = {}     # Dicionário id -> Jogo
        self.backlog = FilaBacklog()
        self.recentes = PilhaRecentes()
        self.historico = []         # Lista de SessaoJogo
        self.tempos_acumulados = {} # Dicionário id_jogo -> tempo total em horas

    # ---------- CATÁLOGO ----------
    def carregar_jogos(self, nome_arquivo):
        """Carrega o dataset CSV e popula o catálogo."""
        if not os.path.exists(nome_arquivo):
            print(f"Arquivo {nome_arquivo} não encontrado.")
            return
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            leitor = csv.DictReader(f)
            for i, linha in enumerate(leitor, start=1):
                try:
                    jogo = Jogo(
                        id_jogo=i,
                        titulo=linha['title'].strip(),
                        console=linha['console'].strip(),
                        genero=linha['genre'].strip(),
                        publisher=linha['publisher'].strip(),
                        developer=linha['developer'].strip(),
                        critic_score=float(linha['critic_score']) if linha['critic_score'] else 0.0,
                        total_sales=float(linha['total_sales']) if linha['total_sales'] else 0.0,
                        na_sales=float(linha['na_sales']) if linha['na_sales'] else 0.0,
                        jp_sales=float(linha['jp_sales']) if linha['jp_sales'] else 0.0,
                        pal_sales=float(linha['pal_sales']) if linha['pal_sales'] else 0.0,
                        other_sales=float(linha['other_sales']) if linha['other_sales'] else 0.0,
                        release_date=linha['release_date'].strip()
                    )
                    self.catalogo.append(jogo)
                    self.catalogo_dict[i] = jogo
                except Exception as e:
                    print(f"Linha ignorada (erro): {e}")
        print(f"Catálogo carregado: {len(self.catalogo)} jogos.")

    def listar_jogos(self, lista=None):
        """Exibe lista de jogos. Se None, exibe todo o catálogo."""
        if lista is None:
            lista = self.catalogo
        if not lista:
            print("Nenhum jogo para exibir.")
            return
        for jogo in lista[:50]:  # Limita a exibição para 50
            print(jogo)
        if len(lista) > 50:
            print(f"... e mais {len(lista)-50} jogos.")

    def buscar_jogo_por_nome(self, termo):
        termo = termo.lower().strip()
        resultados = [j for j in self.catalogo if termo in j.titulo.lower()]
        return resultados

    def filtrar_por_genero(self, genero):
        genero = genero.lower().strip()
        return [j for j in self.catalogo if j.genero.lower() == genero]

    def filtrar_por_console(self, console):
        console = console.lower().strip()
        return [j for j in self.catalogo if j.console.lower() == console]

    def filtrar_por_nota(self, nota_minima):
        return [j for j in self.catalogo if j.critic_score >= nota_minima]

    def filtrar_por_vendas(self, vendas_minimas):
        return [j for j in self.catalogo if j.total_sales >= vendas_minimas]

    def filtrar_por_publisher(self, publisher):
        publisher = publisher.lower().strip()
        return [j for j in self.catalogo if j.publisher.lower() == publisher]

    def ordenar_jogos(self, criterio, lista=None):
        if lista is None:
            lista = self.catalogo[:]
        else:
            lista = lista[:]
        criterio = criterio.lower().strip()
        if criterio == 'titulo':
            lista.sort(key=lambda j: j.titulo.lower())
        elif criterio == 'nota':
            lista.sort(key=lambda j: j.critic_score, reverse=True)
        elif criterio == 'vendas':
            lista.sort(key=lambda j: j.total_sales, reverse=True)
        elif criterio == 'data':
            lista.sort(key=lambda j: j.release_date)
        elif criterio == 'console':
            lista.sort(key=lambda j: j.console.lower())
        elif criterio == 'genero':
            lista.sort(key=lambda j: j.genero.lower())
        else:
            print("Critério inválido.")
            return None
        return lista

    # ---------- BACKLOG ----------
    def adicionar_ao_backlog(self, id_jogo):
        jogo = self.catalogo_dict.get(id_jogo)
        if jogo:
            self.backlog.enqueue(jogo)
            print(f"'{jogo.titulo}' adicionado ao backlog.")
        else:
            print("ID de jogo inválido.")

    def mostrar_backlog(self):
        self.backlog.mostrar()

    def jogar_proximo(self):
        """Inicia o próximo jogo do backlog, move para recentes e registra sessão simulada."""
        jogo = self.backlog.dequeue()
        if jogo is None:
            print("Backlog vazio. Adicione jogos primeiro.")
            return
        print(f"Iniciando: {jogo.titulo}")
        self.recentes.push(jogo)
        # Não registra sessão automaticamente; o usuário usará a opção de registrar tempo depois
        self.salvar_backlog()
        self.salvar_recentes()

    # ---------- RECENTES ----------
    def mostrar_recentes(self):
        self.recentes.mostrar()

    def retomar_ultimo_jogo(self):
        jogo = self.recentes.topo()
        if jogo is None:
            print("Nenhum jogo recente.")
            return None
        print(f"Retomando: {jogo.titulo}")
        self.recentes.push(jogo)  # Empilha novamente (move para topo)
        return jogo

    # ---------- SESSÃO ----------
    def registrar_sessao(self, id_jogo, tempo):
        jogo = self.catalogo_dict.get(id_jogo)
        if jogo is None:
            print("Jogo não encontrado.")
            return
        # Atualiza tempo acumulado
        self.tempos_acumulados[id_jogo] = self.tempos_acumulados.get(id_jogo, 0) + tempo
        # Cria sessão
        sessao = SessaoJogo(jogo, tempo)
        # Atualiza status da sessão com base no tempo acumulado
        sessao.status = SessaoJogo._calcular_status(self.tempos_acumulados[id_jogo])
        self.historico.append(sessao)
        # Empilha nos recentes
        self.recentes.push(jogo)
        self.salvar_historico()
        self.salvar_recentes()
        print(f"Sessão registrada: {jogo.titulo} ({tempo:.1f}h). Total acumulado: {self.tempos_acumulados[id_jogo]:.1f}h. Status: {sessao.status}")

    def mostrar_historico(self):
        if not self.historico:
            print("Nenhuma sessão registrada.")
            return
        print("\n--- HISTÓRICO DE SESSÕES ---")
        for i, s in enumerate(self.historico, 1):
            print(f"{i}. {s.jogo.titulo} | Sessão: {s.tempo_jogado:.1f}h | Total acum: {self.tempos_acumulados.get(s.jogo.id, 0):.1f}h | Status: {s.status} | {s.data_sessao}")
        print("-----------------------------")

    # ---------- RECOMENDAÇÕES ----------
    def recomendar_jogos(self):
        """Gera recomendações baseadas no perfil do usuário."""
        if not self.historico:
            print("Jogue alguns jogos para receber recomendações.")
            return []

        # Gênero mais jogado (por número de sessões)
        generos = {}
        for s in self.historico:
            g = s.jogo.genero
            generos[g] = generos.get(g, 0) + 1
        genero_favorito = max(generos, key=generos.get)

        # Console mais jogado
        consoles = {}
        for s in self.historico:
            c = s.jogo.console
            consoles[c] = consoles.get(c, 0) + 1
        console_favorito = max(consoles, key=consoles.get)

        # Nota média jogada
        notas = [s.jogo.critic_score for s in self.historico]
        nota_media = sum(notas) / len(notas)

        # IDs de jogos já jogados e no backlog
        ids_jogados = set(s.jogo.id for s in self.historico)
        ids_backlog = set(j.id for j in self.backlog.to_list())

        candidatos = []
        for jogo in self.catalogo:
            if jogo.id in ids_jogados or jogo.id in ids_backlog:
                continue
            # Pontuação: gênero favorito (peso 3), console favorito (peso 2), nota próxima (peso 1)
            score = 0
            if jogo.genero == genero_favorito:
                score += 3
            if jogo.console == console_favorito:
                score += 2
            if jogo.critic_score >= nota_media:
                score += 1
            if score > 0:
                candidatos.append((jogo, score))

        # Ordena por score decrescente e depois por nota
        candidatos.sort(key=lambda x: (x[1], x[0].critic_score), reverse=True)

        recomendados = [j for j, _ in candidatos[:10]]

        print(f"\n--- RECOMENDAÇÕES ---")
        print(f"Critérios: Gênero favorito='{genero_favorito}', Console favorito='{console_favorito}', Nota média={nota_media:.1f}")
        if not recomendados:
            print("Nenhuma recomendação disponível.")
        else:
            for i, j in enumerate(recomendados, 1):
                print(f"{i}. {j}")
        print("-----------------------")
        return recomendados

    # ---------- RANKING ----------
    def gerar_ranking_pessoal(self):
        if not self.historico:
            print("Sem dados para ranking.")
            return

        # Jogos mais jogados (tempo acumulado)
        ranking_tempo = sorted(self.tempos_acumulados.items(), key=lambda x: x[1], reverse=True)
        print("\n--- JOGOS MAIS JOGADOS ---")
        for id_j, tempo in ranking_tempo[:10]:
            jogo = self.catalogo_dict.get(id_j)
            if jogo:
                print(f"{jogo.titulo}: {tempo:.1f}h")
        print("----------------------------")

        # Gêneros mais jogados
        generos_tempo = {}
        for s in self.historico:
            g = s.jogo.genero
            generos_tempo[g] = generos_tempo.get(g, 0) + s.tempo_jogado
        ranking_gen = sorted(generos_tempo.items(), key=lambda x: x[1], reverse=True)
        print("\n--- GÊNEROS MAIS JOGADOS ---")
        for gen, t in ranking_gen:
            print(f"{gen}: {t:.1f}h")
        print("-----------------------------")

        # Consoles mais jogados
        consoles_tempo = {}
        for s in self.historico:
            c = s.jogo.console
            consoles_tempo[c] = consoles_tempo.get(c, 0) + s.tempo_jogado
        ranking_con = sorted(consoles_tempo.items(), key=lambda x: x[1], reverse=True)
        print("\n--- CONSOLES MAIS JOGADOS ---")
        for con, t in ranking_con:
            print(f"{con}: {t:.1f}h")
        print("-------------------------------")

        # Top jogos por nota dentro do histórico
        jogos_unicos = {}
        for s in self.historico:
            jogos_unicos[s.jogo.id] = s.jogo
        ranking_nota = sorted(jogos_unicos.values(), key=lambda j: j.critic_score, reverse=True)
        print("\n--- TOP JOGOS POR NOTA NO HISTÓRICO ---")
        for j in ranking_nota[:10]:
            print(f"{j.titulo}: Nota {j.critic_score}")
        print("----------------------------------------")

    # ---------- DASHBOARD ----------
    def exibir_dashboard(self):
        total_catalogo = len(self.catalogo)
        total_backlog = self.backlog.tamanho()
        total_recentes = self.recentes.tamanho()
        total_sessoes = len(self.historico)
        tempo_total = sum(self.tempos_acumulados.values())
        jogo_mais_jogado = None
        if self.tempos_acumulados:
            id_max = max(self.tempos_acumulados, key=self.tempos_acumulados.get)
            jogo_mais_jogado = self.catalogo_dict.get(id_max)

        generos = {}
        for s in self.historico:
            generos[s.jogo.genero] = generos.get(s.jogo.genero, 0) + s.tempo_jogado
        genero_fav = max(generos, key=generos.get) if generos else "-"

        consoles = {}
        for s in self.historico:
            consoles[s.jogo.console] = consoles.get(s.jogo.console, 0) + s.tempo_jogado
        console_fav = max(consoles, key=consoles.get) if consoles else "-"

        notas = [s.jogo.critic_score for s in self.historico]
        nota_media = sum(notas)/len(notas) if notas else 0.0

        status_count = {"iniciado":0, "em andamento":0, "muito jogado":0, "concluído simbolicamente":0}
        for id_j, tem in self.tempos_acumulados.items():
            st = SessaoJogo._calcular_status(tem)
            status_count[st] += 1

        melhor_nota = max(notas) if notas else 0.0
        jogo_melhor_nota = None
        if notas:
            for s in self.historico:
                if s.jogo.critic_score == melhor_nota:
                    jogo_melhor_nota = s.jogo
                    break

        # Jogo mais popular (mais vendas) já jogado
        jogos_jogados = {s.jogo.id: s.jogo for s in self.historico}
        if jogos_jogados:
            jogo_mais_popular = max(jogos_jogados.values(), key=lambda j: j.total_sales)
        else:
            jogo_mais_popular = None

        print("\n========== DASHBOARD STEAMPY ==========")
        print(f"Total de jogos no catálogo: {total_catalogo}")
        print(f"Total de jogos no backlog: {total_backlog}")
        print(f"Total de jogos recentes: {total_recentes}")
        print(f"Total de sessões jogadas: {total_sessoes}")
        print(f"Tempo total jogado: {tempo_total:.1f} horas")
        print(f"Jogo mais jogado: {jogo_mais_jogado.titulo if jogo_mais_jogado else '-'} ({self.tempos_acumulados.get(jogo_mais_jogado.id, 0):.1f}h)" if jogo_mais_jogado else "Jogo mais jogado: -")
        print(f"Gênero favorito: {genero_fav}")
        print(f"Console favorito: {console_fav}")
        print(f"Nota média dos jogos jogados: {nota_media:.1f}")
        print(f"Total de jogos iniciados: {status_count['iniciado']}")
        print(f"Total de jogos em andamento: {status_count['em andamento']}")
        print(f"Total de jogos muito jogados: {status_count['muito jogado']}")
        print(f"Total de jogos concluídos simbolicamente: {status_count['concluído simbolicamente']}")
        print(f"Total de recomendações disponíveis: {len(self.catalogo) - len(jogos_jogados) - total_backlog}")
        print(f"Média de horas por sessão: {tempo_total/total_sessoes if total_sessoes else 0:.1f}h")
        print(f"Jogo mais popular já jogado: {jogo_mais_popular.titulo if jogo_mais_popular else '-'} ({jogo_mais_popular.total_sales}M)" if jogo_mais_popular else "Jogo mais popular já jogado: -")
        print(f"Jogo com melhor nota já jogado: {jogo_melhor_nota.titulo if jogo_melhor_nota else '-'} (Nota {melhor_nota})")
        print("========================================\n")

    # ---------- PERSISTÊNCIA ----------
    def salvar_backlog(self, nome_arquivo="backlog.txt"):
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            for jogo in self.backlog.to_list():
                f.write(f"{jogo.id};{jogo.titulo};{jogo.console}\n")
        print("Backlog salvo.")

    def carregar_backlog(self, nome_arquivo="backlog.txt"):
        if not os.path.exists(nome_arquivo):
            return
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split(';')
                if len(partes) >= 1:
                    try:
                        id_jogo = int(partes[0])
                        jogo = self.catalogo_dict.get(id_jogo)
                        if jogo:
                            self.backlog.enqueue(jogo)
                    except:
                        pass
        print(f"Backlog carregado: {self.backlog.tamanho()} jogos.")

    def salvar_historico(self, nome_arquivo="historico_jogo.txt"):
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            for s in self.historico:
                total_acum = self.tempos_acumulados.get(s.jogo.id, 0)
                f.write(f"{s.jogo.titulo};{s.tempo_jogado:.2f};{total_acum:.2f};{s.status};{s.data_sessao}\n")
        print("Histórico salvo.")

    def carregar_historico(self, nome_arquivo="historico_jogo.txt"):
        if not os.path.exists(nome_arquivo):
            return
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split(';')
                if len(partes) >= 4:
                    titulo, tempo_sessao, tempo_total, status, *resto = partes
                    # Buscar jogo pelo título
                    jogo = None
                    for j in self.catalogo:
                        if j.titulo.lower() == titulo.lower():
                            jogo = j
                            break
                    if jogo:
                        sessao = SessaoJogo(jogo, float(tempo_sessao))
                        sessao.status = status
                        if resto:
                            sessao.data_sessao = resto[0]
                        self.historico.append(sessao)
                        self.tempos_acumulados[jogo.id] = float(tempo_total)
        print(f"Histórico carregado: {len(self.historico)} sessões.")

    def salvar_recentes(self, nome_arquivo="recentes.txt"):
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            for jogo in self.recentes.to_list():
                f.write(f"{jogo.id};{jogo.titulo};{jogo.console}\n")
        print("Recentes salvo.")

    def carregar_recentes(self, nome_arquivo="recentes.txt"):
        if not os.path.exists(nome_arquivo):
            return
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split(';')
                if len(partes) >= 1:
                    try:
                        id_jogo = int(partes[0])
                        jogo = self.catalogo_dict.get(id_jogo)
                        if jogo:
                            self.recentes.push(jogo)
                    except:
                        pass
        print(f"Recentes carregados: {self.recentes.tamanho()} jogos.")

    def carregar_dados(self):
        """Carrega todos os dados persistentes."""
        self.carregar_backlog()
        self.carregar_recentes()
        self.carregar_historico()