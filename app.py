# app.py
import streamlit as st
import matplotlib.pyplot as plt
import base64, math, uuid, hashlib, hmac
from scipy.stats import chisquare

from qrng import generate_random_bits as qrng_bits, example_circuit
from classical_rng import generate_random_bits as crng_bits

# ---------- Helpers ----------
def frequency_test(bits: str):
    return bits.count("0"), bits.count("1")

def runs_test(bits: str):
    if not bits: return 0, 0.0
    runs = 1
    for i in range(1, len(bits)):
        if bits[i] != bits[i-1]:
            runs += 1
    expected = (2*len(bits)-1)/3
    return runs, expected

def entropy(bits: str):
    if not bits: return 0.0
    c0, c1 = bits.count("0"), bits.count("1")
    total = len(bits)
    out = 0.0
    for c in (c0, c1):
        if c:
            p = c/total
            out -= p*math.log2(p)
    return out

def chi_square_01(bits: str):
    zeros, ones = frequency_test(bits)
    total = len(bits)
    if total == 0: return 0.0, 1.0
    chi2, p = chisquare([zeros, ones], f_exp=[total/2, total/2])
    return float(chi2), float(p)

def bits_to_bytes(bits: str) -> bytes:
    if not bits:
        return b""
    return int(bits, 2).to_bytes((len(bits) + 7)//8, "big")

# ---------- Streamlit config ----------
st.set_page_config(page_title="QRNG • Quantum Random Number Generator", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>
:root{
    --bg:#0b0c12; --nav:#10121a; --glass:rgba(255,255,255,.06);
    --text:#eaf0f6; --muted:#a9b3c2; --a1:#6ae7ff; --a2:#ff6ad5;
}
html,body,.stApp{background:var(--bg);color:var(--text);font-family:"Segoe UI",system-ui,sans-serif;}
.nav-wrap{position:sticky;top:0;z-index:999;background:linear-gradient(90deg,var(--nav),#0b0c12);
    border-radius:14px;padding:10px;margin-bottom:18px;box-shadow:0 10px 25px rgba(0,0,0,.35);}
.nav{display:flex;gap:8px;align-items:center;justify-content:center;flex-wrap:wrap;}
.nav button{cursor:pointer;position:relative;border:none;padding:10px 16px;border-radius:10px;
    color:var(--muted);transition:.2s ease;font-weight:600;background:rgba(255,255,255,0.06);}
.nav button:hover{color:white;background:rgba(255,255,255,.12);}
.nav button.active{color:white;background:linear-gradient(90deg,var(--a1),var(--a2));
    box-shadow:0 4px 12px rgba(0,0,0,.4);}
.card{background:var(--glass);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:22px;
    box-shadow:0 8px 24px rgba(0,0,0,.35);}
.grid{display:grid;grid-template-columns:repeat(2,minmax(300px,1fr));gap:18px;}
.small{color:var(--muted);}
hr{border:none;border-top:1px solid rgba(255,255,255,.08);margin:16px 0;}
</style>
""", unsafe_allow_html=True)

# ---------- Navigation ----------
PAGES = ["Home","Theory","Simulator","Generator","Compare","Tests","Real-World","FAQ","Contact"]
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.markdown('<div class="nav-wrap"><div class="nav">', unsafe_allow_html=True)
cols = st.columns(len(PAGES))
for i, p in enumerate(PAGES):
    if cols[i].button(p, key=f"nav_{p}"):
        st.session_state.page = p
st.markdown('</div></div>', unsafe_allow_html=True)

page = st.session_state.page

# ---------- Pages ----------
# HOME
if page == "Home":
    st.markdown("## ⚛️ QRNG — Quantum Random Number Generator")
    st.caption("Design a basic QRNG using **superposition** (Hadamard) and **measurement** to generate random bits.")
    st.markdown('<div class="card"><h3>Overview</h3>'
                '<p>• Generate **quantum random bits** (not algorithmic pseudo-random)<br>'
                '• Visualize the quantum circuit and core theory<br>'
                '• Run quick statistical tests (Frequency, Runs, Entropy, Chi-Square)<br>'
                '• See practical uses: API tokens, HMAC, UUIDs, OTP</p></div>', unsafe_allow_html=True)
    
    st.markdown("#### 🔁 Process Flow")
    fig, ax = plt.subplots(figsize=(10, 2.2))
    steps = ["Quantum Circuit", "Superposition", "Measurement", "Random Bits", "Keys", "Applications"]
    for i, step in enumerate(steps):
        ax.text(i*1.5, 0.5, step, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.5", fc="#6ae7ff", alpha=0.28, ec="#6ae7ff"))
        if i < len(steps) - 1:
            ax.arrow(i*1.5+0.6, 0.5, 0.8, 0, head_width=0.12, head_length=0.18, fc="white", ec="white", length_includes_head=True)
    ax.axis("off")
    st.pyplot(fig)

    st.markdown('<div class="grid">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><h4>Why Quantum?</h4>'
                    '<p class="small">Classical RNGs are algorithmic (seeded), hence *pseudo-random*. '
                    'Quantum randomness is rooted in measurement uncertainty — intrinsically unpredictable.</p></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h4>What You Can Show</h4>'
                    '<p class="small">• Generate keys of 16/32/64/128 bits<br>'
                    '• Visual circuit & theory<br>'
                    '• Quick tests proving balance & entropy<br>'
                    '• Real-world integrations in security workflows</p></div>',
                    unsafe_allow_html=True)

# THEORY
elif page == "Theory":
    st.markdown("## 📚 Theory")
    left, right = st.columns([1,1], gap="large")
    with left:
        st.markdown('<div class="card"><h4>Core Concepts</h4>', unsafe_allow_html=True)
        st.markdown("""
        - **Superposition:** Hadamard gate prepares qubits with equal amplitudes → 50/50 outcomes.
        - **Measurement:** Collapses each qubit to 0 or 1 **unpredictably**.
        - **Independence:** Apply H on each qubit; measure all; concatenate bits.
        - **Extractor (prod use):** Optional step to remove bias if needed.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with right:
        st.markdown('<div class="card"><h4>Visualization</h4>', unsafe_allow_html=True)
        nq = st.slider("Number of qubits (illustration)", 3, 12, 6, key="nq_theory")
        qc = example_circuit(nq)
        try:
            fig = qc.draw(output="mpl")
            st.pyplot(fig)
        except Exception:
            st.code(qc.draw(output="text"), language="text")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("#### 🧠 Concept Snapshot")
    fig2, ax2 = plt.subplots(figsize=(6, 2))
    labels = ["|0⟩", "H", "Superposition", "Measure", "0/1"]
    x = [0, 1.2, 3.0, 4.7, 6.2]
    for i, lab in enumerate(labels):
        ax2.text(x[i], 0.5, lab, ha="center", va="center",
                 bbox=dict(boxstyle="round,pad=0.4", fc="#ff6ad5", alpha=0.28, ec="#ff6ad5"))
        if i < len(labels)-1:
            ax2.arrow(x[i]+0.5, 0.5, x[i+1]-x[i]-1.0, 0, head_width=0.1, head_length=0.2, fc="white", ec="white", length_includes_head=True)
    ax2.axis("off")
    st.pyplot(fig2)

# SIMULATOR
elif page == "Simulator":
    st.markdown("## 🎛️ Quantum Circuit Simulator")
    st.caption("Applies **Hadamard** to each qubit and measures. Uses the current key length if available.")
    if "qrng_bits" in st.session_state and st.session_state.qrng_bits:
        nq = len(st.session_state.qrng_bits)
        st.write(f"Using **{nq} qubits** (synced with your generated key).")
    else:
        nq = st.slider("Number of qubits", 3, 12, 6, key="nq_sim")
        st.info("Tip: Generate a key to auto-sync qubit count here.")
    qc = example_circuit(nq)
    try:
        fig = qc.draw(output="mpl")
        st.pyplot(fig)
    except Exception:
        st.code(qc.draw(output="text"), language="text")

# GENERATOR
elif page == "Generator":
    st.markdown("## 🔐 Quantum Key Generator")
    key_size = st.radio("Key Size (bits)", [16, 32, 64, 128], horizontal=True)
    if st.button(f"Generate {key_size}-bit Quantum Key"):
        bits = qrng_bits(key_size)
        st.session_state.qrng_bits = bits
        st.success("Quantum random bits generated and synced across Simulator, Tests, Compare, and Real-World.")

    if "qrng_bits" in st.session_state and st.session_state.qrng_bits:
        bits = st.session_state.qrng_bits
        st.code(bits, language="text")
        b = bits_to_bytes(bits)
        st.write("**Integer:**", int(bits, 2))
        st.write("**HEX:**", b.hex())
        st.write("**Base64:**", base64.urlsafe_b64encode(b).decode())

# COMPARE
elif page == "Compare":
    st.markdown("## ⚖️ Quantum vs Classical RNG")
    if "qrng_bits" not in st.session_state or not st.session_state.qrng_bits:
        st.warning("⚠️ Generate quantum bits in the Generator first.")
    else:
        q_bits = st.session_state.qrng_bits
        c_bits = crng_bits(len(q_bits))
        st.markdown("### What & How")
        st.markdown("""
        - **What:** Bit balance (0s vs 1s) for **Quantum** vs **Classical** sequences of the **same length**.
        - **How:** Count frequencies and plot percentages. Both should be ~50/50 ideally.
        - **Why Quantum is better in principle:** Classical PRNG is algorithmic and reproducible if the seed/state is known; QRNG outcomes come from physical measurement and are **not** seed-predictable.
        """)
        q0, q1 = frequency_test(q_bits)
        c0, c1 = frequency_test(c_bits)
        qH = entropy(q_bits); cH = entropy(c_bits)
        qchi, qp = chi_square_01(q_bits)
        cchi, cp = chi_square_01(c_bits)
        fig, ax = plt.subplots()
        w = 0.35
        ax.bar([0-w/2, 1-w/2], [q0/len(q_bits)*100, q1/len(q_bits)*100], w, label="Quantum")
        ax.bar([0+w/2, 1+w/2], [c0/len(c_bits)*100, c1/len(c_bits)*100], w, label="Classical")
        ax.set_ylabel("Percentage (%)"); ax.set_title("Distribution of 0s vs 1s"); ax.legend()
        st.pyplot(fig)
        st.markdown("### Result & Interpretation")
        st.write(f"- **Quantum:** {q0} zeros, {q1} ones | Entropy ≈ **{qH:.3f}**, χ²={qchi:.2f}, p={qp:.3f}")
        st.write(f"- **Classical:** {c0} zeros, {c1} ones | Entropy ≈ **{cH:.3f}**, χ²={cchi:.2f}, p={cp:.3f}")
        st.info("Interpretation: Values close to 50/50 with p-value > 0.05 indicate no detectable bias. "
                "Even if both look balanced here, only QRNG is non-seed-based and thus fundamentally unpredictable.")

# TESTS
elif page == "Tests":
    st.markdown("## 🧪 Randomness Tests")
    if "qrng_bits" not in st.session_state or not st.session_state.qrng_bits:
        st.warning("⚠️ Generate quantum bits in the Generator first.")
    else:
        bits = st.session_state.qrng_bits
        n = len(bits)
        st.code(bits, language="text")
        z, o = frequency_test(bits)
        r_obs, r_exp = runs_test(bits)
        H = entropy(bits)
        chi2, p = chi_square_01(bits)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Frequency:** 0s = {z}, 1s = {o} (expected ≈ {n/2:.1f} each)")
            st.markdown(f"**Runs:** observed = {r_obs}, expected ≈ {r_exp:.2f}")
        with c2:
            st.markdown(f"**Entropy:** {H:.3f} bits/symbol (max 1.000)")
            st.markdown(f"**Chi-Square:** χ² = {chi2:.2f}, p = {p:.3f}")
        st.markdown("---")
        st.markdown("### How each test is measured")
        st.markdown(r"""
        **1) Frequency (Monobit) Test**
        - **Goal:** Check if 0 and 1 appear ~ equally often.
        - **Method:** Count zeros Z and ones O in n bits (expected n/2 each).

        **2) Runs Test**
        - **Goal:** Check alternations between 0 and 1 (no long streaks).
        - **Method:** A **run** is a maximal substring of equal bits.
        - **Expected runs:** \( E[\text{runs}] = \frac{2n-1}{3} \). Compare observed vs expected.

        **3) Entropy (Shannon)**
        - **Goal:** Measure unpredictability per symbol.
        - **Formula:** \( H = -\sum_{b \in \{0,1\}} p_b \log_2 p_b \) where \( p_b = \frac{\text{count}(b)}{n} \).
        - **Ideal:** 1.0 bits/symbol when \(p_0 \approx p_1 \approx 0.5\).

        **4) Chi-Square Goodness-of-Fit (2 bins)**
        - **Goal:** Test if observed counts match expected 50/50.
        - **Statistic:** \( \chi^2 = \sum \frac{(O_i - E_i)^2}{E_i} \), with \(E_0 = E_1 = n/2\).
        - **p-value:** Probability of seeing a deviation ≥ observed under fair coin.
        - **Rule of thumb:** p > 0.05 ⇒ no evidence of bias.
        """)
        st.info("Reading results: Near-balanced counts, runs close to expectation, entropy near 1.0, and p > 0.05 "
                "are consistent with high-quality randomness.")

# REAL-WORLD
elif page == "Real-World":
    st.markdown("## 🌐 Real-World Applications & Demos")
    st.caption("All demos below use the currently generated QRNG key (synced).")

    if "qrng_bits" not in st.session_state or not st.session_state.qrng_bits:
        st.warning("⚠️ Generate a quantum key first (Generator).")
    else:
        bits = st.session_state.qrng_bits
        b = bits_to_bytes(bits)
        nbits = len(bits)

        st.markdown("### 🔑 API / Session Token")
        st.caption("Base64URL-encoded raw quantum bytes. Use for bearer/CSRF/reset tokens.")
        if st.button("Make Token from Current Key"):
            token = base64.urlsafe_b64encode(b).decode().rstrip("=")
            st.code(token, language="text")
            st.caption(f"Token derived from {nbits} quantum bits.")

        st.markdown("### 🆔 UUID (QRNG-derived)")
        st.caption("Requires 128 bits. We set version/variant to match UUIDv4 format.")
        if nbits < 128:
            st.warning(f"Need ≥128 bits for a UUID. Your key has {nbits} bits. Generate a 128-bit key in Generator.")
        else:
            if st.button("Make UUID from Current Key"):
                bb = bytearray(b[:16])
                bb[6] = (bb[6] & 0x0F) | 0x40
                bb[8] = (bb[8] & 0x3F) | 0x80
                u = uuid.UUID(bytes=bytes(bb))
                st.code(str(u), language="text")
                st.caption("Universally unique ID seeded by your quantum key.")

        st.markdown("### 🔐 HMAC Integrity (SHA-256)")
        st.caption("Ensures integrity/authenticity of a message. The key here is your QRNG bytes.")
        msg = st.text_input("Message", "QuantumSecuredMessage")
        if st.button("Generate HMAC"):
            digest = hmac.new(b, msg.encode(), hashlib.sha256).hexdigest()
            st.code(digest, language="text")

# FAQ
elif page == "FAQ":
    st.markdown("## ❓ Frequently Asked Questions")
    st.markdown("""
    **Q1:** Why quantum vs classical RNG?  
    **A:** Classical RNG is algorithmic, QRNG is intrinsically unpredictable.

    **Q2:** Can I generate multiple keys?  
    **A:** Yes, each click regenerates fresh bits and refreshes all pages.

    **Q3:** Is this production-ready?  
    **A:** The concept works. For large-scale deployment, use validated QRNG hardware/APIs.

    **Q4:** Can I integrate it with Python, JS, etc.?  
    **A:** Base64 or raw bytes can be fed into any programming environment.
    """)

# CONTACT (updated)
elif page == "Contact":
    st.markdown("## 📬 Contact Me")
    st.markdown('<div class="card" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown(f"""
        <h3>👤 Lakshmi Narayana Sangaraju</h3>
        <p>🌐 HTML &nbsp; 🎨 CSS &nbsp; ✨ ⚛️ React &nbsp; 🐍 Python &nbsp; 🔧 Git &nbsp; 💻 C &nbsp; 🗄️ SQL</p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.markdown(f"""<a href="mailto:sangarajuvamsi6@gmail.com">
                        <button style="width:100%;padding:10px;border-radius:8px;background:#6ae7ff;border:none;color:#000;font-weight:bold;cursor:pointer;">
                        📧 Email</button></a>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<a href="https://github.com/vamsi746" target="_blank">
                        <button style="width:100%;padding:10px;border-radius:8px;background:#ff6ad5;border:none;color:#fff;font-weight:bold;cursor:pointer;">
                        🐙 GitHub</button></a>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<a href="https://www.linkedin.com/in/lakshmi-narayana-sangaraju-a814472b6/" target="_blank">
                        <button style="width:100%;padding:10px;border-radius:8px;background:#0e76a8;border:none;color:#fff;font-weight:bold;cursor:pointer;">
                        🔗 LinkedIn</button></a>""", unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("""
        <p>Feel free to reach out for collaborations, questions, or just to say hi! 😊</p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
