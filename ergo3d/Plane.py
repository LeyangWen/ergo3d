import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import os
from .Point import Point, VirtualPoint, MarkerPoint


class Plane:
    def __init__(self, pt1=None, pt2=None, pt3=None):
        self.random_id = np.random.randint(0, 100000000)
        self.is_empty = True
        if pt1 is not None and pt2 is not None and pt3 is not None:
            self.set_by_pts(pt1, pt2, pt3)

    def set_by_pts(self, pt1, pt2, pt3):
        """
        rhr for vec: pt1->pt2, pt1->pt3
        try to make orthogonal vector positive for one axis
        """
        self.pt1 = pt1
        self.pt2 = pt2
        self.pt3 = pt3
        self.is_empty = False
        self.normal_vector = Point.orthogonal_vector(pt1, pt2, pt3, normalize=1)
        self.normal_vector_end = Point.translate_point(pt1, self.normal_vector, direction=1)

    def set_by_vector(self, pt1, vector, direction=1):
        """
        vector as virtual point
        """
        self.pt1 = pt1
        self.pt2 = None
        self.pt3 = None
        self.is_empty = False
        vector_xyz = vector.xyz
        normal_vector_xyz = vector_xyz / np.linalg.norm(vector_xyz, axis=0) * direction  # normalize vector
        self.normal_vector = Point.point_from_nparray(normal_vector_xyz)
        self.normal_vector_end = Point.translate_point(pt1, vector, direction=direction)

    def project_vector(self, vector, optimize=True):
        """
        project a vector onto the plane
        vector as xyz
        """
        plane_normal = self.normal_vector.xyz
        plane_normal = plane_normal / np.linalg.norm(plane_normal, axis=0)

        # vector = np.array([[1,1,1],[1,1,2]]).T
        # plane_normal = np.array([[0,1,0],[0,1,0]]).T
        # angle = Point.angle(vector, plane_normal)
        if optimize:  # optimized for memory
            diagonal_elements = np.einsum('ij,ij->i', vector.T, plane_normal.T)
            projection = vector - diagonal_elements[None, :] * plane_normal
        else:
            projection = vector - np.diagonal(np.dot(vector.T, plane_normal)) * plane_normal
        return projection

    def project_point(self, point):
        """
        project a point onto the plane
        """
        vector = point.xyz - self.pt1.xyz
        projection = self.project_vector(vector)  # todo: find a less entangled way in the future
        return Point.translate_point(self.pt1, projection)

    def above_or_below(self, point):
        """
        return 1 if point is above the plane, -1 if below
        """
        vector = point.xyz - self.pt1.xyz
        normal_vector = self.normal_vector.xyz
        return np.sign(np.sum(vector * normal_vector, axis=0))

    @staticmethod
    def angle_w_direction(plane1, plane2):
        '''
        return the angle between plane1 and plane2 in range of [-pi, pi]
        '''
        angle = Point.angle(plane1.normal_vector, plane2.normal_vector)
        angle_sign = Point.angle(plane1.normal_vector, plane2.normal_vector_end)
        angle = np.where(angle_sign > np.pi / 2, -angle, angle)
        return angle