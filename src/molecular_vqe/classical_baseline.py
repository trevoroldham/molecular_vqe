from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_algorithms import NumPyMinimumEigensolver
from qiskit_nature.second_q.algorithms import GroundStateEigensolver

def calculate_classical_energy(problem):
    """
    Calculates the exact ground state energy of a molecular problem
    using classical exact diagonalization.
    """
    # 1. Initialize the classical exact eigensolver
    numpy_solver = NumPyMinimumEigensolver()

    # 2. Use the ParityMapper to map the fermions to qubits
    mapper = ParityMapper(num_particles=problem.num_particles)

    # 3. Combine mapper and solver into the GroundStateEigensolver
    calc = GroundStateEigensolver(mapper, numpy_solver)
    
    # 4. Solve the exact problem
    print("Calculating classical exact diagonalization...")
    result = calc.solve(problem)

    # Note: Qiskit's GroundStateEigensolver automatically handles adding 
    # the nuclear repulsion and frozen core constant shifts into `total_energies`.
    return float(result.total_energies[0])