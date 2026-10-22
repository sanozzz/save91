from update_inputs import v
F = "founder view (2026-09-30)"
FB = "founder data (2026-09-30)"
UPDATES = {
 "inputs.csv": {
    "ret_m1": v(0.60, 0.70, 0.80, F, "INC-01", notes="Shape interpolated to meet the founder's 20 at 1 year / 10 at 2 years"),
    "ret_m3": v(0.38, 0.48, 0.60, F, "INC-01"),
    "ret_m6": v(0.24, 0.33, 0.45, F, "INC-01"),
    "ret_m12": v(0.13, 0.20, 0.32, F, "INC-01", notes="Founder: of 100 who start, about 20 still saving after a year. Rider tenure averages about 13 months [INC-01]."),
    "ret_m24": v(0.06, 0.10, 0.20, F, "INC-01", notes="Founder: about 10 of 100 still saving after two years."),
    "loan_ead": v(0.90, 0.80, 0.70, "founder experience (Bueno) applied to saver loans", "", notes="At Bueno nearly all of a loan was still unpaid when it went 90+ late; saver loans run 6 months, so slightly less."),
    "loan_lgd": v(0.60, 0.50, 0.40, "founder experience (Bueno) applied to saver loans", "", notes="Bueno recovered about half of what was owed on loans 90+ days late."),
 },
 "inputs_lending_first.csv": {
    "lf_platform_share": v(0.90, 0.85, 0.80, FB + ": over 75% via platforms", ""),
    "lf_dpd90_repeat": v(0.02, 0.015, 0.01, FB + ": repeat loans 1-2% late", ""),
    "lf_ead": v(0.95, 0.92, 0.90, FB + ": nearly all still unpaid at 90+ late", ""),
    "lf_lgd": v(0.60, 0.50, 0.40, FB + ": about half recovered", ""),
    "lf_underwrite_cost": v(60, 40, 20, FB + ": KYC + bureau Rs 20-60 per applicant", ""),
 },
}
