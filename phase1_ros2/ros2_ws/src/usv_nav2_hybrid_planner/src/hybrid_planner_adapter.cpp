#include "usv_nav2_hybrid_planner/hybrid_planner_adapter.hpp"
#include "nav2_core/planner_exceptions.hpp"
#include "pluginlib/class_list_macros.hpp"
namespace usv_nav2_hybrid_planner {
void HybridPlannerAdapter::configure(const rclcpp_lifecycle::LifecycleNode::WeakPtr &p,std::string n,std::shared_ptr<tf2_ros::Buffer> tf,std::shared_ptr<nav2_costmap_2d::Costmap2DROS> cm){parent_=p;name_=std::move(n);tf_=std::move(tf);costmap_ros_=std::move(cm);}
void HybridPlannerAdapter::cleanup(){tf_.reset();costmap_ros_.reset();}
void HybridPlannerAdapter::activate(){}
void HybridPlannerAdapter::deactivate(){}
nav_msgs::msg::Path HybridPlannerAdapter::createPlan(const geometry_msgs::msg::PoseStamped &,const geometry_msgs::msg::PoseStamped &,std::function<bool()> cancel_checker){if(cancel_checker&&cancel_checker()) throw nav2_core::PlannerCancelled("USV Hybrid A* planning cancelled"); throw nav2_core::PlannerException("USV Hybrid A* core is not connected in the v0.4 scaffold; Q10 and algorithm regression port are required first.");}
}
PLUGINLIB_EXPORT_CLASS(usv_nav2_hybrid_planner::HybridPlannerAdapter, nav2_core::GlobalPlanner)
