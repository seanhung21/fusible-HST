from basic import *
from kserver import *
from tkinter import *
import random
import bisect
import time
import matplotlib
import matplotlib.cm as cm


class Drawing(Frame):

    def __init__(self, master=None, mass_scale=0.7):
        super().__init__(master)
        self.pack()

        self.w = master.winfo_width()
        self.h = master.winfo_height()
        self.canvas = Canvas(self, bg='white')
        self.canvas.pack(fill='both', expand=True)

        self.scale = self._scale(1500, type='w')
        self.x0 = self._scale(50, type='w')
        self.y0 = self._scale(200, type='h')
        self.node_height = self._scale(50, type='h')
        self.level_gap = self._scale(25, type='h')
        self.mass_y0 = self._scale(150, type='h')
        self.mass_height = self._scale(100, type='h')
        self.mass_width = self._scale(4, type='w')
        self.mass_scale = mass_scale

        self.node_border_color = 'white'
        self.node_border_width = self._scale(2, type='w')

        tmp_width = self._scale(4)
        self.canvas.create_line(self.x0, self.mass_y0,
                                self.x0 + self.scale, self.mass_y0,
                                width=tmp_width)
        self.canvas.create_line(self.x0, self.mass_y0,
                                self.x0, self.mass_y0 - self.mass_height,
                                width=tmp_width)
        space_width = self._scale(25, type='w')
        font_size = self._scale(14)
        self.canvas.create_text(self.x0 - space_width, self.mass_y0,
                                text=str(0), font=("Courier", font_size))
        self.canvas.create_text(self.x0 - space_width, self.mass_y0 - self.mass_height,
                                text=str(self.mass_scale), font=("Courier", font_size))

        self.cmap = cm.get_cmap('YlGnBu')

    def draw_mass(self, mass_f):
        self.canvas.delete('mass')
        for i in range(self.scale):
            m = mass_f(Interval(i / self.scale, (i+1) / self.scale))
            self.canvas.create_line(self.x0 + i, self.mass_y0,
                                    self.x0 + i,
                                    self.mass_y0 - self.mass_height * m / self.mass_scale,
                                    fill='blue', width=self.mass_width, tags='mass')

    def draw_tree(self, tree, mass_f, s_alpha):
        self.canvas.delete('tree')
        self._draw_tree(tree.root, 0, mass_f, s_alpha)

    def _draw_tree(self, node, level, mass_f, s_alpha):
        mid_pos = self._draw_node(node, level, mass_f, s_alpha)
        y_stop = self.y0 + (level + 1) * (self.node_height + self.level_gap)
        y_start = y_stop - self.level_gap
        for child in node.children:
            self.canvas.create_line(mid_pos, y_start,
                                    self._draw_tree(child, level + 1, mass_f, s_alpha),
                                    y_stop, tags='tree')
        return mid_pos

    def _draw_node(self, node, level, mass_f, s_alpha):
        mid_pos = None
        mass = 0
        for e in node.data:
            for itv in e[0].data:
                mass += mass_f(itv)
        if mass < s_alpha:
            col_string = '#b3b6b7'      # gray
        else:
            col_string = self._mass2color(mass)
        left_border = self.w
        right_border = 0
        upper = self.y0 + level * (self.node_height + self.level_gap)
        lower = upper + self.node_height
        for e in node.data:         # TODO: change mid_pos calculation
            content = e[0]
            for itv in content.data:
                if mid_pos is None:
                    mid_pos = self.x0 + int(itv.left * self.scale) + \
                              int((itv.right - itv.left) / 2 * self.scale)
                left = self.x0 + int(itv.left * self.scale)
                right = self.x0 + int(itv.right * self.scale)
                left_border = min(left_border, left)
                right_border = max(right_border, right)
                self.canvas.create_rectangle(left, upper, right, lower,
                                             fill=col_string, width=0, tags='tree')
                self.canvas.create_line(left, upper, right, upper,
                                        fill=self.node_border_color,
                                        width=self.node_border_width, tags='tree')
                self.canvas.create_line(left, lower, right, lower,
                                        fill=self.node_border_color,
                                        width=self.node_border_width, tags='tree')
        self.canvas.create_line(left_border, upper, left_border, lower,
                                fill=self.node_border_color,
                                width=self.node_border_width, tags='tree')
        self.canvas.create_line(right_border, upper, right_border, lower,
                                fill=self.node_border_color,
                                width=self.node_border_width, tags='tree')
        return mid_pos

    def _mass2color(self, mass):
        color = self.cmap(float(mass))
        return matplotlib.colors.rgb2hex(color[:3])

    def _scale(self, length, type='m'):
        w = self.w * length / 1600
        h = self.h * length / 900
        if type == 'w':
            return round(w)
        elif type == 'h':
            return round(h)
        else:
            return round(min(w, h))


