cmake_minimum_required(VERSION 3.16)
project(usv_map_core LANGUAGES CXX)

find_package(ament_cmake REQUIRED)

add_library(${PROJECT_NAME}
  src/quadtree.cpp
  src/synthetic_map.cpp)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)
target_include_directories(${PROJECT_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)

install(TARGETS ${PROJECT_NAME} EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)
install(DIRECTORY include/ DESTINATION include)
ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_include_directories(include)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)

  ament_add_gtest(test_geometry test/test_geometry.cpp)
  target_link_libraries(test_geometry ${PROJECT_NAME})

  ament_add_gtest(test_quadtree test/test_quadtree.cpp)
  target_link_libraries(test_quadtree ${PROJECT_NAME})

  ament_add_gtest(test_synthetic_map test/test_synthetic_map.cpp)
  target_link_libraries(test_synthetic_map ${PROJECT_NAME})
endif()

ament_package()
