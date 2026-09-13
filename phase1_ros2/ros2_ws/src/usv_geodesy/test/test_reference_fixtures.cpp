#include <gtest/gtest.h>
#include "usv_geodesy/local_enu.hpp"
using namespace usv_geodesy;
namespace {
void check(const LocalEnu& f,const GeoPoint& p,double e,double n,double u){
  const auto q=f.forward(p); EXPECT_NEAR(q.east_m,e,0.02); EXPECT_NEAR(q.north_m,n,0.02); EXPECT_NEAR(q.up_m,u,0.02);
  const auto r=f.reverse(q); EXPECT_NEAR(r.latitude_deg,p.latitude_deg,1e-9); EXPECT_NEAR(r.longitude_deg,p.longitude_deg,1e-9); EXPECT_NEAR(r.altitude_m,p.altitude_m,1e-5);
}
}
TEST(LocalEnuReference, IndependentWgs84Fixtures){
  LocalEnu f(GeoPoint{40.504594,-73.991544,0.0});
  check(f,{40.504594,-73.991544,0.0},0.0,0.0,0.0);
  check(f,{40.505,-73.990,5.0},130.8718117337646,45.08518631062355,4.998499490336918);
  check(f,{40.504594,-73.990544,0.0},84.76198082711839,0.00048043429718899077,-0.0005624249669687516);
  check(f,{40.505594,-73.991544,0.0},0.0,111.04435439623657,-0.0009690431894620327);
  check(f,{40.641538,-73.844579,0.0},12431.660450374324,15217.378686975018,-30.296311454778905);
}
