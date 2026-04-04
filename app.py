import streamlit as st
import py3Dmol
from stmol import showmol
import time
import io
from contextlib import redirect_stdout

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
st.header(f"Simulation Dashboard: {molecule_choice.upper()}")

# Create a 50/50 split layout
col_render, col_logs = st.columns(2)

if molecule_choice == "custom":
    selected_atoms = parse_xyz_string(custom_xyz)
    xyz_data = generate_xyz_string(selected_atoms, "custom") 
    st.sidebar.caption(f"✅ Parsed {len(selected_atoms)} custom atoms.")
else:
    selected_atoms = MOLECULE_LIBRARY[molecule_choice]
    xyz_data = generate_xyz_string(selected_atoms, molecule_choice)

with col_render:
    st.subheader("Molecular Geometry")
    if len(selected_atoms) > 0:
        view = py3Dmol.view(width=400, height=400) # Shrunk width to fit column
        view.setBackgroundColor('#0E1117') 
        view.addModel(xyz_data, "xyz")
        view.setStyle({'stick': {'radius': 0.15}, 'sphere': {'radius': 0.4}})
        view.zoomTo()
        
        html_code = view._make_html()
        st.components.v1.html(html_code, height=400, width=400)
    else:
        st.error("⚠️ No valid coordinates found.")

with col_logs:
    st.subheader("Execution Logs")
    # Create an empty placeholder where our terminal output will eventually go
    terminal_output = st.empty()
    terminal_output.code("System Idle. Waiting for execution...", language="bash")
# --- 4. Execution Trigger ---
if st.button("Initialize Quantum Solver", type="primary"):
    
    # Validation check for custom atoms
    if not selected_atoms:
        st.error("No valid atoms found in the XYZ input. Please check your formatting.")
    else:
        # 1. Update the spinner text
        with st.spinner("Executing VQE on Local Simulator..."):
            try:
                # 1. Create a fake text file in memory to catch the terminal prints
                log_stream = io.StringIO()
                
                # 2. Force all print() statements to go into log_stream instead of the terminal
                with redirect_stdout(log_stream):
                
                    # Build the Problem
                    factory = MoleculeFactory(atoms=selected_atoms)
                    problem = factory.build_problem(
                        active_electrons=active_electrons, 
                        active_orbitals=active_orbitals
                    )

                    # Run Classical Baseline
                    start_time_c = time.time()
                    c_energy = calculate_classical_energy(problem)
                    c_time = time.time() - start_time_c

                    # Run Quantum VQE
                    start_time_q = time.time()
                    q_energy = run_quantum_vqe(
                        problem=problem, 
                        backend_name="local", 
                        use_session=False 
                    )
                    q_time = time.time() - start_time_q

                # 3. Execution is done. Grab the captured text and push it to the UI!
                captured_logs = log_stream.getvalue()
                
                # If your backend doesn't print much, add a default success message
                if not captured_logs.strip():
                    captured_logs = "Process exited successfully with code 0.\n(No standard output detected)"
                    
                terminal_output.code(captured_logs, language="bash")

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