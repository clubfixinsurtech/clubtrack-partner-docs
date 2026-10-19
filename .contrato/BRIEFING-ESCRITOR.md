# Briefing comum de quem escreve um grupo de operações

Você escreve as páginas de referência de **um grupo** da API B2B da ClubTrack para o site de documentação (Mintlify).
O leitor é quem integra o sistema de um parceiro. As páginas têm de ser exatas, humanas e completas.

## Leia antes de escrever (nesta ordem)

1. `CONVENCOES.md`: voz, modelo de página, o que nunca aparece, relatório final.
2. `.contrato/fatos-transversais.md`: credenciais, envelope, filtros, erros, webhook, já conferidos no código.
3. `referencia/clientes-e-enderecos/listar-clientes.mdx`: a página-modelo. Mesmo nível de detalhe, mesma estrutura, mesma
   qualidade de texto. Só leitura; não a altere.
4. `.contrato/fixtures.json`: dados fictícios únicos para todos os exemplos.
5. `.contrato/operacoes.json`: as operações do seu grupo (campo `group`), com o caminho da página (`page`).

## Como trabalhar cada operação

1. Localize a rota no core (`/home/sergiodj/workspaces/clubfix/apps/.worktrees/base-e24-main`, somente leitura):
   `grep -rn "<trecho do caminho>" src/*/Infrastructure/Http/routes.php`, depois o controller, o `FormRequest`, o `Resource`
   e as ações/handlers chamados. Anote: middleware da rota (chave só, login só, ambos, parceiro ativo), regras de
   validação exatas (tipo, tamanho, enum, obrigatório, nulo), condições de cada 403/404/409/422/502, efeitos colaterais
   (e-mail, cobrança, fila), filtros/ordenações/inclusões permitidos e o que cada escopo faz.
2. Procure o teste de feature da rota em `tests/` e leia só o que mostra mensagem e caso de borda.
3. Compare com a spec (`.contrato/openapi-b2b.json`, só conferência). Divergência: o código manda, e você registra em
   `.contrato/divergencias/<grupo>.md` (uma linha por item, formato do arquivo da página-modelo).
4. Escreva a página no modelo. Cada campo e cada filtro com explicação própria: o que é, formato, limite, padrão, nulo ou
   não, exemplo, e o efeito em linguagem de quem integra. Mensagem de erro igual à que o código emite.
5. Rode `python3 scripts/verificar-contrato.py --grupo <grupo>`. Zero ERRO. Cada AVISO: corrija a página ou registre a
   divergência com o nome do parâmetro ou do status.

## Limites duros

- Escreva **somente** em `referencia/<grupo>/*.mdx` (as páginas do seu grupo) e em `.contrato/divergencias/<grupo>.md`.
  Nada além disso: nem `docs.json`, nem guias, nem fixtures, nem outras páginas. Se precisar de algo fora, diga no relatório.
- Não escreva no core. Não suba o app, não rode teste, não chame rede, não use `git`.
- Links internos só para: as páginas das operações (`/referencia/<grupo>/<slug>`) e estes guias, que existirão:
  `/guias/autenticacao`, `/guias/convencoes`, `/guias/paginacao-filtros-ordenacao`, `/guias/erros`,
  `/guias/limites-e-boas-praticas`, `/guias/fluxo-de-venda`, `/guias/campos-personalizados`, `/guias/webhook`.
- Seja econômico: leia só os arquivos que a operação usa, use `grep` antes de abrir, não releia o que já leu, não abra
  suíte inteira de teste. Escreva cada página uma vez. Se chegar perto de 110 mil tokens, pare, entregue o que está
  pronto e liste no relatório as páginas que faltam.
- Não afirme o que o código não confirma. Dúvida real vira `[lacuna]` no relatório, não texto na página.
- Defeito do core que você achar (id mal formado dando 500, mensagem enganosa, campo sem validação): registre em
  divergências como "defeito conhecido", não descreva como comportamento e não dê instrução para explorar.
- Efeito real: toda operação que grava, cobra ou envia mensagem leva `<Warning>` com o efeito, porque não há ambiente de
  teste e o campo de testes do site (Try it) chama a produção.

## Relatório final (até 200 palavras)

Páginas escritas, quantidade de divergências registradas, `[lacuna]`, páginas que faltam (se parou pelo teto) e o
resultado do verificador. Nada além.
