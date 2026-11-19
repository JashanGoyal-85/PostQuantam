# 🔐 Lattice-Based Post-Quantum Cryptography (PQC)
## Interactive Live Demo & Research Implementation

**Base Paper:** Pérez-Ramos, Hernández-Goya & Caballero-Gil (2026). *Lattice-Based Post-Quantum Cryptography.* JNAER, 15:18.  
**Standard Compliance:** NIST FIPS 203 (ML-KEM / CRYSTALS-Kyber), FIPS 204 (ML-DSA / CRYSTALS-Dilithium).

---

## 🚀 Quick Start (Zero-Install)

Launch the interactive live presentation application with:
```bash
python3 app.py
```
This runs a local zero-dependency web server and immediately opens your default browser at `http://127.0.0.1:8000`.

*(Alternatively, you can open `index.html` directly in any web browser without running python).*

---

## 📂 Repository Contents

```
DEMA/
├── index.html                  # Full interactive web laboratory (HTML5/Canvas/ES6)
├── app.py                      # Local presentation server with auto-browser launch
├── lattice_pqc_engine.py       # Pure Python algorithmic backend (exact Colab replica)
├── PRESENTATION_CHEAT_SHEET.md # Step-by-step speaker script & examiner Q&A defenses
└── README.md                   # Documentation & overview
```

---

## 🎯 Key Interactive Features in the Live Demo

1. **2D Lattice Visualizer & CVP/SVP Playground (Tab 1):**
   - Click anywhere to move Target Point $t$.
   - Switch between **Orthogonal Basis** ($\gamma=1.0$) and **Severely Skewed Basis** ($\gamma \ll 1.0$).
   - Real-time comparison between **True CVP** and **Babai's Rounding Algorithm** (shows visual trapdoor failure).
   - Shortest Vector Problem (SVP) radius visualization.

2. **End-Sem Part A: N-Dimensional Babai CVP Benchmark (Tab 2 - Gap A):**
   - Live Monte Carlo simulation from $n = 2$ to $n = 100$ dimensions.
   - Dual-chart rendering:
     - **Exact Recovery Rate (%) vs Dimension ($n$):** Good Basis stays 100%, Bad Basis plummets to 0% at $n \ge 5$.
     - **Error Explosion vs. Hadamard Defect $\gamma(B)$:** Shows log-scale decay to $10^{-10}$ with exploding Euclidean error.

3. **End-Sem Part B: Deep Learning CVP Stress-Test (Tab 3 - AI Extension):**
   - Simulates PyTorch 3-layer MLP (`Linear(n, 128) -> ReLU -> Linear(128, 64) -> ReLU -> Linear(64, n)`).
   - Geometric analysis of Voronoi cell facets: grows as $2(2^n - 1)$.
   - Demonstrates why neural network accuracy degrades from 98.8% ($n=2$) to $<20\%$ ($n=20$) and is impossible at Kyber's $n=256$ ($>10^{77}$ facets).
   - Interactive single-vector query tester.

4. **End-Sem Part C: Verified LWE Cryptosystem Pipeline (Tab 4 - Gap B):**
   - Full Regev-style KeyGen, Encryption, and Decryption.
   - **Type any custom text message** (e.g. `"POST-QUANTUM 2026"`), encrypt to bit-stream ciphertexts $(u, v)$, and decrypt with 100% accuracy.
   - **Live Noise Budget Bar:** Tracks the internal noise term $|e^T r|$ against the mathematical threshold $q/4$.
   - **Interactive Attack Dials:**
     - 💥 *Noise Overflow Attack:* Dial $\sigma \uparrow$ to cross $q/4$ and induce live bit-flip corruption.
     - 🕵️ *Zero-Noise Crack:* Set $\sigma = 0$ to show how an eavesdropper recovers secret $s$ in 2ms via Gaussian elimination.
   - **1,000-Trial Monte Carlo Reliability Test:** Statistical confirmation of 100% accuracy under safe parameters.

5. **Presenter Cheat Sheet (Tab 5 & Top Bar Modal):**
   - One-click script for what to say during each phase of your evaluation.
   - Ready-made answers to tricky examiner questions on Shor's algorithm, module lattices, and NTT.
