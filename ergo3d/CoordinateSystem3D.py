import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import os
from .Point import Point, VirtualPoint, MarkerPoint
from .Plane import Plane


class CoordinateSystem3D:
    def __init__(self):
        self.random_id = np.random.randint(0, 100000000)
        self.is_empty = True

    def set_by_plane(self, plane, origin_pt, axis_pt, sequence='xyz', axis_positive=True):
        '''
        requirement: need axis_pt and origin_pt to be in the specified plane
        sequence [first, second, thrid axis] meaning:
        first axis is the in-plane axis, if axis_positive is True, the direction is from origin_pt to axis_pt
        second axis is the orthogonal axis to plane
        third axis is orthogonal to the first two (also should be in the plane)
        '''
        '''
        Usage:
        # RShoulder angles
        try:
            PELVIS_b = Point.translate_point(C7_m, Point.create_const_vector(0,0,-1000,examplePt=C7))  # todo: this is temp for this shoulder trial, change to real marker in the future

            zero_frame = [941, 941, None]
            # RSHOULDER_plane = Plane(RSHO_b, RSHO_f, C7_m)
            RSHOULDER_plane = Plane(RSHOULDER, PELVIS_b, C7_m)
            RSHOULDER_coord = CoordinateSystem3D()
            RSHOULDER_coord.set_by_plane(RSHOULDER_plane, RSHOULDER, C7_m, sequence='zxy', axis_positive=False)
            RSHOULDER_angles = JointAngles()
            RSHOULDER_angles.set_zero(zero_frame)
            RSHOULDER_angles.get_flex_abd(RSHOULDER_coord, RELBOW, plane_seq=['xy', 'xz'])
            # RSHOULDER_angles.get_rot(RSHO_b, RSHO_f, RME, RLE)
            RSHOULDER_angles.flexion = Point.angle(Point.vector(RSHOULDER, RELBOW).xyz, Point.vector(C7, PELVIS_b).xyz)
            RSHOULDER_angles.rotation = None

            ##### Visual for debugging #####
            # frame = 1000
            # print(f'RSHOULDER_angles:\n Flexion: {RSHOULDER_angles.flexion[frame]}, \n Abduction: {RSHOULDER_angles.abduction[frame]},\n Rotation: {RSHOULDER_angles.rotation[frame]}')
            # Point.plot_points([RSHOULDER_coord.origin, RSHOULDER_coord.x_axis_end, RSHOULDER_coord.y_axis_end, RSHOULDER_coord.z_axis_end], frame=frame)
            # RSHOULDER_angles.plot_angles(joint_name='Right Shoulder', frame_range=[941, 5756])
            render_dir = os.path.join(trial_name[0], 'render', trial_name[1], 'RSHOULDER')
            RSHOULDER_angles.plot_angles_by_frame(render_dir, joint_name='Right Shoulder', frame_range=[941, 5756])
        except:
            print('RSHOULDER_angles failed')
        '''
        self.plane = plane
        self.is_empty = False
        self.origin = origin_pt
        axis_vec = Point.vector(origin_pt, axis_pt, normalize=1)
        if axis_positive:
            inplane_end = Point.translate_point(origin_pt, axis_vec, direction=1)
        else:
            inplane_end = Point.translate_point(origin_pt, axis_vec, direction=-1)
        orthogonal_end = Point.translate_point(origin_pt, plane.normal_vector)
        if sequence[0] == 'x':
            self.x_axis_end = inplane_end
        elif sequence[0] == 'y':
            self.y_axis_end = inplane_end
        elif sequence[0] == 'z':
            self.z_axis_end = inplane_end
        else:
            raise ValueError(f'sequence must be xyz, xzy, yxz, yzx, zxy, zyx, but {sequence} is given')
        if sequence[1] == 'x':
            self.x_axis_end = orthogonal_end
        elif sequence[1] == 'y':
            self.y_axis_end = orthogonal_end
        elif sequence[1] == 'z':
            self.z_axis_end = orthogonal_end
        else:
            raise ValueError(f'sequence must be xyz, xzy, yxz, yzx, zxy, zyx, but {sequence} is given')
        self.set_third_axis(sequence)
        self.set_plane_from_axis_end()
        # Point.plot_points([self.origin, self.x_axis_end, self.y_axis_end, self.z_axis_end], frame=1000)

    def set_third_axis(self, sequence='xyz'):
        if sequence[-1] == 'x':
            self.x_axis_end = Point.translate_point(self.origin, Point.orthogonal_vector(self.origin, self.y_axis_end, self.z_axis_end, normalize=1))
        elif sequence[-1] == 'y':
            self.y_axis_end = Point.translate_point(self.origin, Point.orthogonal_vector(self.origin, self.z_axis_end, self.x_axis_end, normalize=1))
        elif sequence[-1] == 'z':
            self.z_axis_end = Point.translate_point(self.origin, Point.orthogonal_vector(self.origin, self.x_axis_end, self.y_axis_end, normalize=1))
        else:
            raise ValueError(f'sequence must be xyz, xzy, yxz, yzx, zxy, zyx, but got {sequence}')

    def set_plane_from_axis_end(self):
        self.xy_plane = Plane(self.origin, self.x_axis_end, self.y_axis_end)
        self.zx_plane = Plane(self.origin, self.z_axis_end, self.x_axis_end)
        self.yz_plane = Plane(self.origin, self.y_axis_end, self.z_axis_end)

    def projection_angles(self, target_vector, threshold=1):
        vector = target_vector.xyz
        x_vector = Point.vector(self.origin, self.x_axis_end).xyz
        y_vector = Point.vector(self.origin, self.y_axis_end).xyz
        z_vector = Point.vector(self.origin, self.z_axis_end).xyz
        # xy plane
        xy_projection = self.xy_plane.project_vector(vector)
        xy_angle = Point.angle_w_direction(xy_projection, x_vector, y_vector)
        # xz plane
        xz_projection = self.zx_plane.project_vector(vector)
        xz_angle = Point.angle_w_direction(xz_projection, x_vector, z_vector)
        # yz plane
        yz_projection = self.yz_plane.project_vector(vector)
        yz_angle = Point.angle_w_direction(yz_projection, y_vector, z_vector)
        return xy_angle, xz_angle, yz_angle