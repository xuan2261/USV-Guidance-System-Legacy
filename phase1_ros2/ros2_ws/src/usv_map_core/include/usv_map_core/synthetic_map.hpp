#pragma once

#include "usv_map_core/geometry.hpp"

#include <limits>
#include <vector>

namespace usv_map_core {

struct SyntheticMapConfig {
  double alpha_m{20.0};
  double default_saturation_m{100.0};
};

class SyntheticMap final : public MapQuery {
public:
  explicit SyntheticMap(SyntheticMapConfig config = {});

  void add_collision_box(const AabbM & box);
  void add_caution_box(const AabbM & box);
  void add_traffic_lane_box(const AabbM & box);
  void add_traffic_roundabout_box(const AabbM & box);
  void add_voronoi_segment(const Segment2dM & segment);

  [[nodiscard]] bool intersects(const Point2dM & point, LayerId layer) const override;
  [[nodiscard]] double distance_m(
    const Point2dM & point, LayerId layer,
    double saturation_m = std::numeric_limits<double>::infinity()) const override;
  [[nodiscard]] double voronoi_field(const Point2dM & point) const override;

  [[nodiscard]] const SyntheticMapConfig & config() const noexcept;

private:
  SyntheticMapConfig config_{};
  std::vector<AabbM> collision_boxes_{};
  std::vector<AabbM> caution_boxes_{};
  std::vector<AabbM> traffic_lane_boxes_{};
  std::vector<AabbM> traffic_roundabout_boxes_{};
  std::vector<Segment2dM> voronoi_segments_{};

  [[nodiscard]] const std::vector<AabbM> & boxes_for(LayerId layer) const;
  static void validate_point(const Point2dM & point);
  static void validate_box(const AabbM & box);
  static void validate_segment(const Segment2dM & segment);
};

}  // namespace usv_map_core
