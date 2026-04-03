import argparse
import time
from molecule_builder import Atom, MoleculeFactory
from quantum_solver import run_quantum_vqe
from classical_baseline import calculate_classical_energy
import warnings
from scipy.sparse import SparseEfficiencyWarning

warnings.filterwarnings("ignore", category=SparseEfficiencyWarning)

MOLECULE_LIBRARY = {
    "h2": [Atom("H", 0.0, 0.0, 0.0), Atom("H", 0.0, 0.0, 0.735)],
    "water": [Atom("O", 0.0, 0.0, 0.0), Atom("H", 0.757, 0.586, 0.0), Atom("H", -0.757, 0.586, 0.0)],
    "lih": [Atom("Li", 0.0, 0.0, 0.0), Atom("H", 0.0, 0.0, 1.546)]
}

def main():
    parser = argparse.ArgumentParser(description="VQE Molecular Solver: Local & Cloud QPU")
    parser.add_argument("-m", "--molecule", type=str, choices=MOLECULE_LIBRARY.keys(), default="h2")
    parser.add_argument("-e", "--electrons", type=int, default=None)
    parser.add_argument("-o", "--orbitals", type=int, default=None)
    
    # NEW CLI FLAGS
    parser.add_argument(
        "-b", "--backend", 
        type=str, 
        default="local", 
        help="'local' for Statevector, or provide an IBM backend name (e.g., 'ibm_brisbane')"
    )
    parser.add_argument(
        "--session", 
        action="store_true", 
        help="Enable IBM Quantum Session (Highly recommended for VQE on hardware)"
    )
    
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
    
    # PASS NEW FLAGS TO SOLVER
    q_energy = run_quantum_vqe(
        problem=problem, 
        backend_name=args.backend, 
        use_session=args.session
    )
    
    q_time = time.time() - start_q
    error = abs(c_energy - q_energy)

    # --- Output Report ---
    print("\n" + "="*50)
    print(f"{'Method':<20} | {'Energy (Hartree)':<18} | {'Time (s)':<8}")
    print("-" * 50)
    print(f"{'Classical Exact':<20} | {c_energy:<18.6f} | {c_time:<8.2f}")
    
    # Dynamically update the print label based on execution mode
    q_label = "Quantum (Local)" if args.backend == "local" else f"QPU ({args.backend})"
    print(f"{q_label:<20} | {q_energy:<18.6f} | {q_time:<8.2f}")
    
    print("="*50)
    print(f"Absolute Error: {error:.6f} Hartree\n")

if __name__ == "__main__":
    main()