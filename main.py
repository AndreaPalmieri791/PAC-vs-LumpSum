'''
Confronta l'entrata nel mercato tramite un PAC o tramite Lump Sum
=========
PAC ovvero entrata graduale nel mercato, dato X capitale iniziale in un periodo di tempo Y
il PAC aggisce investendo nell'indice X/Y con la cadenza desiderata
=========
Lump Sum invece, aggisce investendo il capitale iniziale tutto insieme, creando una posizione iniziale massiccia
=========

Risultati attesi: 
Dalla simulazione emergerà che, il PAC distribuendo l'entrada, diminuisce la varianza negativa
garantendoci ritorni massimi negativi minori allo stesso tempo riducendo però i ritorni massimi positivi.
Capiamo anche che più l'intervallo Y è lungo, più gli sbalzi sarannò pareggiati
invece al diminuire di Y avremmo un comportamento uguale al Lump Sum che è sostanzialmente un PAC con Y = 0

Deduciamo che all'aumentare dell'orizzonte temporale del nostro investimento rispetto all'intervallo Y del PAC
i due sistemi iniziano ad assomigliarsi
'''

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Primo Passo, stabiliamo dei valori iniziali (sovrascrivibili da riga di comando)
def parse_args():
    parser = argparse.ArgumentParser(description="Confronta PAC vs Lump Sum sull'indice S&P 500")
    parser.add_argument("--simulazioni", type=int, default=1000,
                         help="Numero di simulazioni casuali da eseguire (default: 1000)")
    parser.add_argument("--capitale", type=float, default=1000,
                         help="Capitale iniziale investito (default: 1000)")
    parser.add_argument("--durata-pac", type=int, default=5,
                         help="Durata del piano di accumulo in anni (default: 5)")
    parser.add_argument("--frequenza-pac", type=int, default=12,
                         help="Rate annue del PAC: 1 annuale, 4 trimestrale, 12 mensile (default: 12)")
    parser.add_argument("--orizzonte", type=int, default=30,
                         help="Orizzonte temporale dell'investimento in anni (default: 30)")
    parser.add_argument("--start", type=str, default="1950-01-01",
                         help="Data minima di partenza YYYY-MM-DD, oppure 0 per usare tutto lo storico disponibile (default: 1950-01-01)")
    parser.add_argument("--seed", type=int, default=42,
                         help="Seed del generatore di numeri casuali, per risultati riproducibili (default: 42)")
    return parser.parse_args()

args = parse_args()
np.random.seed(args.seed)

N_SIMULAZIONI = args.simulazioni
INITIAL_CAPITAL = args.capitale
PAC_DURATION_YEARS = args.durata_pac
PAC_FREQUENCY = args.frequenza_pac
TIME_HORIZON = args.orizzonte
SIMULATION_START = 0 if args.start in ("0", "") else args.start

# Caricare i dati dell'indice (il CSV vive nella stessa cartella dello script)
CSV_PATH = Path(__file__).parent / "sp500_daily_returns.csv"
df = pd.read_csv(CSV_PATH, parse_dates=["date"])

dates = df["date"].values
returns = df["daily_return"].values

def find_position(date):
    return np.searchsorted(dates, pd.Timestamp(date).to_datetime64())

