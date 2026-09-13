#include "usv_map_core/quadtree.hpp"

#include <algorithm>
#include <array>
#include <stdexcept>
#include <utility>

namespace usv_map_core {

struct Quadtree::Item {
  ItemId id{0};
  AabbM bounds{};
};

struct Quadtree::Node {
  AabbM bounds{};
  std::size_t depth{0};
  std::vector<Item> items{};
  std::array<std::unique_ptr<Node>, 4> children{};  // SW, SE, NW, NE

  [[nodiscard]] bool has_children() const noexcept {
    return static_cast<bool>(children[0]);
  }
};

Quadtree::Quadtree(AabbM bounds, std::size_t bucket_capacity, std::size_t max_depth)
: bounds_(bounds), bucket_capacity_(bucket_capacity), max_depth_(max_depth)
{
  if (!bounds_.valid()) {
    throw std::invalid_argument("Quadtree bounds must be finite and ordered");
  }
  if (bounds_.min_x_m == bounds_.max_x_m || bounds_.min_y_m == bounds_.max_y_m) {
    throw std::invalid_argument("Quadtree bounds must have non-zero area");
  }
  if (bucket_capacity_ == 0) {
    throw std::invalid_argument("Quadtree bucket_capacity must be greater than zero");
  }
  root_ = std::make_unique<Node>();
  root_->bounds = bounds_;
}

Quadtree::~Quadtree() = default;
Quadtree::Quadtree(Quadtree &&) noexcept = default;
Quadtree & Quadtree::operator=(Quadtree &&) noexcept = default;

bool Quadtree::insert(ItemId id, const AabbM & bounds)
{
  if (!bounds.valid() || !contains_closed(bounds_, bounds)) {
    return false;
  }
  insert_into(*root_, Item{id, bounds});
  ++size_;
  return true;
}

void Quadtree::insert_into(Node & node, Item item)
{
  if (node.has_children()) {
    const int child_index = exclusive_child_index(node, item.bounds);
    if (child_index >= 0) {
      insert_into(*node.children[static_cast<std::size_t>(child_index)], std::move(item));
      return;
    }
    node.items.push_back(std::move(item));
    return;
  }

  if (node.items.size() >= bucket_capacity_ && node.depth < max_depth_) {
    split(node);
    const int child_index = exclusive_child_index(node, item.bounds);
    if (child_index >= 0) {
      insert_into(*node.children[static_cast<std::size_t>(child_index)], std::move(item));
      return;
    }
  }
  node.items.push_back(std::move(item));
}

void Quadtree::split(Node & node)
{
  const double mid_x = (node.bounds.min_x_m + node.bounds.max_x_m) * 0.5;
  const double mid_y = (node.bounds.min_y_m + node.bounds.max_y_m) * 0.5;
  const std::array<AabbM, 4> child_bounds{{
    {node.bounds.min_x_m, node.bounds.min_y_m, mid_x, mid_y},
    {mid_x, node.bounds.min_y_m, node.bounds.max_x_m, mid_y},
    {node.bounds.min_x_m, mid_y, mid_x, node.bounds.max_y_m},
    {mid_x, mid_y, node.bounds.max_x_m, node.bounds.max_y_m}}};

  for (std::size_t i = 0; i < child_bounds.size(); ++i) {
    node.children[i] = std::make_unique<Node>();
    node.children[i]->bounds = child_bounds[i];
    node.children[i]->depth = node.depth + 1;
  }

  std::vector<Item> retained;
  retained.reserve(node.items.size());
  for (auto & item : node.items) {
    const int child_index = exclusive_child_index(node, item.bounds);
    if (child_index >= 0) {
      insert_into(*node.children[static_cast<std::size_t>(child_index)], std::move(item));
    } else {
      retained.push_back(std::move(item));
    }
  }
  node.items = std::move(retained);
}

int Quadtree::exclusive_child_index(const Node & node, const AabbM & bounds) const noexcept
{
  const double mid_x = (node.bounds.min_x_m + node.bounds.max_x_m) * 0.5;
  const double mid_y = (node.bounds.min_y_m + node.bounds.max_y_m) * 0.5;

  const bool west = bounds.max_x_m < mid_x;
  const bool east = bounds.min_x_m > mid_x;
  const bool south = bounds.max_y_m < mid_y;
  const bool north = bounds.min_y_m > mid_y;

  if ((!west && !east) || (!south && !north)) {
    return -1;
  }
  if (south) {
    return west ? 0 : 1;
  }
  return west ? 2 : 3;
}

int Quadtree::point_child_index(const Node & node, const Point2dM & point) const noexcept
{
  const double mid_x = (node.bounds.min_x_m + node.bounds.max_x_m) * 0.5;
  const double mid_y = (node.bounds.min_y_m + node.bounds.max_y_m) * 0.5;
  const bool west = point.x_m <= mid_x;
  const bool south = point.y_m <= mid_y;
  if (south) {
    return west ? 0 : 1;
  }
  return west ? 2 : 3;
}

std::vector<Quadtree::ItemId> Quadtree::query_point(const Point2dM & point) const
{
  std::vector<ItemId> out;
  if (!contains_closed(bounds_, point)) {
    return out;
  }
  query_point_node(*root_, point, out);
  std::sort(out.begin(), out.end());
  out.erase(std::unique(out.begin(), out.end()), out.end());
  return out;
}

void Quadtree::query_point_node(
  const Node & node, const Point2dM & point, std::vector<ItemId> & out) const
{
  for (const auto & item : node.items) {
    if (contains_closed(item.bounds, point)) {
      out.push_back(item.id);
    }
  }
  if (!node.has_children()) {
    return;
  }
  const int child_index = point_child_index(node, point);
  query_point_node(*node.children[static_cast<std::size_t>(child_index)], point, out);
}

std::vector<Quadtree::ItemId> Quadtree::query_range(const AabbM & bounds) const
{
  std::vector<ItemId> out;
  if (!bounds.valid() || !intersects_closed(bounds_, bounds)) {
    return out;
  }
  query_range_node(*root_, bounds, out);
  std::sort(out.begin(), out.end());
  out.erase(std::unique(out.begin(), out.end()), out.end());
  return out;
}

void Quadtree::query_range_node(
  const Node & node, const AabbM & bounds, std::vector<ItemId> & out) const
{
  if (!intersects_closed(node.bounds, bounds)) {
    return;
  }
  for (const auto & item : node.items) {
    if (intersects_closed(item.bounds, bounds)) {
      out.push_back(item.id);
    }
  }
  if (!node.has_children()) {
    return;
  }
  for (const auto & child : node.children) {
    query_range_node(*child, bounds, out);
  }
}

std::size_t Quadtree::size() const noexcept
{
  return size_;
}

}  // namespace usv_map_core
