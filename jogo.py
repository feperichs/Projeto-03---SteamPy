class Jogo:
    """Representa um jogo do catálogo."""
    def __init__(self, id_jogo, titulo, console, genero, publisher, developer,
                 critic_score, total_sales, na_sales, jp_sales, pal_sales,
                 other_sales, release_date):
        self.id = id_jogo
        self.titulo = titulo
        self.console = console
        self.genero = genero
        self.publisher = publisher
        self.developer = developer
        self.critic_score = critic_score
        self.total_sales = total_sales
        self.na_sales = na_sales
        self.jp_sales = jp_sales
        self.pal_sales = pal_sales
        self.other_sales = other_sales
        self.release_date = release_date

    def __str__(self):
        return f"[{self.id}] {self.titulo} ({self.console}) - Nota: {self.critic_score} | Vendas: {self.total_sales}M"

    def __repr__(self):
        return self.__str__()