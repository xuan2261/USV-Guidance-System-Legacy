#include <gtest/gtest.h>

#include "usv_map_core/geometry.hpp"

namespace {
using usv_map_core::AabbM;
using usv_map_core::Point2dM;
using usv_map_core::Segment2dM;

TEST(GeometryMetric, ClosedAabbContainsBoundaries)
{
  const AabbM box{0.0, 0.0, 10.0, 10.0};
  EXPECT_TRUE(usv_map_core::contains_closed(box, Point2dM{0.0, 0.0}));
  EXPECT_TRUE(usv_map_core::contains_closed(box, Point2dM{10.0, 10.0}));
  EXPECT_FALSE(usv_map_core::contains_closed(box, Point2dM{10.001, 10.0}));
}

TEST(GeometryMetric, PointToAabbDistanceUsesMetres)
{
  const AabbM box{0.0, 0.0, 10.0, 10.0};
  EXPECT_DOUBLE_EQ(usv_map_core::point_to_aabb_distance_m(Point2dM{5.0, 5.0}, box), 0.0);
  EXPECT_DOUBLE_EQ(usv_map_core::point_to_aabb_distance_m(Point2dM{15.0, 5.0}, box), 5.0);
  EXPECT_NEAR(usv_map_core::point_to_aabb_distance_m(Point2dM{13.0, 14.0}, box), 5.0, 1e-12);
}

TEST(GeometryMetric, SegmentDistanceHandlesProjectionAndDegenerateSegment)
{
  const Segment2dM horizontal{{0.0, 0.0}, {10.0, 0.0}};
  EXPECT_DOUBLE_EQ(usv_map_core::point_to_segment_distance_m(Point2dM{5.0, 3.0}, horizontal), 3.0);
  const Segment2dM point_segment{{2.0, 2.0}, {2.0, 2.0}};
  EXPECT_DOUBLE_EQ(usv_map_core::point_to_segment_distance_m(Point2dM{5.0, 6.0}, point_segment), 5.0);
}
}  // namespace
