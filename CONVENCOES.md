# Convenções de escrita do site de documentação

Documento interno. Não é publicado (`.mintignore`). Vale para quem escreve ou revisa qualquer página.

## 1. Para quem escrevemos

Para quem constrói a integração no sistema de um parceiro da ClubTrack: pessoa de desenvolvimento, às vezes com
alguém de operação ao lado. Ela conhece HTTP e JSON. Não conhece o interior da ClubTrack e não precisa conhecer.

Cada página responde, nesta ordem: o que isto faz, quando eu uso, o que preciso ter em mãos, o que mando, o que
recebo, o que pode dar errado e o que faço quando der. A pessoa deve conseguir integrar sem ler código nem abrir chamado.

## 2. Voz

A voz da marca é: **diz o que está acontecendo, sem dramatizar e sem consolar.** Na prática:

- Trate por **você**. Frases curtas, sujeito claro, verbo ativo.
- Concretude antes de abstração. Diga o valor, o limite, o formato. "Até 150 caracteres", não "tamanho razoável".
- Explique o que está **incluído e o que não está**. Quem integra descobre limite em produção; a página deve avisar antes.
- Sem hype, sem superlativo, sem urgência fabricada, sem emoji, sem "poderoso", "robusto", "simples e rápido".
- **Sem travessão de pausa** (o caractere longo ou o médio no meio da frase). Use ponto, vírgula ou dois-pontos. Para
  intervalo, escreva "de 1 a 100". Hífen em palavra composta e em nome de cabeçalho HTTP está certo.
- Sem "não é X, é Y", sem lista de três por reflexo, sem pergunta retórica, sem abertura do tipo "Neste guia você vai aprender".
- Termo técnico entra quando é o nome real do campo ou do cabeçalho. Fora disso, palavra comum: "contato" e não "ping".
- Vocabulário da marca: o produto que a pessoa final enxerga é "bem" ou "Tag" conforme o campo da API; use o nome
  que a API usa (`tag`, `device`) e explique uma vez o que é cada um.
- Português do Brasil, com acentos completos. Nomes de campo, rota e valor ficam como a API os escreve, sem traduzir.

## 3. De onde vem cada afirmação

Ordem de autoridade: **(1) o código** no commit de produção, **(2) a spec**, **(3) documentos antigos**.

- Código de produção, somente leitura: `/home/sergiodj/workspaces/clubfix/apps/.worktrees/base-e24-main` (commit `ff50d33`,
  é a `main` do core). Nunca escreva nessa pasta. Não suba o app, não rode teste, não chame rede.
- Spec congelada para conferência: `.contrato/openapi-b2b.json` (cópia da `docs/api/openapi-b2b.json` no mesmo commit).
  **Não copie texto da spec**: ela tem comentário interno e marcações de implantação que não pertencem a uma página pública.
- Os testes de feature do core (`tests/`) são boa fonte para mensagem de erro e caso de borda.
- Se código e spec divergem, **o código manda**. Registre a divergência em `.contrato/divergencias/<grupo>.md`
  (uma linha por item: operação, o que a spec diz, o que o código faz, arquivo e linha). A Story de normalização da spec
  vai consumir essa lista.
- Se nem o código responde, **a página não afirma**. Escreva no relatório final como `[lacuna]`.
- Não prometa prazo de depreciação, não prometa comportamento futuro, não descreva rota fora de `/api/b2b/v1`. O caminho
  sem `v1` é obsoleto e não aparece em nenhuma página, salvo uma frase no guia de convenções.

## 4. O que nunca aparece numa página pública

- Nomes internos: classes, namespaces, caminhos `src/`, tabelas, filas, nomes de middleware, "Story", "Epic", "E24",
  "Sanctum", "Spatie", "Laravel", "Saloon", "Horizon", "Forge", "core", "tagtrack".
- Qualquer menção a admin interno, painel do time da ClubTrack ou a rotas `api/admin`.
- Cliente, pessoa, empresa, e-mail, telefone, placa, CNPJ ou CPF reais. Só os dados de `.contrato/fixtures.json`.
- Segredos: chaves, tokens, senhas. Use sempre `ttk_...` abreviado ou o texto "sua chave".
- Hosts de painel, portal ou checkout. A API devolve o endereço (`checkout_url`); a página manda usar o que veio.
- Risco de segurança em linguagem de achado. Se uma regra existe por segurança, escreva a regra e o efeito, não o motivo interno.

## 5. Dados de exemplo

Todos os exemplos usam `.contrato/fixtures.json`: mesmos IDs, mesmos nomes, em todas as páginas, para o exemplo de uma
página continuar o da anterior (o cliente criado em "Cadastrar cliente" é o que aparece em "Consultar cliente").
Se faltar um dado, derive de um existente e mantenha o padrão. Não invente nome de empresa com cara de real.
CPF e CNPJ de exemplo passam na validação da API (estão no arquivo de fixtures). Datas: ISO 8601 no formato exato que
a API devolve (confira no código o fuso e o sufixo).

