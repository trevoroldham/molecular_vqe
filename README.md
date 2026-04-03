# Molecular VQE: Scalable Hybrid Quantum-Classical Simulation

A modular command-line tool for simulating molecular ground states using the Variational Quantum Eigensolver (VQE). This package bridges the gap between theoretical quantum chemistry and practical Noisy Intermediate-Scale Quantum (NISQ) hardware constraints. It features a dual-mode execution pipeline, allowing users to validate algorithms via local statevector simulation before deploying seamlessly to physical IBM Quantum processors.

## 🔬 Architecture Overview
This project maps fermionic operators to a qubit Hamiltonian and optimizes the ground state energy via a hybrid feedback loop. It is designed to scale beyond simple diatomic molecules by implementing Active Space approximations and Hardware-Efficient Ansätze.

### Core Features
- **Cloud-Native QPU Execution:** Utilizes Qiskit Primitives (`EstimatorV2`) to seamlessly route circuits from local CPU simulation to cryogenic IBM Quantum processors.
- **Dynamic Molecular Generation:** A `MoleculeFactory` translates atomic coordinates into Qiskit `ElectronicStructureProblem` objects.
- **Active Space Reduction:** Freezes core electrons (e.g., the $1s$ orbital in Oxygen) to drastically reduce the required qubit count and simulation overhead for heavier atoms.
- **Hardware-Efficient Execution:** Replaces deeply parameterized UCCSD circuits with shallow `EfficientSU2` ansätze and `SPSA` optimization, enabling rapid convergence on standard classical hardware and near-term QPUs.
- **Sparse Matrix Optimization:** Utilizes `SparsePauliOp` to bypass the combinatorial memory explosion of multi-qubit statevectors.
- **Exact Classical Validation:** Integrates `NumPyMinimumEigensolver` to continuously benchmark the quantum approximation against exact classical diagonalization.

## 🛠 Tech Stack
- **Languages:** Python 3.12
- **Quantum Framework:** Qiskit 1.0+, Qiskit-Algorithms, Qiskit-Nature, Qiskit-IBM-Runtime
- **Scientific Computing:** PySCF, SciPy, NumPy

## 🚀 Usage

The solver is driven by a command-line interface that allows for dynamic molecular selection, active space configuration, and backend routing.

**1. Local Diatomic Simulation (Hydrogen)**
Runs a full, noiseless statevector simulation of $H_2$ at equilibrium bond length ($0.735$ Å) on your local machine.
```bash
python3 src/main.py --molecule h2 --backend local

```
**2. Scaled Simulation with Active Space (Water)**
Simulates $H_2O$ locally. To prevent an exponential explosion in Hilbert space, we freeze the Oxygen core electrons and isolate the active space to the 8 valence electrons across 6 spatial orbitals.
```bash
python3 src/main.py --molecule water --electrons 8 --orbitals 6
```
**3. Physical Hardware Execution (IBM Quantum)**
Routes the VQE algorithm to a phyysical superconducting quantum processor. Requires an active IMB Quantum API token saved locally.
```bash
python3 src/main.py --molecule h2 --backend ibm_brisbane
```
(Note: Hardware execution utilizes EstimatorV2 with Resilience Level 1 for readout error mitigation. For public Open Plan users, iterations should be kept low to accommodate global queue times).

## 📊 The Expressibility vs. Trainability Trade-off
This codebase explicitly demonstrates the central tension of the NISQ era:
* **UCCSD (Classical approach):** Chemically intuitive and highly accurate, but scales with $O(N^4)$ circuit depth, making it computationally devastating for >4 qubits.
* **Hardware Efficient Ansatz (Implemented):** Computationally cheap and highly parallelizable. It trades absolute chemical precision for runtime speed, relying on Stochastic Perturbation (SPSA) to navigate barren plateaus. The resulting error margin represents the reality of current quantum-classical hybrid algorithms.
