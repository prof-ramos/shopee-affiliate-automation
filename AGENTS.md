# Repository Guidelines

## Estrutura do Projeto e Organizacao de Modulos

- `SKILL.md`: Instrucoes principais da skill e exemplos rapidos.
- `references/`: Recursos detalhados e exemplos.
  - `references/api-endpoints.md`: Referencia de endpoints da API Shopee.
  - `references/graphql-queries.md`: Queries GraphQL prontas.
  - `references/categories.md`: Lista de IDs de categorias.
  - `references/use-cases.md`: Receitas de uso praticas.
  - `references/n8n-workflows.json`: Export de workflow N8N.
- `.env.example`: Exemplo de configuracao.
- `requirements.txt`: Dependencias Python para scripts locais.

## Comandos de Build, Teste e Desenvolvimento

Nao ha automacao de build ou teste definida.
- Quando adicionar validacao, documente os comandos aqui (ex: `python -m pytest`).

## Estilo de Codigo e Convencoes de Nome

- Markdown: mantenha headings curtos e escaneaveis; evite blocos longos em `SKILL.md`.
- Arquivos: use kebab-case para novos docs de referencia (ex: `references/novo-topico.md`).
- Exemplos: mantenha snippets minimos e aponte para o arquivo completo.

## Diretrizes de Teste

- Nao ha framework de testes configurado.
- Se adicionar testes, crie `tests/` e liste o comando de execucao acima.

## Diretrizes de Commit e Pull Request

- O historico so tem o commit inicial, entao nao ha convencao definida.
- Use mensagens curtas no imperativo (ex: "Refinar referencias").
- PRs devem descrever a intencao, listar arquivos tocados e novas referencias.

## Seguranca e Configuracao

- Nunca commite credenciais reais; use `.env.example` como template.
- Se adicionar chaves, documente as variaveis em `SKILL.md`.

## Instrucoes para Agentes

- Mantenha `SKILL.md` conciso e mova detalhes para `references/`.
- Evite duplicacao entre `SKILL.md` e arquivos de referencia.
