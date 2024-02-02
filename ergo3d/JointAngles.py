import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import os
from .Point import Point, VirtualPoint, MarkerPoint
from .Plane import Plane


class JointAngles:
    def __init__(self):
        self.random_id = np.random.randint(0, 100000000)
        self.is_empty = True
        self.zero_frame = [0, 0, 0]

    def set_zero_frame(self, frame):
        '''
        set to None if you don't want to zero the angles
        '''
        if frame is None:
            self.zero_frame = [None, None, None]
        if type(frame) == list:
            if len(frame) != 3:
                raise ValueError('zero frame must be a list of length 3 or a single int')
            self.zero_frame = frame
        elif type(frame) == int:
            self.zero_frame = [frame, frame, frame]

    def get_flex_abd(self, coordinate_system, target_vector, plane_seq=['xy', 'xz'], flip_sign=[1, 1]):
        """
        get flexion and abduction angles of a vector in a coordinate system
        plane_seq: ['xy', None]
        """
        if len(plane_seq) != 2:
            raise ValueError('plane_seq must be a list of length 2, with flexion plane first and abduction plane second, fill None if not needed')
        xy_angle, xz_angle, yz_angle = coordinate_system.projection_angles(target_vector)
        output_angles = []
        zero_angles = []
        for plane_id, plane_name in enumerate(plane_seq):
            if plane_name is not None:
                if plane_name == 'xy':
                    output_angle = xy_angle
                elif plane_name == 'xz' or plane_name == 'zx':
                    output_angle = xz_angle
                elif plane_name == 'yz':
                    output_angle = yz_angle
                else:
                    raise ValueError('plane_name must be one of "xy", "xz", "zx", "yz", or None')
                # output_angle = np.abs(output_angle)
                if self.zero_frame[plane_id] is not None:
                    zero_frame_id = self.zero_frame[plane_id]
                    zero_angles.append(output_angle[zero_frame_id])
                    output_angle = output_angle - zero_angles[-1]
                    # deal with output -pi pi range issue
                    output_angle = np.where(output_angle > np.pi, output_angle - 2 * np.pi, output_angle)
                    output_angle = np.where(output_angle < -np.pi, output_angle + 2 * np.pi, output_angle)
                else:
                    zero_angles.append(None)
                output_angles.append(output_angle)

            else:
                output_angles.append(None)

        self.flexion = output_angles[0] * flip_sign[0]
        self.flexion_info = {'plane': plane_seq[0], 'zero_angle': zero_angles[0], 'zero_frame': self.zero_frame[0], 'flip_sign': flip_sign[0]}
        self.abduction = output_angles[1] * flip_sign[1]
        self.abduction_info = {'plane': plane_seq[1], 'zero_angle': zero_angles[1], 'zero_frame': self.zero_frame[1], 'flip_sign': flip_sign[1]}
        self.is_empty = False
        return output_angles

    def get_rot(self, pt1a, pt1b, pt2a, pt2b, flip_sign=1):
        '''
        get rotation angle between two vectors
        flip_sign: 1 or -1, if the rotation is in the opposite direction
        Example:

        '''
        pt1mid = Point.mid_point(pt1a, pt1b)
        pt2mid = Point.mid_point(pt2a, pt2b)
        plane1 = Plane(pt1a, pt1b, pt2mid)
        plane2 = Plane(pt2a, pt2b, pt1mid)
        rotation_angle = Point.angle(plane1.normal_vector.xyz, plane2.normal_vector.xyz)

        rotation_sign = plane2.above_or_below(pt1a)
        rotation_angle = rotation_angle * rotation_sign * flip_sign

        if self.zero_frame[2] is not None:
            rotation_zero = rotation_angle[self.zero_frame[2]]
            rotation_angle = rotation_angle - rotation_zero
        else:
            rotation_zero = None

        # make plot in -pi to pi range
        rotation_angle = np.where(rotation_angle > np.pi, rotation_angle - 2 * np.pi, rotation_angle)
        rotation_angle = np.where(rotation_angle < -np.pi, rotation_angle + 2 * np.pi, rotation_angle)

        self.rotation = rotation_angle
        self.rotation_info = {'plane': None, 'zero_angle': rotation_zero, 'zero_frame': self.zero_frame[2]}
        self.is_empty = False
        return self.rotation

    def zero_by_idx(self, idx):
        """
        idx is 0, 1, 2, corresponding to flexion, abduction, rotation
        usage:
        RKNEE_angles.flexion = RKNEE_angles.zero_by_idx(0)
        """
        angle = self.flexion if idx == 0 else self.abduction if idx == 1 else self.rotation
        this_zero_frame = self.zero_frame[idx]
        if this_zero_frame is not None:
            zero_angle = angle[this_zero_frame]
            output_angle = angle - zero_angle
            output_angle = np.where(output_angle > np.pi, output_angle - 2 * np.pi, output_angle)
            output_angle = np.where(output_angle < -np.pi, output_angle + 2 * np.pi, output_angle)
        else:
            output_angle = angle
        return output_angle

    def plot_angles(self, joint_name='', alpha=1, linewidth=1, linestyle='-', label=None, frame_range=None):
        if self.is_empty:
            raise ValueError('JointAngles is empty, please set angles first')
        if frame_range is None:
            if self.flexion is not None:
                frame_range = [0, len(self.flexion)]
            elif self.abduction is not None:
                frame_range = [0, len(self.abduction)]
            elif self.rotation is not None:
                frame_range = [0, len(self.rotation)]
            else:
                raise ValueError('all three angles are None, cannot plot')
        fig, ax = plt.subplots(3, 1, sharex=True)
        angle_names = ['Flexion', 'H-Abduction', 'Rotation']
        colors = ['r', 'g', 'b']
        for angle_id, angle in enumerate([self.flexion, self.abduction, self.rotation]):
            # horizontal line at zero, pi, and -pi
            ax[angle_id].axhline(0, color='k', linestyle='--', alpha=0.5, linewidth=0.25)
            ax[angle_id].axhline(90, color='k', linestyle='dotted', alpha=0.5, linewidth=0.25)
            ax[angle_id].axhline(180, color='k', linestyle='--', alpha=0.5, linewidth=0.25)
            ax[angle_id].axhline(-90, color='k', linestyle='dotted', alpha=0.5, linewidth=0.25)
            ax[angle_id].axhline(-180, color='k', linestyle='--', alpha=0.5, linewidth=0.25)
            ax[angle_id].yaxis.set_ticks(np.arange(-180, 181, 90))
            ax[angle_id].set_ylabel(f'{angle_names[angle_id]}')
            ax[angle_id].set_xlim(frame_range[0], frame_range[1])  # set xlim
            ax[angle_id].margins(x=0)
            if angle is not None:
                ax[angle_id].plot(angle[0:frame_range[1]] / np.pi * 180, color=colors[angle_id], alpha=alpha, linewidth=linewidth, linestyle=linestyle, label=label)
            else:
                # plot diagonal line crossing through the chart
                ax[angle_id].plot([frame_range[0], frame_range[1]], [-180, 180], color='black', linewidth=4)

        ax[0].set_title(f'{joint_name} (deg)')
        plt.show()
        return fig, ax

    def plot_angles_by_frame(self, render_dir, joint_name='', alpha=1, linewidth=1, linestyle='-', label=None, frame_range=None, angle_names=['Flexion', 'H-Abduction', 'Rotation']):
        if self.is_empty:
            raise ValueError('JointAngles is empty, please set angles first')
        if frame_range is None:
            if self.flexion is not None:
                frame_range = [0, len(self.flexion)]
            elif self.abduction is not None:
                frame_range = [0, len(self.abduction)]
            elif self.rotation is not None:
                frame_range = [0, len(self.rotation)]
            else:
                raise ValueError('all three angles are None, cannot plot')
        print(f'Saving {joint_name} angle frames to {render_dir}')
        for frame_id in range(frame_range[0], frame_range[1]):
            fig, ax = plt.subplots(3, 1, sharex=True)

            colors = ['r', 'g', 'b']
            for angle_id, angle in enumerate([self.flexion, self.abduction, self.rotation]):
                print(f'frame {frame_id}/{frame_range[1]}', end='\r')
                # horizontal line at zero, pi, and -pi
                ax[angle_id].axhline(0, color='k', linestyle='--', alpha=0.5, linewidth=0.25)
                ax[angle_id].axhline(90, color='k', linestyle='dotted', alpha=0.5, linewidth=0.25)
                ax[angle_id].axhline(180, color='k', linestyle='--', alpha=0.5, linewidth=0.25)
                ax[angle_id].axhline(-90, color='k', linestyle='dotted', alpha=0.5, linewidth=0.25)
                ax[angle_id].axhline(-180, color='k', linestyle='--', alpha=0.5, linewidth=0.25)
                ax[angle_id].yaxis.set_ticks(np.arange(-180, 181, 90))
                ax[angle_id].set_xlim(frame_range[0], frame_range[1])  # set xlim
                ax[angle_id].axvline(frame_id, color='k', linestyle='--', alpha=0.5, linewidth=0.25)  # vertical line at current frame
                # a dot with value at current frame
                ax[angle_id].set_ylabel(f'{angle_names[angle_id]}')
                ax[angle_id].margins(x=0)
                if angle is not None:
                    ax[angle_id].plot(angle[0:frame_id + 1] / np.pi * 180, color=colors[angle_id], alpha=alpha, linewidth=linewidth, linestyle=linestyle, label=label)
                    ax[angle_id].plot(frame_id, angle[frame_id] / np.pi * 180, color=colors[angle_id], marker='o', markersize=5)  # a dot with value at current frame
                    ax[angle_id].text(frame_id, angle[frame_id] / np.pi * 180, f'{angle[frame_id] / np.pi * 180:.1f}', fontsize=12, horizontalalignment='left',
                                      verticalalignment='bottom')  # add text of current angle value
                else:
                    ax[angle_id].plot([frame_range[0], frame_range[1]], [-180, 180], color='gray', linewidth=1)  # plot diagonal line crossing through the chart

            ax[0].set_title(f'{joint_name} (deg)')

            ax[2].xaxis.set_major_locator(MaxNLocator(integer=True))  # set x ticks to integer only
            if not os.path.exists(render_dir):
                os.makedirs(render_dir)
            plt.savefig(os.path.join(render_dir, f'{joint_name}_{frame_id:06d}.png'))
            plt.close()
