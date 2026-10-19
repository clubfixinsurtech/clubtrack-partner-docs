#!/usr/bin/env python3
"""Alinha a série dos dispositivos de exemplo ao arquivo de dados fictícios (série numérica de 15 dígitos).
Mantém o IMEI. Uso: python3 scripts/alinhar-series.py"""
import glob, pathlib
mapa = {'TT-50000001': '000000050000001', 'TT-50000002': '000000050000002', 'TT-50000003': '000000050000003', 'TT-5000': '50000'}
imei = {'860000000000001': '000000050000001', '860000000000002': '000000050000002'}
n = 0
for f in glob.glob('**/*.mdx', recursive=True):
    p = pathlib.Path(f); linhas = p.read_text(encoding='utf-8').split('\n'); novas = []
    for l in linhas:
        o = l
        for a, b in mapa.items(): l = l.replace(a, b)
        if 'imei' not in l.lower():
            for a, b in imei.items(): l = l.replace(a, b)
        n += (l != o); novas.append(l)
    p.write_text('\n'.join(novas), encoding='utf-8')
print('linhas alteradas:', n)
