import qiskit.primitives

# --- Qiskit 1.0 Compatibility Patch ---
# Nature 0.7.2 looks for 'BaseEstimator', but Qiskit 1.0 renamed it to 'BaseEstimatorV1'
if not hasattr(qiskit.primitives, "BaseEstimator"):
    from qiskit.primitives import BaseEstimatorV1
    qiskit.primitives.BaseEstimator = BaseEstimatorV1
# --------------------------------------