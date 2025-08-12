# Nerdqaxe++ Hashrate Benchmark Tool

A Python-based benchmarking tool for optimizing Nerdqaxe++ mining performance by testing different voltage and frequency combinations while monitoring hashrate, temperature, and power efficiency.

---

## ⚠️ Disclaimer
Please use this tool responsibly. Overclocking and voltage modifications can potentially damage your hardware if not done carefully.  
Always ensure proper cooling and monitor your device during benchmarking.  
Use at your own risk — the author(s) are not responsible for any hardware damage.

---

## 🚀 Features
- Automated benchmarking of different voltage/frequency combinations
- Fine-tuning mode (`--fine`) to re-test top 8 combinations in more detail
- Resume mode (`--resume`) to continue from saved progress
- **Automatic resume** if previous results are found
- Temperature and VRM monitoring with safety cutoffs
- Power efficiency calculations (J/TH)
- Input voltage and power draw protection
- Graceful shutdown and automatic restoration of best settings
- JSON result storage with backups

---

## 📋 Prerequisites
- Python 3.11 or higher
- Access to a Nerdqaxe++ miner on your local network
- Git (optional)

---

## 🧪 Installation

### 📦 Standard Installation
```bash
git clone https://github.com/n4rr0w-87/nerdqaxe-benchmark.git
cd nerdqaxe-benchmark
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
---

## ▶️ Usage

### Standard Benchmark
```bash
python nerdqaxe_benchmark.py <NERDQAXE_IP>
```

### Resume Previous Benchmark
```bash
python nerdqaxe_benchmark.py <NERDQAXE_IP> --resume
```

### Fine-tune Top Results
```bash
python nerdqaxe_benchmark.py <NERDQAXE_IP> --fine
```
> `--resume` is automatically enabled with `--fine`

### With Initial Settings
```bash
python nerdqaxe_benchmark.py 192.168.2.26 -v 1175 -f 600
```

---

## ⚙️ Configuration
| Parameter                   | Value           |
|----------------------------|-----------------|
| Max chip temp              | 66 °C           |
| Max VR temp                | 86 °C           |
| Max power draw             | 40 W            |
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

## 💾 Output
- `nerdqaxe_benchmark_results_<ip>.json`
  - All combinations tested
  - Top 8 performers (by hashrate)
  - Top 8 efficient settings (J/TH)

Each result includes:
- Average hashrate (with outlier filtering)
- Average chip & VRM temperature
- Power draw & efficiency
- Input voltage

---

## 🛡️ Safety Features
- Max temp cutoff: 66–68 °C
- VRM temp cutoff: 85–86 °C
- Input voltage limits (11.6–12.0 V)
- Power limit: 100 W
- Rejects unstable or invalid data
- Hashrate validation (±10%)
- Graceful shutdown (Ctrl+C)
- Auto-reset to best settings

---

## 🔄 Benchmarking Process
	1.	Start with default or given voltage/frequency
	2.	Run each configuration for 20 minutes
	3.	Collect temperature, power, and hashrate data every 15 seconds
	4.	Validate & store result
	5.	Proceed with next configuration
	6.	After all tests, apply the best result found

In --fine mode:
	•	Take Top 8 hashrate configs
	•	Fine-tune each with ±5 mV / ±10 MHz
	•	Store new top result and apply

In `--fine` mode:
- Take Top 8 hashrate configs
- Fine-tune with ±5 mV / ±10 MHz
- Store new top result and apply

---

## 🧠 Data Processing
	•	First 6 temperature readings ignored (warmup phase)
	•	3 lowest & 3 highest hashrate samples dropped to remove outliers
	•	Efficiency calculated as:
 
 Efficiency (J/TH) = Avg Power / (Avg Hashrate / 1000)
 
 	•	Results rejected if:
	•	Temps exceed limits
	•	Power exceeds limits
	•	Input voltage outside limits
	•	Hashrate outside ±10% of expected
	•	Missing telemetry data


---

## 🤝 Contributing
Pull requests welcome! Feel free to fork the repo and submit improvements.

---

## 📄 License
GPLv3 – See `LICENSE` file for details.
