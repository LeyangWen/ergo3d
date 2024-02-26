import unittest
import numpy as np
from ..ergo3d.Point import *
from ..ergo3d.Plane import Plane


class TestPlaneMethods(unittest.TestCase):
    def test_project_vector_optimization(self):
        """
        Test if the new optimized method performs the same as the original method
        """
        num_frames = 200

        # Create a Plane object with random points
        pt1 = NpPoints(np.random.rand(num_frames, 3))
        pt2 = NpPoints(np.random.rand(num_frames, 3))
        pt3 = NpPoints(np.random.rand(num_frames, 3))
        plane = Plane(pt1, pt2, pt3)

        # Generate some random vectors
        vectors = np.random.rand(3, num_frames)

        # Calculate projections using original and optimized methods
        projections_original = plane.project_vector(vectors, optimize=False)
        projections_optimized = plane.project_vector(vectors, optimize=True)

        # Assert that the projections are equal
        np.testing.assert_array_almost_equal(projections_original, projections_optimized, decimal=5)


if __name__ == '__main__':
    unittest.main()
