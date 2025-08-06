# =============================================================
#                      IMPORTS & TERMINAL COLORS
# =============================================================
import requests
import time
import json
import signal
import sys
import argparse
import os

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

# =============================================================
#                        ARGUMENT PARSING
# =============================================================
def parse_arguments():
    parser = argparse.ArgumentParser(description='Bitaxe Hashrate Benchmark Tool')
    parser.add_argument('nerdqaxe_ip', nargs='?', help='IP address of the Bitaxe (e.g., 192.168.2.26)')
    parser.add_argument('-v', '--voltage', type=int, default=1150,
                        help='Initial voltage in mV (default: 1150)')
    parser.add_argument('-f', '--frequency', type=int, default=600,
                        help='Initial frequency in MHz (default: 600)')
    parser.add_argument('--resume', action='store_true', help='Resume from previous benchmark results')
    parser.add_argument('--fine', action='store_true', help='Use fine-grained frequency stepping')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()

# =============================================================
#                              SETUP
# =============================================================
args = parse_arguments()

# Setup file names for results and backups
from datetime import datetime
ip_address = args.nerdqaxe_ip
resume_filename = f"nerdqaxe_benchmark_results_{ip_address}.json"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_filename = f"{resume_filename}.{timestamp}.bak"

# Create backup if existing results file is found
if os.path.exists(resume_filename):
    try:
        import shutil
        shutil.copy2(resume_filename, backup_filename)
        print(GREEN + f"Backup created: {backup_filename}" + RESET)
    except Exception as e:
        print(RED + f"Failed to create backup file: {e}" + RESET)

# Automatically activate resume if file exists
if not args.resume and os.path.exists(resume_filename):
    print(YELLOW + f"Found existing results for {ip_address}, automatically resuming..." + RESET)
    args.resume = True

# Fine tuning requires resume mode
if args.fine and not args.resume:
    print(YELLOW + "--fine mode requires previous results. Automatically enabling --resume." + RESET)
    args.resume = True

# Define target device and initial parameters
nerdqaxe_ip = f"http://{ip_address}"
initial_voltage = args.voltage
initial_frequency = args.frequency

# =============================================================
#                    BENCHMARK CONFIGURATION
# =============================================================
voltage_increment = 10
frequency_increment = 10 if args.fine else 20
benchmark_time = 1200
sample_interval = 15
max_temp = 68
max_allowed_voltage = 1200
max_allowed_frequency = 750
max_vr_temp = 85
min_input_voltage = 11600
max_input_voltage = 12000
max_power = 100
small_core_count = None
asic_count = None
min_allowed_voltage = 1120
min_allowed_frequency = 500

# =============================================================
#                        VALIDATION
# =============================================================
if initial_voltage > max_allowed_voltage:
    raise ValueError(RED + f"Error: Initial voltage exceeds the maximum allowed value of {max_allowed_voltage}mV." + RESET)
if initial_frequency > max_allowed_frequency:
    raise ValueError(RED + f"Error: Initial frequency exceeds the maximum allowed value of {max_allowed_frequency}MHz." + RESET)
if initial_voltage < min_allowed_voltage:
    raise ValueError(RED + f"Error: Initial voltage is below the minimum allowed value of {min_allowed_voltage}mV." + RESET)
if initial_frequency < min_allowed_frequency:
    raise ValueError(RED + f"Error: Initial frequency is below the minimum allowed value of {min_allowed_frequency}MHz." + RESET)
if benchmark_time / sample_interval < 7:
    raise ValueError(RED + "Error: Benchmark time is too short. At least 7 samples are required." + RESET)

# =============================================================
#                      RESUME HANDLING
# =============================================================
results = []
tested_combinations = set()
default_voltage = None
default_frequency = None
handling_interrupt = False
system_reset_done = False

resume_filename = f"nerdqaxe_benchmark_results_{args.nerdqaxe_ip}.json"
if args.resume and os.path.exists(resume_filename):
    with open(resume_filename, "r") as f:
        try:
            resume_data = json.load(f)
            if "all_results" in resume_data:
                resume_results = resume_data["all_results"]
            else:
                resume_results = resume_data
            for entry in resume_results:
                tested_combinations.add((entry["coreVoltage"], entry["frequency"]))
            print(GREEN + f"Resuming benchmark. Loaded {len(tested_combinations)} tested combinations." + RESET)
            results.extend(resume_results)
        except Exception as e:
            print(RED + f"Error loading resume data: {e}" + RESET)

