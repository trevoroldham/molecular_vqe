# Molecular VQE: Quantum-Classical Hybrid Simulation
A modern implementation of the Variational Quantum Eigensolver (VQE) for molecular ground state estimation, refactored for the **Qiskit 1.0+** ecosystem.

## 🔬 Overview
This project demonstrates the application of near-term quantum algorithms (NISQ) to computational chemistry. It simulates the ground state energy of a Hydrogen ($H_2$) molecule by mapping fermionic operators to a qubit Hamiltonian and optimizing via a classical-quantum feedback loop.

### Key Features:
- **Qiskit 1.0 Primitives:** Utilizes `EstimatorV2` for high-performance expectation value evaluation.
- **Hardware-Efficient Mapping:** Implements `ParityMapper` with two-qubit reduction to minimize circuit width.
- **Classical Validation:** Integrates `PySCF` and `NumPyMinimumEigensolver` to verify quantum results against exact diagonalization.
- **PES Analysis:** Includes automated scanning of Potential Energy Surfaces (PES) to determine equilibrium bond lengths.

## 🛠 Tech Stack
- **Languages:** Python 3.12
- **Quantum Framework:** Qiskit 1.0+, Qiskit-Algorithms, Qiskit-Nature
- **Scientific Computing:** PySCF, NumPy, Matplotlib
- **Environment:** WSL 2 (Ubuntu) on Windows 11

## 📈 Performance
The VQE implementation achieves **chemical accuracy** ($< 1.6 \text{ mHa}$ absolute error) compared to the exact classical baseline for diatomic systems at equilibrium.