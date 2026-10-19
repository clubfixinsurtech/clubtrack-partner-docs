# Base de conferência

- Commit do core usado como produção: `ff50d33` (`origin/main` do `clubfixinsurtech/clubtrack-core`, lido em 2026-10-19).
- Spec congelada: `openapi-b2b.json`, versão 1.9.0, 35 operações.
- Comportamentos já prontos e **ainda não publicados** no core (as páginas descrevem a produção de hoje; ao mesclar,
  atualize): id mal formado dando 404 (hoje alguns dão 500); e-mail de cliente repetido com 422 igual e teto de tentativas;
  mensagens de validação em português; campo `code` nos erros; spec normalizada.
- Para trocar a base: copie a spec nova, atualize este arquivo e rode `python3 scripts/verificar-contrato.py --final`.