# =============================================================
#                    SYSTEM INTERACTION
# =============================================================
def fetch_default_settings():
    global default_voltage, default_frequency, small_core_count, asic_count
    try:
        response = requests.get(f"{nerdqaxe_ip}/api/system/info", timeout=10)
        response.raise_for_status()
        system_info = response.json()
        default_voltage = system_info.get("coreVoltage", 1150)  # Fallback to 1150 if not found
        default_frequency = system_info.get("frequency", 600)  # Fallback to 600 if not found
        small_core_count = system_info.get("smallCoreCount", 0)
        asic_count = system_info.get("asicCount", 0)
        print(GREEN + f"Current settings determined:\n"
                      f"  Core Voltage: {default_voltage}mV\n"
                      f"  Frequency: {default_frequency}MHz\n"
                      f"  ASIC Configuration: {small_core_count * asic_count} total cores" + RESET)
    except requests.exceptions.RequestException as e:
        print(RED + f"Error fetching default system settings: {e}. Using fallback defaults." + RESET)
        default_voltage = 1150
        default_frequency = 600
        small_core_count = 0
        asic_count = 0

system_reset_done = False
# =============================================================
#             FINE-TUNE FUNCTION FOR TOP PERFORMERS
# =============================================================
def fine_tune_top_performers(top_results):
    print(GREEN + "\n[FINE] Starting fine-tuning phase on top performers..." + RESET)
    fine_voltage_step = 5
    fine_frequency_step = 10

    total_tasks = len(top_results) * 9  # 3x3 grid per top result
    current_task = 1

    for entry in top_results:
        base_voltage = entry["coreVoltage"]
        base_frequency = entry["frequency"]

        for dv in [-fine_voltage_step, 0, fine_voltage_step]:
            for df in [-fine_frequency_step, 0, fine_frequency_step]:
                new_voltage = base_voltage + dv
                new_frequency = base_frequency + df

                if (new_voltage, new_frequency) in tested_combinations:
                    continue
                if not (min_allowed_voltage <= new_voltage <= max_allowed_voltage):
                    continue
                if not (min_allowed_frequency <= new_frequency <= max_allowed_frequency):
                    continue

                print(YELLOW + f"[{current_task}/{total_tasks}] [FINE] Testing: {new_voltage}mV @ {new_frequency}MHz" + RESET)
                current_task += 1
                set_system_settings(new_voltage, new_frequency)
                avg_hashrate, avg_temp, efficiency_jth, hashrate_within_tolerance, avg_vr_temp, error_reason = benchmark_iteration(new_voltage, new_frequency)

                if avg_hashrate and avg_temp and efficiency_jth:
                    result = {
                        "coreVoltage": new_voltage,
                        "frequency": new_frequency,
                        "averageHashRate": avg_hashrate,
                        "averageTemperature": avg_temp,
                        "efficiencyJTH": efficiency_jth
                    }
                    if avg_vr_temp is not None:
                        result["averageVRTemp"] = avg_vr_temp

                    results.append(result)
                    tested_combinations.add((new_voltage, new_frequency))
                else:
                    print(YELLOW + f"[FINE] Skipping unstable result at {new_voltage}mV @ {new_frequency}MHz" + RESET)
# =============================================================
#                      SIGNAL HANDLING
# =============================================================
def handle_sigint(signum, frame):
    global system_reset_done, handling_interrupt

    if handling_interrupt or system_reset_done:
        return

    handling_interrupt = True
    print(RED + "Benchmarking interrupted by user." + RESET)

    try:
        if results:
            reset_to_best_setting()
            save_results()
            print(GREEN + "Bitaxe reset to best or default settings and results saved." + RESET)
        else:
            print(YELLOW + "No valid benchmarking results found. Applying predefined default settings." + RESET)
            set_system_settings(default_voltage, default_frequency)
    finally:
        system_reset_done = True
        handling_interrupt = False
        sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

