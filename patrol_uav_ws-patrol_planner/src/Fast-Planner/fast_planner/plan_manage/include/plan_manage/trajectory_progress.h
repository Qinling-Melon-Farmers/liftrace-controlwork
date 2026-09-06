#pragma once
#include <Eigen/Core>
#include <algorithm>
#include <cmath>

namespace fast_planner {
// Project only onto the next part of the path. A spatially nearby later
// branch of a loop is not a valid shortcut through the intervening obstacle.
template <class Evaluate>
double projectProgress(const Evaluate& position, const Eigen::Vector3d& measured,
                       double previous, double duration) {
  previous = std::max(0.0, std::min(previous, duration));
  const double end = std::min(duration, previous + 1.0);
  double best = previous;
  double distance = (position(previous) - measured).squaredNorm();
  for (double t = previous + 0.02; t <= end + 1e-9; t += 0.02) {
    const double sample = std::min(t, duration);
    const double candidate = (position(sample) - measured).squaredNorm();
    if (candidate < distance) { distance = candidate; best = sample; }
  }
  if (duration - end < 1e-9 &&
      (position(duration) - measured).squaredNorm() < distance) best = duration;
  return best;
}

template <class Evaluate>
double boundedLookahead(const Evaluate& position, const Eigen::Vector3d& measured,
                        double progress, double duration, double distance) {
  double result = progress;
  for (double t = progress + 0.02; t <= duration + 0.02; t += 0.02) {
    const double sample = std::min(t, duration);
    if ((position(sample) - measured).norm() > distance) break;
    result = sample;
    if (sample == duration) break;
  }
  return result;
}
}  // namespace fast_planner
