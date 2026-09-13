#include <gtest/gtest.h>
#include <cmath>
#include "usv_geodesy/local_enu.hpp"
using namespace usv_geodesy;
TEST(LocalEnu, OriginIsZero){GeoPoint o{40.504594,-73.991544,0}; LocalEnu f(o); auto e=f.forward(o); EXPECT_NEAR(e.east_m,0,1e-6); EXPECT_NEAR(e.north_m,0,1e-6);}
TEST(LocalEnu, RoundTrip){GeoPoint o{40.504594,-73.991544,0}, p{40.505,-73.990,5}; LocalEnu f(o); auto q=f.reverse(f.forward(p)); EXPECT_NEAR(q.latitude_deg,p.latitude_deg,1e-9); EXPECT_NEAR(q.longitude_deg,p.longitude_deg,1e-9); EXPECT_NEAR(q.altitude_m,p.altitude_m,1e-5);}
