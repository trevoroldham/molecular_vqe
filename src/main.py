import argparse
import time
from molecule_builder import Atom, MoleculeFactory
from quantum_solver import run_quantum_vqe
from classical_baseline import calculate_classical_energy
import warnings
from scipy.sparse import SparseEfficiencyWarning

# Suppress SciPy warnings from Qiskit's internal mappers
warnings.filterwarnings("ignore", category=SparseEfficiencyWarning)

MOLECULE_LIBRARY = {
    "h2": [
        Atom("H", 0.0, 0.0, 0.0), 
        Atom("H", 0.0, 0.0, 0.735)
    ],
    "water": [
        Atom("O", 0.0, 0.0, 0.0), 
        Atom("H", 0.757, 0.586, 0.0), 
        Atom("H", -0.757, 0.586, 0.0)
    ],
    "lih": [
        Atom("Li", 0.0, 0.0, 0.0), 
        Atom("H", 0.0, 0.0, 1.546)
    ]
}

def main():
    parser = argparse.ArgumentParser(description="VQE Molecular Solver")
    parser.add_argument("-m", "--molecule", type=str, choices=MOLECULE_LIBRARY.keys(), default="h2")
    parser.add_argument("-e", "--electrons", type=int, default=None)
    parser.add_argument("-o", "--orbitals", type=int, default=None)
    args = parser.parse_args()

    print(f"\n--- Initializing {args.molecule.upper()} ---")
    atoms = MOLECULE_LIBRARY[args.molecule]
    factory = MoleculeFactory(atoms=atoms)

    if args.electrons and args.orbitals:
        print(f"Applying Active Space: {args.electrons} electrons, {args.orbitals} orbitals (Core frozen).")
    
    problem = factory.build_problem(active_electrons=args.electrons, active_orbitals=args.orbitals)

    # --- Run Classical Baseline ---
    start_c = time.time()
    c_energy = calculate_classical_energy(problem)
    c_time = time.time() - start_c

    # --- Run Quantum VQE ---
    start_q = time.time()
    q_energy = run_quantum_vqe(problem)
    q_time = time.time() - start_q

    # --- Calculate Error ---
    error = abs(c_energy - q_energy)

    # --- Output Report ---
    print("\n" + "="*50)
    print(f"{'Method':<20} | {'Energy (Hartree)':<18} | {'Time (s)':<8}")
    print("-" * 50)
    print(f"{'Classical Exact':<20} | {c_energy:<18.6f} | {c_time:<8.2f}")
    print(f"{'Quantum HEA (VQE)':<20} | {q_energy:<18.6f} | {q_time:<8.2f}")
    print("="*50)
    print(f"Absolute Error: {error:.6f} Hartree")
    
    if error < 1.6e-3:
        print("RESULT: Within Chemical Accuracy (1.6 mHa). Success!")
    else:
        print("RESULT: Outside Chemical Accuracy. This is expected with shallow HEA circuits.")
        print("        Increase 'reps' in the ansatz to improve accuracy.")
    print("\n")

if __name__ == "__main__":
    main()