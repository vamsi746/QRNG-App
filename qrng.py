# qrng.py
import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Safe batch limit (avoid "circuit too wide" errors seen on some Aer builds)
_BATCH_QUBITS = 24

def _build_circuit(n_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))          # superposition
    qc.measure(range(n_qubits), range(n_qubits))  # measurement
    return qc

def generate_random_bits(n_bits: int) -> str:
    """
    Generate n_bits of quantum random bits using H + measurement on AerSimulator.
    Batches the circuit so it runs reliably on Windows/Python 3.13 + qiskit-aer.
    """
    sim = AerSimulator()  # uses local CPU simulator
    bits_out = []
    remaining = n_bits

    while remaining > 0:
        chunk = min(_BATCH_QUBITS, remaining)
        qc = _build_circuit(chunk)
        compiled = transpile(qc, sim, optimization_level=0)
        job = sim.run(compiled, shots=1)      # one sample is enough; each qubit measured once
        result = job.result()
        # 'counts' includes a single bitstring like '101010' for shots=1
        counts = result.get_counts()
        bitstring = next(iter(counts.keys()))
        bits_out.append(bitstring[::-1])  # reverse to match qubit->classical order
        remaining -= chunk

    return "".join(bits_out)[:n_bits]

def example_circuit(n: int) -> QuantumCircuit:
    """Return a small circuit (for drawing in the Theory page)."""
    n = max(1, min(n, _BATCH_QUBITS))
    return _build_circuit(n)
