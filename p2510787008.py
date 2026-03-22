"""
Magic Formula Tire Model  —  Vehicle Components & Vehicle Dynamics
FH Oberösterreich, WS 2025

Reference:
    Bakker, E., Nyborg, L., Pacejka, H.B. (1987).
    Tyre Modelling for Use in Vehicle Dynamics Studies.
    SAE Transactions.

Author : Samir Aliyev
Student: 2510787008

Usage examples:
    python p2510787008.py --slip 2 --weight 1500 --mu 1.0
    python p2510787008.py --slip 5 --weight 1800 --mu 0.8
    python p2510787008.py --slip 5 --weight 1500 --mu 0.9
"""

#import standard library
import argparse
import os

#import third-party library (use scipy for gravity constant — no hardcoded g)
import scipy.constants

#import local modules
from tire_model import TireModel
from plotter import Plotter


#=========
# Build CLI argument parser
# returns: argparse.ArgumentParser
#=========
def build_arg_parser():
    """Configure and return the CLI argument parser."""
    #import argument parser
    arg_parser_ = argparse.ArgumentParser(
        description=(
            "Pacejka Magic Formula tire model — combined slip. "
            "Plots side force Fy and brake force Fx vs longitudinal "
            "slip kappa (0-100%%). "
            "Reference: Bakker, Nyborg, Pacejka (1987), SAE Transactions."
        )
    )
    #setup required arguments
    arg_parser_.add_argument(
        "--slip",
        type=float,
        default=2.0,
        help="Slip angle alpha in degrees  (default: 2.0)"
    )
    arg_parser_.add_argument(
        "--weight",
        type=float,
        default=1500.0,
        help="Vehicle mass in kg           (default: 1500.0)"
    )
    arg_parser_.add_argument(
        "--mu",
        type=float,
        default=1.0,
        help="Peak friction coefficient mu  (default: 1.0)"
    )
    return arg_parser_


#=========
# Compute per-wheel normal load from vehicle mass
# param in: vehicle_mass_kg — total mass [kg]
# returns : Fz per wheel [N]
#=========
def compute_wheel_load(vehicle_mass_kg=1500.0):
    """Return Fz per wheel [N] with equal 4-wheel distribution."""
    #scipy.constants.g avoids hardcoding gravitational acceleration
    return vehicle_mass_kg * scipy.constants.g / 4.0


#=========
# Build Fz list for multi-curve plot
# param in: fz_derived_n — user-derived Fz [N]
# returns : sorted list of Fz values [N]
#=========
def build_fz_list(fz_derived_n=0.0):
    """Return list of Fz values combining reference and user-derived Fz."""
    #reference Fz values from Bakker et al. (1987) paper figures
    fz_ref_list_  = [2000.0, 4000.0, 6000.0, 8000.0]
    fz_rounded_   = round(fz_derived_n / 500.0) * 500.0
    if fz_rounded_ not in fz_ref_list_:
        fz_ref_list_.append(fz_rounded_)
    return sorted(fz_ref_list_)


#=========
# Print formatted run summary to console
# param in: slip_angle_deg  — alpha [deg]
# param in: vehicle_mass_kg — vehicle mass [kg]
# param in: friction_coeff  — mu [—]
# param in: fz_per_wheel_n  — derived Fz per wheel [N]
#=========
def print_summary(slip_angle_deg=2.0, vehicle_mass_kg=1500.0,
                  friction_coeff=1.0, fz_per_wheel_n=0.0):
    """Print run-parameter summary."""
    print("=" * 52)
    print("  Magic Formula Tire Model  —  Samir Aliyev")
    print("  Student ID : 2510787008")
    print("=" * 52)
    print(f"  Slip angle  alpha : {slip_angle_deg:.2f} deg")
    print(f"  Vehicle mass      : {vehicle_mass_kg:.1f} kg")
    print(f"  Friction    mu    : {friction_coeff:.3f}")
    print(f"  Fz per wheel      : {fz_per_wheel_n:.1f} N")
    print("=" * 52)


#=========
# Main entry point
#=========
def main():
    """Parse CLI args, run tire model and generate plots."""
    arg_parser_     = build_arg_parser()
    cmd_args_       = arg_parser_.parse_args()

    slip_angle_deg_  = cmd_args_.slip
    vehicle_mass_kg_ = cmd_args_.weight
    friction_coeff_  = cmd_args_.mu

    #derive per-wheel normal load
    fz_per_wheel_n_  = compute_wheel_load(vehicle_mass_kg_)

    print_summary(slip_angle_deg_, vehicle_mass_kg_,
                  friction_coeff_, fz_per_wheel_n_)

    #instantiate tire model (coefficients stored as CONSTANTS in class)
    tire_model_  = TireModel()

    #build Fz curve list
    fz_values_n_ = build_fz_list(fz_per_wheel_n_)

    #output directory (same folder as this script)
    base_dir_    = os.path.dirname(os.path.abspath(__file__))
    output_dir_  = os.path.join(base_dir_, "plots")

    #create plotter and generate plot
    plotter_ = Plotter(tire_model_, friction_coeff_, slip_angle_deg_)

    print(f"\n  Fz values plotted: {[int(fz) for fz in fz_values_n_]} N")

    plotter_.plot_forces(fz_values_n=fz_values_n_, output_dir=output_dir_)

    print("\n  Done.")


if __name__ == "__main__":
    main()