def get_system_info():
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(f"{nerdqaxe_ip}/api/system/info", timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.Timeout:
            print(YELLOW + f"Timeout while fetching system info. Attempt {attempt + 1} of {retries}." + RESET)
        except requests.exceptions.ConnectionError:
            print(RED + f"Connection error while fetching system info. Attempt {attempt + 1} of {retries}." + RESET)
        except requests.exceptions.RequestException as e:
            print(RED + f"Error fetching system info: {e}" + RESET)
            break
        time.sleep(5)  # Wait before retrying
    return None
# =============================================================
#                  BENCHMARKING FUNCTION
# =============================================================
def set_system_settings(core_voltage, frequency):
    settings = {
        "coreVoltage": core_voltage,
        "frequency": frequency
    }
    try:
        response = requests.patch(f"{nerdqaxe_ip}/api/system", json=settings, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print(YELLOW + f"Applying settings: Voltage = {core_voltage}mV, Frequency = {frequency}MHz" + RESET)
        time.sleep(2)
        restart_system()
    except requests.exceptions.RequestException as e:
        print(RED + f"Error setting system settings: {e}" + RESET)

def restart_system():
    try:
        is_interrupt = handling_interrupt

        if not is_interrupt:
            print(YELLOW + "Applying new settings and waiting 600s for system stabilization..." + RESET)
            response = requests.post(f"{nerdqaxe_ip}/api/system/restart", timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            time.sleep(600)  # Allow 600s, time for the system to restart and start hashing
        else:
            print(YELLOW + "Applying final settings..." + RESET)
            response = requests.post(f"{nerdqaxe_ip}/api/system/restart", timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(RED + f"Error restarting the system: {e}" + RESET)

def benchmark_iteration(core_voltage, frequency):
    current_time = time.strftime("%H:%M:%S")
    print(GREEN + f"[{current_time}] Starting benchmark for Core Voltage: {core_voltage}mV, Frequency: {frequency}MHz" + RESET)
    hash_rates = []
    temperatures = []
    power_consumptions = []
    vr_temps = []
    total_samples = benchmark_time // sample_interval
    expected_hashrate = frequency * ((small_core_count * asic_count) / 1000)  # Calculate expected hashrate based on frequency

    for sample in range(total_samples):
        info = get_system_info()
        if info is None:
            print(YELLOW + "Skipping this iteration due to failure in fetching system info." + RESET)
            return None, None, None, False, None, "SYSTEM_INFO_FAILURE"

        temp = info.get("temp")
        vr_temp = info.get("vrTemp")  # Get VR temperature if available
        voltage = info.get("voltage")
        if temp is None:
            print(YELLOW + "Temperature data not available." + RESET)
            return None, None, None, False, None, "TEMPERATURE_DATA_FAILURE"

        if temp < 5:
            print(YELLOW + "Temperature is below 5°C. This is unexpected. Please check the system." + RESET)
            return None, None, None, False, None, "TEMPERATURE_BELOW_5"

        # Check both chip and VR temperatures
        if temp >= max_temp:
            print(RED + f"Chip temperature exceeded {max_temp}°C! Stopping current benchmark." + RESET)
            return None, None, None, False, None, "CHIP_TEMP_EXCEEDED"

        if vr_temp is not None and vr_temp >= max_vr_temp:
            print(RED + f"Voltage regulator temperature exceeded {max_vr_temp}°C! Stopping current benchmark." + RESET)
            return None, None, None, False, None, "VR_TEMP_EXCEEDED"

        if voltage < min_input_voltage:
            print(RED + f"Input voltage is below the minimum allowed value of {min_input_voltage}mV! Stopping current benchmark." + RESET)
            return None, None, None, False, None, "INPUT_VOLTAGE_BELOW_MIN"

        if voltage > max_input_voltage:
            print(RED + f"Input voltage is above the maximum allowed value of {max_input_voltage}mV! Stopping current benchmark." + RESET)
            return None, None, None, False, None, "INPUT_VOLTAGE_ABOVE_MAX"

        hash_rate = info.get("hashRate")
        power_consumption = info.get("power")

        if hash_rate is None or power_consumption is None:
            print(YELLOW + "Hashrate or Watts data not available." + RESET)
            return None, None, None, False, None, "HASHRATE_POWER_DATA_FAILURE"

        if power_consumption > max_power:
            print(RED + f"Power consumption exceeded {max_power}W! Stopping current benchmark." + RESET)
            return None, None, None, False, None, "POWER_CONSUMPTION_EXCEEDED"

        hash_rates.append(hash_rate)
        temperatures.append(temp)
        power_consumptions.append(power_consumption)
        if vr_temp is not None and vr_temp > 0:
            vr_temps.append(vr_temp)

        # Calculate percentage progress
        percentage_progress = ((sample + 1) / total_samples) * 100
        status_line = (
            f"[{sample + 1:2d}/{total_samples:2d}] "
            f"{percentage_progress:5.1f}% | "
            f"CV: {core_voltage:4d}mV | "
            f"F: {frequency:4d}MHz | "
            f"H: {int(hash_rate):4d} GH/s | "
            f"IV: {int(voltage):4d}mV | "
            f"T: {int(temp):2d}°C"
        )
        if vr_temp is not None and vr_temp > 0:
            status_line += f" | VR: {int(vr_temp):2d}°C"
        print(status_line + RESET)

        # Only sleep if it's not the last iteration
        if sample < total_samples - 1:
            time.sleep(sample_interval)

    if hash_rates and temperatures and power_consumptions:
        # Remove 3 highest and 3 lowest hashrates in case of outliers
        sorted_hashrates = sorted(hash_rates)
        trimmed_hashrates = sorted_hashrates[3:-3]  # Remove first 3 and last 3 elements
        average_hashrate = sum(trimmed_hashrates) / len(trimmed_hashrates)

        # Sort and trim temperatures (remove lowest 6 readings during warmup)
        sorted_temps = sorted(temperatures)
        trimmed_temps = sorted_temps[6:]  # Remove first 6 elements only
        average_temperature = sum(trimmed_temps) / len(trimmed_temps)

        # Only process VR temps if we have valid readings
        average_vr_temp = None
        if vr_temps:
            sorted_vr_temps = sorted(vr_temps)
            trimmed_vr_temps = sorted_vr_temps[6:]  # Remove first 6 elements only
            average_vr_temp = sum(trimmed_vr_temps) / len(trimmed_vr_temps)

        average_power = sum(power_consumptions) / len(power_consumptions)

        # Add protection against zero hashrate
        if average_hashrate > 0:
            efficiency_jth = average_power / (average_hashrate / 1_000)
        else:
            print(RED + "Warning: Zero hashrate detected, skipping efficiency calculation" + RESET)
            return None, None, None, False, None, "ZERO_HASHRATE"

        # Calculate if hashrate is within 10% of expected
        hashrate_within_tolerance = (average_hashrate >= expected_hashrate * 0.90)

        print(GREEN + f"Average Hashrate: {average_hashrate:.2f} GH/s (Expected: {expected_hashrate:.2f} GH/s)" + RESET)
        print(GREEN + f"Average Temperature: {average_temperature:.2f}°C" + RESET)
        if average_vr_temp is not None:
            print(GREEN + f"Average VR Temperature: {average_vr_temp:.2f}°C" + RESET)
        print(GREEN + f"Efficiency: {efficiency_jth:.2f} J/TH" + RESET)

        return average_hashrate, average_temperature, efficiency_jth, hashrate_within_tolerance, average_vr_temp, None
    else:
        print(YELLOW + "No Hashrate or Temperature or Watts data collected." + RESET)
        return None, None, None, False, None, "NO_DATA_COLLECTED"

# =============================================================
#                  RESULT HANDLING
# =============================================================
def save_results():
    try:
        # Extract IP from nerdqaxe_ip global variable and remove 'http://'
        ip_address = nerdqaxe_ip.replace('http://', '')
        filename = f"nerdqaxe_benchmark_results_{ip_address}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=4)
        print(GREEN + f"Results saved to {filename}" + RESET)
        print()  # Add empty line

    except IOError as e:
        print(RED + f"Error saving results to file: {e}" + RESET)

def reset_to_best_setting():
    if not results:
        print(YELLOW + "No valid benchmarking results found. Applying predefined default settings." + RESET)
        set_system_settings(default_voltage, default_frequency)
    else:
        best_result = sorted(results, key=lambda x: x["averageHashRate"], reverse=True)[0]
        best_voltage = best_result["coreVoltage"]
        best_frequency = best_result["frequency"]

        print(GREEN + f"Applying the best settings from benchmarking:\n"
                      f"  Core Voltage: {best_voltage}mV\n"
                      f"  Frequency: {best_frequency}MHz" + RESET)
        set_system_settings(best_voltage, best_frequency)

    restart_system()

# =============================================================
#                  MAIN LOGIC
# =============================================================
try:
    fetch_default_settings()

    if args.fine:
        if not results:
            print(RED + "No previous results loaded. Cannot fine-tune without baseline data." + RESET)
            sys.exit(1)

        top_8_results = sorted(results, key=lambda x: x["averageHashRate"], reverse=True)[:8]
        fine_tune_top_performers(top_8_results)
        save_results()
        reset_to_best_setting()
        print(GREEN + "✔ Fine-tuning completed. Results saved and best settings applied." + RESET)
        sys.exit(0)

    # Add disclaimer
    print(RED + "\nDISCLAIMER:" + RESET)
    print("This tool will stress test your Bitaxe by running it at various voltages and frequencies.")
    print("While safeguards are in place, running hardware outside of standard parameters carries inherent risks.")
    print("Use this tool at your own risk. The author(s) are not responsible for any damage to your hardware.")
    print("\nNOTE: Ambient temperature significantly affects these results. The optimal settings found may not")
    print("work well if room temperature changes substantially. Re-run the benchmark if conditions change.\n")

    current_voltage = initial_voltage
    current_frequency = initial_frequency

    while current_voltage <= max_allowed_voltage and current_frequency <= max_allowed_frequency:
        if (current_voltage, current_frequency) in tested_combinations:
            print(YELLOW + f"[SKIP] Already tested: {current_voltage:4d} mV @ {current_frequency:4d} MHz" + RESET)

            if current_frequency + frequency_increment <= max_allowed_frequency:
                current_frequency += frequency_increment
            elif current_voltage + voltage_increment <= max_allowed_voltage:
                current_voltage += voltage_increment
                current_frequency = min_allowed_frequency
            else:
                print(GREEN + "✔ Benchmark complete. No remaining combinations." + RESET)
                break

            continue  #

        print(GREEN + f"[RUN] Testing: {current_voltage:4d} mV @ {current_frequency:4d} MHz" + RESET)

        set_system_settings(current_voltage, current_frequency)
        avg_hashrate, avg_temp, efficiency_jth, hashrate_within_tolerance, avg_vr_temp, error_reason = benchmark_iteration(current_voltage, current_frequency)

        if avg_hashrate is not None and avg_temp is not None and efficiency_jth is not None:
            result = {
                "coreVoltage": current_voltage,
                "frequency": current_frequency,
                "averageHashRate": avg_hashrate,
                "averageTemperature": avg_temp,
                "efficiencyJTH": efficiency_jth
            }

            if avg_vr_temp is not None:
                result["averageVRTemp"] = avg_vr_temp

            results.append(result)

            if hashrate_within_tolerance:
                if current_frequency + frequency_increment <= max_allowed_frequency:
                    current_frequency += frequency_increment
                else:
                    break
            else:
                if current_voltage + voltage_increment <= max_allowed_voltage:
                    current_voltage += voltage_increment
                    current_frequency = max(current_frequency - frequency_increment, min_allowed_frequency)
                    print(YELLOW + f"# Hashrate too low. Retry with higher voltage {current_voltage}mV and same frequency." + RESET)
                else:
                    break
        else:
            print(GREEN + "Reached thermal or stability limits. Stopping further testing." + RESET)
            break

    save_results()

except Exception as e:
    print(RED + f"An unexpected error occurred: {e}" + RESET)
    if results:
        reset_to_best_setting()
        save_results()
    else:
        print(YELLOW + "No valid benchmarking results found. Applying predefined default settings." + RESET)
        set_system_settings(default_voltage, default_frequency)
        restart_system()
finally:
    if not system_reset_done:
        if results:
            reset_to_best_setting()
            save_results()
            print(GREEN + "Bitaxe reset to best or default settings and results saved." + RESET)
        else:
            print(YELLOW + "No valid benchmarking results found. Applying predefined default settings." + RESET)
            set_system_settings(default_voltage, default_frequency)
            restart_system()
        system_reset_done = True

    # Print results summary only if we have results
    if results:
        # Sort results by averageHashRate in descending order and get the top 8
        top_8_results = sorted(results, key=lambda x: x["averageHashRate"], reverse=True)[:8]
        top_8_efficient_results = sorted(results, key=lambda x: x["efficiencyJTH"], reverse=False)[:8]

        # Create a dictionary containing all results and top performers
        final_data = {
            "all_results": results,
            "top_performers": [
                {
                    "rank": i,
                    "coreVoltage": result["coreVoltage"],
                    "frequency": result["frequency"],
                    "averageHashRate": result["averageHashRate"],
                    "averageTemperature": result["averageTemperature"],
                    "efficiencyJTH": result["efficiencyJTH"],
                    **({"averageVRTemp": result["averageVRTemp"]} if "averageVRTemp" in result else {})
                }
                for i, result in enumerate(top_8_results, 1)
            ],
            "most_efficient": [
                {
                    "rank": i,
                    "coreVoltage": result["coreVoltage"],
                    "frequency": result["frequency"],
                    "averageHashRate": result["averageHashRate"],
                    "averageTemperature": result["averageTemperature"],
                    "efficiencyJTH": result["efficiencyJTH"],
                    **({"averageVRTemp": result["averageVRTemp"]} if "averageVRTemp" in result else {})
                }
                for i, result in enumerate(top_8_efficient_results, 1)
            ]
        }

        # Save the final data to JSON
        ip_address = nerdqaxe_ip.replace('http://', '')
        filename = f"nerdqaxe_benchmark_results_{ip_address}.json"
        with open(filename, "w") as f:
            json.dump(final_data, f, indent=4)

        print(GREEN + "Benchmarking completed." + RESET)
        if top_8_results:
            print(GREEN + "\nTop 8 Highest Hashrate Settings:" + RESET)
            for i, result in enumerate(top_8_results, 1):
                print(GREEN + f"\nRank {i}:" + RESET)
                print(GREEN + f"  Core Voltage: {result['coreVoltage']}mV" + RESET)
                print(GREEN + f"  Frequency: {result['frequency']}MHz" + RESET)
                print(GREEN + f"  Average Hashrate: {result['averageHashRate']:.2f} GH/s" + RESET)
                print(GREEN + f"  Average Temperature: {result['averageTemperature']:.2f}°C" + RESET)
                print(GREEN + f"  Efficiency: {result['efficiencyJTH']:.2f} J/TH" + RESET)
                if "averageVRTemp" in result:
                    print(GREEN + f"  Average VR Temperature: {result['averageVRTemp']:.2f}°C" + RESET)

            print(GREEN + "\nTop 5 Most Efficient Settings:" + RESET)
            for i, result in enumerate(top_8_efficient_results, 1):
                print(GREEN + f"\nRank {i}:" + RESET)
                print(GREEN + f"  Core Voltage: {result['coreVoltage']}mV" + RESET)
                print(GREEN + f"  Frequency: {result['frequency']}MHz" + RESET)
                print(GREEN + f"  Average Hashrate: {result['averageHashRate']:.2f} GH/s" + RESET)
                print(GREEN + f"  Average Temperature: {result['averageTemperature']:.2f}°C" + RESET)
                print(GREEN + f"  Efficiency: {result['efficiencyJTH']:.2f} J/TH" + RESET)
                if "averageVRTemp" in result:
                    print(GREEN + f"  Average VR Temperature: {result['averageVRTemp']:.2f}°C" + RESET)
        else:
            print(RED + "No valid results were found during benchmarking." + RESET)

# =============================================================
#                  CLEANUP
# =============================================================
def cleanup_and_exit(reason=None):
    global system_reset_done
    if system_reset_done:
        return

    try:
        if results:
            reset_to_best_setting()
            save_results()
            print(GREEN + "Bitaxe reset to best settings and results saved." + RESET)
        else:
            print(YELLOW + "No valid benchmarking results found. Applying predefined default settings." + RESET)
            set_system_settings(default_voltage, default_frequency)
    finally:
        system_reset_done = True
        if reason:
            print(RED + f"Benchmarking stopped: {reason}" + RESET)
        print(GREEN + "Benchmarking completed." + RESET)
        sys.exit(0)