class App(Frame):

    def __init__(self, kserver, mass_f, big_alpha, small_alpha, r,
                 master=None, mass_sequence=None, mass_scale=0.7):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        self.root = master

        master.update()
        self.drawing = Drawing(self, mass_scale=mass_scale)
        self.drawing.pack(side='left', fill='both', expand=True)

        self.kserver = kserver
        self.mass = mass_f
        self.b_alpha = big_alpha
        self.s_alpha = small_alpha
        self.r = r
        self.fhg = self.kserver.fuse_heavy_generator(self.mass, self.b_alpha, self.r)
        self._draw_mass()
        self._draw_tree()

        self.mass_sequence = mass_sequence
        if self.mass_sequence is not None:
            self._animate_mass_seq('<Button-1>')

    def _draw_mass(self):
        self.drawing.draw_mass(self.mass)

    def _draw_tree(self):
        self.drawing.draw_tree(self.kserver.tree, self.mass, self.s_alpha)

    def _fuse_last(self):
        for e in self.fhg:
            None

    def _fuse_last_event(self, event):
        self._fuse_last()
        self._draw_tree()

    def _animate_mass_seq(self, event):
        if self.mass_sequence is None:
            raise Exception('No input mass sequence')
        try:
            for mf in self.mass_sequence:
                self.mass = mf
                self.kserver = generate_kserver(len(self.kserver.semi_clusterings)-1)
                self.fhg = self.kserver.fuse_heavy_generator(self.mass, self.b_alpha, self.r)
                self._fuse_last()
                self._draw_mass()
                self._draw_tree()
                self.drawing.canvas.update_idletasks()
                time.sleep(0.2)
        except KeyboardInterrupt:
            self.root.destroy()


def generate_kserver(N):

    sps = []
    sps.append([Interval(0, 1)])
    for i in range(N):
        intervals = []
        for itv in sps[i]:
            mid = (itv.left + itv.right) / 2
            intervals.append(Interval(itv.left, mid))
            intervals.append(Interval(mid, itv.right))
        sps.append(intervals)
    for sp in sps:
        for i in range(len(sp)):
            sp[i] = IntervalsSet([sp[i]])
    sps = [SemiPartition(sp) for sp in sps]
    return KServer(sps)


def generate_mass_from_list(mass_list):
    num = len(mass_list)
    positions = [(2*i+1)/(2*num) for i in range(num)]

    total = 0
    for i in range(num):
        total += mass_list[i]
    mass_list = [m / total for m in mass_list]

    prefix_sum = []
    total = 0
    for m in mass_list:
        total += m
        prefix_sum.append(total)

    def mf(itv):     # itv half-closed [a, b)
        """Mass contained in the given interval.

        Args:
            itv (:obj:`Interval`): The given interval.

        Returns:
            int: The amount of mass contained in the interval.
        """
        points_list = positions
        mass_prefix = prefix_sum
        left = bisect.bisect_left(points_list, itv.left) - 1
        right = bisect.bisect_left(points_list, itv.right) - 1
        cum_mass_left = mass_prefix[left] if left >= 0 else 0
        cum_mass_right = mass_prefix[right] if right >= 0 else 0
        return cum_mass_right - cum_mass_left

    return mf


def animate_mass_sequence(sequence, mass_func_display_scale=0.7):
    """Run visualization with an input sequence of mass distributions.

    Args:
        sequence (:obj:`List` of `List`): The input sequence of mass
        distributions. Each element of the outer list is a list specifying the
        amount of mass. A list l of length n with total mass M represents a
        distribution with Prob((2i+1)/(2n)) = l[i] / M .
        mass_func_display_scale (float): A real value between 0 and 1
        specifying the display scale of the mass function. Default to 0.7.
    """
    mass_func_sequence = [generate_mass_from_list(l) for l in sequence]
    main(mass_func_sequence, mass_func_display_scale)


def main(mass_sequence, mass_func_display_scale=0.7):
    ks = generate_kserver(8)
    root = Tk()
    root.title("Visualization")
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    app = App(ks, (mass_sequence[0] if len(mass_sequence) > 0 else None),
              0.9, 0.01, 4, master=root, mass_sequence=mass_sequence,
              mass_scale=mass_func_display_scale)
    root.mainloop()
