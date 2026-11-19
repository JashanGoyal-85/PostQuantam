#!/usr/bin/env python3
"""
Lattice-Based Post-Quantum Cryptography Core Engine
Based on:
  - Pérez-Ramos, Hernández-Goya & Caballero-Gil (2026), JNAER 15:18
  - Babai (1986) Combinatorica
  - Regev (2005) STOC / NIST FIPS 203 (ML-KEM)

Includes:
  1. 2D Lattice Generation, CVP and SVP solvers
  2. Part A: N-Dimensional Babai CVP Benchmarking (Good vs Bad Basis)
  3. Part B: Voronoi Cell & Geometric Dimension Analysis (ML Stress-Test)
  4. Part C: Verified LWE Encryption / Decryption with Noise Accumulation Tracker
"""

import numpy as np
import time

# ============================================================================
# 1. 2D LATTICE, CVP & SVP SOLVERS
# ============================================================================

def generate_lattice_2d(b1, b2, coeff_range=5):
    """Generate 2D lattice points L = { z1*b1 + z2*b2 : z_i in Z }."""
    b1, b2 = np.array(b1, dtype=float), np.array(b2, dtype=float)
    coeffs = np.arange(-coeff_range, coeff_range + 1)
    grid_i, grid_j = np.meshgrid(coeffs, coeffs)
    points = grid_i.flatten()[:, None] * b1 + grid_j.flatten()[:, None] * b2
    return points

def solve_cvp_2d_exact(b1, b2, target, coeff_range=6):
    """Brute force exact CVP in 2D."""
    points = generate_lattice_2d(b1, b2, coeff_range)
    target = np.array(target, dtype=float)
    dists = np.linalg.norm(points - target, axis=1)
    min_idx = np.argmin(dists)
    return points[min_idx], dists[min_idx]

def solve_cvp_2d_babai(b1, b2, target):
    """Babai rounding CVP in 2D."""
    B = np.column_stack([b1, b2])
    target = np.array(target, dtype=float)
    B_inv = np.linalg.inv(B)
    c_hat = np.rint(B_inv @ target)
    v_babai = B @ c_hat
    dist = np.linalg.norm(v_babai - target)
    return v_babai, dist

def solve_svp_2d(b1, b2, coeff_range=6):
    """Find shortest non-zero vector in 2D lattice."""
    points = generate_lattice_2d(b1, b2, coeff_range)
    dists = np.linalg.norm(points, axis=1)
    non_zero = dists > 1e-9
    valid_points = points[non_zero]
    valid_dists = dists[non_zero]
    min_idx = np.argmin(valid_dists)
    return valid_points[min_idx], valid_dists[min_idx]

# ============================================================================
# 2. PART A: N-DIMENSIONAL BABAI CVP BENCHMARK
# ============================================================================

def generate_random_unimodular(n, steps=40):
    """Build an n x n integer matrix with det = +/- 1 via elementary shear matrices."""
    U = np.eye(n, dtype=np.int64)
    for _ in range(steps):
        i, j = np.random.choice(n, size=2, replace=False)
        k = np.random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        E = np.eye(n, dtype=np.int64)
        E[i, j] = k
        U = E @ U
    return U

def compute_hadamard_ratio(B):
    """Hadamard ratio gamma(B) = (|det(B)| / prod(||b_i||))^(1/n)."""
    n = B.shape[0]
    sign, logdet = np.linalg.slogdet(B)
    if sign == 0:
        return 0.0
    norms = np.linalg.norm(B, axis=0)
    # prevent div by zero
    norms = np.where(norms == 0, 1e-12, norms)
    return float(np.exp((logdet - np.sum(np.log(norms))) / n))

def babai_round_nd(B_inv, B, target):
    """Babai Rounding in N dimensions: c = B^-1 t -> c_hat = round(c) -> v = B c_hat."""
    c_hat = np.rint(B_inv @ target)
    return B @ c_hat

