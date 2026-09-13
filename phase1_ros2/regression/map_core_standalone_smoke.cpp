#include "usv_map_core/geometry.hpp"
#include "usv_map_core/quadtree.hpp"
#include "usv_map_core/synthetic_map.hpp"

#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>

namespace {
void require(bool condition, const char * message)
{
  if (!condition) {
    throw std::runtime_error(message);
  }
}
}  // namespace

int main()
{
  using namespace usv_map_core;

  const AabbM box{0.0, 0.0, 10.0, 10.0};
  require(contains_closed(box, Point2dM{10.0, 10.0}), "closed AABB boundary failed");
  require(std::abs(point_to_aabb_distance_m(Point2dM{13.0, 14.0}, box) - 5.0) < 1e-12,
          "AABB metric distance failed");
  require(std::abs(point_to_segment_distance_m(Point2dM{5.0, 3.0}, Segment2dM{{0.0, 0.0}, {10.0, 0.0}}) - 3.0) < 1e-12,
          "segment metric distance failed");

  Quadtree tree(AabbM{0.0, 0.0, 100.0, 100.0}, 1, 6);
  require(tree.insert(10, AabbM{10.0, 10.0, 20.0, 20.0}), "quadtree insert 10 failed");
  require(tree.insert(20, AabbM{80.0, 80.0, 90.0, 90.0}), "quadtree insert 20 failed");
  require(tree.insert(30, AabbM{40.0, 40.0, 60.0, 60.0}), "quadtree straddle insert failed");
  for (int i = 0; i < 1000; ++i) {
    require(tree.query_point(Point2dM{50.0, 50.0}) == std::vector<Quadtree::ItemId>({30}),
            "quadtree split-boundary regression failed");
  }
  require(tree.query_point(Point2dM{-1.0, 50.0}).empty(), "quadtree outside query failed closed");

  const SyntheticMapConfig config{10.0, 20.0};
  SyntheticMap map(config);
  map.add_collision_box(AabbM{10.0, 10.0, 20.0, 20.0});
  map.add_voronoi_segment(Segment2dM{{0.0, 25.0}, {100.0, 25.0}});
  require(map.intersects(Point2dM{15.0, 15.0}, LayerId::Collision), "collision query failed");
  require(map.distance_m(Point2dM{100.0, 100.0}, LayerId::Collision, 20.0) == 20.0,
          "distance saturation failed");
  bool invalid_point_rejected = false;
  try {
    (void)map.intersects(Point2dM{std::numeric_limits<double>::quiet_NaN(), 0.0}, LayerId::Collision);
  } catch (const std::invalid_argument &) {
    invalid_point_rejected = true;
  }
  require(invalid_point_rejected, "invalid point must fail fast");

  const double d_land_m = 2.0;
  const double d_voronoi_m = 3.0;
  const double expected =
    (config.alpha_m / (config.alpha_m + d_land_m)) *
    (d_voronoi_m / (d_voronoi_m + d_land_m)) *
    (((d_land_m - config.default_saturation_m) * (d_land_m - config.default_saturation_m)) /
     (config.default_saturation_m * config.default_saturation_m));
  require(std::abs(map.voronoi_field(Point2dM{20.0, 22.0}) - expected) < 1e-12,
          "legacy Voronoi formula regression failed");

  std::cout << "PASS: standalone metric map-core smoke + boundary regression\n";
  return 0;
}
