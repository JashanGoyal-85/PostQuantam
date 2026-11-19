# 🎙️ Live Demo Cheat Sheet

Run the app in terminal:
```bash
python3 app.py
```
*(Or double-click `index.html` in your folder to open it in Chrome).*

---

## 3 Quick Things to Show On the Spot:

### 1. Babai Algorithm (Plots 1 & 2)
* **What to change:** Drag the **Dimension (n)** slider to 100, or move the **Basis Skewness** slider.
* **What happens:** Plot 1 immediately shows the **Good Basis (Green)** stays at 100%, while the **Bad Basis (Red)** collapses to 0%. Plot 2 shows the error distance shooting up.
* **1-line statement:** *"Sir, in our End-Sem extension, Babai's algorithm on the public bad basis fails at 0% accuracy, while the private key trapdoor remains 100%."*

---

### 2. Deep Learning Stress-Test (Plots 3 & 4)
* **What to change:** Click button **n = 2** (shows 98.8%), then click button **n = 20** (shows 18.4%).
* **What happens:** Plot 3 highlights the accuracy collapsing from 98.8% down to 18.4%. Plot 4 shows training loss failing to converge.
* **1-line statement:** *"In high dimensions, the Voronoi cell facets grow to over 2 million at n=20, so even neural networks cannot solve CVP."*

---

### 3. LWE Encryption & Noise Threshold (Plot 5)
* **What to change:** 
  * Click **"Safe (σ=1.5)"** $\to$ Noise dot is in the green zone $\to$ Decrypted: **Bit 0 (Correct)**.
  * Drag the **Noise slider** to 6.5 or click **"Overflow (σ=6.5)"** $\to$ Noise dot crosses the red dashed line ($q/4 = 24$) $\to$ Decrypted: **Bit 1 (Flipped!)**.
* **1-line statement:** *"When noise stays below the mathematical threshold q/4, decryption is 100% correct. If noise exceeds the threshold, decryption fails."*
