# Site de documentação da API B2B da ClubTrack

Documentação pública para parceiros que integram pela API B2B (`https://core.clubtrack.com.br/api/b2b/v1`). Projeto Mintlify
independente do site da ClubFix.

## Como rodar

```bash
mint dev            # prévia local em http://localhost:3000
mint broken-links   # links internos quebrados
python3 scripts/verificar-contrato.py --final   # contrato x páginas, guias, menu, termos proibidos, texto automático
python3 scripts/gerar-indice-referencia.py       # refaz referencia/index.mdx a partir das páginas
python3 scripts/alinhar-series.py                # alinha a série dos dispositivos de exemplo aos dados fictícios
```

Tudo que o verificador aponta como `ERRO` impede publicar. `AVISO` pede decisão: ou se corrige a página, ou se registra a
divergência em `.contrato/divergencias/` citando o nome do parâmetro ou do status.

## Estrutura

| Caminho | O que é |
|---|---|
| `docs.json` | Tema, navegação e configuração do Mintlify |
| `index.mdx`, `primeira-chamada.mdx`, `guias/` | Guias de conceito e integração |
| `referencia/<grupo>/<operacao>.mdx` | Uma página por operação (35) |
| `historico-de-mudancas.mdx` | Changelog por mudança de contrato |
| `logo/`, `images/`, `favicon.png`, `style.css` | Identidade visual (HumanStudio, projeto ClubTrack) |
| `.contrato/` | **Interno.** Spec congelada, manifesto das operações, dados fictícios, fatos conferidos no código, divergências |
| `scripts/` | **Interno.** Verificador de contrato |
| `CONVENCOES.md` | **Interno.** Voz, modelo de página, o que nunca aparece |

`.mintignore` mantém `.contrato/`, `scripts/`, `README.md` e `CONVENCOES.md` fora do site publicado. Não remova essas linhas.
O repositório deve ser **privado**.

## Fonte da verdade

1. O código do `tagtrack-core` no commit de produção citado em `.contrato/LEIA-ME.md`.
2. A spec `docs/api/openapi-b2b.json` do mesmo commit (cópia em `.contrato/`), só para conferência.

Quando o core mudar, atualize a cópia da spec e rode o verificador: ele aponta o que envelheceu. Divergências conhecidas
entre spec e código estão em `.contrato/divergencias/`.

## Sem ambiente de teste

A API não tem sandbox. O campo de testes (Try it, `api.playground.display = interactive`) chama a API de produção direto do navegador, sem
proxy (`proxy = false`; o CORS do core aceita `api/*`) e sem preencher os campos com os exemplos. Toda página que descreve escrita,
cobrança ou envio de mensagem avisa do efeito real.
