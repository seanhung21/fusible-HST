from basic import *
from kserver import *
from tkinter import *
from main import generate_kserver


class TreeDrawing:

    def __init__(self, canvas, tree, mass_f, small_alpha):
        self.canvas = canvas
        self.tree = tree
        self.mass = mass_f
        self.s_alpha = small_alpha
        self.scale = 1500
        self.x0 = 50
        self.y0 = 200
        self.node_height = 50
        self.level_gap = 25
        self.node_color = 0
        self.draw_mass(mass_f, 150, 100, small_alpha)
        self.draw_tree(mass_f, small_alpha)

    def draw_tree(self, mass_f, small_alpha):
        self._draw_tree(self.tree.root, 0, mass_f, small_alpha)

    def _draw_tree(self, node, level, mass_f, small_alpha):
        mid_pos = self._draw_node(node, level, mass_f, small_alpha)
        y_stop = self.y0 + (level + 1) * (self.node_height + self.level_gap)
        y_start = y_stop - self.level_gap
        for child in node.children:
            self.canvas.create_line(mid_pos, y_start,
                                    self._draw_tree(child, level + 1, mass_f, small_alpha),
                                    y_stop, tags='tree')
        return mid_pos

    def _draw_node(self, node, level, mass_f, small_alpha):
        mid_pos = None
        mass = 0
        for e in node.data:
            for itv in e[0].data:
                mass += mass_f(itv)
        if mass < small_alpha:
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

    def draw_mass(self, mass_f, y0, height, alpha):
        self.canvas.create_line(self.x0, y0, self.x0 + self.scale, y0,
                                width=4)
        for i in range(self.scale):
            m = mass_f(Interval(i / self.scale, (i+1) / self.scale))
            self.canvas.create_line(self.x0 + i, y0,
                                    self.x0 + i, y0 - height * m,
                                    fill='blue')

    def update_tree(self):
        self.canvas.delete('tree')
        self.draw_tree(self.mass, self.s_alpha)


class App(Frame):

    def __init__(self, kserver, mass_f, big_alpha, small_alpha, r, master=None):
        super().__init__(master)
        self.pack()

        self.canvas_frame = Frame()
        self.user_frame = Frame()
        self.canvas_frame.pack(side='left')
        self.user_frame.pack(side='right', fill='y')

        self.canvas = Canvas(self.canvas_frame, width=1600, height=900,
                             bg='white')
        self.canvas.pack()

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
        self.td = TreeDrawing(self.canvas, kserver.tree, self.mass, self.s_alpha)

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
            self.td.update_tree()
        except Exception:
            print('error')

    def _fuse_step(self, event):
        try:
            self.last_fused.set(next(self.fhg))
        except StopIteration:
            # TODO: error message
            None
        self.td.update_tree()

    def _fuse_last(self, event):
        for e in self.fhg:
            self.last_fused.set(e)   # TODO: change only during last iteration
        self.td.update_tree()


def visualize(kserver, mass_f, big_alpha, small_alpha, r):
    root = Tk()
    root.title("draw_tree")
    app = App(kserver, mass_f, big_alpha, small_alpha, r, master=root)
    root.mainloop()
