import qiskit.primitives
from qiskit.primitives import BaseEstimatorV1, StatevectorEstimator
qiskit.primitives.BaseEstimator = BaseEstimatorV1

from qiskit.quantum_info import SparsePauliOp
from qiskit.circuit.library import EfficientSU2
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_nature.second_q.circuit.library import HartreeFock
from qiskit_algorithms.optimizers import SPSA
from qiskit_algorithms import VQE

def run_quantum_vqe(problem):
    """
    Executes the VQE algorithm using a high-speed Hardware Efficient Ansatz.
    """
    # 1. Map Fermions to Qubits
    mapper = ParityMapper(num_particles=problem.num_particles)
    
    # 2. Extract Hamiltonian and cast to Sparse format for massive speedup
    fermionic_hamiltonian = problem.hamiltonian.second_q_op()
    qubit_hamiltonian = mapper.map(fermionic_hamiltonian)
    if not isinstance(qubit_hamiltonian, SparsePauliOp):
        qubit_hamiltonian = SparsePauliOp(qubit_hamiltonian)
    
    # 3. Prepare the Quantum State (The Ansatz)
    # We still start with the classical Hartree-Fock guess so the 
    # optimizer isn't starting completely blind.
    initial_state = HartreeFock(
        problem.num_spatial_orbitals,
        problem.num_particles,
        mapper,
    )
    
    # Build the Hardware Efficient Ansatz
    ansatz = EfficientSU2(
        num_qubits=qubit_hamiltonian.num_qubits,
        su2_gates=['ry'],        # Y-rotations are usually sufficient for real Hamiltonians
        entanglement='linear',   # Connects qubits sequentially (0->1, 1->2, etc.)
        reps=3,                  # Number of repeating layers. 1 is extremely shallow!
        initial_state=initial_state
    )

    # 4. Define Optimizer and Estimator
    # SPSA requires far fewer circuit evaluations per step than COBYLA
    optimizer = SPSA(maxiter=1000) 
    estimator = StatevectorEstimator() 

# 5. Run VQE
    vqe = VQE(estimator, ansatz, optimizer)
    
    print(f"Executing VQE... (Ansatz Depth: {ansatz.depth()} gates, Qubits: {qubit_hamiltonian.num_qubits})")
    result = vqe.compute_minimum_eigenvalue(qubit_hamiltonian)
    
    # NEW FIX: The Hamiltonian stores the Nuclear Repulsion AND the Frozen Core energy as constants
    constant_shift = sum(problem.hamiltonian.constants.values())
    
    # Total Energy = Quantum Valence Energy + Classical Core Energy + Nuclear Repulsion
    total_energy = result.eigenvalue.real + constant_shift
    
    return float(total_energy)
    
