import numpy as np
import matplotlib.pyplot as plt
from classical_baseline import calculate_classical_energy
from quantum_solver import run_quantum_vqe

def generate_dissociation_curve():
    # 1. Define the range of bond distances (in Angstroms)
    # We go from very close (0.3) to pulled apart (2.5)
    distances = np.linspace(0.3, 2.5, 20)
    
    classical_energies = []
    quantum_energies = []

    print(f"Starting PES Scan ({len(distances)} points)...")
    
    for i, d in enumerate(distances):
        print(f"[{i+1}/{len(distances)}] Calculating distance: {d:.3f} A")
        
        # Classical Result (Fixing the index right here)
        c_res = calculate_classical_energy(d)
        classical_energies.append(float(c_res.total_energies[0]))
        
        # Quantum Result
        q_res = run_quantum_vqe(d)
        quantum_energies.append(float(q_res))

    # 2. Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(distances, classical_energies, 'r-', label='Classical (Exact)')
    plt.plot(distances, quantum_energies, 'bo', label='Quantum (VQE)')
    
    plt.title('H2 Dissociation Curve (Potential Energy Surface)')
    plt.xlabel('Interatomic Distance (Angstroms)')
    plt.ylabel('Total Energy (Hartree)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    # Identify the equilibrium bond length (the minimum of the curve)
    min_energy_idx = np.argmin(quantum_energies)
    eq_dist = distances[min_energy_idx]
    plt.annotate(f'Equilibrium: ~{eq_dist:.3f} A', 
                 xy=(eq_dist, quantum_energies[min_energy_idx]),
                 xytext=(eq_dist+0.2, quantum_energies[min_energy_idx]+0.2),
                 arrowprops=dict(facecolor='black', shrink=0.05))

    # Save the plot
    plt.savefig('h2_dissociation_curve.png', dpi=300)
    print("\nScan complete! Plot saved as 'h2_dissociation_curve.png'")
    plt.show()

if __name__ == "__main__":
    generate_dissociation_curve()