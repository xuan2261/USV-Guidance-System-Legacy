#include <gtest/gtest.h>
#include <array>
#include <cmath>
#include <string>
#include "usv_model_core/viknes830.hpp"

using usv_model_core::ControlSetpoint;
using usv_model_core::VesselState;
using usv_model_core::Viknes830;

namespace {
constexpr double kDt = 0.1;
constexpr double kTol = 1e-9;
struct Fixture {
  const char * id;
  double duration;
  VesselState initial;
  ControlSetpoint command;
  VesselState expected;
};
const std::array<Fixture, 6> kFixtures{{
  {"zero_equilibrium",2.0,{0,0,0,0,0,0},{0,0},{0,0,0,0,0,0}},
  {"surge_step",20.0,{0,0,0,0,0,0},{2,0},{38.00000000412237,0,0,1.9999999958776182,0,0}},
  {"yaw_step",20.0,{0,0,0,1,0,0},{1,0.5},{19.041654671216826,6.5353591745973603,0.49999999997529165,1,-0.054544134154237367,3.1902690943073337e-11}},
  {"combined_state",20.0,{0,0,0.2,1,0.1,0.02},{2,1},{26.892782214326868,27.94505780713682,0.99999999997796074,1.999999997938809,-0.070064308265726349,2.8456338190571082e-11}},
  {"wrap_179_to_minus179",10.0,{0,0,3.12413936106985,1,0,0},{1,-3.12413936106985},{-10.001965703434641,0.028224819628330618,3.1590458154185326,1,-0.017657273057461356,1.6874435631790919e-07}},
  {"exact_pi_boundary",2.0,{0,0,3.141592653589793,1,0,0},{1,0},{-1.9741846180482985,-0.31095980713542931,3.3767025858069069,1,0.07490691439032178,0.22242099189785502}}
}};
VesselState integrate(const Fixture & f) {
  Viknes830 model;
  VesselState s = f.initial;
  const int n = static_cast<int>(std::llround(f.duration / kDt));
  for (int i=0; i<n; ++i) s = model.step_rk4(s, f.command, kDt);
  return s;
}
void expect_state(const VesselState & a, const VesselState & b) {
  EXPECT_NEAR(a.x_m,b.x_m,kTol); EXPECT_NEAR(a.y_m,b.y_m,kTol);
  EXPECT_NEAR(a.yaw_rad,b.yaw_rad,kTol); EXPECT_NEAR(a.u_mps,b.u_mps,kTol);
  EXPECT_NEAR(a.v_mps,b.v_mps,kTol); EXPECT_NEAR(a.r_radps,b.r_radps,kTol);
}
}
TEST(Viknes830LegacyFixtures, PinnedLegacyFinalStates) {
  for (const auto & f : kFixtures) {
    SCOPED_TRACE(f.id);
    expect_state(integrate(f), f.expected);
  }
}