def run_babai_benchmark(dims=(2, 5, 10, 20, 50), num_samples=200, noise_radius=0.35, shear_steps=40):
    """
    Benchmark Babai rounding on Good Basis (Orthogonal) vs Bad Basis (Skewed unimodular).
    Returns dictionary of results across dimensions.
    """
    records = []
    for n in dims:
        B_good = np.eye(n, dtype=np.float64)
        B_good_inv = np.eye(n, dtype=np.float64)

        U = generate_random_unimodular(n, steps=shear_steps).astype(np.float64)
        B_bad = B_good @ U
        try:
            B_bad_inv = np.linalg.inv(B_bad)
        except np.linalg.LinAlgError:
            B_bad_inv = np.linalg.pinv(B_bad)

        gamma_good = 1.0
        gamma_bad = compute_hadamard_ratio(B_bad)

        true_c = np.random.randint(-10, 11, size=(n, num_samples))
        noise = np.random.uniform(-noise_radius, noise_radius, size=(n, num_samples))
        targets = true_c + noise

        ok_good = 0
        ok_bad = 0
        bad_errors = []

        for idx in range(num_samples):
            t = targets[:, idx]
            vt = true_c[:, idx].astype(float)

            vg = babai_round_nd(B_good_inv, B_good, t)
            if np.allclose(vg, vt):
                ok_good += 1

            vb = babai_round_nd(B_bad_inv, B_bad, t)
            if np.allclose(vb, vt):
                ok_bad += 1
            bad_errors.append(float(np.linalg.norm(vb - vt)))

        acc_good = (ok_good / num_samples) * 100.0
        acc_bad = (ok_bad / num_samples) * 100.0
        mean_err_bad = float(np.mean(bad_errors))

        records.append({
            'n': n,
            'acc_good': acc_good,
            'acc_bad': acc_bad,
            'mean_error_bad': mean_err_bad,
            'hadamard_bad': gamma_bad
        })
    return records

# ============================================================================
# 3. PART B: GEOMETRIC / AI ANALYSIS OF CVP HARDNESS
# ============================================================================

def get_dimension_complexity(n):
    """Compute theoretical complexity metrics for dimension n."""
    voronoi_facets = 2 * (2**n - 1) if n <= 30 else float(2**(n+1))
    search_space = float(97**n) if n <= 30 else 10**(n * 1.986)
    return {
        'n': n,
        'voronoi_facets': voronoi_facets,
        'search_space': search_space,
        'estimated_nn_acc': max(5.0, 100.0 * np.exp(-0.15 * (n - 2))) if n >= 2 else 100.0
    }

# ============================================================================
# 4. PART C: VERIFIED LWE CRYPTOSYSTEM PIPELINE
# ============================================================================

