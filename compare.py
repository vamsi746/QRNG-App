from collections import Counter
import matplotlib.pyplot as plt
from scipy.stats import chisquare
from qrng import generate_random_bits as qrng_bits
from classical_rng import generate_random_bits as crng_bits

N_BITS = 32       # bits per sample (keep ≤ 29 for quantum backend, but safe wrapper allows bigger)
N_SAMPLES = 100   # number of random numbers generated

def frequency_test(samples):
    """Count frequency of 0s and 1s in bitstrings."""
    zeros, ones = 0, 0
    for s in samples:
        c = Counter(s)
        zeros += c.get("0", 0)
        ones += c.get("1", 0)
    total = zeros + ones
    return zeros, ones, total

def chi_square_test(zeros, ones, total):
    """Perform Chi-square test for uniformity (0s vs 1s)."""
    expected = [total / 2, total / 2]
    observed = [zeros, ones]
    chi2, p_value = chisquare(f_obs=observed, f_exp=expected)
    return chi2, p_value

if __name__ == "__main__":
    # Generate samples
    q_samples = [qrng_bits(N_BITS) for _ in range(N_SAMPLES)]
    c_samples = [crng_bits(N_BITS) for _ in range(N_SAMPLES)]

    # Frequency counts
    q0, q1, q_total = frequency_test(q_samples)
    c0, c1, c_total = frequency_test(c_samples)

    # Chi-square tests
    q_chi2, q_p = chi_square_test(q0, q1, q_total)
    c_chi2, c_p = chi_square_test(c0, c1, c_total)

    # Print results
    print("=== Quantum Random (QRNG) ===")
    print("Example bits:", q_samples[0])
    print(f"0s: {q0/q_total:.2%}, 1s: {q1/q_total:.2%}")
    print(f"Chi-square: {q_chi2:.3f}, p-value: {q_p:.3f}")

    print("\n=== Classical Random (PRNG) ===")
    print("Example bits:", c_samples[0])
    print(f"0s: {c0/c_total:.2%}, 1s: {c1/c_total:.2%}")
    print(f"Chi-square: {c_chi2:.3f}, p-value: {c_p:.3f}")

    # Plot bar chart
    labels = ["0s", "1s"]
    quantum_values = [q0 / q_total * 100, q1 / q_total * 100]
    classical_values = [c0 / c_total * 100, c1 / c_total * 100]

    x = range(len(labels))
    width = 0.35

    plt.bar([i - width/2 for i in x], quantum_values, width, label="Quantum QRNG")
    plt.bar([i + width/2 for i in x], classical_values, width, label="Classical PRNG")

    plt.ylabel("Percentage (%)")
    plt.title("Frequency of 0s and 1s (Quantum vs Classical)")
    plt.xticks(x, labels)
    plt.legend()
    plt.show()
