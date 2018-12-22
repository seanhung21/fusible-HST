from basic import *
from kserver import *
from tkinter import *
import random
import bisect
import time


class Drawing(Frame):

    def __init__(self, master=None, mass_scale=0.7):
        super().__init__(master)
        self.pack()

        self.canvas = Canvas(self, width=1600, height=900,
                             bg='white')
        self.canvas.pack()

        self.scale = 1500
        self.x0 = 50
        self.y0 = 200
        self.node_height = 50
        self.level_gap = 25
        self.mass_y0 = 150
        self.mass_height = 100
        self.mass_scale = mass_scale

        self.canvas.create_line(self.x0, self.mass_y0,
                                self.x0 + self.scale, self.mass_y0, width=4)
        self.canvas.create_line(self.x0, self.mass_y0,
                                self.x0, self.mass_y0 - self.mass_height,
                                width=4)
        self.canvas.create_text(self.x0 - 25, self.mass_y0,
                                text=str(0), font=("Courier", 14))
        self.canvas.create_text(self.x0 - 25, self.mass_y0 - self.mass_height,
                                text=str(self.mass_scale), font=("Courier", 14))

    def draw_mass(self, mass_f):
        self.canvas.delete('mass')
        for i in range(self.scale):
            m = mass_f(Interval(i / self.scale, (i+1) / self.scale))
            self.canvas.create_line(self.x0 + i, self.mass_y0,
                                    self.x0 + i,
                                    self.mass_y0 - self.mass_height * m / self.mass_scale,
                                    fill='blue', width=4, tags='mass')

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
            rg_value = 255 - min(255, int(mass * 128 + 128))
            rgb = (rg_value, rg_value, 255)
            col_string = '#' + ''.join('{:02X}'.format(c) for c in rgb)
        left_border = 1600
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
                border_color = 'white'
                border_width = 2
                self.canvas.create_rectangle(left, upper, right, lower,
                                             fill=col_string, width=0, tags='tree')
                self.canvas.create_line(left, upper, right, upper,
                                        fill=border_color, width=border_width, tags='tree')
                self.canvas.create_line(left, lower, right, lower,
                                        fill=border_color, width=border_width, tags='tree')
        self.canvas.create_line(left_border, upper, left_border, lower,
                                fill=border_color, width=border_width, tags='tree')
        self.canvas.create_line(right_border, upper, right_border, lower,
                                fill=border_color, width=border_width, tags='tree')
        return mid_pos


