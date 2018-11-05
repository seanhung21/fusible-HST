from basic import *
from kserver import *
from tkinter import *


class Drawing(Frame):

    def __init__(self, master=None):
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

        self.canvas.create_line(self.x0, self.mass_y0,
                                self.x0 + self.scale, self.mass_y0, width=4)

    def draw_mass(self, mass_f):
        self.canvas.delete('mass')
        for i in range(self.scale):
            m = mass_f(Interval(i / self.scale, (i+1) / self.scale))
            self.canvas.create_line(self.x0 + i, self.mass_y0,
                                    self.x0 + i,
                                    self.mass_y0 - self.mass_height * m,
                                    fill='blue', tags='mass')

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

    def __init__(self, kserver, mass_f, big_alpha, small_alpha, r, master=None):
        super().__init__(master)
        self.pack()

        self.drawing = Drawing()
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
        self.fuse_all_button.bind('<Button-1>', self._fuse_last)
        self.fusion_label0 = Label(self.user_frame, text='Last fused: ')
        self.last_fused = StringVar()
        self.fusion_label1 = Label(self.user_frame)
        self.last_fused.set('None')
        self.fusion_label1["textvariable"] = self.last_fused
        self.fusion_label0.pack()
        self.fusion_label1.pack()

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

    def _fuse_last(self, event):
        for e in self.fhg:
            self.last_fused.set(e)   # TODO: change only during last iteration
        self._draw_tree()


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


def generate_simple_m(x):
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


def tmp_m(itv):
    total = 0
    if itv.contains(0.3):
        total += 0.91
    if itv.contains(0.9):
        total += 0.09
    return total


if __name__ == '__main__':
    ks = generate_kserver(8)
    root = Tk()
    root.title("Visualization")
    app = App(ks, tmp_m, 0.9, 0.01, 4, master=root)
    root.mainloop()
