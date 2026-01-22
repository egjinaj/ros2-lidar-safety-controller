import threading
import time
from collections import deque

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from rt1_assignment2_interfaces.srv import GetAverageVel


class UInode(Node):
    """
    Reads user input: linear_x angular_z duration_sec
    Publishes Twist on /cmd_vel, waits duration, then publishes zero Twist to stop.
    Keeps last 5 velocity inputs (lin, ang) and provides /get_average_vel.
    """

    def __init__(self):
        super().__init__('ui_node')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self._last_cmds = deque(maxlen=5)  # stores (lin, ang)
        self._lock = threading.Lock()

        self._avg_srv = self.create_service(GetAverageVel, '/get_average_vel', self.handle_get_average)

        t = threading.Thread(target=self._input_loop, daemon=True)
        t.start()

        self.get_logger().info(
            "Teleop ready.\n"
            "Type: <linear_x> <angular_z> <duration_sec>\n"
            "Example: 0.2 0.0 1.5   or   0.0 0.8 0.7\n"
            "Service: /get_average_vel"
        )

    def _publish_stop(self):
        self.cmd_pub.publish(Twist())

    def _input_loop(self):
        while rclpy.ok():
            try:
                raw = input("Enter lin ang duration (or 'q' to quit): ").strip()
                if raw.lower() in ('q', 'quit', 'exit'):
                    self.get_logger().info("Exiting teleop.")
                    rclpy.shutdown()
                    return

                parts = raw.split()
                if len(parts) != 3:
                    print("Enter exactly 3 values: linear_x angular_z duration_sec")
                    continue

                lin = float(parts[0])
                ang = float(parts[1])
                duration = float(parts[2])

                if duration <= 0.0:
                    print("duration_sec must be > 0")
                    continue

                msg = Twist()
                msg.linear.x = lin
                msg.angular.z = ang
                self.cmd_pub.publish(msg)

                with self._lock:
                    self._last_cmds.append((lin, ang))

                # wait then stop
                time.sleep(duration)
                self._publish_stop()

            except ValueError:
                print("Invalid input. Example: 0.2 -0.5 1.0")
            except (EOFError, KeyboardInterrupt):
                rclpy.shutdown()
                return
            except Exception as e:
                print(f"Error: {e}")

    def handle_get_average(self, request, response):
        with self._lock:
            n = len(self._last_cmds)
            if n == 0:
                response.avg_linear = 0.0
                response.avg_angular = 0.0
                response.samples = 0
                return response

            response.avg_linear = float(sum(v[0] for v in self._last_cmds) / n)
            response.avg_angular = float(sum(v[1] for v in self._last_cmds) / n)
            response.samples = int(n)
            return response


def main():
    rclpy.init()
    node = UInode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
