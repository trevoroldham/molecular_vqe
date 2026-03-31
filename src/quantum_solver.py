import numpy as np
import qiskit.primitives
from qiskit.primitives import BaseEstimatorV1, StatevectorEstimator
# Patching for Nature 0.7.2 compatibility with Qiskit 1.0
qiskit.primitives.BaseEstimator = BaseEstimatorV1

from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_nature.second_q.circuit.library import UCCSD, HartreeFock
from qiskit_algorithms.optimizers import COBYLA
from qiskit_algorithms import VQE

def run_quantum_vqe(distance=0.735):
    # 1. Molecular Setup (Matches the classical script)
    driver = PySCFDriver(
        atom=f"H 0 0 0; H 0 0 {distance}",
        basis="sto3g",
        unit=DistanceUnit.ANGSTROM
    )
    problem = driver.run()

    # 2. Map Fermions to Qubits (Parity Mapper with 2-qubit reduction)
    mapper = ParityMapper(num_particles=problem.num_particles)
    
    # 3. Prepare the Quantum State
    # HartreeFock provides a good starting "guess" for the electrons
    ansatz = UCCSD(
        problem.num_spatial_orbitals,
        problem.num_particles,
        mapper,
        initial_state=HartreeFock(
            problem.num_spatial_orbitals,
            problem.num_particles,
            mapper,
        ),
    )

    # 4. Define the Optimizer and the Estimator (V2)
    optimizer = COBYLA(maxiter=100)
    estimator = StatevectorEstimator() # Ideal simulator for your desktop

    # 5. Run VQE

    # Extract the Hamiltonian and Run VQE
    # Get the fermionic Hamiltonian from the problem
    fermionic_hamiltonian = problem.hamiltonian.second_q_op()

    # Map Fermions to Qubits
    qubit_hamiltonian = mapper.map(fermionic_hamiltonian)

    #Initialize the VQE runner
    vqe = VQE(estimator, ansatz, optimizer)
    
    
    print("Starting VQE optimization on quantum simulator...")
    result = vqe.compute_minimum_eigenvalue(qubit_hamiltonian)
    
    # Add the nuclear repulsion energy back to get the total molecular energy
    total_energy = result.eigenvalue.real + problem.nuclear_repulsion_energy
    return total_energy

if __name__ == "__main__":
    energy = run_quantum_vqe()
    print(f"\n--- Quantum VQE Results ---")
    print(f"VQE Ground State Energy: {energy:.6f} Hartree")