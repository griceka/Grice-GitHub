import os
import tkinter as tk
from tkinter import filedialog, messagebox
from cclib.io import ccopen
from cclib.parser.utils import PeriodicTable

HARTREE_TO_KCAL_MOL = 627.509

def gaussian_terminated_normally(log_path):
    """Check if Gaussian log has normal termination."""
    with open(log_path, 'r') as f:
        for line in reversed(f.readlines()):
            if 'Normal termination' in line:
                return True
    return False

def extract_xyz_with_gibbs(log_path):
    if not gaussian_terminated_normally(log_path):
        print(f"Skipping {os.path.basename(log_path)} — no normal termination.")
        return None

    mol = ccopen(log_path).parse()

    # Gibbs free energy (Hartree → kcal/mol)
    if hasattr(mol, 'freeenergy') and mol.freeenergy is not None:
        gibbs_kcal = mol.freeenergy * HARTREE_TO_KCAL_MOL
        comment = f"{os.path.basename(log_path)} | Gibbs Free Energy = {gibbs_kcal:.2f} kcal/mol"
    else:
        comment = f"{os.path.basename(log_path)} | Gibbs Free Energy = N/A"

    atoms = mol.atomnos
    coords = mol.atomcoords[-1]
    pt = PeriodicTable()
    lines = [f"{len(atoms)}", comment]
    for atom, coord in zip(atoms, coords):
        symbol = pt.element[atom]
        x, y, z = coord
        lines.append(f"{symbol} {x:.6f} {y:.6f} {z:.6f}")
    return "\n".join(lines)

def main():
    # Tkinter root
    root = tk.Tk()
    root.withdraw()

    # Ask user for existing XYZ file
    xyz_file = filedialog.askopenfilename(
        title="Select existing XYZ file",
        filetypes=[("XYZ files", "*.xyz")]
    )
    if not xyz_file:
        messagebox.showwarning("No file", "No XYZ file selected. Exiting.")
        return

    # Ask user for folder containing log files
    log_folder = filedialog.askdirectory(title="Select folder containing Gaussian log files")
    if not log_folder:
        messagebox.showwarning("No folder", "No log folder selected. Exiting.")
        return

    # Find all .log files
    log_files = [f for f in os.listdir(log_folder) if f.endswith(".log")]
    if not log_files:
        messagebox.showwarning("No logs", "No .log files found in the selected folder.")
        return

    added = []
    skipped = []

    try:
        with open(xyz_file, "a") as f:  # append mode
            for log in log_files:
                log_path = os.path.join(log_folder, log)
                xyz_block = extract_xyz_with_gibbs(log_path)
                if xyz_block:
                    f.write("\n" + xyz_block)
                    added.append(log)
                else:
                    skipped.append(log)

        # Final popup summary
        summary = f"✅ Added {len(added)} structures to:\n{xyz_file}"
        if skipped:
            summary += f"\n\n⚠️ Skipped {len(skipped)} (no normal termination):\n" + "\n".join(skipped)
        messagebox.showinfo("Done", summary)

    except Exception as e:
        messagebox.showerror("Error", f"Failed while processing logs.\n\nError: {e}")

if __name__ == "__main__":
    main()
