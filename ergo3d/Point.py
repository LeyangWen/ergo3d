import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import os


class Point:
    def __init__(self, data=None, name=None):
        self.random_id = np.random.randint(0, 100000000)
        self.name = name
        if data is not None:
            self.data = data.reshape(-1, 3)
            self.type = 'point'
            self.x, self.y, self.z = data.T
            self.xyz = np.array([self.x, self.y, self.z])
            self.x = self.xyz[0]
            self.y = self.xyz[1]
            self.z = self.xyz[2]
            self.frame_no = self.data.shape[0]
            self.exist = np.ones(self.frame_no, dtype=bool).tolist()

    def copy(self):
        copied_point = MarkerPoint([self.x, self.y, self.z, self.exist])
        return copied_point

    @staticmethod
    def mid_point(p1, p2, precentage=0.5):
        '''
        return the midpoint of p1 and p2, if precentage is 0.5, return the mid point, if 0.25, return the point 1/4 way from p1 to p2
        '''
        try:
            xyz = p1.xyz * precentage + p2.xyz * (1 - precentage)
            exist = p1.exist and p2.exist  # exist need to be in pyton list, not np array
            p_out = VirtualPoint((xyz, exist))
            return p_out
        except:
            print('Error in "mid_point", Point not defined or exist not in python list')
            raise ValueError

    @staticmethod
    def distance(p1, p2 = None):
        if p2 is None:
            return np.linalg.norm(p1.xyz, axis=0)
        else:
            return np.linalg.norm(p1.xyz - p2.xyz,axis=0)

    @staticmethod
    def vector(p1, p2, normalize=None):
        """
        return the vector from p1 to p2
        normalize: None->return the vector, 1->return the unit vector, other->return the vector with length normalize
        """
        xyz = (p2.xyz - p1.xyz)
        if normalize is not None:
            xyz = xyz/Point.distance(p1, p2) * normalize
        exist = p1.exist and p2.exist
        return VirtualPoint((xyz, exist))

    @staticmethod
    def orthogonal_vector(p1, p2, p3, normalize=None):
        """
        return the vector orthogonal to the plane defined by p1, p2, p3
        direction is determined by the right hand rule based on vector p1->p2 and then p1->p3
        normalize: None->return the vector, 1->return the unit vector, other->return the vector with length normalize
        p1.xyz, p2.xyz, p3.xyz are 3xn np arrays
        """
        v1 = Point.vector(p1, p2, normalize=1)
        v2 = Point.vector(p1, p3, normalize=1)
        xyz = np.cross(v1.xyz.T, v2.xyz.T).T
        if normalize is not None:
            xyz = xyz / np.linalg.norm(xyz, axis=0) * normalize
        exist = p1.exist and p2.exist and p3.exist
        return VirtualPoint((xyz, exist))

    @staticmethod
    def translate_point(p, vector, direction=1):
        """
        move p in the direction of vector with length of distance
        """
        if type(vector) is np.ndarray:
            vector = Point.point_from_nparray(vector)
        xyz = p.xyz + direction * vector.xyz
        exist = p.exist and vector.exist
        return VirtualPoint((xyz, exist))

    @staticmethod
    def create_const_vector(x, y, z, frame=100, examplePt=None):
        '''
        x, y, z are float
        frame is ignored if examplePt is not None
        '''
        if examplePt:
            frame = examplePt.frame_no
        xyz = np.vstack((np.ones(frame) * x, np.ones(frame) * y, np.ones(frame) * z))
        exist = np.ones(frame, dtype=bool).tolist()
        return VirtualPoint((xyz, exist))

    @staticmethod
    def angle(v1, v2):
        """
        return the angle between v1 and v2
        v1 and v2 are vectors with shape (3, n)
        """
        return np.arccos(np.sum(v1 * v2, axis=0) / (np.linalg.norm(v1, axis=0) * np.linalg.norm(v2, axis=0)))

    @staticmethod
    def angle_w_direction(target_vector, main_axis_vector, secondary_axis_vector):
        """
        return the angle between main_axis_pt and target_pt using right hand rule
        secondary_axis_pt is used to determine the direction of the angle
        """
        angle_abs = Point.angle(target_vector, main_axis_vector)
        angle_sign = Point.angle(target_vector, secondary_axis_vector)
        angle = np.where(angle_sign > np.pi / 2, -angle_abs, angle_abs)
        return angle

    @staticmethod
    def plot_points(point_list, ax=None, fig=None, frame=0):
        """
        plot a list of points
        """
        if ax is None or fig is None:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

        x = []
        y = []
        z = []
        # make legend with point sequence
        for i, p in enumerate(point_list):
            ax.scatter(p.x[frame], p.y[frame], p.z[frame], label=str(i))
        # make sure the axis are equal
        ax.set_aspect('equal')
        # labels
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        # legend
        ax.legend()
        plt.show()
        return ax, fig

    @staticmethod
    def point_from_nparray(xyz):
        exist = np.ones(xyz.shape[0], dtype=bool).tolist()
        return VirtualPoint((xyz, exist))

    @staticmethod
    def batch_export_to_nparray(point_list):
        '''
        point_list is a list of Point objects
        return a np array with shape (frame, keypoints, 3)
        '''
        xyz = np.array([p.xyz.T for p in point_list])
        xyz = np.swapaxes(xyz, 0, 1)
        return xyz

    @staticmethod
    def swap_trajectory(p1, p2, index):
        '''
        swap p1 and p2 trajectory from index forward (including index)
        '''
        out1 = p1.copy()
        out2 = p2.copy()
        index = index
        out1.xyz[:, index:], out2.xyz[:, index:] = p2.xyz[:, index:], p1.xyz[:, index:]
        out1.exist[index:], out2.exist[index:] = p2.exist[index:], p1.exist[index:]
        return out1, out2

    @staticmethod
    def check_marker_swap(p1, p2, threshold=35):
        '''
        check if p1 and p2 are swapped, one way, need to check both directions
        this does not work well when the marker pairs are moving fast in the direction of each other
        '''
        p1_xyz = p1.xyz[:, :-1]
        p2_xyz = p2.xyz[:, :-1]
        p2_xyz_shift = p2.xyz[:, 1:]
        criteria = np.linalg.norm(p1_xyz - p2_xyz_shift, axis=0) < np.linalg.norm(p2_xyz - p2_xyz_shift, axis=0)  # check for swaps when both markers are present
        swap_index = criteria.nonzero()[0]+1
        p2_missing = (~np.array(p2.exist)).nonzero()[0]
        for swap_id in swap_index:
            if swap_id in p2_missing or swap_id - 1 in p2_missing:
                if p1.exist[swap_id-1]:  # if p1 is present at swap_id-1 and p2 is missing, then it is not a swap
                    check = True
                else:
                    criteria_2 = np.linalg.norm(p1_xyz[:, swap_id - 1] - p2_xyz_shift[:, swap_id - 1])
                    check = criteria_2 < threshold and criteria_2 > 0  # check for swaps when p2 is actually missing (p1 is incorrectly swapped and labeled as missing instead)
                    check = not check
                if check:
                    swap_index = np.delete(swap_index, np.where(swap_index == swap_id))
                else:
                    print(f'Caught by check: swap_id: ', swap_id, 'check: ', check)
        # todo: can not detect when p1 is missing before and p2 is present
        return swap_index

    @staticmethod
    def check_marker_swap_by_speed(p1, p2, threshold=15, interval_frames=1):
        '''
        check if p1 and p2 are swapped by speed threshold only, one way, need to check both directions
        '''
        p1_xyz = p1.xyz[:, :-interval_frames]
        p2_xyz_shift = p2.xyz[:, interval_frames:]
        criteria_value = np.linalg.norm(p1_xyz - p2_xyz_shift, axis=0)
        criteria = np.logical_and(criteria_value < (threshold), criteria_value > 0)
        swap_index = criteria.nonzero()[0]+1
        return swap_index

    def check_marker_speed(self, threshold=35, interval_frames=1):
        '''
        check if marker speed is too high
        '''
        xyz = self.xyz[:, :-interval_frames]
        xyz_shift = self.xyz[:, interval_frames:]
        criteria = np.linalg.norm(xyz - xyz_shift, axis=0) > (threshold)  # * interval_frames)
        swap_index = criteria.nonzero()[0]+1
        for swap_id in swap_index:
            if (not self.exist[swap_id-1]) or (not self.exist[swap_id]):
                swap_index = np.delete(swap_index, np.where(swap_index == swap_id))
        return swap_index