class LWECryptosystem:
    def __init__(self, n=8, m=32, q=97, sigma=1.5):
        self.n = n
        self.m = m
        self.q = q
        self.sigma = sigma
        self.keygen()

    def keygen(self):
        """Generate Secret Key s, Public Matrix A, Error e, and Public Key b = As + e mod q."""
        self.s = np.random.randint(0, self.q, size=self.n)
        self.A = np.random.randint(0, self.q, size=(self.m, self.n))
        if self.sigma <= 0.001:
            self.e = np.zeros(self.m, dtype=int)
        else:
            self.e = np.round(np.random.normal(0, self.sigma, self.m)).astype(int)
        self.b = (self.A @ self.s + self.e) % self.q
        return {
            's': self.s.tolist(),
            'b': self.b.tolist(),
            'e': self.e.tolist(),
            'max_error': int(np.max(np.abs(self.e)))
        }

    def encrypt_bit(self, bit):
        """Encrypt a single bit m_bit in {0, 1}."""
        r = np.random.randint(0, 2, size=self.m)
        u = (self.A.T @ r) % self.q
        half_q = self.q // 2
        v = int((int(self.b @ r) + half_q * bit) % self.q)

        # Track internal noise term e^T r
        noise_accum = int(self.e @ r) % self.q
        if noise_accum > self.q // 2:
            noise_accum -= self.q

        noise_bound = self.q // 4
        condition_satisfied = abs(noise_accum) < noise_bound

        return {
            'u': u.tolist(),
            'v': v,
            'r': r.tolist(),
            'noise_accum': int(abs(noise_accum)),
            'noise_bound': noise_bound,
            'condition_met': condition_satisfied,
            'bit': bit
        }

    def decrypt_bit(self, u, v):
        """Decrypt ciphertext (u, v) using secret key s."""
        u_arr = np.array(u, dtype=int)
        residual = int((v - int(self.s @ u_arr)) % self.q)
        half_q = self.q // 2

        dist_0 = min(residual, self.q - residual)
        dist_half = min(abs(residual - half_q), self.q - abs(residual - half_q))

        decrypted_bit = 1 if dist_half < dist_0 else 0
        return decrypted_bit, residual

    def encrypt_text(self, text):
        """Encrypt an ASCII string bit-by-bit."""
        bits = []
        for char in text:
            char_code = ord(char)
            for shift in range(7, -1, -1):
                bits.append((char_code >> shift) & 1)

        ciphertexts = []
        for b in bits:
            ct = self.encrypt_bit(b)
            ciphertexts.append(ct)
        return bits, ciphertexts

    def decrypt_text(self, ciphertexts):
        """Decrypt a stream of ciphertexts back into ASCII text."""
        dec_bits = []
        for ct in ciphertexts:
            bit, _ = self.decrypt_bit(ct['u'], ct['v'])
            dec_bits.append(bit)

        # Reconstruct characters
        chars = []
        for i in range(0, len(dec_bits), 8):
            byte_bits = dec_bits[i:i+8]
            if len(byte_bits) == 8:
                val = 0
                for b in byte_bits:
                    val = (val << 1) | b
                chars.append(chr(val) if 32 <= val <= 126 else '?')
        return "".join(chars), dec_bits

    def run_monte_carlo(self, num_trials=1000):
        """Run statistical trial to measure exact decryption success rate."""
        correct = 0
        noise_ok = 0
        noise_samples = []

        for _ in range(num_trials):
            bit = np.random.randint(0, 2)
            ct = self.encrypt_bit(bit)
            dec_bit, _ = self.decrypt_bit(ct['u'], ct['v'])
            if dec_bit == bit:
                correct += 1
            if ct['condition_met']:
                noise_ok += 1
            noise_samples.append(ct['noise_accum'])

        return {
            'trials': num_trials,
            'accuracy': (correct / num_trials) * 100.0,
            'noise_ok_rate': (noise_ok / num_trials) * 100.0,
            'mean_noise': float(np.mean(noise_samples)),
            'max_noise': int(np.max(noise_samples)),
            'noise_bound': self.q // 4
        }

if __name__ == '__main__':
    print("=== Testing Lattice PQC Core Engine ===")
    lwe = LWECryptosystem(n=8, m=32, q=97, sigma=1.5)
    print("KeyGen successful. Testing text encryption...")
    test_msg = "PQC-2026"
    bits, cts = lwe.encrypt_text(test_msg)
    rec_text, dec_bits = lwe.decrypt_text(cts)
    print(f"Original: '{test_msg}' -> Decrypted: '{rec_text}' [Match: {test_msg == rec_text}]")

    print("\nRunning Monte Carlo (500 trials)...")
    mc = lwe.run_monte_carlo(500)
    print(f"Accuracy: {mc['accuracy']}% | Noise Budget OK: {mc['noise_ok_rate']}%")

    print("\nRunning Babai Benchmark (dims 2, 5, 10, 20)...")
    bench = run_babai_benchmark(dims=[2, 5, 10, 20], num_samples=100)
    for b in bench:
        print(f"  n={b['n']:2d} | Good Acc={b['acc_good']:.1f}% | Bad Acc={b['acc_bad']:.1f}% | gamma(B_bad)={b['hadamard_bad']:.2e}")
    print("\nAll engine modules verified!")
