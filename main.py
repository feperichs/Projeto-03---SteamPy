from steam_py import SteamPy

def menu():
    steam = SteamPy()
    steam.carregar_jogos("dataset.csv")
    steam.carregar_dados()

    while True:
        print("\n========== MENU STEAMPY ==========")
        print("1. Listar catálogo")
        print("2. Buscar jogo por nome")
        print("3. Filtrar por gênero")
        print("4. Filtrar por console")
        print("5. Filtrar por nota mínima")
        print("6. Filtrar por vendas mínimas")
        print("7. Filtrar por publisher")
        print("8. Ordenar catálogo")
        print("9. Adicionar jogo ao backlog")
        print("10. Ver backlog")
        print("11. Jogar próximo do backlog")
        print("12. Ver jogos recentes")
        print("13. Retomar último jogo")
        print("14. Registrar tempo de jogo")
        print("15. Ver histórico completo")
        print("16. Ver recomendações")
        print("17. Ver ranking pessoal")
        print("18. Ver dashboard")
        print("19. Salvar dados")
        print("20. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            steam.listar_jogos()

        elif opcao == "2":
            termo = input("Digite parte do título: ")
            resultados = steam.buscar_jogo_por_nome(termo)
            if resultados:
                steam.listar_jogos(resultados)
            else:
                print("Nenhum jogo encontrado.")

        elif opcao == "3":
            genero = input("Digite o gênero: ")
            resultados = steam.filtrar_por_genero(genero)
            steam.listar_jogos(resultados)

        elif opcao == "4":
            console = input("Digite o console: ")
            resultados = steam.filtrar_por_console(console)
            steam.listar_jogos(resultados)

        elif opcao == "5":
            try:
                nota = float(input("Nota mínima (0-10): "))
                resultados = steam.filtrar_por_nota(nota)
                steam.listar_jogos(resultados)
            except:
                print("Valor inválido.")

        elif opcao == "6":
            try:
                vendas = float(input("Vendas totais mínimas (milhões): "))
                resultados = steam.filtrar_por_vendas(vendas)
                steam.listar_jogos(resultados)
            except:
                print("Valor inválido.")

        elif opcao == "7":
            pub = input("Digite o publisher: ")
            resultados = steam.filtrar_por_publisher(pub)
            steam.listar_jogos(resultados)

        elif opcao == "8":
            print("Ordenar por: titulo, nota, vendas, data, console, genero")
            criterio = input("Critério: ").strip()
            ordenados = steam.ordenar_jogos(criterio)
            if ordenados:
                steam.listar_jogos(ordenados)

        elif opcao == "9":
            try:
                id_jogo = int(input("ID do jogo para adicionar ao backlog: "))
                steam.adicionar_ao_backlog(id_jogo)
            except:
                print("ID inválido.")

        elif opcao == "10":
            steam.mostrar_backlog()

        elif opcao == "11":
            steam.jogar_proximo()

        elif opcao == "12":
            steam.mostrar_recentes()

        elif opcao == "13":
            steam.retomar_ultimo_jogo()

        elif opcao == "14":
            try:
                id_jogo = int(input("ID do jogo jogado: "))
                tempo = float(input("Tempo jogado nesta sessão (horas): "))
                steam.registrar_sessao(id_jogo, tempo)
            except:
                print("Dados inválidos.")

        elif opcao == "15":
            steam.mostrar_historico()

        elif opcao == "16":
            steam.recomendar_jogos()

        elif opcao == "17":
            steam.gerar_ranking_pessoal()

        elif opcao == "18":
            steam.exibir_dashboard()

        elif opcao == "19":
            steam.salvar_backlog()
            steam.salvar_historico()
            steam.salvar_recentes()
            print("Todos os dados foram salvos.")

        elif opcao == "20":
            steam.salvar_backlog()
            steam.salvar_historico()
            steam.salvar_recentes()
            print("Encerrando SteamPy. Até logo!")
            break

        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()