

import random as rd
import tkinter as tk
import threading
import time
from PIL import ImageGrab  # do pip3 install pillow
from PIL import Image

HEIGHT = 768
WIDTH = 360

class RandomCourt:
    def __init__(self):
        self.choice = [0, 1, 2, 3, 4]
        self.parking_or_hoop = []  # ['parking', 'hoop', ...]
        self.pos_to_put = []    # [1, 0, 3, 4, ...] max 4, min 0
        self.pos_with_tree = []
        self.tree_with_code = []


    def random(self):
        self._set_parking_or_hoop()
        self._set_pos_to_put()
        self._set_tree_pos()

    def _set_parking_or_hoop(self):
        line_all = ['parking', 'parking', 'parking']
        line_3_8 = ['hoop', 'hoop', 'hoop', 'parking', 'parking', 'parking']
        rd.shuffle(line_3_8)
        [line_all.insert(2, x) for x in line_3_8]
        self.parking_or_hoop = line_all

    def _set_pos_to_put(self):
        self.pos_to_put.clear()
        for _ in range(9):
            self.pos_to_put.append(rd.choice(self.choice))

    def _set_tree_pos(self):
        tree = []
        for i in range(12):
            tree.append(i)
        rd.shuffle(tree)
        self.pos_with_tree = tree[:10]
        self.tree_with_code = tree[:5]

    def ran_print(self):
        self.random()
        print(self.parking_or_hoop)
        print(self.pos_to_put)
        print(self.pos_with_tree)
        print(self.tree_with_code)

