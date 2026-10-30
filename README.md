<p align="center"><img src="docs/banner.png" alt="Conferência de Operações"></p>

# Conferência de Operações

Pipeline de dados automatizado, com painel web, que **extrai, normaliza e reconcilia XMLs de NF-e, remessas bancárias (CNAB 400 / .BAN) e PDFs de CT-e/NFS-e**, aplica regras de qualidade de dados e mostra apenas as exceções. Tudo certo? Fica verde.

> Todas as imagens e os dados de exemplo deste repositório são **fictícios** (empresas, CNPJs, clientes, gerentes e marca genéricos).

## O que ela faz

- **Automação:** monitora as pastas e reprocessa sozinho quando chega arquivo novo (inclusive PDF atrasado); carga diária de uma consulta SQL Server agendada.
- Compara título, valor, vencimento, endereço, CEP, chave de acesso e ocorrência.
- Classifica em **Alerta**, **Atenção**, **Aguardando TXT** ou **OK**, com a divergência explicada lado a lado.
- Lê vencimentos e parcelas em texto livre nos dados adicionais da NF ("15 ddl", "Vencimento 1: …").
- Confere CT-e e NFS-e sem XML a partir do PDF (valor, vencimento, CNPJ do cliente).
- Mostra o gerente de cada cliente a partir de uma consulta SQL Server (ODBC, 1×/dia, com cache local).
- Controle de acesso por perfil, selo "conferido por…", histórico permanente e área de operações desconsideradas, com motivo.

## Painel

| Lista do dia | Divergência explicada |
|---|---|
| ![](docs/01_lista_claro.png) | ![](docs/02_detalhe_alerta.png) |
| **Título não lançado** | **CT-e conferido pelo PDF** |
| ![](docs/03_detalhe_nao_lancado.png) | ![](docs/04_detalhe_cte_pdf.png) |
| **Desconsideradas** | **Modo escuro** |
| ![](docs/07_desconsideradas.png) | ![](docs/08_lista_escuro.png) |

## Arquitetura de dados

```
XML NF-e ─┐
TXT CNAB ─┼─► parsers ─► motor de regras ─► SQLite ─► API HTTP ─► painel web
.BAN/ZIP ─┤   (layout     (19 regras
PDF ──────┤    posicional) configuráveis)
SQL Server┘ (gerente via ODBC)
```

- **Parsers:** layout posicional (CNAB 400, 1-based), detecção UTF-8/latin-1, normalização de parcelas (`001` = `A`), chave de acesso de 44 dígitos.
- **Motor:** cada TXT pertence a uma única operação (por chave da NF-e, depois número, depois horário); regras e severidades configuráveis em `config.json`.
- **Persistência:** SQLite (usuários, conferências, histórico, cache de gerentes).

## Stack

Python 3 (biblioteca padrão: `http.server`, `sqlite3`, `threading`) · `pypdf` · `pyodbc` · SQL Server · JavaScript/HTML/CSS sem framework · testes com `unittest`.

## Como rodar a demonstração

```bash
pip install -r requirements.txt -r requirements-demo.txt
python app.py --demo
```

Abra `http://localhost:8080` e, no primeiro acesso, crie a senha do administrador. A demo gera uma pasta `exemplos_pasta/` com operações fictícias que têm erros plantados (vencimento, valor, endereço, título não lançado, PDF divergente).

## Testes

```bash
python -m unittest tests.test_demo
```

## Uso com dados reais

Copie `config.example.json` para `config.json` e ajuste as pastas (`PastaRaiz`, `PastaPdfs`, `FontesZip`) e, se quiser o gerente, a seção `Indicantes` (conexão ODBC e consulta que devolve CNPJ e nome). O `config.json` está no `.gitignore`: **não publique credenciais nem arquivos de clientes**.
