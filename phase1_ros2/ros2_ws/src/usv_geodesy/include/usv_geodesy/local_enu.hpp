#pragma once
#include <GeographicLib/LocalCartesian.hpp>
namespace usv_geodesy {
struct GeoPoint { double latitude_deg{0}; double longitude_deg{0}; double altitude_m{0}; };
struct EnuPoint { double east_m{0}; double north_m{0}; double up_m{0}; };
class LocalEnu {
public: explicit LocalEnu(const GeoPoint & origin); EnuPoint forward(const GeoPoint & p) const; GeoPoint reverse(const EnuPoint & p) const; GeoPoint origin() const {return origin_;}
private: GeoPoint origin_; GeographicLib::LocalCartesian frame_;
};
}
