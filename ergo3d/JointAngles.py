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
        self.zero_frame_or_angle = [None, None, None]
        self.zero_by_frame_not_angle = False
        self.ergo_name = {'flexion':'flexion', 'abduction':'abduction', 'rotation':'rotation'}

    def set_zero(self, frame_or_angle, by_frame=False):
        '''
        set to None if you don't want to zero the angles
        if by_frame is True, zero_frame_or_angle is a list of 3 frame numbers
        if by_frame is False, zero_frame_or_angle is a list of 3 angles in degrees
        '''
        if frame_or_angle is None:
            output = [None, None, None]
        if type(frame_or_angle) == list:
            if len(frame_or_angle) != 3:
                raise ValueError('zero frame must be a list of length 3 or a single int')
            output = [np.radians(x) for x in frame_or_angle]
        elif type(frame_or_angle) == int:
            frame_or_angle = np.radians(frame_or_angle)  # convert to radian
            output = [frame_or_angle, frame_or_angle, frame_or_angle]
        self.zero_frame_or_angle = output
        self.zero_by_frame_not_angle = by_frame

    def get_flex_abd(self, coordinate_system, target_vector, plane_seq=['xy', 'xz'], flip_sign=[1, 1]):
        """
        get flexion and abduction angles of a vector in a coordinate system
        plane_seq: ['xy', None]
        """
        if len(plane_seq) != 2:
            raise ValueError('plane_seq must be a list of length 2, with flexion plane first and abduction plane second, fill None if not needed')
        xy_angle, xz_angle, yz_angle = coordinate_system.projection_angles(target_vector)
        output_angles = []
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
                if self.zero_frame_or_angle[plane_id] is not None:
                    if self.zero_by_frame_not_angle:
                        zero_frame_id = self.zero_frame_or_angle[plane_id]
                        zero_angle = output_angle[zero_frame_id]
                    else:  # zero by angle directly
                        zero_angle = self.zero_frame_or_angle[plane_id]
                    output_angle = output_angle - zero_angle
                    # deal with output -pi pi range issue
                    output_angle = np.where(output_angle > np.pi, output_angle - 2 * np.pi, output_angle)
                    output_angle = np.where(output_angle < -np.pi, output_angle + 2 * np.pi, output_angle)
                output_angles.append(output_angle)

            else:
                output_angles.append(None)

        self.flexion = output_angles[0] * flip_sign[0]
        # self.flexion_info = {'plane': plane_seq[0], 'zero_angle': zero_angles[0], 'zero_frame': self.zero_frame[0], 'flip_sign': flip_sign[0]}
        self.abduction = output_angles[1] * flip_sign[1]
        # self.abduction_info = {'plane': plane_seq[1], 'zero_angle': zero_angles[1], 'zero_frame': self.zero_frame[1], 'flip_sign': flip_sign[1]}
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

        if self.zero_frame_or_angle[2] is not None:
            if self.zero_by_frame_not_angle:
                rotation_zero = rotation_angle[self.zero_frame_or_angle[2]]
            else:
                rotation_zero = self.zero_frame_or_angle[2]
            rotation_angle = rotation_angle - rotation_zero
        else:
            rotation_zero = None

        # make plot in -pi to pi range
        rotation_angle = np.where(rotation_angle > np.pi, rotation_angle - 2 * np.pi, rotation_angle)
        rotation_angle = np.where(rotation_angle < -np.pi, rotation_angle + 2 * np.pi, rotation_angle)

        self.rotation = rotation_angle
        self.rotation_info = {'plane': None, 'zero_angle': rotation_zero, 'zero_frame': self.zero_frame_or_angle[2]}
        self.is_empty = False
        return self.rotation

    def zero_by_idx(self, idx):
        """
        idx is 0, 1, 2, corresponding to flexion, abduction, rotation
        usage:
        RKNEE_angles.flexion = RKNEE_angles.zero_by_idx(0)
        """
        angle = self.flexion if idx == 0 else self.abduction if idx == 1 else self.rotation
        this_zero_frame = self.zero_frame_or_angle[idx]
        if this_zero_frame is not None:
            if self.zero_by_frame_not_angle:
                zero_angle = angle[this_zero_frame]
            else:
                zero_angle = this_zero_frame
            output_angle = angle - zero_angle
            output_angle = np.where(output_angle > np.pi, output_angle - 2 * np.pi, output_angle)
            output_angle = np.where(output_angle < -np.pi, output_angle + 2 * np.pi, output_angle)
        else:
            output_angle = angle

        return output_angle

    def output_np(self):
        output_list = []
        if self.flexion is not None:
            output_list.append(self.flexion)
        if self.abduction is not None:
            output_list.append(self.abduction)
        if self.rotation is not None:
            output_list.append(self.rotation)
        return np.array(output_list)

    def plot_angles(self, joint_name='', alpha=1, linewidth=1, linestyle='-', label=None, frame_range=None, colors=['r', 'g', 'b'], overlay=None):
        """
        plot angles
        overlay: [fig, ax] to overlay on an existing plot
        """
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
        if overlay is None:
            fig, ax = plt.subplots(3, 1, sharex=True)
        else:
            fig, ax = overlay
        angle_names = ['Flexion', 'H-Abduction', 'Rotation']
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
                ax[angle_id].plot([frame_range[0], frame_range[1]], [-180, 180], color='gray', linewidth=1)

        ax[0].set_title(f'{joint_name} (deg)')
        # plt.show()
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


