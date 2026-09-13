#include "usv_map_core/synthetic_map.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

namespace usv_map_core {

SyntheticMap::SyntheticMap(SyntheticMapConfig config) : config_(config)
{
  if (!std::isfinite(config_.alpha_m) || config_.alpha_m <= 0.0) {
    throw std::invalid_argument("SyntheticMap alpha_m must be finite and greater than zero");
  }
  if (!std::isfinite(config_.default_saturation_m) || config_.default_saturation_m <= 0.0) {
    throw std::invalid_argument(
            "SyntheticMap default_saturation_m must be finite and greater than zero");
  }
}

void SyntheticMap::validate_point(const Point2dM & point)
{
  if (!std::isfinite(point.x_m) || !std::isfinite(point.y_m)) {
    throw std::invalid_argument("SyntheticMap point coordinates must be finite metres");
  }
}

void SyntheticMap::validate_box(const AabbM & box)
{
  if (!box.valid()) {
    throw std::invalid_argument("SyntheticMap box must be finite and ordered");
  }
}

void SyntheticMap::validate_segment(const Segment2dM & segment)
{
  const bool valid = std::isfinite(segment.a.x_m) && std::isfinite(segment.a.y_m) &&
    std::isfinite(segment.b.x_m) && std::isfinite(segment.b.y_m);
  if (!valid) {
    throw std::invalid_argument("SyntheticMap segment coordinates must be finite metres");
  }
}

void SyntheticMap::add_collision_box(const AabbM & box)
{
  validate_box(box);
  collision_boxes_.push_back(box);
}

void SyntheticMap::add_caution_box(const AabbM & box)
{
  validate_box(box);
  caution_boxes_.push_back(box);
}

void SyntheticMap::add_traffic_lane_box(const AabbM & box)
{
  validate_box(box);
  traffic_lane_boxes_.push_back(box);
}

void SyntheticMap::add_traffic_roundabout_box(const AabbM & box)
{
  validate_box(box);
  traffic_roundabout_boxes_.push_back(box);
}

void SyntheticMap::add_voronoi_segment(const Segment2dM & segment)
{
  validate_segment(segment);
  voronoi_segments_.push_back(segment);
}

const std::vector<AabbM> & SyntheticMap::boxes_for(LayerId layer) const
{
  switch (layer) {
    case LayerId::Collision:
      return collision_boxes_;
    case LayerId::Caution:
      return caution_boxes_;
    case LayerId::TrafficLane:
      return traffic_lane_boxes_;
    case LayerId::TrafficRoundabout:
      return traffic_roundabout_boxes_;
    case LayerId::Voronoi:
      throw std::invalid_argument("Voronoi is a line layer, not an area layer");
  }
  throw std::invalid_argument("Unknown map layer");
}

bool SyntheticMap::intersects(const Point2dM & point, LayerId layer) const
{
  validate_point(point);
  const auto & boxes = boxes_for(layer);
  return std::any_of(boxes.begin(), boxes.end(), [&](const AabbM & box) {
    return contains_closed(box, point);
  });
}

double SyntheticMap::distance_m(
  const Point2dM & point, LayerId layer, double saturation_m) const
{
  validate_point(point);
  if (std::isnan(saturation_m) || saturation_m < 0.0) {
    throw std::invalid_argument("saturation_m must be non-negative or infinity");
  }

  double best = std::numeric_limits<double>::infinity();
  if (layer == LayerId::Voronoi) {
    for (const auto & segment : voronoi_segments_) {
      best = std::min(best, point_to_segment_distance_m(point, segment));
    }
  } else {
    const auto & boxes = boxes_for(layer);
    for (const auto & box : boxes) {
      best = std::min(best, point_to_aabb_distance_m(point, box));
    }
  }

  if (std::isfinite(saturation_m)) {
    return std::min(best, saturation_m);
  }
  return best;
}

double SyntheticMap::voronoi_field(const Point2dM & point) const
{
  const double distance_to_land_m =
    distance_m(point, LayerId::Collision, config_.default_saturation_m);
  const double distance_to_voronoi_m =
    distance_m(point, LayerId::Voronoi, config_.default_saturation_m);

  const double sum_distance_m = distance_to_voronoi_m + distance_to_land_m;
  if (sum_distance_m == 0.0) {
    return 0.0;
  }

  const double saturation_sq = config_.default_saturation_m * config_.default_saturation_m;
  const double land_delta_m = distance_to_land_m - config_.default_saturation_m;
  return (config_.alpha_m / (config_.alpha_m + distance_to_land_m)) *
         (distance_to_voronoi_m / sum_distance_m) *
         ((land_delta_m * land_delta_m) / saturation_sq);
}

const SyntheticMapConfig & SyntheticMap::config() const noexcept
{
  return config_;
}

}  // namespace usv_map_core
