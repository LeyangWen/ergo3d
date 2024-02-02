# Plane Module in ergo3d

The `Plane.py` module in the `ergo3d` package provides classes and methods for handling and manipulating planes in 3D space. This module is essential for the geometric and ergonomic calculations in the package.

## Classes

The module contains the following class:

- `Plane`: This class represents a plane in 3D space. It provides methods to set the plane by points or by a vector, project a vector or a point onto the plane, and determine whether a point is above or below the plane.

## Key Methods

Here are some key methods provided in this module:

- `set_by_pts(pt1, pt2, pt3)`: Sets the plane by three points. The direction of the normal vector is determined by the right-hand rule based on the vector from `pt1` to `pt2` and then from `pt1` to `pt3`.

- `set_by_vector(pt1, vector, direction=1)`: Sets the plane by a point and a vector. The direction of the normal vector is determined by the `direction` parameter.

- `project_vector(vector)`: Projects a vector onto the plane.

- `project_point(point)`: Projects a point onto the plane.

- `above_or_below(point)`: Determines whether a point is above or below the plane. Returns 1 if the point is above the plane, -1 if it's below.

- `angle_w_direction(plane1, plane2)`: Returns the angle between `plane1` and `plane2` in the range of [-pi, pi].

## Usage

To use the `Plane.py` module, you can import the `Plane` class as follows:

```python
from ergo3d.Plane import Plane