# todo: make them not senstive to 180 overflow errors.
def angle_diff(angle1, angle2, input_rad=True, output_rad=True):
    """
    smaller angle difference between two angles in circular space
    input -pi to pi range angles
    returns within -pi to pi range
    """
    if not input_rad:
        angle1 = np.deg2rad(angle1)
        angle2 = np.deg2rad(angle2)
    diff = angle1 - angle2
    diff = np.where(diff > np.pi, diff - 2 * np.pi, diff)
    diff = np.where(diff < -np.pi, diff + 2 * np.pi, diff)
    if not output_rad:
        diff = np.rad2deg(diff)
    return diff


def bland_altman_plot(data1, data2, title='', xlabel='Mean (\N{DEGREE SIGN})', ylabel='Difference (\N{DEGREE SIGN})', save_path=None,
                      plot_percentage=0.05, csfont={'fontname':'Times New Roman'}):
    """
    Bland-Altman plot
    data1, data2: two sets of measurements
    """
    data1 = np.rad2deg(data1)
    data2 = np.rad2deg(data2)
    mean = np.nanmean([data1, data2], axis=0)
    diff = angle_diff(data1, data2, input_rad=False, output_rad=False)
    md = np.nanmean(diff)
    sd = np.nanstd(diff, axis=0)
    # only plot 10% of the data
    idx = np.random.choice(range(len(mean)), int(len(mean) * plot_percentage), replace=False)
    plt.scatter(mean[idx], diff[idx], alpha=0.2, s=1)
    plt.axhline(md, color='red', linestyle='--')
    plt.axhline(md + 1.96 * sd, color='red', linestyle='--')
    plt.axhline(md - 1.96 * sd, color='red', linestyle='--')
    text_height = 1
    text_right_pos = 0.98 * (plt.gca().get_xlim()[1] - plt.gca().get_xlim()[0]) + plt.gca().get_xlim()[0]
    # text above the line on the right hand side "+1.9, weight='bold'6 SD, size
    t1 = plt.text(text_right_pos, md + 1.96 * sd + text_height, f'+1.96 SD: {md+1.96*sd:.1f}\N{DEGREE SIGN}', horizontalalignment='right', verticalalignment='bottom',  fontsize=19, weight='bold', **csfont)
    t2 = plt.text(text_right_pos, md - 1.96 * sd - text_height, f'-1.96 SD: {md-1.96*sd:.1f}\N{DEGREE SIGN}', horizontalalignment='right', verticalalignment='top',     fontsize=19, weight='bold', **csfont)
    t3 = plt.text(text_right_pos, md , f'Mean: {md:.1f}\N{DEGREE SIGN}',                                      horizontalalignment='right', verticalalignment='bottom',  fontsize=19, weight='bold', **csfont)
    for t in [t1, t2, t3]:
        t.set_bbox(dict(facecolor='white', alpha=0.5, edgecolor='white', linewidth=0))
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(title,    fontsize=28, weight='bold', **csfont)
    # plt.xlabel(xlabel,  fontsize=22, **csfont)
    # plt.ylabel(ylabel,  fontsize=22, **csfont)
    plt.ylim([-35, 35])
    # plt.text(0.5, 0.95, f'Mean diff: {md:.2f}, std {sd:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    if save_path is not None:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()
    return md, sd


def mean_absolute_error(data1, data2):
    """
    data1, data2: two sets of measurements
    """
    diff = angle_diff(data1, data2, input_rad=True, output_rad=False)
    return np.nanmean(np.abs(diff))


def root_mean_squared_error(data1, data2):
    """
    data1, data2: two sets of measurements
    """
    diff = angle_diff(data1, data2, input_rad=True, output_rad=False)
    return np.nanmean(diff ** 2)**0.5


# def bland_altman_plot_batch(ja1, ja2, angle_names):
#     """
#     ja1, ja2: two sets of JointAngle objects
#     set ja2 to gt
#     """
#     for angle_index, this_angle_name in enumerate(angle_names):
#
#         # md, sd = bland_altman_plot(ja1[this_angle_name].flexion, ja2[this_angle_name].flexion, title=this_angle_name) #, save_path=f'frames/MB_angles/{this_angle_name}_bland_altman.png')
#         # print(f'Visualizing - {this_angle_name}: md: {md:.2f}, sd: {sd:.2f}')
#         MSE, sd = mean_squared_error(ja1[this_angle_name].flexion, ja2[this_angle_name].flexion)
#         print(f'MSE - {this_angle_name}: mean: {MSE:.2f}, sd: {sd:.2f}')
#
#         MAE = mean_absolute_error(ja1[this_angle_name].flexion, ja2[this_angle_name].flexion)
#         print(f'MAE - {this_angle_name}: {MAE:.2f}')

# bland_altman_plot_batch(estimate_ergo_angles, GT_ergo_angles, GT_skeleton.angle_names)
#
# ja1 = GT_ergo_angles
# ja2 = estimate_ergo_angles
#
# this_angle_name = 'left_wrist'
# for i, angle in enumerate(estimate_ergo_angles[this_angle_name].flexion):
#     if np.isnan(angle):
#         print(i)