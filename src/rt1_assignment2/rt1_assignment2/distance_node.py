import math
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

from rt1_assignment2_interfaces.msg import ObstacleInfo
from rt1_assignment2_interfaces.srv import SetThreshold


class DistanceNode(Node):
    def __init__(self):
        super().__init__('distance_node')

        self.declare_parameter('threshold', 0.6)
        self.threshold = float(self.get_parameter('threshold').value)

        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.on_scan, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.info_pub = self.create_publisher(ObstacleInfo, '/obstacle_info', 10)

        self.th_srv = self.create_service(SetThreshold, '/set_threshold', self.handle_set_threshold)

        self._is_backing_up = False
        self._backup_end_time = 0.0
        self._timer = self.create_timer(0.05, self._backup_tick)

        self.get_logger().info(f"Safety monitor ready. Threshold={self.threshold:.2f} m")

    def handle_set_threshold(self, request, response):
        if request.threshold <= 0.0 or (not math.isfinite(request.threshold)):
            response.success = False
            response.message = "Threshold must be a positive finite number."
            return response

        self.threshold = float(request.threshold)
        response.success = True
        response.message = f"Threshold set to {self.threshold:.3f} m"
        self.get_logger().info(response.message)
        return response

    def on_scan(self, scan: LaserScan):
        if not scan.ranges:
            return

        # Replace invalid readings with inf
        ranges = []
        for r in scan.ranges:
            if r is None:
                ranges.append(float('inf'))
            elif math.isfinite(r) and r > 0.0:
                ranges.append(r)
            else:
                ranges.append(float('inf'))

        min_dist = min(ranges)
        min_i = ranges.index(min_dist) if math.isfinite(min_dist) else -1

        direction = "unknown"
        if min_i >= 0:
            angle = scan.angle_min + min_i * scan.angle_increment
            deg = math.degrees(angle)
            if -30.0 <= deg <= 30.0:
                direction = "front"
            elif 30.0 < deg <= 150.0:
                direction = "left"
            elif -150.0 <= deg < -30.0:
                direction = "right"

        info = ObstacleInfo()
        info.closest_distance = float(min_dist) if math.isfinite(min_dist) else float('inf')
        info.direction = direction
        info.threshold = float(self.threshold)
        self.info_pub.publish(info)

        if math.isfinite(min_dist) and (min_dist < self.threshold) and (not self._is_backing_up):
            self._start_backup()

    def _start_backup(self):
        self._is_backing_up = True
        self._backup_end_time = time.time() + 0.6
        self.get_logger().warn("Too close! Backing up...")

    def _backup_tick(self):
        if not self._is_backing_up:
            return

        if time.time() < self._backup_end_time:
            msg = Twist()
            msg.linear.x = -0.2
            msg.angular.z = 0.0
            self.cmd_pub.publish(msg)
        else:
            self.cmd_pub.publish(Twist())
            self._is_backing_up = False
            self.get_logger().info("Backup complete. Stopped.")


def main():
    rclpy.init()
    node = DistanceNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()