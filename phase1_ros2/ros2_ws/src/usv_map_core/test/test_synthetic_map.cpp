#include <gtest/gtest.h>

#include "usv_map_core/synthetic_map.hpp"

#include <cmath>
#include <stdexcept>

namespace {
using usv_map_core::AabbM;
using usv_map_core::LayerId;
using usv_map_core::Point2dM;
using usv_map_core::Segment2dM;
using usv_map_core::SyntheticMap;
using usv_map_core::SyntheticMapConfig;

TEST(SyntheticMapMetric, CollisionAndCautionQueriesAreDeterministic)
{
  SyntheticMap map;
  map.add_collision_box(AabbM{10.0, 10.0, 20.0, 20.0});
  map.add_caution_box(AabbM{30.0, 30.0, 40.0, 40.0});
  EXPECT_TRUE(map.intersects(Point2dM{15.0, 15.0}, LayerId::Collision));
  EXPECT_FALSE(map.intersects(Point2dM{25.0, 25.0}, LayerId::Collision));
  EXPECT_TRUE(map.intersects(Point2dM{35.0, 35.0}, LayerId::Caution));
  EXPECT_THROW(map.intersects(Point2dM{0.0, 0.0}, LayerId::Voronoi), std::invalid_argument);
}

TEST(SyntheticMapMetric, DistanceSaturatesLikeLegacyMapService)
{
  SyntheticMap map;
  map.add_collision_box(AabbM{10.0, 10.0, 20.0, 20.0});
  EXPECT_DOUBLE_EQ(map.distance_m(Point2dM{25.0, 15.0}, LayerId::Collision, 20.0), 5.0);
  EXPECT_DOUBLE_EQ(map.distance_m(Point2dM{100.0, 100.0}, LayerId::Collision, 20.0), 20.0);
  SyntheticMap empty;
  EXPECT_TRUE(std::isinf(empty.distance_m(Point2dM{0.0, 0.0}, LayerId::Collision)));
  EXPECT_DOUBLE_EQ(empty.distance_m(Point2dM{0.0, 0.0}, LayerId::Collision, 12.0), 12.0);
}

TEST(SyntheticMapMetric, VoronoiFieldPreservesPinnedLegacyFormulaInMetres)
{
  const SyntheticMapConfig config{10.0, 20.0};
  SyntheticMap map(config);
  map.add_collision_box(AabbM{10.0, 10.0, 20.0, 20.0});
  map.add_voronoi_segment(Segment2dM{{0.0, 25.0}, {100.0, 25.0}});
  const double d_land_m = 2.0;
  const double d_voronoi_m = 3.0;
  const double expected =
    (config.alpha_m / (config.alpha_m + d_land_m)) *
    (d_voronoi_m / (d_voronoi_m + d_land_m)) *
    (((d_land_m - config.default_saturation_m) * (d_land_m - config.default_saturation_m)) /
     (config.default_saturation_m * config.default_saturation_m));
  EXPECT_NEAR(map.voronoi_field(Point2dM{20.0, 22.0}), expected, 1e-12);
}

TEST(SyntheticMapMetric, InvalidConfigurationAndNegativeSaturationFailClosed)
{
  EXPECT_THROW(SyntheticMap(SyntheticMapConfig{0.0, 20.0}), std::invalid_argument);
  EXPECT_THROW(SyntheticMap(SyntheticMapConfig{10.0, 0.0}), std::invalid_argument);
  SyntheticMap map;
  EXPECT_THROW(map.distance_m(Point2dM{}, LayerId::Collision, -1.0), std::invalid_argument);
}
}  // namespace
