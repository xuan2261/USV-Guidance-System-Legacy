#include <cstdlib>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <string>
#include "usv_model_core/viknes830.hpp"
using namespace usv_model_core;
int main(int argc,char**argv){
  if(argc!=11){std::cerr<<"usage: runner duration dt x y yaw u v r surge yaw_setpoint\n";return 2;}
  const double duration=std::stod(argv[1]),dt=std::stod(argv[2]);
  VesselState s{std::stod(argv[3]),std::stod(argv[4]),std::stod(argv[5]),std::stod(argv[6]),std::stod(argv[7]),std::stod(argv[8])};
  ControlSetpoint cmd{std::stod(argv[9]),std::stod(argv[10])};
  Viknes830 m;
  std::cout<<std::setprecision(17)<<"t,x,y,yaw,u,v,r\n";
  auto emit=[&](double t){std::cout<<t<<','<<s.x_m<<','<<s.y_m<<','<<s.yaw_rad<<','<<s.u_mps<<','<<s.v_mps<<','<<s.r_radps<<'\n';};
  emit(0.0); const int n=static_cast<int>(std::llround(duration/dt));
  for(int i=0;i<n;++i){s=m.step_rk4(s,cmd,dt);emit((i+1)*dt);} return 0;
}
