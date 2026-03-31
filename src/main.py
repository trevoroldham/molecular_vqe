import time
import numpy as np
from classical_baseline import calculate_classical_energy
from quantum_solver import run_quantum_vqe

def main():
    dist = 0.735
    print(f"--- Molecular Analysis for H2 (Bond Distance: {dist} A) ---")
    
    # 1. Run Classical
    start_c = time.time()
    c_result = calculate_classical_energy(dist)
    # Explicitly extract the first element as a float
    c_energy = float(c_result.total_energies[0])
    c_time = time.time() - start_c
    
    # 2. Run Quantum
    start_q = time.time()
    # run_quantum_vqe already returns a float (.real)
    q_energy = float(run_quantum_vqe(dist))
    q_time = time.time() - start_q
    
    # 3. Calculate Error (Now handles two floats, so 'error' is a float)
    error = abs(c_energy - q_energy)
    
    print("\n" + "="*40)
    print(f"{'Method':<15} | {'Energy (Hartree)':<18} | {'Time (s)':<8}")
    print("-" * 40)
    print(f"{'Classical':<15} | {c_energy:<18.8f} | {c_time:<8.4f}")
    print(f"{'Quantum (VQE)':<15} | {q_energy:<18.8f} | {q_time:<8.4f}")
    print("="*40)
    print(f"Absolute Error: {error:.8e} Hartree")
    
    # Chemical Accuracy check (approx 1.6 mHartree)
    if error < 1.6e-3:
        print("RESULT: Within Chemical Accuracy (1.6 mHartree). Success!")
    else:
        print("RESULT: Outside Chemical Accuracy. Optimization tuning required.")

if __name__ == "__main__":
    main()
