# RT1 - Assignment 2  
ROS 2 Jazzy - Obstacle Detection and Safety Control

This project implements a multi-node ROS 2 system that controls a mobile robot in a Gazebo simulation while enforcing safety constraints using laser scan data.

The system allows user-controlled motion and automatic obstacle avoidance using custom ROS messages and services.

---

## Project Overview

The project includes:

- A Python UI node (`ui_node`) that allows the user to send velocity commands to the robot
- A Python distance/safety node (`distance_node`) that:
  - Monitors laser scan data
  - Detects the closest obstacle and its direction
  - Forces the robot to move backward and stop when an obstacle is too close
- Custom ROS 2 messages and services
- Integration with a Gazebo simulation provided by the instructor

---

## Project Structure

```
ros2_ws/src/
├── rt1_assignment2_interfaces/
│   ├── msg/
│   │   └── ObstacleInfo.msg
│   └── srv/
│       ├── SetThreshold.srv
│       └── GetAverageVel.srv
│
├── rt1_assignment2/
│   ├── package.xml
│   ├── setup.py
│   └── rt1_assignment2/
│       ├── ui_node.py          # user interface node
│       └── distance_node.py    # safety / distance node
│
└── bme_gazebo_sensors/          # provided simulation package

```

---

**How to Build**

- In one terminal:

```
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

**How to Run**
- Terminal 1 - Start the Gazebo simulation:
```
ros2 launch bme_gazebo_sensors spawn_robot.launch.py
```
- Terminal 2 - Start the distance node:
```
ros2 run rt1_assignment2 distance_node
```

- Terminal 3 - Start the UI node:
```
ros2 run rt1_assignment2 ui_node
```

**Node Descriptions**

UI_NODE.PY:

- Terminal-based user interface
- Allows the user to:
  - Enter linear velocity
  - Enter angular velocity
  - Specify a duration (seconds)
- Each command is applied for the given duration, then the robot automatically stops
- Stores the last 5 velocity commands

Service provided:
```
/get_average_vel
```

DISTANCE_NODE.PY

- Subscribes to:
  ```
  /scan (LaserScan)
  ```
- Computes:
  - Closest obstacle distance
  - Obstacle direction (left / front / right)
- Publishes obstacle information using a custom message
- Enforces safety behavior:
  - If distance < threshold → robot moves backward briefly
  - Then the robot stops

Topic published:
```
/obstacle_info
```

Service provided:
```
/set_threshold
```

---

**How to Use Messages and Services**

Monitor Obstacle Information
The distance node continuously publishes obstacle data.
```
ros2 topic echo /obstacle_info
```
This shows:
- Closest obstacle distance
- Direction of the obstacle
- Current safety threshold

Change Safety Threshold at Runtime
```
ros2 service call /set_threshold rt1_assignment2_interfaces/srv/SetThreshold "{threshold: 0.4}"
```
This updates the minimum allowed distance to obstacles without restarting the node.

Get Average Velocity
After sending several velocity commands using the UI node:

```
ros2 service call /get_average_vel rt1_assignment2_interfaces/srv/GetAverageVel "{}"
```
The service returns:
- Average linear velocity
- Average angular velocity
- Number of samples used

---
**Logic Summary**

- The robot moves only when commanded by the user.
- Each velocity command is applied for a limited time.
- The robot never collides with obstacles:
  - Movement is automatically corrected if an obstacle is too close.
- Safety parameters can be modified at runtime via services
- Obstacle information is continuously published for monitoring


**Requirements**
- Ubuntu 22.04 (WSL or native)
- ROS2 Jazzy
- Gazebo (gz-sim)
- Python 3

**Notes**
- The Gazebo simulation package (bme_gazebo_sensors) is provided by the instructor.
- Nodes are intentionally run in separate terminals to allow interactive user input
- No launch file is required for correct execution

---

**Author: Endri Gjinaj**
