# Nerdqaxe++ Hashrate Benchmark Tool

Ein in Python geschriebenes Benchmark-Tool zur Optimierung der Nerdqaxe++-Mining-Performance.  
Es testet automatisch verschiedene Spannungs- und Frequenzkombinationen und überwacht dabei Hashrate, Temperatur und Energieeffizienz.

---

## ⚠️ Haftungsausschluss
Bitte nutze dieses Tool verantwortungsvoll.  
Übertaktung und Spannungsänderungen können deine Hardware beschädigen, wenn sie nicht sorgfältig durchgeführt werden.  
Sorge stets für ausreichende Kühlung und überwache dein Gerät während des Benchmarks.  
Verwendung auf eigenes Risiko – die Autor(en) übernehmen keine Verantwortung für mögliche Schäden.

---

## 🚀 Funktionen
- Automatisches Benchmarking verschiedener Spannungs-/Frequenzkombinationen
- Feinabstimmungsmodus (`--fine`), um die Top-8-Kombinationen detaillierter zu testen
- Fortsetzungsmodus (`--resume`), um einen Benchmark aus gespeicherten Ergebnissen fortzusetzen
- **Automatisches Resume**, wenn vorhandene Ergebnisse gefunden werden
- Temperatur- und VRM-Überwachung mit Sicherheitsabschaltungen
- Berechnung der Energieeffizienz (J/TH)
- Schutz vor zu niedriger/hoher Eingangsspannung und zu hoher Leistungsaufnahme
- Sauberes Beenden und automatisches Wiederherstellen der besten Einstellungen
- Speicherung der Ergebnisse als JSON mit Backups

---

## 📋 Voraussetzungen
- Python 3.11 oder höher
- Zugriff auf einen Nerdqaxe++-Miner im lokalen Netzwerk
- Git (optional)

---

## 🧪 Installation

### 📦 Standardinstallation
```bash
git clone https://github.com/n4rr0w-87/nerdqaxe-benchmark.git
cd nerdqaxe-benchmark
python -m venv venv
source venv/bin/activate  # oder venv\Scripts\activate unter Windows
pip install -r requirements.txt
```
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
> `--resume` wird automatisch mit `--fine`

### Mit benutzerdefinierten Startwerten
```bash
python nerdqaxe_benchmark.py  192.168.2.26 -v 1175 -f 775
```

---

## ⚙️ Konfiguration

| Parameter                   | Value           |
|----------------------------|-----------------|
| Max chip temp              | 66 °C           |
| Max VR temp                | 86 °C           |
| Max power draw             | 100 W            |
| Min voltage                | 1120 mV         |
| Max voltage                | 1200 mV         |
| Min frequency              | 500 MHz         |
| Max frequency              | 7500 MHz        |
| Input voltage min          | 1160 mV         |
| Input voltage max          | 1200 mV         |
| Benchmark duration         | 20 min/test     |
| Sampling interval          | 15 sec          |
| Voltage increment          | 20 mV           |
| Frequency increment        | 25 MHz          |
| Min valid samples per run  | 7               |

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

	•	Max. Chip-Temp-Abschaltung: 68 °C
	•	Max. VRM-Temp-Abschaltung: 85 °C
	•	Eingangsspannungsgrenzen: 11,6–12,0 V
	•	Leistungsaufnahme-Limit: 100 W
	•	Ablehnung instabiler oder ungültiger Daten
	•	Hashrate-Validierung (±10 %)
	•	Sauberes Beenden bei Ctrl+C
	•	Automatisches Wiederherstellen der besten Einstellungen


---

## 🔄 Benchmark-Ablauf

	1.	Start mit Standard- oder angegebenen Spannung/Frequenz
	2.	Jede Konfiguration für 20 Minuten ausführen
	3.	Temperatur, Leistung und Hashrate alle 15 Sekunden erfassen
	4.	Ergebnisse validieren und speichern
	5.	Nächste Konfiguration testen
	6.	Nach Abschluss beste Einstellungen anwenden

Im `--fine`-Modus:

	•	Top-8-Hashrate-Kombinationen auswählen
	•	Jede mit ±5 mV / ±10 MHz feinabstimmen
	•	Neues Top-Ergebnis speichern und anwenden

---

## 🧠 Datenverarbeitung

	•	Erste 6 Temperaturmessungen ignorieren (Aufwärmphase)
	•	3 niedrigste & 3 höchste Hashrate-Werte entfernen (Ausreißer)
 	•	Effizienz-Berechnung:
  Effizienz (J/TH) = Durchschnittsleistung / (Durchschnitts-Hashrate / 1000)
  
	•	Ergebnis wird verworfen, wenn:
	•	Temperaturgrenzen überschritten werden
	•	Leistungsaufnahme-Limit überschritten wird
	•	Eingangsspannung außerhalb der Grenzen liegt
	•	Hashrate außerhalb ±10 % des Sollwertes liegt
	•	Telemetriedaten fehlen

---

## 🤝 Mitwirken

Pull Requests sind willkommen! Forke das Repository und reiche deine Verbesserungen ein.

---

## 📄 Lizenz

GPLv3 – Siehe die Datei `LICENSE` für Details.
