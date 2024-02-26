# JointAngles Module in ergo3d

The `JointAngles.py` module in the `ergo3d` package provides a class for handling and manipulating joint angles in 3D space. This module is essential for the geometric and ergonomic calculations in the package.

## Classes

The module contains the following class:

- `JointAngles`: This class represents joint angles in 3D space. It provides methods to set the joint angles by a plane, origin point, and axis point, and to calculate projection angles of a target vector.

## Key Methods

Here are some key methods provided in this module:

- `set_zero(frame)`: Sets the zero frame for the joint angles.

- `get_flex_abd(coordinate_system, target_vector, plane_seq=['xy', 'xz'], flip_sign=[1, 1])`: Gets the flexion and abduction angles of a target vector in a coordinate system.

- `get_rot(pt1a, pt1b, pt2a, pt2b, flip_sign=1)`: Gets the rotation angle between two vectors.

- `zero_by_idx(idx)`: Zeroes the joint angles by index.

- `plot_angles(joint_name='', alpha=1, linewidth=1, linestyle='-', label=None, frame_range=None)`: Plots the joint angles.

- `plot_angles_by_frame(render_dir, joint_name='', alpha=1, linewidth=1, linestyle='-', label=None, frame_range=None, angle_names=['Flexion', 'H-Abduction', 'Rotation'])`: Plots the joint angles by frame.

## Usage

To use the `JointAngles.py` module, you can import the `JointAngles` class as follows:

```python
from ergo3d.JointAngles import JointAngles