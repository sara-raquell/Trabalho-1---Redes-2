import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('resultados.csv')

# Remove linhas duplicadas/antigas sem tc
df = df[~((df['protocolo'] == 'TCP') & (df['cenario'] == 'A') & (df['throughput_kbps'].astype(float) > 50000))]
df = df[~((df['protocolo'] == 'RUDP') & (df['cenario'] == 'A') & (df['throughput_kbps'].astype(float) > 1000))]

df['throughput_kbps'] = df['throughput_kbps'].astype(float)

# Estatísticas
stats = df.groupby(['cenario', 'protocolo'])['throughput_kbps'].agg(
    minimo='min',
    media='mean',
    maximo='max',
    desvio='std'
).reset_index()

print("=== ESTATÍSTICAS ===")
print(stats.to_string(index=False))

# Gráfico 1 — Média por cenário
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
cenarios = ['A', 'B', 'C']
titulos = ['Cenário A\n(0% perda / 10ms)', 'Cenário B\n(5% perda / 50ms)', 'Cenário C\n(10% perda / 100ms)']
cores = {'TCP': '#2196F3', 'RUDP': '#FF5722'}

for i, cenario in enumerate(cenarios):
    sub = stats[stats['cenario'] == cenario]
    protocolos = sub['protocolo'].tolist()
    medias = sub['media'].tolist()
    desvios = sub['desvio'].tolist()

    bars = axes[i].bar(protocolos, medias, yerr=desvios, capsize=8,
                       color=[cores[p] for p in protocolos], alpha=0.85, edgecolor='black')
    axes[i].set_title(titulos[i], fontsize=12)
    axes[i].set_ylabel('Throughput (KB/s)')
    axes[i].set_xlabel('Protocolo')

    for bar, media in zip(bars, medias):
        axes[i].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(desvios)*0.05,
                     f'{media:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.suptitle('TCP vs R-UDP — Throughput Médio por Cenário\nSara Raquel de Castro Moraes', fontsize=14)
plt.tight_layout()
plt.savefig('grafico_comparativo.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico salvo: grafico_comparativo.png")

# Gráfico 2 — Evolução por cenário
fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))
protocolos = ['TCP', 'RUDP']

for i, protocolo in enumerate(protocolos):
    sub = stats[stats['protocolo'] == protocolo].sort_values('cenario')
    axes2[i].plot(sub['cenario'], sub['media'], marker='o', linewidth=2,
                  color=cores[protocolo], label=protocolo)
    axes2[i].fill_between(sub['cenario'],
                          sub['media'] - sub['desvio'],
                          sub['media'] + sub['desvio'],
                          alpha=0.2, color=cores[protocolo])
    axes2[i].set_title(f'{protocolo} — Degradação por Cenário')
    axes2[i].set_ylabel('Throughput (KB/s)')
    axes2[i].set_xlabel('Cenário')
    axes2[i].grid(True, alpha=0.3)

plt.suptitle('Degradação do Throughput com Aumento de Perda/Delay', fontsize=13)
plt.tight_layout()
plt.savefig('grafico_degradacao.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico salvo: grafico_degradacao.png")