class Window:
    def __init__(self):
        #random thing
        self.randomcourt = RandomCourt()
        self.randomflag = False
        self.randomfreq = 0.1

        #GUI
        self.root = tk.Tk()
        self.root.title('无人机场地')
        self.root.geometry("600x800+300+20")  # on Mac x is 117 + ~  y is 25 + ~


        self.frame = tk.Frame(self.root, width=WIDTH)
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, background='grey')
        self.randombutton = tk.Button(self.frame, text='开始随机', command=self.startrandom)
        self.stopbutton = tk.Button(self.frame, text='停止随机', command=self.stoprandom)
        self.confirmbutton = tk.Button(self.frame, text='确定场地', command=self.confirmcourt)

        #draw
        self.coef = WIDTH / 15   # hard code, 450->width
        self.tree_pos = []   # tree coordinate
        self._get_12tree_coor()

        #layout and fixed
        self._set_layout()
        self._draw_court_fixed()

        #screenshot save and read
        self.url = '/Users/yuhu/Desktop/01.png'

    def startrandom(self):
        self.randombutton['state'] = tk.DISABLED
        self.stopbutton['state'] = tk.NORMAL
        self.randomflag = True

        self.t1 = threading.Thread(target=self._startrandom)
        self.t1.setDaemon(True)
        self.t1.start()

    def stoprandom(self):

        self.stopbutton['state'] = tk.DISABLED
        self.randombutton['state'] = tk.NORMAL
        self.randomflag = False

    def confirmcourt(self):
        self.confirmbutton['state'] = tk.DISABLED
        if self.getter():
            img = Image.open(self.url)
            img.show()


    def _set_layout(self):
        self.frame.pack(side=tk.BOTTOM)
        self.randombutton.pack(side=tk.LEFT, expand=tk.NO, anchor=tk.S)
        self.confirmbutton.pack(side=tk.RIGHT, expand=tk.NO, anchor=tk.S)
        self.stopbutton.pack(side=tk.RIGHT, expand=tk.NO, anchor=tk.S)
        self.canvas.pack(side=tk.TOP)



    def _startrandom(self):
        while(self.randomflag):
            time.sleep(self.randomfreq)
            self.randomcourt.random()
            self.canvas.delete('delete')
            self._canvas_update()

    def _canvas_update(self):

        #draw top court
        for i in self.randomcourt.pos_with_tree[5:]:
            self._draw_tree_base_on_pos(i, color='red')
        for j in self.randomcourt.tree_with_code:
            self._draw_tree_base_on_pos(j, color='pink')

        self._draw_sequence_base_on_pos()


    def _draw_court_fixed(self):
        self.canvas.create_rectangle(0, 0, 1.2 * self.coef, 1.2 * self.coef, fill='yellow')
        self.canvas.create_text(0.6 * self.coef, 0.6 * self.coef, text='H')
        self.canvas.create_rectangle(WIDTH - 1.2 * self.coef, 0, WIDTH, 1.2 * self.coef, fill='yellow')
        self.canvas.create_text(WIDTH - 0.6 * self.coef, 0.6 * self.coef, text='H')
        self.canvas.create_line(0, 0.375 * HEIGHT - 3, WIDTH, 0.375 * HEIGHT - 3, fill='blue', width=3)
        self.canvas.create_rectangle(WIDTH / 2 - 0.6 * self.coef, HEIGHT, WIDTH / 2 + 0.6 * self.coef,
                                     HEIGHT - 1.2 * self.coef, fill='yellow')
        self.canvas.create_text(WIDTH / 2, HEIGHT - 0.6 * self.coef, text='0')

        for i in range(9):
            self.canvas.create_line(0, (0.0625 * (9 - i) + 0.375) * HEIGHT, WIDTH,
                                    (0.0625 * (9 - i) + 0.375) * HEIGHT, dash=(2, 2))

        for i in range(5):
            self.canvas.create_line((i + 1) * WIDTH * 0.2, 0.375 * HEIGHT,  (i + 1) * WIDTH * 0.2, HEIGHT, dash=(2, 2))

    def _draw_sequence_base_on_pos(self):

        def get_outer_rec(num_y, pos_x):  # num_y 1-9    pos_x 0-4
            left_top_x = pos_x * WIDTH * 0.2
            left_top_y = (0.0625 * (9 - num_y) + 0.375) * HEIGHT
            right_bot_x = left_top_x + 0.2 * WIDTH
            right_bot_y = left_top_y + 0.0625 * HEIGHT
            return left_top_x, left_top_y, right_bot_x, right_bot_y

        def get_inner_drawing_square(x1, y1, x2, y2):
            rec_size = (y2 - y1) * 0.80
            left_top_x = x1 + ((x2 - x1) - rec_size) / 2
            left_top_y = y1 * 0.9 + y2 * 0.1
            return (left_top_x, left_top_y, left_top_x + rec_size, left_top_y + rec_size), rec_size


        for i in range(9): # 9 rows i = 0~8
            x_1, y_1, x_2, y_2 = get_outer_rec(i + 1, self.randomcourt.pos_to_put[i])
            drawing_square, inner_size = get_inner_drawing_square(x_1, y_1, x_2, y_2)
            if self.randomcourt.parking_or_hoop[i] == 'parking':
                self.canvas.create_rectangle(drawing_square, fill='yellow', tags=('delete'))
            else:
                self.canvas.create_oval(drawing_square, tags=('delete'))
            self.canvas.create_text(drawing_square[0] + inner_size / 2,
                                    drawing_square[1] + inner_size / 2, text=str(i+1), tags=('delete'))

    def _draw_tree_base_on_pos(self, pos, color='pink'):
        self.canvas.create_oval(self.tree_pos[pos], fill=color, dash=(4, 4), tags=('delete'))
        tree_rectangle = (self.tree_pos[pos][0] + self.coef * 0.75, self.tree_pos[pos][1],
                          self.tree_pos[pos][0] + self.coef * 1.25, self.tree_pos[pos][1] - self.coef / 2)
        self.canvas.create_rectangle(tree_rectangle, fill=color, tags=('delete'))

    def _get_12tree_coor(self):

        def get_one_tree_coor(x_left, y_top):
            rad = 1 * self.coef
            return x_left * self.coef, y_top * self.coef, x_left * self.coef + 2 * rad, y_top * self.coef + 2 * rad

        tree_0 = get_one_tree_coor(2.5, 1.5)
        self.tree_pos.append(tree_0)
        tree_1 = get_one_tree_coor(5, 1.5)
        self.tree_pos.append(tree_1)
        tree_2 = get_one_tree_coor(8.5, 1.5)
        self.tree_pos.append(tree_2)
        tree_3 = get_one_tree_coor(11.5, 1.5)
        self.tree_pos.append(tree_3)

        tree_4 = get_one_tree_coor(1.5, 5)  # ??
        self.tree_pos.append(tree_4)
        tree_5 = get_one_tree_coor(5, 5)
        self.tree_pos.append(tree_5)
        tree_6 = get_one_tree_coor(8.5, 5)
        self.tree_pos.append(tree_6)
        tree_7 = get_one_tree_coor(12, 5)
        self.tree_pos.append(tree_7)

        tree_8 = get_one_tree_coor(1.5, 8.5)
        self.tree_pos.append(tree_8)
        tree_9 = get_one_tree_coor(5, 8.5)
        self.tree_pos.append(tree_9)
        tree_10 = get_one_tree_coor(8.5, 8.5)
        self.tree_pos.append(tree_10)
        tree_11 = get_one_tree_coor(12, 8.5)
        self.tree_pos.append(tree_11)

    def getter(self):
        x = (self.root.winfo_rootx() + self.canvas.winfo_x()) * 2
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x+WIDTH * 2
        y1 = y * 2 + HEIGHT * 2
        print('x is {}'.format(x))
        print('y is {}'.format(y))
        print('x1 is {}'.format(x1))
        print('y1 is {}'.format(y1))
        ImageGrab.grab((x, y, x1, y1)).save(self.url)
        return 1



if __name__ == '__main__':

    a = RandomCourt()
    for _ in range(5):
        a.ran_print()


    a = Window()
    a.root.mainloop()


