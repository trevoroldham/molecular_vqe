import streamlit as st
import py3Dmol
from stmol import showmol
import time

# Import your existing backend
from src.molecule_builder import Atom, MoleculeFactory
from src.quantum_solver import run_quantum_vqe
from src.classical_baseline import calculate_classical_energy

MOLECULE_LIBRARY = {
    "h2": [Atom("H", 0.0, 0.0, 0.0), Atom("H", 0.0, 0.0, 0.735)],
    "water": [Atom("O", 0.0, 0.0, 0.0), Atom("H", 0.757, 0.586, 0.0), Atom("H", -0.757, 0.586, 0.0)],
    "lih": [Atom("Li", 0.0, 0.0, 0.0), Atom("H", 0.0, 0.0, 1.546)]
}

def generate_xyz_string(atoms, name="molecule"):
    """Translates a list of Atom objects into a standard XYZ string."""
    xyz = f"{len(atoms)}\n{name}\n"
    for atom in atoms:
        xyz += f"{atom.symbol} {atom.x} {atom.y} {atom.z}\n"
    return xyz

def parse_xyz_string(xyz_str):
    """Parses a raw XYZ text block into a list of Atom objects."""
    atoms = []
    # splitlines() safely handles invisible Windows \r\n carriage returns
    for line in xyz_str.strip().splitlines():
        parts = line.split()
        # Require at least 4 parts (Symbol, X, Y, Z)
        if len(parts) >= 4:
            try:
                # Force standard chemical capitalization (e.g., c -> C)
                symbol = parts[0].capitalize()
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                atoms.append(Atom(symbol, x, y, z))
            except ValueError:
                # Safely ignore header strings or blank lines
                continue 
    return atoms

# --- 1. Page Configuration ---
# --- 1. Page Configuration ---
# Set the favicon to something thematic, and keep the layout wide
st.set_page_config(page_title="Molecular VQE", page_icon="🌌", layout="wide")
st.title("🌌 Hybrid Quantum-Classical VQE Solver")
st.markdown("---") # Adds a sleek horizontal divider line

# --- 2. Sidebar Controls ---
st.sidebar.header("Simulation Parameters")

molecule_choice = st.sidebar.selectbox(
    "Target Molecule",
    options=["h2", "water", "lih", "custom"],
    format_func=lambda x: x.upper() if x != "custom" else "Custom XYZ Input"
)

# New Custom XYZ Text Area
custom_xyz = ""
if molecule_choice == "custom":
    # Use a triple-quoted multi-line string to force Streamlit to respect line breaks
    default_methane = """C 0.0 0.0 0.0
                        H 0.6276 0.6276 0.6276
                        H -0.6276 -0.6276 0.6276
                        H -0.6276 0.6276 -0.6276
                        H 0.6276 -0.6276 -0.6276"""
    
    custom_xyz = st.sidebar.text_area(
        "Paste XYZ Coordinates",
        value=default_methane,
        height=150,
        help="Paste standard XYZ formatting. Headers are ignored."
    )

st.sidebar.subheader("Active Space Reduction")
use_active_space = st.sidebar.checkbox("Freeze Core Orbitals")

active_electrons = None
active_orbitals = None
if use_active_space:
    active_electrons = st.sidebar.number_input("Active Electrons", min_value=1, value=8)
    active_orbitals = st.sidebar.number_input("Active Orbitals", min_value=1, value=6)

st.sidebar.markdown("---")
st.sidebar.info(
    "🔒 **Public Demo Mode**\n\n"
    "Hardware execution is disabled for this public deployment. "
    "The quantum solver is currently locked to the local noiseless statevector simulator."
)

# --- 3. Parsing and Dynamic Rendering ---
st.header(f"Geometry: {molecule_choice.upper()}")

if molecule_choice == "custom":
    selected_atoms = parse_xyz_string(custom_xyz)
    xyz_data = generate_xyz_string(selected_atoms, "custom") 
    st.caption(f"✅ Successfully parsed {len(selected_atoms)} atoms from custom input.")
else:
    selected_atoms = MOLECULE_LIBRARY[molecule_choice]
    xyz_data = generate_xyz_string(selected_atoms, molecule_choice)

# 🐛 DEBUG EXPANDER: See exactly what the parser is handing to py3Dmol
with st.expander("🔍 View Raw Parsed Data (Debug)"):
    st.code(xyz_data, language="text")

# Render the 3D Model ONLY if atoms were successfully parsed
if len(selected_atoms) > 0:
    view = py3Dmol.view(width=800, height=400)

    # NEW: Match the Streamlit dark background exactly

    view.setBackgroundColor('#0E1117')
    view.addModel(xyz_data, "xyz")
    view.setStyle({'stick': {'radius': 0.15}, 'sphere': {'radius': 0.4}})
    view.zoomTo()
    
    # We use Streamlit's native HTML renderer here to bypass stmol caching quirks
    html_code = view._make_html()
    st.components.v1.html(html_code, height=400, width=800)
else:
    st.error("⚠️ No valid coordinates found. The parser returned 0 atoms. Please check the XYZ formatting.")

# --- 4. Execution Trigger ---
if st.button("Initialize Quantum Solver", type="primary"):
    
    # Validation check for custom atoms
    if not selected_atoms:
        st.error("No valid atoms found in the XYZ input. Please check your formatting.")
    else:
        # 1. Update the spinner text
        with st.spinner("Executing VQE on Local Simulator..."):
            try:
                # 1. Build the Problem
                factory = MoleculeFactory(atoms=selected_atoms)
                problem = factory.build_problem(
                    active_electrons=active_electrons, 
                    active_orbitals=active_orbitals
                )

                # 2. Run Classical Baseline
                start_time_c = time.time()
                c_energy = calculate_classical_energy(problem)
                c_time = time.time() - start_time_c

                # 3. Run Quantum VQE
                start_time_q = time.time()
                q_energy = run_quantum_vqe(
                    problem=problem, 
                    backend_name="local", # 2. Hardcoded securely to 'local'
                    use_session=False 
                )
                q_time = time.time() - start_time_q
                
                # ... (The rest of your display logic remains exactly the same)

                # 4. Calculate Error
                error = abs(c_energy - q_energy)

                st.success("Simulation Complete!")
                
                # 5. Display Dynamic Results
                col1, col2 = st.columns(2)
                col1.metric(
                    label="Classical Exact", 
                    value=f"{c_energy:.6f} Ha", 
                    delta=f"{c_time:.2f} s", 
                    delta_color="off"
                )
                col2.metric(
                    label="Quantum Estimation", 
                    value=f"{q_energy:.6f} Ha", 
                    delta=f"Error: {error:.6f} Ha", 
                    delta_color="inverse"
                )

            except Exception as e:
                st.error(f"An error occurred during execution: {e}")