class App(Frame):

    def __init__(self, kserver, mass_f, big_alpha, small_alpha, r,
                 master=None, mass_sequence=None, mass_scale=0.7):
        super().__init__(master)
        self.pack()
        self.root = master

        self.drawing = Drawing(mass_scale=mass_scale)
        self.user_frame = Frame()
        self.drawing.pack(side='left')
        self.user_frame.pack(side='right', fill='y')

        input_rule = "insert <level> <left> <right>\n" + \
                     "delete <level> <value>\n" + \
                     "fusion <level> <cluster1> <cluster2>\n" + \
                     "fission <level> <cluster>\n"
        self.label = Label(self.user_frame, text=input_rule)

        self.entry = Entry(self.user_frame)
        self.button = Button(self.user_frame, text='Enter')
        self.button.pack(side="bottom")
        self.entry.pack(side="bottom")
        self.label.pack(side="bottom")
        self.kserver = kserver
        self.mass = mass_f
        self.b_alpha = big_alpha
        self.s_alpha = small_alpha
        self.r = r
        self.fhg = self.kserver.fuse_heavy_generator(self.mass, self.b_alpha, self.r)
        self._draw_mass()
        self._draw_tree()

        self.operation = StringVar()
        self.entry["textvariable"] = self.operation
        # TODO: bind 'Return' to self._do_operation
        self.button.bind('<Button-1>', self._do_operation)

        self.fuse_button = Button(self.user_frame, text='fuse (step)')
        self.fuse_all_button = Button(self.user_frame, text='fuse (last)')
        self.fuse_button.pack(side="top")
        self.fuse_all_button.pack(side="top")
        self.fuse_button.bind('<Button-1>', self._fuse_step)
        self.fuse_all_button.bind('<Button-1>', self._fuse_last_event)
        self.fusion_label0 = Label(self.user_frame, text='Last fused: ')
        self.last_fused = StringVar()
        self.fusion_label1 = Label(self.user_frame)
        self.last_fused.set('None')
        self.fusion_label1["textvariable"] = self.last_fused
        self.fusion_label0.pack()
        self.fusion_label1.pack()

        self.empty_label2 = Label(self.user_frame, text='\n\n')
        self.empty_label2.pack()

        self.param_label0 = Label(self.user_frame, text="Parameters:")
        self.param_label1 = Label(self.user_frame, text="heavy = ")
        self.param_label2 = Label(self.user_frame, text="inactive = ")
        self.param_label3 = Label(self.user_frame, text="neighbor range = ")
        self.param_entry1 = Entry(self.user_frame)
        self.param_entry2 = Entry(self.user_frame)
        self.param_entry3 = Entry(self.user_frame)
        self.param_input1 = StringVar()
        self.param_input2 = StringVar()
        self.param_input3 = StringVar()
        self.param_input1.set(str(0.9))
        self.param_input2.set(str(0.01))
        self.param_input3.set(str(4))
        self.param_entry1["textvariable"] = self.param_input1
        self.param_entry2["textvariable"] = self.param_input2
        self.param_entry3["textvariable"] = self.param_input3
        self.param_button = Button(self.user_frame, text='Apply')
        self.param_button.bind('<Button-1>', self._apply_params)

        self.param_label0.pack()
        self.param_label1.pack()
        self.param_entry1.pack()
        self.param_label2.pack()
        self.param_entry2.pack()
        self.param_label3.pack()
        self.param_entry3.pack()
        self.param_button.pack()

        self.empty_label0 = Label(self.user_frame, text='\n\n')
        self.empty_label0.pack()

        self.generate_tree_label0 = Label(self.user_frame,
                                          text='Generate New Tree:')
        self.generate_tree_label1 = Label(self.user_frame, text='levels (0~8) = ')
        self.generate_tree_entry = Entry(self.user_frame)
        self.generate_tree_button = Button(self.user_frame, text='Generate')
        self.tree_levels_input = StringVar()
        self.tree_levels_input.set(str(8))
        self.generate_tree_entry["textvariable"] = self.tree_levels_input
        self.generate_tree_button.bind('<Button-1>',
                                       self._generate_new_tree)
        self.generate_tree_label0.pack()
        self.generate_tree_label1.pack()
        self.generate_tree_entry.pack()
        self.generate_tree_button.pack()

        self.degenerate_label0 = Label(self.user_frame,
                                          text='New Degenerate Distribution:')
        self.degenerate_label1 = Label(self.user_frame, text='x (in [0, 1]) =')
        self.degenerate_entry = Entry(self.user_frame)
        self.degenerate_button = Button(self.user_frame, text='Generate')
        self.degenerate_input = StringVar()
        self.degenerate_input.set(str(0.33))
        self.degenerate_entry["textvariable"] = self.degenerate_input
        self.degenerate_button.bind('<Button-1>',
                                    self._generate_new_degenerate)
        self.degenerate_label0.pack()
        self.degenerate_label1.pack()
        self.degenerate_entry.pack()
        self.degenerate_button.pack()

        self.rand_label0 = Label(self.user_frame,
                                          text='New Random Distribution:')
        self.rand_label1 = Label(self.user_frame,
                                      text='number of points = ')
        self.rand_entry = Entry(self.user_frame)
        self.rand_button = Button(self.user_frame, text='Generate')
        self.rand_input = StringVar()
        self.rand_input.set(str(10))
        self.rand_entry["textvariable"] = self.rand_input
        self.rand_button.bind('<Button-1>',
                                   self._generate_new_rand)
        self.rand_label0.pack()
        self.rand_label1.pack()
        self.rand_entry.pack()
        self.rand_button.pack()

        self.empty_label1 = Label(self.user_frame, text='\n\n')
        self.empty_label1.pack()

        self.moving_point_label0 = Label(self.user_frame,
                                         text='Single Moving Point:')
        self.moving_point_label1 = Label(self.user_frame, text='From')
        self.moving_point_entry1 = Entry(self.user_frame)
        self.moving_point_label2 = Label(self.user_frame, text='To')
        self.moving_point_entry2 = Entry(self.user_frame)
        self.moving_point_button = Button(self.user_frame, text='Animate')
        self.moving_point_input1 = StringVar()
        self.moving_point_input1.set(str(0))
        self.moving_point_input2 = StringVar()
        self.moving_point_input2.set(str(1))
        self.moving_point_entry1["textvariable"] = self.moving_point_input1
        self.moving_point_entry2["textvariable"] = self.moving_point_input2
        self.moving_point_button.bind('<Button-1>',
                                      self._animate_moving_point)
        self.moving_point_label0.pack()
        self.moving_point_label1.pack()
        self.moving_point_entry1.pack()
        self.moving_point_label2.pack()
        self.moving_point_entry2.pack()
        self.moving_point_button.pack()

        self.rand_seq_label0 = Label(self.user_frame,
                                         text='Random Distribution Sequence:')
        self.rand_seq_label1 = Label(self.user_frame, text='sequence length = ')
        self.rand_seq_entry1 = Entry(self.user_frame)
        self.rand_seq_label2 = Label(self.user_frame, text='number of points = ')
        self.rand_seq_entry2 = Entry(self.user_frame)
        self.rand_seq_button = Button(self.user_frame, text='Animate')
        self.rand_seq_input1 = StringVar()
        self.rand_seq_input1.set(str(20))
        self.rand_seq_input2 = StringVar()
        self.rand_seq_input2.set(str(10))
        self.rand_seq_entry1["textvariable"] = self.rand_seq_input1
        self.rand_seq_entry2["textvariable"] = self.rand_seq_input2
        self.rand_seq_button.bind('<Button-1>',
                                  self._animate_rand_seq)
        self.rand_seq_label0.pack()
        self.rand_seq_label1.pack()
        self.rand_seq_entry1.pack()
        self.rand_seq_label2.pack()
        self.rand_seq_entry2.pack()
        self.rand_seq_button.pack()

        self.mass_sequence = mass_sequence
        self.mass_seq_label = Label(self.user_frame, text='Input Mass Sequence:')
        self.mass_seq_button = Button(self.user_frame, text='Animate Again')
        self.mass_seq_button.bind('<Button-1>', self._animate_mass_seq)
        self.mass_seq_label.pack()
        self.mass_seq_button.pack()
        if self.mass_sequence is not None:
            self._animate_mass_seq('<Button-1>')

    def _draw_mass(self):
        self.drawing.draw_mass(self.mass)

    def _draw_tree(self):
        self.drawing.draw_tree(self.kserver.tree, self.mass, self.s_alpha)

    def _do_operation(self, event):
        try:
            token = self.operation.get().split()
            op = token[0]
            token_num = {'insert': 4, 'delete': 3, 'fusion': 4, 'fission': 3}
            if op not in token_num.keys():
                raise Exception()
            if op == 'insert':
                self.kserver.insert(int(token[1]),
                                    Interval(float(token[2]), float(token[3])))
            elif op == 'delete':
                self.kserver.delete(int(token[1]), float(token[2]))
            if op == 'fusion':
                self.kserver.fusion(int(token[1]), int(token[2]),
                                    int(token[3]))
            elif op == 'fission':
                self.kserver.fission(int(token[1]), int(token[2]))
            self._draw_tree()
        except Exception:
            print('error')

    def _fuse_step(self, event):
        try:
            self.last_fused.set(next(self.fhg))
        except StopIteration:
            # TODO: error message
            None
        self._draw_tree()

    def _fuse_last(self):
        for e in self.fhg:
            self.last_fused.set(e)   # TODO: change only during last iteration

    def _fuse_last_event(self, event):
        self._fuse_last()
        self._draw_tree()

    def _generate_new_tree(self, event):
        try:
            N = int(self.generate_tree_entry.get())
            if N < 0:
                raise Exception()
            self.kserver = generate_kserver(N)
            self.fhg = self.kserver.fuse_heavy_generator(self.mass, self.b_alpha, self.r)
            self._draw_mass()
            self._draw_tree()
        except Exception:
            print('invalid input levels')

    def _apply_params(self, event):
        try:
            heavy = float(self.param_input1.get())
            inactive = float(self.param_input2.get())
            neighbor = int(self.param_input3.get())
            self.b_alpha = heavy
            self.s_alpha = inactive
            self.r = neighbor
            self.kserver = generate_kserver(len(self.kserver.semi_clusterings)-1)
            self.fhg = self.kserver.fuse_heavy_generator(self.mass, self.b_alpha, self.r)
            self._draw_tree()
        except Exception:
            print('invalid parameters')

    def _generate_new_degenerate(self, event):
        try:
            x = float(self.degenerate_entry.get())
            self._new_degenerate(x)
            self._draw_mass()
            self._draw_tree()
        except Exception:
            print('invalid input x')

    def _new_degenerate(self, x):
        if x < 0 or x > 1:
            raise Exception()
        self.mass = new_degenerate_mass(x)
        self.kserver = generate_kserver(len(self.kserver.semi_clusterings)-1)
        self.fhg = self.kserver.fuse_heavy_generator(self.mass, self.b_alpha, self.r)

    def _generate_new_rand(self, event):
        try:
            num = int(self.rand_entry.get())
            self._new_random(num)
            self._draw_mass()
            self._draw_tree()
        except Exception:
            print('invalid input number of points')

    def _new_random(self, num):
        if num <= 0:
            raise Exception()
        self.mass = new_random_mass(num)
        self.kserver = generate_kserver(len(self.kserver.semi_clusterings)-1)
        self.fhg = self.kserver.fuse_heavy_generator(self.mass, self.b_alpha, self.r)

    def _animate_moving_point(self, event):
        try:
            curr = float(self.moving_point_input1.get())
            end = float(self.moving_point_input2.get())
            if curr < 0 or end > 1 or curr > end:
                raise Exception()
            step = 3e-2
            while curr < end:
                self._new_degenerate(curr)
                self._fuse_last()
                self._draw_mass()
                self._draw_tree()
                self.drawing.canvas.update_idletasks()
                curr += step
            self._new_degenerate(end)
            self._fuse_last()
            self._draw_mass()
            self._draw_tree()
        except KeyboardInterrupt:
            print('you pressed ctrl-c')
            self.root.destroy()
        except Exception:
            print('invalid input range')

    def _animate_rand_seq(self, event):
        try:
            n = int(self.rand_seq_input1.get())
            num = int(self.rand_seq_input2.get())
            if n < 0:
                raise Exception()
            for i in range(n):
                self._new_random(num)
                self._fuse_last()
                self._draw_mass()
                self._draw_tree()
                self.drawing.canvas.update_idletasks()
                time.sleep(0.2)
        except KeyboardInterrupt:
            print('you pressed ctrl-c')
            self.root.destroy()
        except Exception:
            print('invalid input')

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
            print('you pressed ctrl-c')
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


