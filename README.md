# PAC vs Lump Sum — S&P 500

Simulazione Monte Carlo che confronta due strategie di ingresso nel mercato azionario sull'indice **S&P 500**, usando dati storici reali dal 1928 a oggi:

- **PAC (Piano di Accumulo Capitale)** — investi il capitale gradualmente nel tempo, con rate periodiche (es. mensili) distribuite su un certo numero di anni.
- **Lump Sum** — investi tutto il capitale in un'unica soluzione, subito.

Lo script estrae centinaia (o migliaia) di date di partenza casuali dallo storico dell'indice, simula entrambe le strategie da ciascuna data, e confronta i risultati con statistiche e grafici.

## Perché questo confronto

Il dibattito "PAC o Lump Sum?" è uno dei più comuni in ambito di investimenti personali. La risposta intuitiva ("distribuire l'ingresso riduce il rischio") è vera solo in parte: statisticamente, il Lump Sum batte il PAC nella maggioranza degli scenari storici, perché tenere capitale fuori dal mercato ha un costo — si perdono i rendimenti positivi durante l'attesa.

Questo script quantifica esattamente **quanto spesso** e **in quali condizioni** il PAC conviene, usando dati reali invece di intuizioni.

## Cosa emerge dalla simulazione

- Il PAC riduce la varianza dei risultati: meno probabilità di un pessimo risultato, ma anche meno probabilità di un risultato eccezionale.
- Il PAC "vince" sul Lump Sum quasi esclusivamente quando il mercato **scende** durante la finestra di ingresso (i primi anni del piano). Se il mercato sale durante quella finestra, il Lump Sum ha già incassato quei rendimenti e il PAC parte svantaggiato.
- Su tutto lo storico disponibile (1928–oggi, che include il crollo del 1929) il PAC batte il Lump Sum in circa il 20% delle simulazioni. Limitandosi al dopoguerra (dal 1950, un'economia più stabile) scende a circa il 9%.
- Più lungo è il periodo di accumulo del PAC rispetto all'orizzonte totale dell'investimento, più i due sistemi si assomigliano.

## Requisiti

- Python 3.9+
- `pandas`, `numpy`, `matplotlib`

```bash
pip install pandas numpy matplotlib
```

## Struttura della repo

```
main.py                     # script principale (simulazione + grafici)
sp500_daily_returns.csv     # dati storici: data, prezzo di chiusura, rendimento giornaliero
sp500_trend.png             # andamento storico dell'indice (scala logaritmica)
```

Il CSV copre ogni giorno di calendario dal 1928 a oggi (weekend e festivi inclusi, con il prezzo dell'ultimo giorno di borsa aperto), così qualunque data casuale generata dalla simulazione ha sempre un prezzo disponibile.

## Come si usa

Lancia lo script dalla cartella del progetto:

```bash
python3 main.py
```

Di default esegue 1000 simulazioni, capitale iniziale 1000€, PAC su 5 anni con rate mensili, orizzonte di investimento di 30 anni, usando solo date di partenza dal 1950 in poi.

Ogni parametro è sovrascrivibile da riga di comando, senza dover modificare il codice:

| Argomento | Significato | Default |
|---|---|---|
| `--simulazioni` | Numero di simulazioni casuali da eseguire | `1000` |
| `--capitale` | Capitale iniziale investito | `1000` |
| `--durata-pac` | Durata del piano di accumulo, in anni | `5` |
| `--frequenza-pac` | Rate annue del PAC: `1` annuale, `4` trimestrale, `12` mensile | `12` |
| `--orizzonte` | Orizzonte temporale totale dell'investimento, in anni | `30` |
| `--start` | Data minima di partenza (`YYYY-MM-DD`), oppure `0` per usare tutto lo storico dal 1928 | `1950-01-01` |

### Esempi

Usare tutto lo storico disponibile, incluso il crollo del 1929:

```bash
python3 main.py --start 0
```

Capitale più alto, PAC più breve (3 anni), su 5000 simulazioni:

```bash
python3 main.py --capitale 10000 --durata-pac 3 --simulazioni 5000
```

PAC trimestrale su un orizzonte più corto:

```bash
python3 main.py --frequenza-pac 4 --orizzonte 15
```

Vedere tutte le opzioni disponibili:

```bash
python3 main.py --help
```

## Cosa produce

**In terminale**, un riepilogo con media, deviazione standard, e caso peggiore/migliore (con relativa data di partenza) per entrambe le strategie.

**Tre grafici**:
1. **Distribuzione dei rendimenti** — istogramma sovrapposto del guadagno percentuale di PAC e Lump Sum su tutte le simulazioni.
2. **Casi estremi** — confronto della media del 10% dei risultati peggiori e del 10% dei migliori, per entrambe le strategie.
3. **Il PAC aiuta quando il mercato scende in fase di ingresso?** — grafico a dispersione che mette in relazione il rendimento del mercato durante la finestra di ingresso del PAC con il vantaggio (o svantaggio) del PAC rispetto al Lump Sum su quella stessa simulazione.

## Fonte dei dati

Dati storici dell'indice S&P 500 (`^GSPC`) scaricati da Yahoo Finance.

## Licenza

Questo progetto è a scopo educativo/divulgativo. Non è una consulenza finanziaria.
