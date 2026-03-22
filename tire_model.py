"""
TireModel — Pacejka Magic Formula (pure + combined slip).

IMPORTANT NOTE ON UNITS:
    The coefficients in Table 2 & 3 (Bakker 1987) are calibrated so that:
      - Slip angle  alpha  is passed in DEGREES  (not radians)
      - Longitudinal slip  kappa  is passed in PERCENT 0-100  (not 0-1 fraction)
      - Normal force  Fz   is passed in NEWTONS  (converted to kN inside)
    This is consistent with how the basic curves are plotted in the paper.

Reference:
    Bakker, E., Nyborg, L., Pacejka, H.B. (1987).
    Tyre Modelling for Use in Vehicle Dynamics Studies.
    SAE Transactions. Table 2, 3 and Eq. 16-18.

Author : Samir Aliyev
Student: 2510787008
"""

#import standard library
import math


class TireModel:
    """
    Implements the Pacejka Magic Formula (pure and combined slip).

    Coefficient tables are stored as class-level CONSTANTS.
    Source: Bakker, Nyborg, Pacejka (1987), SAE Transactions, Table 2 & 3.
    """

    # ------------------------------------------------------------------
    # Table 2 — Fy coefficients   (Fz in kN,  alpha in DEGREES)
    # Source: Bakker, Nyborg, Pacejka (1987), SAE Transactions, Table 2
    # ------------------------------------------------------------------
    FY_C   =  1.30
    FY_A1  = -22.1
    FY_A2  =  1011.0
    FY_A3  =  1078.0
    FY_A4  =  1.82
    FY_A5  =  0.208
    FY_A6  =  0.000
    FY_A7  = -0.354
    FY_A8  =  0.707

    # Table 3 — Fy camber coefficients   (gamma in DEGREES)
    # Source: Bakker, Nyborg, Pacejka (1987), SAE Transactions, Table 3
    FY_A9  =  0.028
    FY_A10 =  0.000
    FY_A11 =  14.8
    FY_A12 =  0.022
    FY_A13 =  0.000

    # ------------------------------------------------------------------
    # Table 2 — Fx coefficients   (Fz in kN,  kappa in PERCENT 0-100)
    # Source: Bakker, Nyborg, Pacejka (1987), SAE Transactions, Table 2
    # ------------------------------------------------------------------
    FX_C   =  1.65
    FX_A1  = -21.3
    FX_A2  =  1144.0
    FX_A3  =  49.6
    FX_A4  =  226.0
    FX_A5  =  0.069
    FX_A6  = -0.006
    FX_A7  =  0.056
    FX_A8  =  0.486

    # ------------------------------------------------------------------
    #  Pure Fy — Magic Formula
    # ------------------------------------------------------------------

    #=========
    # Compute peak factor D for Fy
    # param in: fz_kn — normal force [kN]
    # param in: mu    — peak friction coefficient [—]
    # returns : D [N]
    #=========
    def _peak_fy(self, fz_kn=0.0, mu=1.0):
        """Return peak side force D = (a1*Fz^2 + a2*Fz) * mu."""
        return (self.FY_A1 * fz_kn ** 2 + self.FY_A2 * fz_kn) * mu

    #=========
    # Compute stiffness factor B for Fy
    # param in: fz_kn     — normal force [kN]
    # param in: coeff_c   — shape factor C [—]
    # param in: coeff_d   — peak factor D [N]
    # param in: gamma_deg — camber angle [deg]
    # returns : B [1/deg]
    #=========
    def _stiffness_fy(self, fz_kn=0.0, coeff_c=1.30,
                      coeff_d=1.0, gamma_deg=0.0):
        """Return stiffness factor B for side force."""
        numerator_   = self.FY_A3 * math.sin(
            self.FY_A4 * math.atan(self.FY_A5 * fz_kn))
        camber_term_ = 1.0 - self.FY_A12 * abs(gamma_deg)
        denom_       = coeff_c * coeff_d
        if abs(denom_) < 1e-9:
            denom_ = 1e-9
        return (numerator_ / denom_) * camber_term_

    #=========
    # Compute curvature factor E for Fy
    # param in: fz_kn — normal force [kN]
    # returns : E [—]
    #=========
    def _curvature_fy(self, fz_kn=0.0):
        """Return curvature factor E for side force."""
        return self.FY_A6 * fz_kn ** 2 + self.FY_A7 * fz_kn + self.FY_A8

    #=========
    # Compute generalised slip phi for Fy
    # param in: alpha_deg — slip angle in DEGREES
    # param in: coeff_b   — stiffness factor [1/deg]
    # param in: coeff_e   — curvature factor [—]
    # param in: delta_sh  — horizontal shift [deg]
    # returns : phi [deg]
    #=========
    def _phi_fy(self, alpha_deg=0.0, coeff_b=1.0,
                coeff_e=0.0, delta_sh=0.0):
        """Return generalised slip phi for Fy (alpha in degrees)."""
        arg_   = alpha_deg + delta_sh
        inv_b_ = 1.0 / coeff_b if abs(coeff_b) > 1e-9 else 1e-9
        return (1.0 - coeff_e) * arg_ + coeff_e * inv_b_ * math.atan(coeff_b * arg_)

    #=========
    # Compute pure side force Fy0
    # param in: alpha_deg — slip angle [deg]
    # param in: fz_n      — normal force [N]
    # param in: mu        — peak friction coefficient [—]
    # param in: gamma_deg — camber angle [deg]
    # returns : Fy0 [N]
    #=========
    def compute_fy(self, alpha_deg=0.0, fz_n=2000.0,
                   mu=1.0, gamma_deg=0.0):
        """
        Return pure side force Fy0 [N].

        NOTE: alpha_deg is passed directly in DEGREES to the formula.
        The Table 2 coefficients are calibrated for alpha in degrees.

        Formula: Fy = D * sin(C * arctan(B*phi)) + delta_Sv
        Source : Bakker, Nyborg, Pacejka (1987), side-force equation.
        """
        fz_kn_ = fz_n / 1000.0

        coeff_d_  = self._peak_fy(fz_kn_, mu)
        coeff_c_  = self.FY_C
        coeff_b_  = self._stiffness_fy(fz_kn_, coeff_c_, coeff_d_, gamma_deg)
        coeff_e_  = self._curvature_fy(fz_kn_)
        delta_sh_ = self.FY_A9 * gamma_deg
        delta_sv_ = (self.FY_A10 * fz_kn_ ** 2
                     + self.FY_A11 * fz_kn_) * gamma_deg

        #alpha in DEGREES — coefficients calibrated for degrees input
        phi_ = self._phi_fy(alpha_deg, coeff_b_, coeff_e_, delta_sh_)
        return coeff_d_ * math.sin(coeff_c_ * math.atan(coeff_b_ * phi_)) + delta_sv_

    # ------------------------------------------------------------------
    #  Pure Fx — Magic Formula
    # ------------------------------------------------------------------

    #=========
    # Compute peak factor D for Fx
    # param in: fz_kn — normal force [kN]
    # param in: mu    — peak friction coefficient [—]
    # returns : D [N]
    #=========
    def _peak_fx(self, fz_kn=0.0, mu=1.0):
        """Return peak brake force D = (a1*Fz^2 + a2*Fz) * mu."""
        return (self.FX_A1 * fz_kn ** 2 + self.FX_A2 * fz_kn) * mu

    #=========
    # Compute stiffness factor B for Fx
    # param in: fz_kn   — normal force [kN]
    # param in: coeff_c — shape factor C [—]
    # param in: coeff_d — peak factor D [N]
    # returns : B [1/pct]
    #=========
    def _stiffness_fx(self, fz_kn=0.0, coeff_c=1.65, coeff_d=1.0):
        """Return stiffness factor B for brake force."""
        numerator_ = self.FX_A3 * fz_kn ** 2 + self.FX_A4 * fz_kn
        exp_term_  = math.exp(self.FX_A5 * fz_kn)
        denom_     = coeff_c * coeff_d * exp_term_
        if abs(denom_) < 1e-9:
            denom_ = 1e-9
        return numerator_ / denom_

    #=========
    # Compute curvature factor E for Fx
    # param in: fz_kn — normal force [kN]
    # returns : E [—]
    #=========
    def _curvature_fx(self, fz_kn=0.0):
        """Return curvature factor E for brake force."""
        return self.FX_A6 * fz_kn ** 2 + self.FX_A7 * fz_kn + self.FX_A8

    #=========
    # Compute generalised slip phi for Fx
    # param in: kappa_pct — longitudinal slip in PERCENT (0-100)
    # param in: coeff_b   — stiffness factor [1/pct]
    # param in: coeff_e   — curvature factor [—]
    # returns : phi [pct]
    #=========
    def _phi_fx(self, kappa_pct=0.0, coeff_b=1.0, coeff_e=0.0):
        """Return generalised slip phi for Fx (kappa in percent)."""
        inv_b_ = 1.0 / coeff_b if abs(coeff_b) > 1e-9 else 1e-9
        return ((1.0 - coeff_e) * kappa_pct
                + coeff_e * inv_b_ * math.atan(coeff_b * kappa_pct))

    #=========
    # Compute pure brake force Fx0
    # param in: kappa_frac — longitudinal slip fraction [0, 1]
    # param in: fz_n       — normal force [N]
    # param in: mu         — peak friction coefficient [—]
    # returns : Fx0 [N]
    #=========
    def compute_fx(self, kappa_frac=0.0, fz_n=2000.0, mu=1.0):
        """
        Return pure brake force Fx0 [N].

        NOTE: kappa_frac (0-1) is converted to percent internally.
        The Table 2 coefficients are calibrated for kappa in percent.

        Formula: Fx = D * sin(C * arctan(B*phi))
        Source : Bakker, Nyborg, Pacejka (1987), brake-force equation.
        """
        fz_kn_     = fz_n / 1000.0
        kappa_pct_ = kappa_frac * 100.0   #convert fraction → percent

        coeff_d_ = self._peak_fx(fz_kn_, mu)
        coeff_c_ = self.FX_C
        coeff_b_ = self._stiffness_fx(fz_kn_, coeff_c_, coeff_d_)
        coeff_e_ = self._curvature_fx(fz_kn_)

        phi_ = self._phi_fx(kappa_pct_, coeff_b_, coeff_e_)
        return coeff_d_ * math.sin(coeff_c_ * math.atan(coeff_b_ * phi_))

    # ------------------------------------------------------------------
    #  Combined slip — Eq. 16 & 18 (Bakker et al. 1987)
    # ------------------------------------------------------------------

    #=========
    # Compute combined-slip Fx and Fy
    # param in: kappa_frac — longitudinal slip fraction [0, 1]
    # param in: alpha_deg  — slip angle [deg]
    # param in: fz_n       — normal force [N]
    # param in: mu         — peak friction coefficient [—]
    # returns : tuple (|Fx| [N], |Fy| [N])
    #=========
    def compute_combined(self, kappa_frac=0.0, alpha_deg=0.0,
                         fz_n=2000.0, mu=1.0):
        """
        Return (|Fx|, |Fy|) [N] using the combined-slip method.

        Theoretical slip components (Eq. 16):
            sigma_x = kappa / (1 + kappa)          longitudinal
            sigma_y = tan(alpha_rad) / (1 + kappa)  lateral
            sigma   = sqrt(sigma_x^2 + sigma_y^2)   combined

        Basic curves evaluated at combined sigma (Eq. 18):
            Fx0 at sigma: kappa_equiv = sigma/(1-sigma)  [fraction]
            Fy0 at sigma: alpha_equiv = degrees(atan(sigma))

        Combined forces (Eq. 18):
            |Fx| = (sigma_x / sigma) * Fx0(sigma)
            |Fy| = (sigma_y / sigma) * Fy0(sigma)

        Source: Bakker, Nyborg, Pacejka (1987), Eq. 16 and 18.
        """
        alpha_rad_ = math.radians(abs(alpha_deg))
        kappa_frac_ = abs(kappa_frac)

        #theoretical slip components - Eq. 16 (using fractions)
        denom_slip_ = max(1.0 + kappa_frac_, 1e-9)
        sigma_x_    = kappa_frac_ / denom_slip_
        sigma_y_    = math.tan(alpha_rad_) / denom_slip_
        sigma_tot_  = math.sqrt(sigma_x_ ** 2 + sigma_y_ ** 2)

        #pure cornering case (kappa = 0, sigma = tan(alpha))
        if sigma_tot_ < 1e-9:
            return 0.0, abs(self.compute_fy(alpha_deg, fz_n, mu))

        #map combined sigma back to pure-slip equivalent inputs - Eq. 18
        #for Fx0: sigma = kappa_frac/(1+kappa_frac) → kappa_frac = sigma/(1-sigma)
        kappa_equiv_frac_ = sigma_tot_ / max(1.0 - sigma_tot_, 1e-4)
        kappa_equiv_frac_ = min(kappa_equiv_frac_, 100.0)

        #for Fy0: sigma = tan(alpha_rad) → alpha = atan(sigma) in degrees
        alpha_equiv_deg_ = math.degrees(math.atan(sigma_tot_))

        #evaluate pure basic curves at combined sigma
        fx0_ = abs(self.compute_fx(kappa_equiv_frac_, fz_n, mu))
        fy0_ = abs(self.compute_fy(alpha_equiv_deg_, fz_n, mu))

        #scale by slip direction ratios - Eq. 18
        fx_out_ = (sigma_x_ / sigma_tot_) * fx0_
        fy_out_ = (sigma_y_ / sigma_tot_) * fy0_

        return fx_out_, fy_out_
