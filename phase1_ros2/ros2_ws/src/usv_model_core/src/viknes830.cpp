#include "usv_model_core/viknes830.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>
namespace usv_model_core {
namespace {
constexpr double kPi = 3.141592653589793238462643383279502884;
VesselState add(const VesselState & s, const StateDerivative & k, double h) {
  return {s.x_m+h*k.x_mps, s.y_m+h*k.y_mps, s.yaw_rad+h*k.yaw_radps,
          s.u_mps+h*k.u_mps2, s.v_mps+h*k.v_mps2, s.r_radps+h*k.r_radps2};
}
StateDerivative combine(const StateDerivative & a, const StateDerivative & b,
                        const StateDerivative & c, const StateDerivative & d) {
  return {(a.x_mps+2*b.x_mps+2*c.x_mps+d.x_mps)/6.0,
          (a.y_mps+2*b.y_mps+2*c.y_mps+d.y_mps)/6.0,
          (a.yaw_radps+2*b.yaw_radps+2*c.yaw_radps+d.yaw_radps)/6.0,
          (a.u_mps2+2*b.u_mps2+2*c.u_mps2+d.u_mps2)/6.0,
          (a.v_mps2+2*b.v_mps2+2*c.v_mps2+d.v_mps2)/6.0,
          (a.r_radps2+2*b.r_radps2+2*c.r_radps2+d.r_radps2)/6.0};
}
}
Viknes830::Viknes830() : Viknes830(Parameters{}) {}
Viknes830::Viknes830(Parameters parameters) : p_(parameters) {
  if (p_.mass_kg <= 0 || p_.iz_kgm2 <= 0 || p_.rudder_arm_m <= 0) {
    throw std::invalid_argument("invalid vessel parameters");
  }
}
double Viknes830::wrap_angle(double a) {
  return std::remainder(a, 2.0 * kPi);
}
double Viknes830::legacy_ssa(double a) {
  return std::fmod(a + kPi, 2.0 * kPi) - kPi;
}
double Viknes830::legacy_normalize_angle_diff(double angle, double angle_ref) {
  if (std::isinf(angle) || std::isinf(angle_ref)) return angle;
  const double diff0 = angle_ref - angle;
  double out;
  if (diff0 > 0) out = angle + (diff0 - std::fmod(diff0, 2.0 * kPi));
  else out = angle + (diff0 + std::fmod(-diff0, 2.0 * kPi));
  const double diff1 = angle_ref - out;
  if (diff1 > kPi) out += 2.0 * kPi;
  else if (diff1 < -kPi) out -= 2.0 * kPi;
  return out;
}
StateDerivative Viknes830::derivative(const VesselState & s, const ControlSetpoint & sp) const {
  const bool legacy = p_.heading_policy == HeadingPolicy::LegacyCompatible;
  const double psi = legacy ? legacy_ssa(s.yaw_rad) : wrap_angle(s.yaw_rad);
  const double cy = std::cos(psi), sy = std::sin(psi);

  const double cv0 = (-p_.mass_kg * s.v_mps) * s.r_radps;
  const double cv1 = ( p_.mass_kg * s.u_mps) * s.r_radps;
  const double cv2 = ( p_.mass_kg * s.v_mps) * s.u_mps + (-p_.mass_kg * s.u_mps) * s.v_mps;

  const double dv0 = -(p_.x_u + p_.x_uu*std::abs(s.u_mps) + p_.x_uuu*s.u_mps*s.u_mps) * s.u_mps;
  const double dv1 = -((p_.y_v*s.v_mps + p_.y_r*s.r_radps) +
                       (p_.y_vv*std::abs(s.v_mps)*s.v_mps + p_.y_vvv*s.v_mps*s.v_mps*s.v_mps));
  const double dv2 = -((p_.n_v*s.v_mps + p_.n_r*s.r_radps) +
                       (p_.n_rr*std::abs(s.r_radps)*s.r_radps + p_.n_rrr*s.r_radps*s.r_radps*s.r_radps));

  double fx = cv0 + dv0 + p_.kp_u * p_.mass_kg * (sp.surge_mps - s.u_mps);
  double yaw_error;
  if (legacy) {
    const double desired = legacy_normalize_angle_diff(sp.yaw_rad, psi);
    yaw_error = desired - psi;
  } else {
    yaw_error = wrap_angle(sp.yaw_rad - psi);
  }
  double fy = (p_.kp_yaw * p_.iz_kgm2 * (yaw_error - p_.kd_yaw*s.r_radps)) / p_.rudder_arm_m;
  fx = std::clamp(fx, p_.fx_min_n, p_.fx_max_n);
  fy = std::clamp(fy, p_.fy_min_n, p_.fy_max_n);
  const double fn = p_.rudder_arm_m * fy;

  return {cy*s.u_mps - sy*s.v_mps,
          sy*s.u_mps + cy*s.v_mps,
          s.r_radps,
          (fx - cv0 - dv0) / p_.mass_kg,
          (fy - cv1 - dv1) / p_.mass_kg,
          (fn - cv2 - dv2) / p_.iz_kgm2};
}
VesselState Viknes830::step_rk4(const VesselState & s, const ControlSetpoint & sp, double dt) const {
  if (!(dt > 0)) throw std::invalid_argument("dt must be positive");
  const auto k1 = derivative(s, sp);
  const auto k2 = derivative(add(s, k1, dt/2.0), sp);
  const auto k3 = derivative(add(s, k2, dt/2.0), sp);
  const auto k4 = derivative(add(s, k3, dt), sp);
  const auto k = combine(k1, k2, k3, k4);
  auto out = add(s, k, dt);
  if (p_.heading_policy == HeadingPolicy::Normalized) out.yaw_rad = wrap_angle(out.yaw_rad);
  return out;
}
}
