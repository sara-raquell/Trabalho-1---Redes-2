import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('resultados_http.csv')
df['throughput_kbps'] = df['throughput_kbps'].astype(float)

stats = df.groupby(['cenario', 'protocolo', 'arquivo'])['throughput_kbps'].agg(
    minimo='min', media='mean', maximo='max', desvio='std'
).reset_index()

print("=== ESTATÍSTICAS ===")
print(stats.to_string(index=False))

cores = {'TCP': '#2196F3', 'RUDP': '#FF5722'}
arquivos = ['arquivo_100kb.txt', 'arquivo_1mb.txt', 'arquivo_10mb.txt']
labels = ['100KB', '1MB', '10MB']
cenarios = ['A', 'B', 'C']
titulos_cen = ['Cenário A\n(0%/10ms)', 'Cenário B\n(5%/50ms)', 'Cenário C\n(10%/100ms)']

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
for i, (arq, label) in enumerate(zip(arquivos, labels)):
    sub = stats[stats['arquivo'] == arq]
    for j, cenario in enumerate(cenarios):
        s = sub[sub['cenario'] == cenario]
        x = [j - 0.2, j + 0.2]
        medias = []
        desvios = []
        protos = []
        for proto in ['RUDP', 'TCP']:
            row = s[s['protocolo'] == proto]
            if not row.empty:
                medias.append(row['media'].values[0])
                desvios.append(row['desvio'].values[0])
                protos.append(proto)
        axes[i].bar([j - 0.2, j + 0.2], medias, width=0.35,
                    yerr=desvios, capsize=5,
                    color=[cores[p] for p in protos],
                    alpha=0.85, edgecolor='black')
    axes[i].set_title(f'Arquivo {label}')
    axes[i].set_ylabel('Throughput (KB/s)')
    axes[i].set_xticks([0, 1, 2])
    axes[i].set_xticklabels(cenarios)
    axes[i].set_xlabel('Cenário')
    from matplotlib.patches import Patch
    axes[i].legend(handles=[
        Patch(color=cores['RUDP'], label='R-UDP'),
        Patch(color=cores['TCP'], label='TCP')
    ])

plt.suptitle('HTTP TCP vs R-UDP — Throughput por Arquivo e Cenário\nSara Raquel de Castro Moraes', fontsize=13)
plt.tight_layout()
plt.savefig('grafico_http_comparativo.png', dpi=150, bbox_inches='tight')
plt.show()
print("Salvo: grafico_http_comparativo.png")

fig2, axes2 = plt.subplots(1, 3, figsize=(16, 5))
for i, (arq, label) in enumerate(zip(arquivos, labels)):
    sub = stats[stats['arquivo'] == arq]
    for proto in ['TCP', 'RUDP']:
        s = sub[sub['protocolo'] == proto].sort_values('cenario')
        axes2[i].plot(s['cenario'], s['media'], marker='o',
                      color=cores[proto], label=proto, linewidth=2)
        axes2[i].fill_between(s['cenario'],
                              s['media'] - s['desvio'],
                              s['media'] + s['desvio'],
                              alpha=0.2, color=cores[proto])
    axes2[i].set_title(f'Degradação — {label}')
    axes2[i].set_ylabel('Throughput (KB/s)')
    axes2[i].set_xlabel('Cenário')
    axes2[i].legend()
    axes2[i].grid(True, alpha=0.3)

plt.suptitle('Degradação do Throughput HTTP por Tamanho de Arquivo', fontsize=13)
plt.tight_layout()
plt.savefig('grafico_http_degradacao.png', dpi=150, bbox_inches='tight')
plt.show()
print("Salvo: grafico_http_degradacao.png")