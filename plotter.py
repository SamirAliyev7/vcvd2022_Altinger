"""
Plotter — Fx and Fy vs longitudinal slip (combined slip model).

Reference:
    Bakker, E., Nyborg, L., Pacejka, H.B. (1987).
    Tyre Modelling for Use in Vehicle Dynamics Studies.
    SAE Transactions. Fig. 19 & 20.

Author : Samir Aliyev
Student: 2510787008
"""

#import standard library
import os

#import third-party libraries
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

#import local module
from tire_model import TireModel


class Plotter:
    """
    Creates Fx / Fy vs longitudinal-slip plots using combined-slip model.

    Matches the layout of Fig. 19 & 20 in the reference:
      - Fx (brake force): rises from 0, peaks, then gradually decreases
      - Fy (side force): starts at pure-cornering value, decreases with slip

    Reference:
        Bakker, Nyborg, Pacejka (1987), SAE Transactions, Fig. 19 & 20.
    """

    #colour cycle for up to 6 Fz curves
    _COLOURS_     = ["tab:blue", "tab:orange", "tab:red",
                     "tab:purple", "tab:brown", "tab:cyan"]
    _NUM_POINTS_  = 500   #kappa sample count

    #=========
    # Constructor
    # param in: tire_model     — TireModel instance
    # param in: friction_coeff — mu, scales peak force D [—]
    # param in: slip_angle_deg — slip angle alpha [deg]
    #=========
    def __init__(self, tire_model, friction_coeff=1.0,
                 slip_angle_deg=2.0):
        """Initialise with model reference and run parameters."""
        self._tire_model_     = tire_model
        self._friction_coeff_ = friction_coeff
        self._slip_angle_deg_ = slip_angle_deg

    #=========
    # Build kappa array [0,1] (fraction)
    # returns: numpy array
    #=========
    def _kappa_frac_array(self):
        """Return kappa in [0, 1] fraction."""
        return np.linspace(0.0, 1.0, self._NUM_POINTS_)

    #=========
    # Compute Fx, Fy arrays over kappa for one Fz
    # param in: kappa_frac_arr — array of kappa fractions [0,1]
    # param in: fz_n           — normal force [N]
    # returns : (fx_arr, fy_arr) in [N]
    #=========
    def _forces_over_kappa(self, kappa_frac_arr, fz_n=2000.0):
        """Return (Fx, Fy) arrays using combined-slip model."""
        fx_list_ = []
        fy_list_ = []
        for kappa_ in kappa_frac_arr:
            fx_val_, fy_val_ = self._tire_model_.compute_combined(
                kappa_frac=kappa_,
                alpha_deg=self._slip_angle_deg_,
                fz_n=fz_n,
                mu=self._friction_coeff_
            )
            fx_list_.append(max(fx_val_, 0.0))
            fy_list_.append(max(fy_val_, 0.0))
        return np.array(fx_list_), np.array(fy_list_)

    #=========
    # Draw all Fz curves onto a matplotlib Axes
    # param in: axes       — Axes object
    # param in: kappa_pct  — kappa in percent [0,100]
    # param in: fz_list_n  — list of normal force values [N]
    #=========
    def _draw_curves(self, axes, kappa_pct, fz_list_n):
        """Plot Fx (solid) and Fy (dashed) for each Fz on axes."""
        for idx_, fz_n_ in enumerate(fz_list_n):
            colour_   = self._COLOURS_[idx_ % len(self._COLOURS_)]
            fz_label_ = f"Fz = {fz_n_/1000:.0f} kN  ({idx_+1})"

            fx_arr_, fy_arr_ = self._forces_over_kappa(
                kappa_pct / 100.0, fz_n_)

            #brake force — solid line (matches paper Fig 19/20)
            axes.plot(kappa_pct, fx_arr_,
                      color=colour_, linestyle="-", linewidth=2.0,
                      label=f"-Fx  {fz_label_}")
            #side force — dashed line (matches paper Fig 19/20)
            axes.plot(kappa_pct, fy_arr_,
                      color=colour_, linestyle="--", linewidth=2.0,
                      label=f"Fy   {fz_label_}")

    #=========
    # Apply styling to axes
    # param in: axes — Axes object
    #=========
    def _style_axes(self, axes):
        """Set labels, grid, legend and force-type annotations."""
        axes.set_xlabel("Longitudinal slip  -κ  [%]", fontsize=12)
        axes.set_ylabel("Side force  Fy  |N|  /  Brake force  -Fx  |N|",
                        fontsize=11)
        axes.set_title(
            "Side Force Fy  and  Brake Force Fx  vs  Longitudinal Slip\n"
            f"α = {self._slip_angle_deg_:.2f} °,   μ = {self._friction_coeff_}",
            fontsize=13
        )
        axes.set_xlim(0, 100)
        axes.set_ylim(bottom=0)
        axes.grid(True, alpha=0.35)
        axes.legend(loc="upper right", fontsize=8, ncol=2)
        axes.annotate("— Calculations  -Fx",
                      xy=(0.62, 0.62), xycoords="axes fraction", fontsize=10)
        axes.annotate("-- Calculations   Fy",
                      xy=(0.62, 0.56), xycoords="axes fraction", fontsize=10)

    #=========
    # Generate and save the plot
    # param in: fz_values_n — list of normal forces [N]
    # param in: output_dir  — destination folder for PNG
    # returns : saved file path [str]
    #=========
    def plot_forces(self, fz_values_n=None, output_dir="plots"):
        """Create, style and export the combined-slip force plot as PNG."""
        if fz_values_n is None:
            fz_values_n = [2000.0, 4000.0, 6000.0, 8000.0]

        kappa_arr_ = self._kappa_frac_array()
        kappa_pct_ = kappa_arr_ * 100.0

        figure_, axes_ = plt.subplots(figsize=(11, 7))
        self._draw_curves(axes_, kappa_pct_, fz_values_n)
        self._style_axes(axes_)
        figure_.tight_layout()

        filename_    = (f"forces_alpha{self._slip_angle_deg_:.2f}deg"
                        f"_mu{self._friction_coeff_}.png")
        output_path_ = os.path.join(output_dir, filename_)
        os.makedirs(output_dir, exist_ok=True)
        figure_.savefig(output_path_, dpi=150, bbox_inches="tight")
        plt.close(figure_)
        print(f"  Plot saved -> {output_path_}")
        return output_path_