## 6. Modelo de página de operação

Arquivo: `referencia/<grupo>/<slug>.mdx`, com o caminho definido em `.contrato/operacoes.json` (campo `page`).

````mdx
---
title: "Listar clientes"
description: "Uma frase, até 160 caracteres, que diz o que a chamada devolve e para quem."
api: "GET /api/b2b/v1/customers"
---

Dois ou três parágrafos curtos: o que a chamada faz, em que momento da integração você a usa, o que ela não faz.
Inclua o que acontece de efeito colateral (e-mail enviado, cobrança criada) quando houver, em `<Warning>`.

## Quando usar

Casos reais, em frase corrida ou lista curta.

## Autenticação e permissões

Qual credencial vale (chave de API, login humano, ou só um dos dois), qual papel é exigido, o que acontece com parceiro
suspenso. Uma frase de remissão para o guia de autenticação, nunca repetir o guia.

## Parâmetros

### Cabeçalhos
<ParamField header="X-Api-Key" type="string" required>…</ParamField>

### Caminho
<ParamField path="id" type="string (UUID)" required>…</ParamField>

### Consulta
<ParamField query="filter[status]" type="string">significado, valores aceitos, tipo de comparação (exata ou parcial), exemplo</ParamField>

### Corpo
<ParamField body="name" type="string" required>…</ParamField>

## Resposta

Frase com o status de sucesso e o que ele significa.

<ResponseField name="data[].id" type="string (UUID)">…</ResponseField>

## Erros

| Status | Quando acontece | O que fazer |
|---|---|---|

## Exemplos

<RequestExample> blocos cURL, JavaScript, Python e PHP, nesta ordem </RequestExample>
<ResponseExample> um bloco por status documentado, com o corpo real </ResponseExample>

## Detalhes que ajudam

Só o que muda o comportamento do integrador: idempotência, repetição, limites, ordem de chamadas, diferença entre
campo nulo e ausente. Se não houver, omita a seção.
````

Regras do modelo:

- Seções, nomes e ordem acima são fixos; o script `scripts/verificar-contrato.py` confere.
- Em cada `ParamField` e `ResponseField`: **o que é, formato, limites, padrão, se aceita nulo, exemplo**. Campo sem explicação
  é falha. "Identificador do cliente" não é explicação de `id`; diga de onde ele vem e onde se usa.
- Filtros: um `ParamField query="filter[nome]"` por filtro, dizendo o que ele compara, se é exato ou parcial (e se ignora
  maiúscula), como combina com os outros (todos juntos, "e"), e um exemplo de URL. Escopos (`active`, `with_binding`...)
  ganham explicação de efeito, não do nome.
- `sort`: diga que `-campo` inverte e quais campos aceita. `include`: o que cada valor acrescenta na resposta.
- Tipos: `string`, `string (UUID)`, `string (data e hora ISO 8601)`, `integer`, `boolean`, `object`, `string[]`, `object[]`.
  Valores fixos: liste todos, com o significado de cada um.
- Erros: uma linha por status que a rota pode devolver segundo o **código**, não só a spec. Mostre o corpo de erro real
  num `ResponseExample`. Todo erro tem corpo `{"message": "..."}`; 422 acrescenta `errors`. Escreva a mensagem
  como o código a emite hoje (inclusive quando estiver em inglês, que é o caso de filtro inválido e de campo inválido).
- Exemplos: os quatro idiomas fazem a **mesma** chamada. Chave lida do ambiente (`CLUBTRACK_API_KEY`), base
  `https://core.clubtrack.com.br`. JSON de requisição e de resposta precisa ser válido e coerente com o esquema.
  Resposta de sucesso completa, sem reticências dentro do JSON. Em lista, dois itens bastam e `links` e `meta` completos.
- Efeito real: toda chamada que escreve, cobra ou envia mensagem leva `<Warning>` dizendo o efeito, porque não existe
  ambiente de teste e o playground está desligado.
- Componentes permitidos: `ParamField`, `ResponseField`, `RequestExample`, `ResponseExample`, `Note`, `Tip`, `Info`,
  `Warning`, `Steps`, `Tabs`, `Accordion`, `Expandable`, `CodeGroup`. Nada de HTML cru, nada de `iframe`.
- Links internos sempre absolutos a partir da raiz do site: `/guias/erros`, `/referencia/clientes-e-enderecos/consultar-cliente`.

## 7. Relatório final de quem escreve um grupo

Até 200 palavras: arquivos escritos, divergências registradas (quantas), `[lacuna]` encontradas, perguntas para Sergio
(só se bloquearem). O detalhe fica em arquivo, não na resposta.

## 8. Conferência antes de entregar

```bash
python3 scripts/verificar-contrato.py --grupo <slug-do-grupo>
```

Zero `ERRO`. Cada `AVISO` ou é resolvido na página ou aparece em `.contrato/divergencias/<grupo>.md` com o nome do
parâmetro ou do status, para o script reconhecer que foi uma decisão.
