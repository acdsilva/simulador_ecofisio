# 🔬 Modelo científico do EcoFisioLab

O simulador tem dois níveis. O **modo simples** mostra índices relativos (didáticos). O
**modo científico** (toggle no simulador) aplica leis de fisiologia animal com constantes
típicas da literatura. É um **modelo educacional fundamentado** — usa valores representativos
por classe/espécie, não medições do indivíduo.

Implementação: [`backend/app/physiology.py`](backend/app/physiology.py) e constantes em
[`backend/app/species_data.py`](backend/app/species_data.py) (`PHYSIOLOGY`).

## Fórmulas

### 1. Taxa metabólica basal — Lei de Kleiber (endotérmicos)
```
TMB (kcal/dia) = a · massa_kg^0,75
```
`a ≈ 70` para mamíferos e `≈ 78` para aves. (Kleiber, 1932; Lasiewski & Dawson, 1967.)

### 2. Metabolismo de ectotérmicos — efeito Q10 (réptil)
O réptil **conforma** a temperatura corporal ao ambiente, e o metabolismo varia com ela:
```
SMR (kcal/dia) = a_ecto · massa_kg^0,75 · Q10^((Tb − 30)/10)
```
`a_ecto = 6`, `Q10 = 2,5`, `Tb = temperatura ambiente`. Assim o metabolismo **sobe no calor
e cai no frio** (corrige o modelo antigo, que sempre diminuía).

### 3. Temperatura corporal
Saída calculada (não é entrada): endotérmico = `body_temp_c` da espécie (mamífero ~38 °C,
ave ~41 °C; casos especiais: preguiça ~33 °C, boto ~36 °C). Ectotérmico = temperatura ambiente.

### 4. Custo de termorregulação (endotérmicos)
```
custo = TMB · 1,5 · estresse_térmico
```
onde `estresse_térmico` cresce conforme o ambiente se afasta da faixa térmica ideal.

### 5. Respirometria (consumo de O₂)
```
VO₂ (L/min) = ventilação · (O₂inspirado − O₂expirado)/100
VO₂ (mL/g/h) = VO₂(L/min) · 60 / massa_kg
energia (kcal/dia) = VO₂(L/min) · 4,8 · 1440
```
4,8 kcal/L é o equivalente calórico do oxigênio. Ventilação em repouso estimada por alometria
`≈ 0,38 · massa^0,8` L/min.

### 6. Balanço energético
```
gasto_total = TMB + custo_termo + 0,5·TMB (atividade) + 0,3·TMB (se predador)
balanço = alimento_kcal − gasto_total
```
Balanço **negativo** = déficit (risco de inanição).

### 7. Sobrevivência e composição do estresse
Combina estresse térmico, hídrico, energético (déficit) e de predação; `stress_breakdown`
mostra a contribuição (%) de cada fator.

## Constantes por espécie (literatura)

| Espécie | Classe | massa (kg) | a (Kleiber) | Tb (°C) |
|---|---|---|---|---|
| Capivara | mamífero | 50 | 70 | 38 |
| Quero-quero | ave | 0,28 | 78 | 41 |
| Preá | mamífero | 0,5 | 70 | 38,5 |
| Teiú | réptil (ecto) | 3,5 | — (Q10) | = ambiente |
| Onça-pintada | mamífero | 85 | 70 | 38 |
| Arara-azul | ave | 1,5 | 78 | 41 |
| Boto-cor-de-rosa | mamífero | 120 | 70 | 36 |
| Mico-leão-dourado | mamífero | 0,6 | 70 | 38 |
| Onça-parda | mamífero | 55 | 70 | 38,5 |
| Preguiça | mamífero | 4 | 70 | 33 |
| Veado-catingueiro | mamífero | 17 | 70 | 38,5 |
| Tatu-bola | mamífero | 1,5 | 70 | 35 |
| Asa-branca | ave | 0,35 | 78 | 41 |

## Referências
- Kleiber, M. (1932). *Body size and metabolism.* Hilgardia.
- Lasiewski, R. C. & Dawson, W. R. (1967). *A re-examination of the relation between standard
  metabolic rate and body weight in birds.* Condor.
- Schmidt-Nielsen, K. *Animal Physiology: Adaptation and Environment.*
- Equivalente calórico do O₂ ≈ 4,8 kcal/L (fisiologia do exercício/respirometria).

> Transparência: constantes são valores típicos por classe/espécie para fins **educacionais**,
> não dados medidos de cada indivíduo. As fórmulas, porém, são as leis reais.
