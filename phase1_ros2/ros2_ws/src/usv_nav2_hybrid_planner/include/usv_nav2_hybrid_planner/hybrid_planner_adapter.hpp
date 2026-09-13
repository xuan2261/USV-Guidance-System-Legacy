#pragma once
#include <memory>
#include <string>
#include "nav2_core/global_planner.hpp"
namespace usv_nav2_hybrid_planner {
class HybridPlannerAdapter : public nav2_core::GlobalPlanner {
public:
 void configure(const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent, std::string name, std::shared_ptr<tf2_ros::Buffer> tf, std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) override;
 void cleanup() override; void activate() override; void deactivate() override;
 nav_msgs::msg::Path createPlan(const geometry_msgs::msg::PoseStamped & start, const geometry_msgs::msg::PoseStamped & goal, std::function<bool()> cancel_checker) override;
private:
 rclcpp_lifecycle::LifecycleNode::WeakPtr parent_; std::string name_; std::shared_ptr<tf2_ros::Buffer> tf_; std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros_;
};
}
