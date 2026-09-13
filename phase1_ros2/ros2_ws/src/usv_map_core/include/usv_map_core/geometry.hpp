#pragma once

#include "usv_map_core/map_query.hpp"

#include <algorithm>
#include <cmath>
#include <limits>

namespace usv_map_core {

struct AabbM {
  double min_x_m{0.0};
  double min_y_m{0.0};
  double max_x_m{0.0};
  double max_y_m{0.0};

  [[nodiscard]] bool valid() const noexcept {
    return std::isfinite(min_x_m) && std::isfinite(min_y_m) &&
           std::isfinite(max_x_m) && std::isfinite(max_y_m) &&
           min_x_m <= max_x_m && min_y_m <= max_y_m;
  }
};

struct Segment2dM {
  Point2dM a{};
  Point2dM b{};
};

[[nodiscard]] inline bool contains_closed(const AabbM & box, const Point2dM & point) noexcept {
  return box.valid() && std::isfinite(point.x_m) && std::isfinite(point.y_m) &&
         point.x_m >= box.min_x_m && point.x_m <= box.max_x_m &&
         point.y_m >= box.min_y_m && point.y_m <= box.max_y_m;
}

[[nodiscard]] inline bool contains_closed(const AabbM & outer, const AabbM & inner) noexcept {
  return outer.valid() && inner.valid() &&
         inner.min_x_m >= outer.min_x_m && inner.max_x_m <= outer.max_x_m &&
         inner.min_y_m >= outer.min_y_m && inner.max_y_m <= outer.max_y_m;
}

[[nodiscard]] inline bool intersects_closed(const AabbM & lhs, const AabbM & rhs) noexcept {
  if (!lhs.valid() || !rhs.valid()) {
    return false;
  }
  return !(lhs.max_x_m < rhs.min_x_m || rhs.max_x_m < lhs.min_x_m ||
           lhs.max_y_m < rhs.min_y_m || rhs.max_y_m < lhs.min_y_m);
}

[[nodiscard]] inline double point_to_aabb_distance_m(const Point2dM & point, const AabbM & box) noexcept {
  if (!box.valid() || !std::isfinite(point.x_m) || !std::isfinite(point.y_m)) {
    return std::numeric_limits<double>::infinity();
  }
  const double dx = std::max({box.min_x_m - point.x_m, 0.0, point.x_m - box.max_x_m});
  const double dy = std::max({box.min_y_m - point.y_m, 0.0, point.y_m - box.max_y_m});
  return std::hypot(dx, dy);
}

[[nodiscard]] inline double point_to_segment_distance_m(
  const Point2dM & point, const Segment2dM & segment) noexcept
{
  if (!std::isfinite(point.x_m) || !std::isfinite(point.y_m) ||
      !std::isfinite(segment.a.x_m) || !std::isfinite(segment.a.y_m) ||
      !std::isfinite(segment.b.x_m) || !std::isfinite(segment.b.y_m)) {
    return std::numeric_limits<double>::infinity();
  }

  const double vx = segment.b.x_m - segment.a.x_m;
  const double vy = segment.b.y_m - segment.a.y_m;
  const double length_sq = vx * vx + vy * vy;
  if (length_sq == 0.0) {
    return std::hypot(point.x_m - segment.a.x_m, point.y_m - segment.a.y_m);
  }

  const double wx = point.x_m - segment.a.x_m;
  const double wy = point.y_m - segment.a.y_m;
  const double t = std::clamp((wx * vx + wy * vy) / length_sq, 0.0, 1.0);
  const double projected_x = segment.a.x_m + t * vx;
  const double projected_y = segment.a.y_m + t * vy;
  return std::hypot(point.x_m - projected_x, point.y_m - projected_y);
}

}  // namespace usv_map_core