class MarkerPoint(Point):
    def __init__(self, data, name=None):
        """
        data: [x, y, z, exist]
        """
        super().__init__()
        self.data = data
        self.type = 'marker'
        self.x, self.y, self.z, self.exist = data
        self.xyz = np.array([self.x, self.y, self.z])
        self.x = self.xyz[0]
        self.y = self.xyz[1]
        self.z = self.xyz[2]
        self.frame_no = len(self.exist)
        self.name = name


class VirtualPoint(Point):
    def __init__(self, data, name=None):
        """
        data: [xyz, exist]
        """
        super().__init__()
        self.data = data
        self.type = 'virtual'
        self.xyz, self.exist = data
        self.xyz = np.array(self.xyz)
        self.x = self.xyz[0]
        self.y = self.xyz[1]
        self.z = self.xyz[2]
        self.frame_no = len(self.exist)
        self.name = name

    def output_format(self):
        return (self.xyz, self.exist)


class NpPoints(Point):
    def __init__(self, data, name=None):
        """
        data: np array with shape (frame, 3)
        assume exist is always true
        """
        super().__init__()
        self.data = data
        self.type = 'np'
        self.xyz = data.T
        self.x = self.xyz[0]
        self.y = self.xyz[1]
        self.z = self.xyz[2]
        self.frame_no = data.shape[0]
        self.name = name
        self.exist = np.ones(self.frame_no, dtype=bool).tolist()
