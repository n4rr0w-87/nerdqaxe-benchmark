# Nerdqaxe++ Hashrate Benchmark Tool

This repository contains a Python script for automatically benchmarking and optimizing voltage and frequency settings on your **Nerdqaxe++** miner.

The goal is to identify the most **efficient**, **safe**, and **high-performance** configuration — with built-in thermal protection, power limits, and intelligent tuning features.

---

## 🚀 Features

- 📊 Automated benchmarking over customizable voltage and frequency ranges
- 🔍 Optional fine-tuning mode (`--fine`) for the **Top 8** best-performing combinations
- 🔁 Resume support (`--resume`) to continue benchmarking from previously saved results
- 🧠 Safety checks:
  - Over-temperature protection (chip and VRM)
  - Power draw limits
  - Input voltage guard rails
- 💾 Saves detailed results in JSON:
  - All tested combinations
  - Top 8 by **hashrate**
  - Top 8 by **efficiency (J/TH)**
- ✅ Automatically resets to best-performing settings after benchmark
- 📈 Real-time feedback during benchmarking: voltage, frequency, hashrate, temperature, and power

---

## 🛠️ Requirements

- Python 3.7+
- `requests` library (`pip install requests`)
- A Nerdqaxe++ device connected to your network with an accessible HTTP API

---

## 🧪 How to Use

```bash
python nerdqaxe_hashrate_benchmark.py <NERDQAXE_IP> [options]
