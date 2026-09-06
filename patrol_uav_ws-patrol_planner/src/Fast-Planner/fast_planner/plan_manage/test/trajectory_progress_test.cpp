#include <gtest/gtest.h>
#include <plan_manage/trajectory_progress.h>

using fast_planner::projectProgress;
using fast_planner::boundedLookahead;

int main(int argc, char** argv) {
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}

TEST(TrajectoryProgress, DoesNotJumpToLaterLoopBranch) {
  auto line = [](double t) { return Eigen::Vector3d(t <= 2 ? t : 4-t, 0, 0); };
  const Eigen::Vector3d actual(0.2, 0, 0);
  EXPECT_NEAR(projectProgress(line, actual, 0.0, 4.0), 0.2, 0.021);
  EXPECT_LT(boundedLookahead(line, actual, 0.2, 4.0, 0.4), 0.63);
}
TEST(TrajectoryProgress, LostTrackingDoesNotSelectEndpoint) {
  auto line = [](double t) { return Eigen::Vector3d(t, 0, 0); };
  const Eigen::Vector3d actual(0, 2, 0);
  EXPECT_DOUBLE_EQ(boundedLookahead(line, actual, 0, 10, 0.4), 0.0);
}
TEST(TrajectoryProgress, ProgressIsMonotonicAndIncludesEndpoint) {
  auto line = [](double t) { return Eigen::Vector3d(t, 0, 0); };
  EXPECT_DOUBLE_EQ(projectProgress(line, Eigen::Vector3d(0.2, 0, 0), 0.5, 2), 0.5);
  EXPECT_DOUBLE_EQ(projectProgress(line, Eigen::Vector3d(1.013, 0, 0), 1, 1.013), 1.013);
}
