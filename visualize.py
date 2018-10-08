from basic import *
from kserver import *
from tkinter import *


class TreeDrawing:

    def __init__(self, canvas, tree):
        self.canvas = canvas
        self.tree = tree
        self.scale = 1000
        self.x0 = 300
        self.y0 = 50
        self.node_color = 0

    def draw_tree(self):
        self._draw_tree(self.tree.root, 0)

    def _draw_tree(self, node, level):
        mid_pos = self.draw_node(node, level)
        for child in node.children:
            self.canvas.create_line(mid_pos, self.y0 + level * 100 + 50,
                                    self._draw_tree(child, level + 1),
                                    self.y0 + (level + 1) * 100)
        return mid_pos

    def draw_node(self, node, level):
        col_string = '#{0:06x}'.format(self.node_color)
        self.node_color = (self.node_color + 100003) % 16777216
        mid_pos = None
        for e in node.data:
            content = e[0]
            for itv in content.data:
                if mid_pos is None:
                    mid_pos = self.x0 + int(itv.left * self.scale) + \
                              int((itv.right - itv.left) / 2 * self.scale)
                self.canvas.create_rectangle(
                    self.x0 + int(itv.left * self.scale),
                    self.y0 + level * 100,
                    self.x0 + int(itv.right * self.scale),
                    self.y0 + level * 100 + 50,
                    fill=col_string, width=0)
        return mid_pos


class App(Frame):

    def __init__(self, kserver, master=None):
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
        self.td = TreeDrawing(self.canvas, kserver.tree)
        self.td.draw_tree()

        self.operation = StringVar()
        self.entry["textvariable"] = self.operation
        self.button.bind('<Button-1>', self.do_operation)
        # TODO: bind 'Return' to self.do_operation

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


def visualize(kserver):
    root = Tk()
    root.title("draw_tree")
    app = App(kserver, master=root)
    root.mainloop()
