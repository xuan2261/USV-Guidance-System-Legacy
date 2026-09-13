#pragma once
#include "usv_model_core/vessel_state.hpp"
namespace usv_model_core {
enum class HeadingPolicy {
  LegacyCompatible,
  Normalized
};
class Viknes830 {
public:
  struct Parameters {
    double mass_kg{3980.0};
    double iz_kgm2{19703.0};
    double length_m{10.0};
    double width_m{4.0};
    double x_u{-50.0}, y_v{-200.0}, y_r{0.0}, n_v{0.0}, n_r{-3224.0};
    double x_uu{-135.0}, y_vv{-2000.0}, n_rr{0.0}, x_uuu{0.0}, y_vvv{0.0}, n_rrr{-3224.0};
    double fx_min_n{-6550.0}, fx_max_n{13100.0};
    double fy_min_n{-645.0}, fy_max_n{645.0};
    double rudder_arm_m{4.0};
    double kp_u{1.0}, kp_yaw{5.0}, kd_yaw{1.0};
    HeadingPolicy heading_policy{HeadingPolicy::LegacyCompatible};
  };
  Viknes830();
  explicit Viknes830(Parameters parameters);
  static double wrap_angle(double angle_rad);
  static double legacy_ssa(double angle_rad);
  static double legacy_normalize_angle_diff(double angle_rad, double angle_ref_rad);
  StateDerivative derivative(const VesselState & state, const ControlSetpoint & setpoint) const;
  VesselState step_rk4(const VesselState & state, const ControlSetpoint & setpoint, double dt_s) const;
  const Parameters & parameters() const { return p_; }
private:
  Parameters p_;
};
}
