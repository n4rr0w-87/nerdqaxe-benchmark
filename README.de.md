# Nerdqaxe++ Hashrate Benchmark Tool

Ein Python-basiertes Benchmarking-Tool zur Optimierung der Mining-Leistung von Nerdqaxe++, das verschiedene Kombinationen von Spannung und Frequenz testet und dabei Hashrate, Temperatur und Energieeffizienz überwacht.

---

## ⚠️ Haftungsausschluss

Bitte verwende dieses Tool verantwortungsvoll. Übertaktung und Spannungsänderungen können deine Hardware beschädigen, wenn sie unsachgemäß durchgeführt werden. Sorge stets für ausreichende Kühlung und überwache dein Gerät während des Benchmarkings.

---

## 🚀 Funktionen

- Automatisiertes Benchmarking verschiedener Spannungs-/Frequenzkombinationen
- Feintuning-Modus (`--fine`), um die 8 besten Kombinationen detaillierter zu testen
- Fortsetzungsmodus (`--resume`), um einen unterbrochenen Benchmark fortzusetzen
- Temperatur- und VRM-Überwachung mit Sicherheitsabschaltung
- Berechnung der Energieeffizienz (Joule/TH)
- Schutz vor zu hoher Leistungsaufnahme und Eingangsspannung
- Sauberer Abbruch und automatische Wiederherstellung der besten Einstellungen
- Speicherung der Ergebnisse im JSON-Format

---

## 📋 Voraussetzungen

- Python 3.11 oder neuer
- Zugang zu einem Nerdqaxe++ Miner im lokalen Netzwerk
- Git (optional, für die Installation)

---

## 🧪 Installation

### 📦 Standard-Installation

```bash
git clone https://github.com/n4rr0w-87/nerdqaxe-benchmark.git
cd nerdqaxe-benchmark
python -m venv venv
source venv/bin/activate  # unter Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶️ Nutzung

### Standard-Benchmark
```bash
python nerdqaxe_benchmark.py <NERDQAXE_IP>
```

### Benchmark fortsetzen
```bash
python nerdqaxe_benchmark.py <NERDQAXE_IP> --resume
```

### Feintuning der besten Ergebnisse
```bash
python nerdqaxe_benchmark.py  <NERDQAXE_IP> --fine
```
> `--resume` is wird automatisch mit `--fine`

### Mit benutzerdefinierten Startwerten
```bash
python nerdqaxe_benchmark.py  192.168.2.26 -v 1175 -f 775
```

---

## ⚙️ Konfiguration

| Parameter                     | Wert           |
|------------------------------|----------------|
| Maximale Chip-Temperatur     | 66 °C          |
| Maximale VRM-Temperatur      | 86 °C          |
| Maximale Leistungsaufnahme   | 40 W           |
| Minimale Spannung            | 1000 mV        |
| Maximale Spannung            | 1400 mV        |
| Minimale Frequenz            | 400 MHz        |
| Maximale Frequenz            | 1200 MHz       |
| Minimale Eingangsspannung    | 4800 mV        |
| Maximale Eingangsspannung    | 5500 mV        |
| Benchmark-Dauer pro Test     | 10 Minuten     |
| Messintervall                | 15 Sekunden    |
| Spannungs-Inkrement          | 20 mV          |
| Frequenz-Inkrement           | 25 MHz         |
| Mindestanzahl gültiger Werte | 7              |

---

## 💾 Ausgabe

- `nerdqaxe_benchmark_results_<ip>.json`
  - Alle getesteten Kombinationen
  - Top 8 Kombinationen (nach Hashrate)
  - Top 8 Kombinationen (nach Effizienz, J/TH)

Jedes Ergebnis enthält:
- Durchschnittliche Hashrate (mit Ausreißerfilterung)
- Durchschnittliche Chip- & VRM-Temperatur
- Leistungsaufnahme & Effizienz
- Eingangsspannung

---

## 🛡️ Sicherheitsfunktionen

- Temperaturabschaltung bei 66–68 °C
- VRM-Abschaltung bei 85–86 °C
- Eingangs­spannungsgrenzen: 11,6–12,0 V
- Leistungsgrenze: 100 W
- Ungültige oder instabile Daten werden verworfen
- Hashrate-Validierung (±10 %)
- Sicherer Abbruch mit `Ctrl+C`
- Automatische Wiederherstellung der besten Einstellungen

---

## 🔄 Benchmark-Ablauf

1. Start mit Standard- oder benutzerdefinierten Werten (Spannung/Frequenz)
2. Führe jede Konfiguration für 10 Minuten aus
3. Messe Temperatur, Leistung und Hashrate
4. Validiere und speichere das Ergebnis
5. Fahre mit der nächsten Konfiguration fort
6. Nach Abschluss wird die beste Konfiguration angewendet

Im `--fine`-Modus:
- Auswahl der 8 besten Konfigurationen (nach Hashrate)
- Feintuning mit ±5 mV / ±10 MHz
- Speichere und aktiviere das neue beste Ergebnis

---

## 🧠 Datenverarbeitung

- Die ersten 6 Temperaturmesswerte werden ignoriert (Aufwärmphase)
- Jeweils 3 niedrigste & 3 höchste Hashrate-Werte werden verworfen
- Effizienz = Durchschnittsleistung / Durchschnitts-Hashrate (J/TH)
- Ungültige oder instabile Ergebnisse werden verworfen

---

## 🤝 Mitwirken

Pull Requests sind willkommen! Forke das Repository und reiche deine Verbesserungen ein.

---

## 📄 Lizenz

GPLv3 – Siehe die Datei `LICENSE` für Details.
