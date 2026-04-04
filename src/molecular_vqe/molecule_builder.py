from dataclasses import dataclass
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.transformers import ActiveSpaceTransformer
from qiskit_nature.units import DistanceUnit

@dataclass
class Atom:
    """Represents a single atom in a 3D coordinate space."""
    symbol: str
    x: float
    y: float
    z: float

    def to_pyscf_string(self) -> str:
        """Formats the atom for the PySCF driver."""
        return f"{self.symbol} {self.x} {self.y} {self.z}"

class MoleculeFactory:
    """Generates Qiskit ElectronicStructureProblems from a list of Atoms."""
    def __init__(self, atoms: list[Atom], charge: int = 0, spin: int = 0, basis: str = "sto3g"):
        self.atoms = atoms
        self.charge = charge
        self.spin = spin
        self.basis = basis

    def get_geometry_string(self) -> str:
        """Joins all atoms into the semicolon-separated string PySCF expects."""
        return "; ".join([atom.to_pyscf_string() for atom in self.atoms])

    def build_problem(self, active_electrons: int = None, active_orbitals: int = None):
        """
        Runs the classical driver and optionally applies an Active Space reduction
        to freeze core electrons and reduce qubit requirements.
        """
        # 1. Initialize the Classical Driver
        driver = PySCFDriver(
            atom=self.get_geometry_string(),
            basis=self.basis,
            charge=self.charge,
            spin=self.spin,
            unit=DistanceUnit.ANGSTROM
        )
        problem = driver.run()

        # 2. Apply the Active Space Transformer (if parameters are provided)
        if active_electrons is not None and active_orbitals is not None:
            transformer = ActiveSpaceTransformer(
                num_electrons=active_electrons,
                num_spatial_orbitals=active_orbitals
            )
            problem = transformer.transform(problem)

        return problem
    
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