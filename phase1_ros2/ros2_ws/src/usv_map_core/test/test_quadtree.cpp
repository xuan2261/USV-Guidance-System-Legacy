#include <gtest/gtest.h>

#include "usv_map_core/quadtree.hpp"

#include <vector>

namespace {
using usv_map_core::AabbM;
using usv_map_core::Point2dM;
using usv_map_core::Quadtree;

TEST(QuadtreeMetric, RejectsInvalidOrOutsideItems)
{
  Quadtree tree(AabbM{0.0, 0.0, 100.0, 100.0}, 1, 6);
  EXPECT_FALSE(tree.insert(1, AabbM{-1.0, 0.0, 1.0, 1.0}));
  EXPECT_FALSE(tree.insert(2, AabbM{2.0, 2.0, 1.0, 3.0}));
  EXPECT_EQ(tree.size(), 0U);
}

TEST(QuadtreeMetric, BoundaryAndStraddleQueriesNeverLoseItems)
{
  Quadtree tree(AabbM{0.0, 0.0, 100.0, 100.0}, 1, 6);
  ASSERT_TRUE(tree.insert(10, AabbM{10.0, 10.0, 20.0, 20.0}));
  ASSERT_TRUE(tree.insert(20, AabbM{80.0, 80.0, 90.0, 90.0}));
  ASSERT_TRUE(tree.insert(30, AabbM{40.0, 40.0, 60.0, 60.0}));
  ASSERT_TRUE(tree.insert(40, AabbM{50.0, 5.0, 50.0, 15.0}));

  EXPECT_EQ(tree.query_point(Point2dM{15.0, 15.0}), std::vector<Quadtree::ItemId>({10}));
  EXPECT_EQ(tree.query_point(Point2dM{50.0, 50.0}), std::vector<Quadtree::ItemId>({30}));
  EXPECT_EQ(tree.query_point(Point2dM{50.0, 10.0}), std::vector<Quadtree::ItemId>({40}));
  EXPECT_TRUE(tree.query_point(Point2dM{-0.001, 50.0}).empty());

  for (int i = 0; i < 100; ++i) {
    EXPECT_EQ(tree.query_point(Point2dM{50.0, 50.0}), std::vector<Quadtree::ItemId>({30}));
  }
}

TEST(QuadtreeMetric, RangeQueryIsSortedUniqueAndClosedOnBoundaries)
{
  Quadtree tree(AabbM{0.0, 0.0, 100.0, 100.0}, 1, 6);
  ASSERT_TRUE(tree.insert(9, AabbM{0.0, 0.0, 10.0, 10.0}));
  ASSERT_TRUE(tree.insert(2, AabbM{10.0, 10.0, 20.0, 20.0}));
  ASSERT_TRUE(tree.insert(7, AabbM{70.0, 70.0, 80.0, 80.0}));
  EXPECT_EQ(tree.query_range(AabbM{10.0, 10.0, 10.0, 10.0}), std::vector<Quadtree::ItemId>({2, 9}));
}
}  // namespace
