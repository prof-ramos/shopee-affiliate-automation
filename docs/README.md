# Shopee Affiliate Automation Skill

Este repositorio empacota uma skill Claude para automatizar fluxos de afiliados
Shopee. O foco e acesso GraphQL a API de Afiliados da Shopee, entrega via
Telegram e orquestracao com N8N. As instrucoes centrais ficam em `SKILL.md`, e
os detalhes completos em `references/`.

## Orientacao rapida

- Comece por: `SKILL.md` (triggers e exemplos rapidos).
- Referencia de API: `references/api-endpoints.md`.
- Biblioteca de queries: `references/graphql-queries.md`.
- Categorias: `references/categories.md`.
- Casos de uso: `references/use-cases.md`.
- Export N8N: `references/n8n-workflows.json`.

## O que esta skill permite

- Buscar ofertas e produtos via GraphQL.
- Gerar links curtos com subIds para rastreamento de canais.
- Automatizar entrega de ofertas com Telegram ou N8N.
- Consultar relatorios de conversao com paginacao via scrollId.
