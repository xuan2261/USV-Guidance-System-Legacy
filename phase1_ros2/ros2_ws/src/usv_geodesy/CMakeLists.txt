cmake_minimum_required(VERSION 3.16)
project(usv_geodesy LANGUAGES CXX)

find_package(ament_cmake REQUIRED)

# Prefer an upstream GeographicLib config package, but support the Debian/Ubuntu
# layout used on Ubuntu 24.04 where FindGeographicLib.cmake is installed under
# /usr/share/cmake/geographiclib and is not in CMake's default module path.
find_package(GeographicLib CONFIG QUIET)
if(NOT GeographicLib_FOUND)
  if(EXISTS "/usr/share/cmake/geographiclib/FindGeographicLib.cmake")
    list(APPEND CMAKE_MODULE_PATH "/usr/share/cmake/geographiclib")
  endif()
  find_package(GeographicLib REQUIRED MODULE)
endif()

add_library(${PROJECT_NAME} src/local_enu.cpp)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)
target_include_directories(${PROJECT_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
  ${GeographicLib_INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME} PUBLIC ${GeographicLib_LIBRARIES})

install(TARGETS ${PROJECT_NAME} EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib LIBRARY DESTINATION lib RUNTIME DESTINATION bin)
install(DIRECTORY include/ DESTINATION include)
ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_include_directories(include)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_local_enu test/test_local_enu.cpp)
  target_link_libraries(test_local_enu ${PROJECT_NAME})
  ament_add_gtest(test_reference_fixtures test/test_reference_fixtures.cpp)
  target_link_libraries(test_reference_fixtures ${PROJECT_NAME})
endif()

ament_package()
