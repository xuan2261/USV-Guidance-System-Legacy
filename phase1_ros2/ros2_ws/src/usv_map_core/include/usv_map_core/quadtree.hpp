#pragma once

#include "usv_map_core/geometry.hpp"

#include <cstddef>
#include <cstdint>
#include <memory>
#include <vector>

namespace usv_map_core {

class Quadtree {
public:
  using ItemId = std::uint64_t;

  Quadtree(AabbM bounds, std::size_t bucket_capacity = 4, std::size_t max_depth = 8);
  ~Quadtree();

  Quadtree(const Quadtree &) = delete;
  Quadtree & operator=(const Quadtree &) = delete;
  Quadtree(Quadtree &&) noexcept;
  Quadtree & operator=(Quadtree &&) noexcept;

  [[nodiscard]] bool insert(ItemId id, const AabbM & bounds);
  [[nodiscard]] std::vector<ItemId> query_point(const Point2dM & point) const;
  [[nodiscard]] std::vector<ItemId> query_range(const AabbM & bounds) const;
  [[nodiscard]] std::size_t size() const noexcept;

private:
  struct Item;
  struct Node;

  AabbM bounds_{};
  std::size_t bucket_capacity_{4};
  std::size_t max_depth_{8};
  std::size_t size_{0};
  std::unique_ptr<Node> root_;

  void insert_into(Node & node, Item item);
  void split(Node & node);
  [[nodiscard]] int exclusive_child_index(const Node & node, const AabbM & bounds) const noexcept;
  [[nodiscard]] int point_child_index(const Node & node, const Point2dM & point) const noexcept;
  void query_point_node(const Node & node, const Point2dM & point, std::vector<ItemId> & out) const;
  void query_range_node(const Node & node, const AabbM & bounds, std::vector<ItemId> & out) const;
};

}  // namespace usv_map_core
