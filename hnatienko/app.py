from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

def calculate_system_metrics(performances):
    # Define subsystems
    subsystems = {
        'Підсистема 1': [0, 1, 2, 3, 4],  # devices 1-5 (0-based indexing)
        'Підсистема 2': [5, 6, 7, 8],     # devices 6-9
        'Підсистема 3': [9, 10, 11, 12]   # devices 10-13
    }
    
    results = {
        'device_loads': [],
        'subsystem_performances': {},
        'total_real_performance': 0,
        'total_peak_performance': sum(performances),
        'incompatibility': 0,
        'system_load': 0,
        'system_acceleration': 0
    }
    
    # Calculate device loads and subsystem performances
    for subsystem_name, device_indices in subsystems.items():
        subsystem_performances = [performances[i] for i in device_indices]
        min_performance = min(subsystem_performances)
        
        # Calculate device loads
        for i in device_indices:
            load = min_performance / performances[i]
            results['device_loads'].append({
                'device': i + 1,  # Convert to 1-based indexing for display
                'load': round(load, 3)
            })
        
        # Calculate real subsystem performance
        real_performance = min_performance * len(device_indices)
        results['subsystem_performances'][subsystem_name] = real_performance
    
    # Calculate total real performance
    results['total_real_performance'] = min(results['subsystem_performances'].values())
    
    # Calculate incompatibility
    results['incompatibility'] = results['total_peak_performance'] - results['total_real_performance']
    
    # Calculate system load (ρ = r / π)
    results['system_load'] = round(results['total_real_performance'] / results['total_peak_performance'], 3)
    
    # Calculate system acceleration (S = r / max(πᵢ))
    max_device_performance = max(performances)
    results['system_acceleration'] = round(results['total_real_performance'] / max_device_performance, 3)
    
    # Generate recommendations
    recommendations = []
    for subsystem_name, device_indices in subsystems.items():
        subsystem_performances = [performances[i] for i in device_indices]
        min_performance = min(subsystem_performances)
        bottleneck_devices = [i + 1 for i, p in enumerate(subsystem_performances) if p == min_performance]
        
        if len(bottleneck_devices) > 0:
            recommendations.append(
                f"{subsystem_name} має пристрої-вузькі місця: {', '.join(map(str, bottleneck_devices))}. "
                f"Рекомендується підвищити їх продуктивність з {min_performance} для покращення ефективності системи."
            )
    
    results['recommendations'] = recommendations
    
    return results

def calculate_amdahl_metrics(N, n, s):
    # Calculate β (share of sequential operations)
    beta = n / N
    
    # Calculate Rₛ (system acceleration) using Amdahl's 2nd Law
    R_s = s / (s * beta + (1 - beta))
    
    # Calculate Eₛ (system efficiency)
    E_s = R_s / s
    
    return {
        'beta': round(beta, 2),
        'acceleration': round(R_s, 2),
        'efficiency': round(E_s, 2)
    }

def calculate_amdahl_lab8(parallel_fraction, processors, threshold_percent):
    # Calculate β (share of sequential operations)
    beta = 1 - parallel_fraction
    
    # Calculate maximum acceleration using Amdahl's 2nd Law
    S_max = processors / (beta * processors + (1 - beta))
    
    # Calculate minimum number of processors using Amdahl's 3rd Law
    # We need to solve: l / (β * l + (1 - β)) >= threshold * S_max
    # Rearranging: l >= (threshold * S_max * (1 - β)) / (1 - threshold * S_max * β)
    threshold = threshold_percent / 100
    l_min = (threshold * S_max * (1 - beta)) / (1 - threshold * S_max * beta)
    
    return {
        'beta': round(beta, 2),
        'max_acceleration': round(S_max, 2),
        'min_processors': math.ceil(l_min)  # Round up to nearest integer
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