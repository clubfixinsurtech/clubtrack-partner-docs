#!/usr/bin/env python3
"""Gera referencia/index.mdx a partir do manifesto e do frontmatter das páginas de operação.
Uso: python3 scripts/gerar-indice-referencia.py   (rode de novo quando uma página mudar de título ou descrição)"""
import json, pathlib, re
R = pathlib.Path(__file__).resolve().parent.parent
ops = [o for o in json.loads((R / '.contrato/operacoes.json').read_text(encoding='utf-8')) if o.get('publicado', True)]
docs = json.loads((R / 'docs.json').read_text(encoding='utf-8'))
ordem = []
def varrer(n):
    if isinstance(n, str):
        if n.startswith('referencia/') and n != 'referencia/index': ordem.append(n)
    elif isinstance(n, dict):
        for k in ('pages', 'groups', 'tabs', 'languages'):
            for x in n.get(k, []): varrer(x)
    elif isinstance(n, list):
        for x in n: varrer(x)
varrer(docs['navigation'])
por_pagina = {o['page'][:-4]: o for o in ops}
grupos = {}
for p in ordem:
    o = por_pagina[p]
    grupos.setdefault(o['group_title'], []).append(o)
def fm(o):
    t = (R / o['page']).read_text(encoding='utf-8')
    m = re.match(r'---\n(.*?)\n---', t, flags=re.S)
    d = dict(l.split(':', 1) for l in m.group(1).splitlines() if ':' in l)
    return d['title'].strip().strip('"'), d['description'].strip().strip('"')
saida = ['---', 'title: "Referência da API"', 'description: "Todas as operações da API B2B da ClubTrack, por assunto, com o que cada uma faz."', '---', '',
 'Cada operação tem a sua página, com parâmetros, filtros, respostas, erros e exemplos em quatro linguagens. Esta página é o mapa.', '',
 'Todas as chamadas começam em `https://core.clubtrack.com.br` e usam o caminho `/api/b2b/v1`. Se você ainda não se autenticou, comece por [Autenticação](/guias/autenticacao).', '']
for g, lista in grupos.items():
    saida += [f'## {g}', '', '| Chamada | O que faz |', '|---|---|']
    for o in lista:
        t, d = fm(o)
        caminho = o['path'].replace('/api/b2b/v1', '')
        saida.append(f"| `{o['method']}` `{caminho}` | [{t}](/{o['page'][:-4]}). {d} |")
    saida.append('')
(R / 'referencia/index.mdx').write_text('\n'.join(saida), encoding='utf-8')
print('referencia/index.mdx gerado com', sum(len(v) for v in grupos.values()), 'operações')