# Funzione per simulare il PAC
def PAC(start):
    pos = find_position(start)
    current_date = dates[pos]
    end_date = (pd.Timestamp(current_date) + pd.DateOffset(years=TIME_HORIZON)).to_datetime64()

    installment = INITIAL_CAPITAL / PAC_DURATION_YEARS / PAC_FREQUENCY  # rata
    total_installments = PAC_DURATION_YEARS * PAC_FREQUENCY             # totale delle rate da versare

    invested_capital = installment    # prima rata versata subito, il giorno di start
    safe_capital = INITIAL_CAPITAL - installment
    installments_made = 1    # rate versate

    installment_step = pd.DateOffset(months=12 // PAC_FREQUENCY)    # 12 // 12 mensile 12 // 1 annuale...
    next_installment_date = (pd.Timestamp(current_date) + installment_step).to_datetime64()

    while(current_date < end_date):
        gain = returns[pos]
        invested_capital *= (1 + gain)

        # versa una nuova rata
        if installments_made < total_installments and current_date >= next_installment_date:
            invested_capital += installment
            safe_capital -= installment
            installments_made += 1
            next_installment_date = (pd.Timestamp(next_installment_date) + installment_step).to_datetime64()

        current_capital = invested_capital + safe_capital

        pos += 1
        current_date = dates[pos]

    return current_capital

# Funzione per simulare il LumpSum
def LumpSum(start):
    pos = find_position(start)
    start_date = dates[pos]
    end_date = (pd.Timestamp(start_date) + pd.DateOffset(years=TIME_HORIZON)).to_datetime64()
    end_pos = find_position(end_date)

    growth_factor = np.prod(1 + returns[pos:end_pos])
    return INITIAL_CAPITAL * growth_factor

def totalGain(start, end):
    return ((end - start) / start) * 100

# Rendimento del mercato durante un periodo di "years" anni da "start"
# (serve per vedere come si è mosso l'indice durante la finestra di entrata del PAC)
def period_return(start, years):
    pos = find_position(start)
    start_date = dates[pos]
    end_date = (pd.Timestamp(start_date) + pd.DateOffset(years=years)).to_datetime64()
    end_pos = find_position(end_date)

    growth_factor = np.prod(1 + returns[pos:end_pos])
    return (growth_factor - 1) * 100

# ============
#     main
# ============

def main():
    CHARTS_DIR = Path(__file__).parent / "charts"
    CHARTS_DIR.mkdir(exist_ok=True)

    top_end = df["date"].max() - pd.DateOffset(years=TIME_HORIZON)
    if(SIMULATION_START):
        bottom_end = pd.Timestamp(SIMULATION_START)    # converte la stringa "YYYY-MM-DD" in Timestamp
    else:
        bottom_end = df["date"].min()

    totalgain_PAC_results = []
    totalgain_lumpsum_results = []
    entry_period_returns = []
    start_dates = []
    for i in range(0, N_SIMULAZIONI):
        total_days = (top_end - bottom_end).days
        random_offset = np.random.randint(0, total_days)
        start = bottom_end + pd.Timedelta(days=random_offset)

        pac_end_capital = PAC(start)
        totalgain_PAC_results.append(totalGain(INITIAL_CAPITAL, pac_end_capital))
        lumpsum_end_capital = LumpSum(start)
        totalgain_lumpsum_results.append(totalGain(INITIAL_CAPITAL, lumpsum_end_capital))
        entry_period_returns.append(period_return(start, PAC_DURATION_YEARS))
        start_dates.append(start)

    totalgain_PAC_results = np.array(totalgain_PAC_results)
    totalgain_lumpsum_results = np.array(totalgain_lumpsum_results)
    entry_period_returns = np.array(entry_period_returns)
    pac_advantage = totalgain_PAC_results - totalgain_lumpsum_results

    # indice (posizione nell'array dei risultati) del caso peggiore/migliore per ciascun metodo
    pac_worst_idx = np.argmin(totalgain_PAC_results)
    pac_best_idx = np.argmax(totalgain_PAC_results)
    lumpsum_worst_idx = np.argmin(totalgain_lumpsum_results)
    lumpsum_best_idx = np.argmax(totalgain_lumpsum_results)

    # ============
    #   riepilogo testuale
    # ============

    print("=" * 56)
    print(f"  Simulazioni eseguite : {N_SIMULAZIONI}")
    print(f"  Capitale iniziale    : {INITIAL_CAPITAL} €")
    print(f"  Orizzonte temporale  : {TIME_HORIZON} anni")
    print(f"  Durata PAC           : {PAC_DURATION_YEARS} anni ({PAC_FREQUENCY} rate/anno)")
    print("=" * 56)
    print(f"{'Metrica':<18}{'PAC':>18}{'Lump Sum':>18}")
    print("-" * 56)
    print(f"{'Media':<18}{np.mean(totalgain_PAC_results):>17.2f}%{np.mean(totalgain_lumpsum_results):>17.2f}%")
    print(f"{'Dev. standard':<18}{np.std(totalgain_PAC_results):>17.2f}%{np.std(totalgain_lumpsum_results):>17.2f}%")
    print(f"{'Peggiore':<18}{np.min(totalgain_PAC_results):>17.2f}%{np.min(totalgain_lumpsum_results):>17.2f}%")
    print(f"{'  data inizio':<18}{start_dates[pac_worst_idx].strftime('%Y-%m-%d'):>18}{start_dates[lumpsum_worst_idx].strftime('%Y-%m-%d'):>18}")
    print(f"{'Migliore':<18}{np.max(totalgain_PAC_results):>17.2f}%{np.max(totalgain_lumpsum_results):>17.2f}%")
    print(f"{'  data inizio':<18}{start_dates[pac_best_idx].strftime('%Y-%m-%d'):>18}{start_dates[lumpsum_best_idx].strftime('%Y-%m-%d'):>18}")
    print("=" * 56)

    # ============
    #   grafico 1: distribuzione del guadagno percentuale
    # ============

    plt.figure(figsize=(10, 6))
    plt.hist(totalgain_lumpsum_results, bins=50, alpha=0.6, label="Lump Sum", color="#1f77b4")
    plt.hist(totalgain_PAC_results, bins=50, alpha=0.6, label="PAC", color="#ff7f0e")
    plt.xlabel("Guadagno percentuale sul capitale (%)")
    plt.ylabel("Numero di simulazioni")
    plt.title(f"Distribuzione del guadagno percentuale — PAC vs Lump Sum\n"
              f"({N_SIMULAZIONI} simulazioni, orizzonte {TIME_HORIZON} anni)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "01_distribuzione_rendimenti.png", dpi=150)
    plt.show()

    # ============
    #   grafico 2: media del 10% dei casi più estremi, negativi e positivi
    # ============

    N_EXTREMES = N_SIMULAZIONI // 10

    def worst_best(results, n=N_EXTREMES):
        sorted_results = np.sort(results)
        return sorted_results[:n], sorted_results[-n:]

    pac_worst, pac_best = worst_best(totalgain_PAC_results)
    lumpsum_worst, lumpsum_best = worst_best(totalgain_lumpsum_results)

    categories = [f"Media dei\npeggiori {N_EXTREMES}", f"Media dei\nmigliori {N_EXTREMES}"]
    pac_values = [np.mean(pac_worst), np.mean(pac_best)]
    lumpsum_values = [np.mean(lumpsum_worst), np.mean(lumpsum_best)]

    x = np.arange(len(categories))
    width = 0.35

    plt.figure(figsize=(10, 6))
    pac_bars = plt.bar(x - width / 2, pac_values, width, label="PAC", color="#ff7f0e")
    lumpsum_bars = plt.bar(x + width / 2, lumpsum_values, width, label="Lump Sum", color="#1f77b4")

    for bars in (pac_bars, lumpsum_bars):
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.0f}%",
                      ha="center", va="bottom" if height >= 0 else "top")

    plt.xticks(x, categories)
    plt.axhline(0, color="gray", linewidth=1)
    plt.ylabel("Guadagno percentuale medio (%)")
    plt.title(f"Caso peggiore vs caso migliore — media dei {N_EXTREMES} scenari estremi")
    plt.legend()
    plt.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "02_casi_estremi.png", dpi=150)
    plt.show()

    # ============
    #   grafico 3: il PAC aiuta quando il mercato scende durante l'entrata?
    # ============

    colors = np.where(pac_advantage >= 0, "#00ff00", "#ff0000")

    trend_coeffs = np.polyfit(entry_period_returns, pac_advantage, 1)
    trend_x = np.array([entry_period_returns.min(), entry_period_returns.max()])
    trend_y = trend_coeffs[0] * trend_x + trend_coeffs[1]

    plt.figure(figsize=(10, 6))
    plt.scatter(entry_period_returns, pac_advantage, c=colors, alpha=0.6, edgecolors="none")
    plt.plot(trend_x, trend_y, color="black", linewidth=1.5, linestyle="--", label="tendenza")
    plt.axhline(0, color="gray", linewidth=1)
    plt.axvline(0, color="gray", linewidth=1)
    plt.xlabel(f"Rendimento del mercato nei primi {PAC_DURATION_YEARS} anni (finestra di entrata del PAC) (%)")
    plt.ylabel("Vantaggio del PAC sul Lump Sum (%)\n(PAC − Lump Sum)")
    plt.title("Il PAC aiuta quando il mercato scende durante l'entrata?")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "03_entrata_vs_vantaggio.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
