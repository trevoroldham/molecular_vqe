# Patch for Qiskit 1.0 + Nature compatibility
import qiskit.primitives
from qiskit.primitives import BaseEstimatorV1
qiskit.primitives.BaseEstimator = BaseEstimatorV1
from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_algorithms import NumPyMinimumEigensolver
from qiskit_nature.second_q.algorithms import GroundStateEigensolver

def calculate_classical_energy(distance=0.735):
    """
    Calculates the exact ground state energy of H2 using classical diagonalization.
    This serves as the baseline to evaluate the accuracy of the VQE algorithm.
    """
    # 1. Define the molecule (Hydrogen, H2) at a specific bond distance
    driver = PySCFDriver(
        atom=f"H 0 0 0; H 0 0 {distance}",
        basis="sto3g",
        charge=0,
        spin=0,
        unit=DistanceUnit.ANGSTROM,
    )

    # 2. Run the driver to generate the molecular data (integrals)
    problem = driver.run()

    # 3. Initialize the classical exact eigensolver
    numpy_solver = NumPyMinimumEigensolver()

    # 4. Use the ParityMapper to map the fermionic operators to qubit operators
    mapper = ParityMapper(num_particles=problem.num_particles)

    # 5. Combine the mapper and solver to calculate the ground state
    calc = GroundStateEigensolver(mapper, numpy_solver)
    result = calc.solve(problem)

    return result

if __name__ == "__main__":
    print("Calculating exact classical baseline for H2...")
    result = calculate_classical_energy()
    print(f"\n--- Classical Results ---")
    print(f"Total Ground State Energy: {result.total_energies[0]:.6f} Hartree")
    print(f"Nuclear Repulsion Energy:  {result.nuclear_repulsion_energy:.6f} Hartree")