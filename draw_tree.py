from basic import *
from kserver import *
from tkinter import *
from test import ks


class TreeDrawing:

    def __init__(self, canvas, tree):
        self.canvas = canvas
        self.tree = tree
        self.scale = 1000
        self.x0 = 300
        self.y0 = 50
        self.node_color = 0
        # self.setWindowTitle('Tree')

    def draw_tree(self):
        self._draw_tree(self.tree.root, 0)

    def _draw_tree(self, node, level):
        mid_pos = self.draw_node(node, level)
        for child in node.children:
            canvas.create_line(mid_pos, self.y0 + level * 100 + 50,
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
                canvas.create_rectangle(self.x0 + int(itv.left * self.scale),
                                        self.y0 + level * 100,
                                        self.x0 + int(itv.right * self.scale),
                                        self.y0 + level * 100 + 50,
                                        fill=col_string, width=0)
        return mid_pos


if __name__ == '__main__':
    root = Tk()
    root.title("draw_tree")

    canvas = Canvas(root, width=1600, height=900, bg='white')
    canvas.pack()

    td = TreeDrawing(canvas, ks.tree)
    td.draw_tree()

    root.mainloop()
