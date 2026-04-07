import qiskit.primitives
from qiskit.primitives import BaseEstimatorV1, StatevectorEstimator
qiskit.primitives.BaseEstimator = BaseEstimatorV1
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit.quantum_info import SparsePauliOp
from qiskit.circuit.library import EfficientSU2
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_nature.second_q.circuit.library import HartreeFock
from qiskit_algorithms.optimizers import SPSA
from qiskit_algorithms import VQE

# Import IBM Runtime modules
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as IBMEstimator, Session, EstimatorOptions

def run_quantum_vqe(problem, backend_name="local", use_session=False):
    """
    Executes the VQE algorithm locally or on IBM Quantum hardware.
    """
    # 1. Map Fermions to Qubits
    mapper = ParityMapper(num_particles=problem.num_particles)
    
    # 2. Extract Hamiltonian (Sparse for efficiency)
    fermionic_hamiltonian = problem.hamiltonian.second_q_op()
    qubit_hamiltonian = mapper.map(fermionic_hamiltonian)
    if not isinstance(qubit_hamiltonian, SparsePauliOp):
        qubit_hamiltonian = SparsePauliOp(qubit_hamiltonian)
    
    # 3. Prepare the Quantum State (Hardware Efficient Ansatz)
    initial_state = HartreeFock(
        problem.num_spatial_orbitals,
        problem.num_particles,
        mapper,
    )
    ansatz = EfficientSU2(
        num_qubits=qubit_hamiltonian.num_qubits,
        su2_gates=['ry'],        
        entanglement='linear',   
        reps=3, 
        initial_state=initial_state
    )

    # 4. Define Optimizer
    optimizer = SPSA(maxiter=100) # Kept at 100 to save your IBM queue time during testing

    # 5. Routing: Local vs. Hardware Execution
    if backend_name == "local":
        print(f"Executing VQE locally via StatevectorEstimator... (Depth: {ansatz.depth()}, Qubits: {qubit_hamiltonian.num_qubits})")
        estimator = StatevectorEstimator()
        vqe = VQE(estimator, ansatz, optimizer)
        result = vqe.compute_minimum_eigenvalue(qubit_hamiltonian)
        
    else:
        print(f"Authenticating with IBM Quantum... Target Backend: {backend_name}")
        # The service will automatically look for the API key saved on your machine
        service = QiskitRuntimeService(channel="ibm_quantum_platform")
        backend = service.backend(backend_name)
        
        print("Transpiling and executing on QPU...")
        if use_session:
            print("Session ACTIVE: Reserving QPU for continuous SPSA optimization.")
            
            # 1. Transpile the ansatz to match the backend ISA
            pm = generate_preset_pass_manager(target=backend.target, optimization_level=3)
            isa_ansatz = pm.run(ansatz)
            
            # 2. Open the session using the backend
            options = EstimatorOptions()
            options.resilience_level = 1  # TREX measurement error mitigation

            with Session(backend=backend) as session:
                estimator = IBMEstimator(mode=session, options=options)  # pass at construction
                vqe = VQE(estimator, isa_ansatz, optimizer)
                result = vqe.compute_minimum_eigenvalue(qubit_hamiltonian)
        else:
            # Executes via individual jobs (Warning: highly inefficient for VQE queues

            # 1. Create a pass manager tailored to the specific IBM chip
            pm = generate_preset_pass_manager(target=backend.target, optimization_level=3)

            # 2. Transpile ONLY your abstract ansatz into an ISA-compliant ansatz
            isa_ansatz = pm.run(ansatz)

            # REMOVE the manual isa_hamiltonian mapping line completely.

            # 3. Initialize the Estimator and VQE
            estimator = IBMEstimator(mode=backend)
            vqe = VQE(estimator, isa_ansatz, optimizer)

            # 4. Pass the ORIGINAL abstract qubit_hamiltonian. 
            # VQE will automatically apply isa_ansatz.layout to it internally.
            result = vqe.compute_minimum_eigenvalue(qubit_hamiltonian)

    # 6. Calculate Final Energy
    constant_shift = sum(problem.hamiltonian.constants.values())
    total_energy = result.eigenvalue.real + constant_shift
    
    return float(total_energy)