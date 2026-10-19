# Código x guia de autenticação (`guias/autenticacao.mdx`), grupo conta-e-equipe

Guia não editado. Uma linha por item: o que o guia diz | o que o código faz | fonte.

- Seção "Login de usuário": "`owner` ... gerencia usuários: convida e cria outros" | pela API B2B o `owner` só **cria** o usuário (`POST /partner-users`, com senha no corpo); não há convite por e-mail nessa rota. O convite por e-mail (link de 7 dias) existe só no cadastro feito pela equipe da ClubTrack | `PartnerUserController.php:store`, `CreatePartnerUserHandler.php`
- Seção "Filiais" e tabela de erros: "Use uma filial que `GET /branches` devolve para esse usuário" | `GET /branches` devolve o hub e **todas** as filiais do hub, inclusive as que o usuário não pode acessar; não filtra por acesso do usuário. Não há chamada que liste só as filiais do usuário | `B2bBranchController.php:index`
- Seção "Login de usuário": "o token deixa de valer quando ... o acesso dele expira" | confere na chamada seguinte (401 `Usuário inativo.`), mas o próprio login ainda devolve 200 e token para usuário com acesso vencido | `PartnerAuthController.php:login`, `ResolvesPartnerContext.php:34`