def new_degenerate_mass(x):
    def m(itv):
        """Mass contained in the given interval.

        Args:
            itv (:obj:`Interval`): The given interval.

        Returns:
            int: The amount of mass contained in the interval.
        """
        if itv.contains(x):
            return 1
        else:
            return 0
    return m


def new_random_mass(num_points):
    points = []
    for i in range(num_points):
        points.append(random.random())
    points.sort()
    mass = []
    total = 0
    for i in range(num_points):
        rand = random.random()
        mass.append(rand)
        total += rand
    mass = [m / total for m in mass]

    # reduce error caused by floating points
    sum = 0
    for m in mass:
        sum += m
    diff = 1.0 - sum
    randi = random.randrange(num_points)
    tmp = mass[randi] + diff
    while tmp > 1.0 or tmp < 0.0:
        randi = random.randrange(num_points)
        tmp = mass[randi] + diff
    mass[randi] += diff

    prefix_sum = []
    total = 0
    for m in mass:
        total += m
        prefix_sum.append(total)

    def mf(itv):     # itv half-closed [a, b)
        points_list = points
        mass_prefix = prefix_sum
        left = bisect.bisect_left(points_list, itv.left) - 1
        right = bisect.bisect_left(points_list, itv.right) - 1
        cum_mass_left = mass_prefix[left] if left >= 0 else 0
        cum_mass_right = mass_prefix[right] if right >= 0 else 0
        return cum_mass_right - cum_mass_left

    return mf


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
    app = App(ks, new_degenerate_mass(0.33), 0.9, 0.01, 4,
              master=root, mass_sequence=mass_sequence,
              mass_scale=mass_func_display_scale)
    root.mainloop()


if __name__ == '__main__':
    main(None)
