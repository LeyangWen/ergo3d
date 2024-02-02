# Point Module in ergo3d

The `Point.py` module in the `ergo3d` package provides classes and methods for handling and manipulating points in 3D space. This module is essential for the geometric and ergonomic calculations in the package.

## Classes

The module contains the following classes:

- `Point`: This is the base class for points in 3D space. It provides basic properties and methods for a point.

- `MarkerPoint`: This class initiates a Point object from Vicon Nexus marker output, input data format is [x, y, z, exists]

- `VirtualPoint`: This class initiates a Point object from Vicon Nexus virtual point output, input data format is [[x, y, z], exists]


## Key Methods

Here are some key methods provided in this module:

- `mid_point(p1, p2, precentage=0.5)`: Returns the midpoint of `p1` and `p2`. If `precentage` is 0.5, it returns the mid point, if 0.25, it returns the point 1/4 way from `p1` to `p2`.

- `distance(p1, p2 = None)`: Returns the distance between `p1` and `p2`. If `p2` is `None`, it returns the distance from `p1` to the origin.

- `vector(p1, p2, normalize=None)`: Returns the vector from `p1` to `p2`. If `normalize` is not `None`, it returns the normalized vector or the vector with length `normalize`.

- `orthogonal_vector(p1, p2, p3, normalize=None)`: Returns the vector orthogonal to the plane defined by `p1`, `p2`, and `p3`.

- `translate_point(p, vector, direction=1)`: Moves point `p` in the direction of `vector` with length of `distance`.

- `angle(v1, v2)`: Returns the angle between vectors `v1` and `v2`.

- `angle_w_direction(target_vector, main_axis_vector, secondary_axis_vector)`: Returns the angle between `main_axis_vector` and `target_vector` using the right-hand rule. `secondary_axis_vector` is used to determine the direction of the angle.

- `plot_points(point_list, ax=None, fig=None, frame=0)`: Plots a list of points.

## Usage

To use the `Point.py` module, you can import the classes you need as follows:

```python
from ergo3d.Point import Point, MarkerPoint, VirtualPoint