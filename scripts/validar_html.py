
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

RAIZ = Path(__file__).resolve().parent.parent
PASTA_HTML = RAIZ / "paginas"


class ValidadorLinks(HTMLParser):
    def __init__(self, arquivo):
        super().__init__()
        self.arquivo = arquivo
        self.erros = []

    def handle_starttag(self, tag, attrs):
        for atributo, valor in attrs:
            if atributo not in ("src", "href", "poster"):
                continue

            if not valor:
                continue

            # Ignora links externos e referencias internas.
            if valor.startswith(("#", "//")):
                continue

            url = urlsplit(valor)

            if url.scheme or url.netloc:
                continue

            caminho = unquote(url.path)

            if not caminho:
                continue

            # Caminhos iniciados por / usam a raiz do site.
            if caminho.startswith("/"):
                destino = RAIZ / caminho.lstrip("/")
            else:
                destino = self.arquivo.parent / caminho

            if not destino.exists():
                self.erros.append(
                    f"{self.arquivo.relative_to(RAIZ)}: "
                    f"arquivo inexistente -> {valor}"
                )


def main():
    arquivos = sorted(PASTA_HTML.rglob("*.html"))

    if not arquivos:
        print("ERRO: nenhum arquivo HTML encontrado.")
        raise SystemExit(1)

    erros = []

    for arquivo in arquivos:
        validador = ValidadorLinks(arquivo)
        validador.feed(arquivo.read_text(encoding="utf-8"))
        erros.extend(validador.erros)

    if erros:
        print("Falha na validacao:")
        for erro in erros:
            print(f" - {erro}")
        raise SystemExit(1)

    print(f"Validacao aprovada: {len(arquivos)} paginas verificadas.")


if __name__ == "__main__":
    main()
