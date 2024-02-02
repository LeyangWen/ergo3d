# CoordinateSystem3D Module in ergo3d

The `CoordinateSystem3D.py` module in the `ergo3d` package provides a class for handling and manipulating 3D coordinate systems. This module is essential for the geometric and ergonomic calculations in the package.

## Classes

The module contains the following class:

- `CoordinateSystem3D`: This class represents a 3D coordinate system. It provides methods to set the coordinate system by a plane, origin point, and axis point, and to calculate projection angles of a target vector.

## Key Methods

Here are some key methods provided in this module:

- `set_by_plane(plane, origin_pt, axis_pt, sequence='xyz', axis_positive=True)`: Sets the coordinate system by a plane, an origin point, and an axis point. The sequence parameter determines the order of the axes.

- `set_third_axis(sequence='xyz')`: Sets the third axis of the coordinate system based on the sequence parameter.

- `set_plane_from_axis_end()`: Sets the planes of the coordinate system from the end points of the axes.

- `projection_angles(target_vector, threshold=1)`: Calculates the projection angles of a target vector onto the planes of the coordinate system.

## Usage

To use the `CoordinateSystem3D.py` module, you can import the `CoordinateSystem3D` class as follows:

```python
from ergo3d.CoordinateSystem3D import CoordinateSystem3D