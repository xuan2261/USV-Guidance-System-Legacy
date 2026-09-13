#pragma once
namespace usv_model_core {
struct VesselState {
  double x_m{0.0};
  double y_m{0.0};
  double yaw_rad{0.0};
  double u_mps{0.0};
  double v_mps{0.0};
  double r_radps{0.0};
};
struct ControlSetpoint {
  double surge_mps{0.0};
  double yaw_rad{0.0};
};
struct StateDerivative {
  double x_mps{0.0};
  double y_mps{0.0};
  double yaw_radps{0.0};
  double u_mps2{0.0};
  double v_mps2{0.0};
  double r_radps2{0.0};
};
}
