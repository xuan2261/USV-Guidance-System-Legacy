#include "usv_geodesy/local_enu.hpp"
namespace usv_geodesy {
LocalEnu::LocalEnu(const GeoPoint&o):origin_(o),frame_(o.latitude_deg,o.longitude_deg,o.altitude_m){}
EnuPoint LocalEnu::forward(const GeoPoint&p) const {EnuPoint e; frame_.Forward(p.latitude_deg,p.longitude_deg,p.altitude_m,e.east_m,e.north_m,e.up_m); return e;}
GeoPoint LocalEnu::reverse(const EnuPoint&p) const {GeoPoint g; frame_.Reverse(p.east_m,p.north_m,p.up_m,g.latitude_deg,g.longitude_deg,g.altitude_m); return g;}
}
