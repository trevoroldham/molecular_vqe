# Molecular VQE: Scalable Hybrid Quantum-Classical Simulation

A modular command-line tool for simulating molecular ground states using the Variational Quantum Eigensolver (VQE). This package bridges the gap between theoretical quantum chemistry and practical Noisy Intermediate-Scale Quantum (NISQ) hardware constraints.

## 🔬 Architecture Overview
This project maps fermionic operators to a qubit Hamiltonian and optimizes the ground state energy via a hybrid feedback loop. It is designed to scale beyond simple diatomic molecules by implementing Active Space approximations and Hardware-Efficient Ansätze.

### Core Features
- **Dynamic Molecular Generation:** A `MoleculeFactory` translates atomic coordinates into Qiskit `ElectronicStructureProblem` objects.
- **Active Space Reduction:** Freezes core electrons (e.g., the $1s$ orbital in Oxygen) to drastically reduce the required qubit count and simulation overhead for heavier atoms.
- **Hardware-Efficient Execution:** Replaces deeply parameterized UCCSD circuits with shallow `EfficientSU2` ansätze and `SPSA` optimization, enabling rapid convergence on standard classical hardware and near-term QPUs.
- **Sparse Matrix Optimization:** Utilizes `SparsePauliOp` to bypass the combinatorial memory explosion of multi-qubit statevectors.
- **Exact Classical Validation:** Integrates `NumPyMinimumEigensolver` to continuously benchmark the quantum approximation against exact classical diagonalization.

## 🛠 Tech Stack
- **Languages:** Python 3.12
- **Quantum Framework:** Qiskit 1.0+, Qiskit-Algorithms, Qiskit-Nature
- **Scientific Computing:** PySCF, SciPy, NumPy

## 🚀 Usage

The solver is driven by a command-line interface that allows for dynamic molecular selection and active space configuration.

**1. Basic Diatomic Simulation (Hydrogen)**
Runs a full quantum simulation of $H_2$ at equilibrium bond length ($0.735$ Å).
```bash
python3 src/main.py --molecule h2