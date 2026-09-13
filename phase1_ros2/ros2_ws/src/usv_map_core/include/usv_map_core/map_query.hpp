#pragma once
#include <limits>
namespace usv_map_core {
struct Point2dM { double x_m{0}; double y_m{0}; };
enum class LayerId { Collision, Caution, Voronoi, TrafficLane, TrafficRoundabout };
class MapQuery {
public:
 virtual ~MapQuery()=default;
 virtual bool intersects(const Point2dM & point, LayerId layer) const=0;
 virtual double distance_m(const Point2dM & point, LayerId layer, double saturation_m=std::numeric_limits<double>::infinity()) const=0;
 virtual double voronoi_field(const Point2dM & point) const=0;
};
}
