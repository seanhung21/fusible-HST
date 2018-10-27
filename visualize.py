from basic import *
from kserver import *
from tkinter import *


class TreeDrawing:

    def __init__(self, canvas, tree, mass_f, small_alpha):
        self.canvas = canvas
        self.tree = tree
        self.scale = 1000
        self.x0 = 300
        self.y0 = 50
        self.node_color = 0
        self.draw_tree(mass_f, small_alpha)

    def draw_tree(self, mass_f, small_alpha):
        self._draw_tree(self.tree.root, 0, mass_f, small_alpha)

    def _draw_tree(self, node, level, mass_f, small_alpha):
        mid_pos = self._draw_node(node, level, mass_f, small_alpha)
        for child in node.children:
            self.canvas.create_line(mid_pos, self.y0 + level * 100 + 50,
                                    self._draw_tree(child, level + 1, mass_f, small_alpha),
                                    self.y0 + (level + 1) * 100)
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
            # col_string = '#{0:06x}'.format(self.node_color)
            # self.node_color = (self.node_color + 100003) % 16777216

        left_border = 1600
        right_border = 0
        upper = self.y0 + level * 100
        lower = upper + 50
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
                border_color = 'black'
                self.canvas.create_rectangle(
                    left, upper, right, lower, fill=col_string, width=0)
                self.canvas.create_line(left, upper, right, upper, fill=border_color)
                self.canvas.create_line(left, lower, right, lower, fill=border_color)
        self.canvas.create_line(left_border, upper, left_border, lower, fill=border_color)
        self.canvas.create_line(right_border, upper, right_border, lower, fill=border_color)
        return mid_pos


class App(Frame):

    def __init__(self, kserver, mass_f, small_alpha, master=None):
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
        self.draw_button = Button(self.user_frame, text='Draw')
        self.draw_button.pack(side="top")
        self.button.pack(side="bottom")
        self.entry.pack(side="bottom")
        self.label.pack(side="bottom")
        self.kserver = kserver
        self.mass = mass_f
        self.s_alpha = small_alpha
        self.td = TreeDrawing(self.canvas, kserver.tree, self.mass, self.s_alpha)
        # self.td.draw_tree()

        self.operation = StringVar()
        self.entry["textvariable"] = self.operation
        # TODO: bind 'Return' to self.do_operation
        self.button.bind('<Button-1>', self.do_operation)
        self.draw_button.bind('<Button-1>', self.draw)

    def do_operation(self, event):
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
            self.canvas.delete('all')
            self.td.draw_tree()
        except Exception:
            print('error')

    def draw(self, event):
        self.td.draw_tree(self.mass, self.s_alpha)


def visualize(kserver, mass_f, small_alpha):
    root = Tk()
    root.title("draw_tree")
    app = App(kserver, mass_f, small_alpha, master=root)
    root.mainloop()
