from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

def calculate_system_metrics(performances):
    # Define subsystems
    subsystems = {
        'Підсистема 1': [0, 1, 2, 3, 4, 5],  # devices π₀ to π₅
        'Підсистема 2': [6, 7, 8, 9],        # devices π₆ to π₉
        'Підсистема 3': [10, 11, 12, 13, 14] # devices π₁₀ to π₁₄
    }
    
    results = {
        'device_loads': [],
        'subsystem_performances': {},
        'total_real_performance': 0,
        'total_peak_performance': sum(performances),  # π = π₀ + π₁ + ... + π₁₄
        'incompatibility': 0,
        'system_load': 0,
        'system_acceleration': 0,
        'formulas': {
            'device_load': 'pᵢ = πᵣ / πᵢ, де πᵢ — продуктивність i-го пристрою, πᵣ — мінімальна продуктивність у підсистемі',
            'subsystem_performance': 'rᵢ = πᵣ × lᵢ, де lᵢ — кількість пристроїв у підсистемі',
            'total_real_performance': 'r = r₁ + r₂ + r₃',
            'peak_performance': 'π = π₀ + π₁ + ... + π₁₄',
            'incompatibility': 'Δ = π - r',
            'system_load': 'ρ = r / π',
            'system_acceleration': 'S = r / max(πᵢ)'
        }
    }
    
    # Calculate device loads and subsystem performances
    for subsystem_name, device_indices in subsystems.items():
        subsystem_performances = [performances[i] for i in device_indices]
        min_performance = min(subsystem_performances)  # πᵣ
        
        # Calculate device loads (pᵢ = πᵣ / πᵢ)
        for i in device_indices:
            load = min_performance / performances[i]
            results['device_loads'].append({
                'device': i,  # Keep 0-based indexing for π notation
                'load': round(load, 3)
            })
        
        # Calculate real subsystem performance (rᵢ = πᵣ × lᵢ)
        real_performance = min_performance * len(device_indices)
        results['subsystem_performances'][subsystem_name] = real_performance
    
    # Calculate total real performance (r = r₁ + r₂ + r₃)
    results['total_real_performance'] = sum(results['subsystem_performances'].values())
    
    # Calculate incompatibility (Δ = π - r)
    results['incompatibility'] = results['total_peak_performance'] - results['total_real_performance']
    
    # Calculate system load (ρ = r / π)
    results['system_load'] = round(results['total_real_performance'] / results['total_peak_performance'], 3)
    
    # Calculate system acceleration (S = r / max(πᵢ))
    max_device_performance = max(performances)
    results['system_acceleration'] = round(results['total_real_performance'] / max_device_performance, 3)
    
    # Generate recommendations with improved logic
    recommendations = []
    for subsystem_name, device_indices in subsystems.items():
        subsystem_performances = [performances[i] for i in device_indices]
        min_performance = min(subsystem_performances)
        
        # Find devices with minimum performance
        bottleneck_devices = [(i, p) for i, p in enumerate(subsystem_performances) if p == min_performance]
        
        if bottleneck_devices:
            # Calculate average performance excluding minimum values
            other_performances = [p for p in subsystem_performances if p > min_performance]
            if other_performances:
                avg_performance = sum(other_performances) / len(other_performances)
                target_performance = round(avg_performance, 2)
                
                # Format device numbers with π notation
                device_list = [f"π{i}" for i, _ in bottleneck_devices]
                
                recommendations.append(
                    f"{subsystem_name} містить пристрої з мінімальною продуктивністю: {', '.join(device_list)}. "
                    f"Рекомендується підвищити їх продуктивність з {min_performance} до {target_performance} "
                    f"для покращення ефективності системи."
                )
    
    results['recommendations'] = recommendations
    
    return results

def calculate_amdahl_metrics(N, n, s):
    # Calculate β (share of sequential operations)
    beta = n / N  # β = n / N
    
    # Calculate Rₛ (system acceleration) using Amdahl's 2nd Law
    R_s = s / (s * beta + (1 - beta))  # Rₛ = s / (s × β + (1 - β))
    
    # Calculate Eₛ (system efficiency)
    E_s = R_s / s  # Eₛ = Rₛ / s
    
    return {
        'beta': round(beta, 2),
        'acceleration': round(R_s, 2),
        'efficiency': round(E_s, 2),
        'formulas': {
            'beta': 'β = n / N, де n — кількість послідовних операцій, N — загальна кількість операцій',
            'acceleration': 'Rₛ = s / (s × β + (1 - β)), де s — кількість процесорів',
            'efficiency': 'Eₛ = Rₛ / s'
        }
    }

def calculate_amdahl_lab8(parallel_fraction, processors, threshold_percent):
    # Calculate β (share of sequential operations)
    beta = 1 - parallel_fraction  # β = 1 - (частка паралельних обчислень)
    
    # Calculate maximum acceleration using Amdahl's 2nd Law
    S_max = processors / (beta * processors + (1 - beta))  # Sₘₐₓ = l / (β × l + (1 - β))
    
    # Calculate minimum number of processors using Amdahl's 3rd Law
    threshold = threshold_percent / 100
    l_min = (threshold * S_max * (1 - beta)) / (1 - threshold * S_max * beta)
    
    return {
        'beta': round(beta, 2),
        'max_acceleration': round(S_max, 2),
        'min_processors': math.ceil(l_min),
        'formulas': {
            'beta': 'β = 1 - (частка паралельних обчислень)',
            'max_acceleration': 'Sₘₐₓ = l / (β × l + (1 - β)), де l — кількість процесорів',
            'min_processors': 'S_l ≥ α × Sₘₐₓ, де α — поріг прискорення'
        }
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    performances = [float(x) for x in data['performances']]
    results = calculate_system_metrics(performances)
    return jsonify(results)

@app.route('/calculate_amdahl', methods=['POST'])
def calculate_amdahl():
    data = request.get_json()
    N = float(data['N'])
    n = float(data['n'])
    s = float(data['s'])
    results = calculate_amdahl_metrics(N, n, s)
    return jsonify(results)

@app.route('/calculate_amdahl_lab8', methods=['POST'])
def calculate_amdahl_lab8_route():
    data = request.get_json()
    parallel_fraction = float(data['parallel_fraction'])
    processors = float(data['processors'])
    threshold_percent = float(data['threshold_percent'])
    results = calculate_amdahl_lab8(parallel_fraction, processors, threshold_percent)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True) 