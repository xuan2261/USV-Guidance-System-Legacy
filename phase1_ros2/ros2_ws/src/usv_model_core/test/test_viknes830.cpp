#include <gtest/gtest.h>
#include <cmath>
#include "usv_model_core/viknes830.hpp"
using namespace usv_model_core;
namespace { constexpr double kPi = 3.14159265358979323846; }
TEST(Viknes830, ZeroStateEquilibrium){Viknes830 m; VesselState s; ControlSetpoint u; auto d=m.derivative(s,u); EXPECT_DOUBLE_EQ(d.x_mps,0); EXPECT_DOUBLE_EQ(d.u_mps2,0); EXPECT_DOUBLE_EQ(d.r_radps2,0);}
TEST(Viknes830, PositiveSurgeSetpointAccelerates){Viknes830 m; VesselState s; ControlSetpoint u; u.surge_mps=2; auto d=m.derivative(s,u); EXPECT_GT(d.u_mps2,0);}
TEST(Viknes830, NormalizedWrapBounded){EXPECT_LE(std::abs(Viknes830::wrap_angle(7.0)),kPi);}
TEST(Viknes830, Rk4Finite){Viknes830 m; VesselState s; ControlSetpoint u{2.0,0.2}; auto n=m.step_rk4(s,u,0.05); EXPECT_TRUE(std::isfinite(n.x_m)); EXPECT_TRUE(std::isfinite(n.u_mps));}
TEST(Viknes830, LegacyPiBoundaryTurnsPositive){Viknes830 m; VesselState s; s.yaw_rad=kPi; s.u_mps=1.0; ControlSetpoint u{1.0,0.0}; auto d=m.derivative(s,u); EXPECT_GT(d.r_radps2,0.0);}
TEST(Viknes830, NormalizedPiBoundaryIsExplicitlyDifferent){Viknes830::Parameters p; p.heading_policy=HeadingPolicy::Normalized; Viknes830 m(p); VesselState s; s.yaw_rad=kPi; s.u_mps=1.0; ControlSetpoint u{1.0,0.0}; auto d=m.derivative(s,u); EXPECT_LT(d.r_radps2,0.0);}
