#coding=gbk
import wx
import os
import time
import copy
import pdb
import random

class Sudoku:
    SCALE               = 3             # 游戏规模为 scale * scale
    GRID_NUM            = SCALE ** 2    # 每一行列的格数
    GRID_WIDTH          = 48            # 每个格子的宽
    FONT_SIZE           = 20            # 文字字号
    __puzzle_idx        = 0             # 题号，此题在题目文件中的索引，从0开始
    __progress          = 0
    __anchor_pos        = (0, 0)        # 游戏绘制起点坐标
    __puzzle_sudoku     = []            # 数独谜题二维数字, 第一维为行, 第二维为列
    __answer_sudoku     = []            # 数独答案二维数组
    __draft_sudoku      = []            # 数独草稿三维数组, 前一二维同上, 第三维为单元格中可能存在的数字
    __actived_grid      = (-1, -1)      # 当前激活格
    __actived_num       = 0             # 当前激活格中的数字
    __affected_grids    = []            # 当前激活格所影响到的范围, 每一个元素是一个单元格点
    __puzzle_lib        = []            # 数独题库


    def __init__(self, pos = (0, 0)):
        self.__anchor_pos       = pos
        self.__puzzle_sudoku    = [[0 for a in range(1, Sudoku.GRID_NUM + 1)] for b in range(Sudoku.GRID_NUM)]
        self.__answer_sudoku    = copy.deepcopy(self.__puzzle_sudoku)
        self.__draft_sudoku     = [[[] for a in range(1, Sudoku.GRID_NUM + 1)] for b in range(Sudoku.GRID_NUM)]


    def init_sudoku(self, init_str = "", puzzle_file = "game.pzl"):
        '''初始化指定谜题'''

        #如果没有指定则使用随机题
        if len(init_str) == 0:
            if len(self.__puzzle_lib) == 0:
                f = file(puzzle_file, 'r')
                self.__puzzle_lib = f.readlines()
                f.close()
            while len(init_str) == 0:
                self.__puzzle_idx = random.randint(0, len(self.__puzzle_lib) - 1)
                init_str = self.__puzzle_lib[self.__puzzle_idx].strip('\n')

        self.__puzzle_sudoku   = [[0 for a in range(1, Sudoku.GRID_NUM + 1)] for b in range(Sudoku.GRID_NUM)]
        if len(init_str) == Sudoku.GRID_NUM ** 2 and init_str.isdigit():
            for i in range(Sudoku.GRID_NUM):        # Y轴循环
                for j in range(Sudoku.GRID_NUM):    # X轴循环
                    self.__puzzle_sudoku[i][j] = int(init_str[i * Sudoku.GRID_NUM + j])

        # 初始化草稿
        self.__draft_sudoku     = [[[] for a in range(1, Sudoku.GRID_NUM + 1)] for b in range(Sudoku.GRID_NUM)]

        # 初始化答案
        self.__answer_sudoku    = copy.deepcopy(self.__puzzle_sudoku)
        self.__progress = 0
        for i in range(Sudoku.GRID_NUM):
            for j in range(Sudoku.GRID_NUM):
                if self.__answer_sudoku[i][j] != 0:
                    self.__progress += 1

        # 初始化激活区
        self.__actived_grid     = (-1, -1)
        self.__affected_grids   = []
        self.__actived_num      = 0


    def __debug_print(self, arr):
        '''在控制台调试打印数组'''
        print "----------------------"
        for i in range(len(arr)):        # Y轴循环
            for j in range(len(arr[i])):    # X轴循环
                print arr[i][j],'|',
            print
        print "----------------------"


    def get_puzzle_str(self):
        s = ''
        for i in range(Sudoku.GRID_NUM):        # Y轴循环
            for j in range(Sudoku.GRID_NUM):    # X轴循环
                s += str(self.__puzzle_sudoku[i][j])
        return s


    def get_answer_str(self):
        s = ''
        for i in range(Sudoku.GRID_NUM):        # Y轴循环
            for j in range(Sudoku.GRID_NUM):    # X轴循环
                s += str(self.__answer_sudoku[i][j])
        return s


    def get_progress(self):
        return self.__progress


    def get_puzzle_num(self):
        return self.__puzzle_idx + 1


    def get_width(self):
        return Sudoku.GRID_NUM * Sudoku.GRID_WIDTH


    def get_height(self):
        return Sudoku.GRID_NUM * Sudoku.GRID_WIDTH


    def ai_calc(self):
        '''自动计算'''
        loop = True
        while loop:
            loop = False

            # step1.计算所以空白格子中可能出现的数字
            self.__fill_draft()

            # step2.找草稿中只有一个数字的填入答案
            for i in range(Sudoku.GRID_NUM):        # Y轴循环
                for j in range(Sudoku.GRID_NUM):    # X轴循环
                    if len(self.__draft_sudoku[i][j]) == 1:
                        self.__actived_grid = (i, j)
                        self.__affected_grids = self.__get_affect(self.__actived_grid)
                        self.__actived_num = self.__draft_sudoku[i][j][0]
                        print "单元格", j, i, "只有一个可能数字", self.__draft_sudoku[i][j][0]
                        self.input_num(self.__draft_sudoku[i][j][0])
                        loop = True
                        del self.__draft_sudoku[i][j][:]
                        return


            # step3.找草稿中行列区内唯一的数字填入答案
            #self.__debug_print(self.__answer_sudoku)
            for i in range(Sudoku.GRID_NUM):        # Y轴循环
                for j in range(Sudoku.GRID_NUM):    # X轴循环
                    for k in range(len(self.__draft_sudoku[i][j])):
                        if self.__is_unique_one(self.__draft_sudoku, i, j, self.__draft_sudoku[i][j][k]):
                            # 获得新答案
                            self.__actived_grid = (i, j)
                            self.__affected_grids = self.__get_affect(self.__actived_grid)
                            self.__actived_num = self.__draft_sudoku[i][j][k]
                            print "单元格", j, i, "区内唯一数字", self.__draft_sudoku[i][j][k]
                            self.input_num(self.__draft_sudoku[i][j][k])
                            loop = True
                            del self.__draft_sudoku[i][j][:]
                            return
                            break

        # 运行到这说明根据草稿没有得到直观解，对草稿做二次排除
        self.__reduce_draft()


    def __fill_draft(self, grid = (-1, -1)):
        '''自动填充草稿

        grid - 指定的单元格, 若不指定, 则计算所有空白格'''
        if grid >= (0, 0):
            # 计算指定格子
            del self.__draft_sudoku[grid[0]][grid[1]][:]    #清空该格草稿
            if self.__answer_sudoku[grid[0]][grid[1]] <= 0:
                for k in range(1, Sudoku.GRID_NUM + 1):
                    if self.__is_unique_all(self.__answer_sudoku, grid[0], grid[1], k):
                        self.__draft_sudoku[grid[0]][grid[1]].append(k)
        else:
            # 未指定格子, 计算全部
            for i in range(Sudoku.GRID_NUM):        # Y轴循环
                for j in range(Sudoku.GRID_NUM):    # X轴循环
                    self.__fill_draft((i, j))


    def __reduce_draft(self):
        '''对草稿二次处理，继续排出不可能的数字'''
        # 循环9个区
        for i in range(Sudoku.SCALE):       # Y
            for j in range(Sudoku.SCALE):   # X
                # 在每个区中探查每个数字
                for n in range(1, Sudoku.GRID_NUM + 1):
                    x_uniq = -1
                    y_uniq = -1
                    for y in range(i * Sudoku.SCALE, (i + 1) * Sudoku.SCALE):
                        for x in range(j * Sudoku.SCALE, (j + 1) * Sudoku.SCALE):
                            if n in self.__draft_sudoku[y][x]:
                                if x_uniq == -1:
                                    x_uniq = x
                                elif x_uniq != x:
                                    # 这表示此当前查找的数字存在于2个x坐标中，没有帮助
                                    x_uniq = -2

                                if y_uniq == -1:
                                    y_uniq = y
                                elif y_uniq != y:
                                    y_uniq = -2
                    if x_uniq > 0:
                        # 此n已在此区独占x_uniq轴，与其同列的另外两区中x_uniq上不可能存在n
                        for yy in range(Sudoku.GRID_NUM):
                            if (yy // Sudoku.SCALE) != i and n in self.__draft_sudoku[yy][x_uniq]:
                                print x_uniq, yy, "不应有", n, "已被", j, i, "区独占"
                                self.__draft_sudoku[yy][x_uniq].remove(n)

                    if y_uniq > 0:
                        for xx in range(Sudoku.GRID_NUM):
                            if (xx // Sudoku.SCALE) != j and n in self.__draft_sudoku[y_uniq][xx]:
                                print xx, y_uniq, "不应有", n, "已被", j, i, "区独占"
                                self.__draft_sudoku[y_uniq][xx].remove(n)


    def __take_draft(self):
        '''自动移除草稿'''
        pass


    def __clear_draft(self, row, col, num):
        """清除指定格行列区中指定数字的草稿"""
        for i in range(Sudoku.GRID_NUM):        # Y轴循环
            for j in range(Sudoku.GRID_NUM):    # X轴循环
                if row == i and col == j:   # 同格, 清除该格内所有草稿
                    del self.__draft_sudoku[i][j][:]
                    continue
                else:
                    erase = False
                    if row == i:  # 同行
                        erase = True
                    elif col == j:  # 同列
                        erase = True
                    elif row // Sudoku.SCALE == i // Sudoku.SCALE and col // Sudoku.SCALE == j // Sudoku.SCALE:     # 同区
                        erase = True;

                    if erase and num in self.__draft_sudoku[i][j]:  # 同行/列/区, 清除草稿中的该数字
                        self.__draft_sudoku[i][j].remove(num)


    def __is_unique_all(self, arr, row, col, var = 0):
        '''检查指定位置数字是否行列区内唯一

        arr[row][col]可以是整形数字, 也可以是list
        如果var小于0, 则使用arr[row][col]进行判断
        唯一返回True, 否则返回False'''
        return self.__is_unique_row(arr, row, col, var) and self.__is_unique_col(arr, row, col, var) and self.__is_unique_zone(arr, row, col, var)


    def __is_unique_one(self, arr, row, col, var = 0):
        '''检查指定位置数字是否行或列或区内唯一

        arr[row][col]可以是整形数字, 也可以是list
        如果var小于0, 则使用arr[row][col]进行判断
        唯一返回True, 否则返回False'''
        #print self.__is_unique_row(arr, row, col, var)
        #print self.__is_unique_col(arr, row, col, var)
        #print self.__is_unique_zone(arr, row, col, var)
        return self.__is_unique_row(arr, row, col, var) or self.__is_unique_col(arr, row, col, var) or self.__is_unique_zone(arr, row, col, var)


    def __is_unique_row(self, arr, row, col, var = 0):
        '''检查指定位置数字是否行内唯一

        arr[row][col]可以是整形数字, 也可以是list
        如果var小于0, 则使用arr[row][col]进行判断.
        唯一返回True, 否则返回False'''
        if var <= 0:
            var = arr[row][col]
        if var > 0:
            for i in range(len(arr[row])):
                if i != col:
                    if type(0) == type(arr[row][i]):
                        if var == arr[row][i]:
                            return False
                    elif type([]) == type(arr[row][i]):
                        if var in arr[row][i]:
                            return False

        return True


    def __is_unique_col(self, arr, row, col, var = 0):
        '''检查指定位置数字是否列内唯一

        arr[row][col]可以是整形数字, 也可以是list
        如果var小于0, 则使用arr[row][col]进行判断
        唯一返回True, 否则返回False'''
        if var <= 0:
            var = arr[row][col]
        if var > 0:
            for i in range(len(arr)):
                if i != row:
                    if type(0) == type(arr[i][col]):
                        if var == arr[i][col]:
                            return False    # 在列内找到重复数字
                    elif type([]) == type(arr[i][col]):
                        if var in arr[i][col]:
                            return False

        return True


    def __is_unique_zone(self, arr, row, col, var = 0):
        '''检查指定位置数字是否区内唯一

        arr[row][col]可以是整形数字, 也可以是list
        如果var小于0, 则使用arr[row][col]进行判断
        唯一返回True, 否则返回False'''
        if var <= 0:
            var = arr[row][col]
        # 找到该区内第一个格子的位置
        if var > 0:
            start_row = (row // Sudoku.SCALE) * Sudoku.SCALE
            start_col = (col // Sudoku.SCALE) * Sudoku.SCALE
            for i in range(Sudoku.SCALE):
                for j in range(Sudoku.SCALE):
                    if start_row + i != row or start_col + j != col:
                        #print "i:",i,", j",j
                        if type(0) == type(arr[start_row + i][start_col + j]):
                            if var == arr[start_row + i][start_col + j]:
                                return False    # 在区内找到重复数字
                        elif type([]) == type(arr[start_row + i][start_col + j]):
                            #print var, 'in', arr[start_row + i][start_col + j]
                            if var in arr[start_row + i][start_col + j]:
                                return False    # 在区内找到重复数字

        return True

    def __get_affect(self, grid):
        '''返回与指定格有影响的格子'''
        result_list = []
        if grid >= (0, 0) and grid <= (Sudoku.GRID_NUM - 1, Sudoku.GRID_NUM - 1):
            for i in range(Sudoku.GRID_NUM):
                for j in range(Sudoku.GRID_NUM):
                    if i == grid[0] or j == grid[1] or (i // Sudoku.SCALE == grid[0] // Sudoku.SCALE and j // Sudoku.SCALE == grid[1] // Sudoku.SCALE):
                        result_list.append((i, j))
        return result_list


    def __get_same_row(self, grid):
        '''获得与指定格同一行的格子'''
        result_list = []
        if grid >= (0, 0) and grid <= (Sudoku.GRID_NUM - 1, Sudoku.GRID_NUM - 1):
            for j in range(Sudoku.GRID_NUM):
                result_list.append(grid[0], j)
        return result_list


    def __get_same_col(self, grid):
        '''获得与指定格同一列的格子'''
        result_list = []
        if grid >= (0, 0) and grid <= (Sudoku.GRID_NUM - 1, Sudoku.GRID_NUM - 1):
            for i in range(Sudoku.GRID_NUM):
                result_list.append(i, grid[1])
        return result_list


    def __get_same_area(self, grid):
        '''获得与指定格同一列的格子'''
        result_list = []
        if grid >= (0, 0) and grid <= (Sudoku.GRID_NUM - 1, Sudoku.GRID_NUM - 1):
            for i in range(Sudoku.GRID_NUM):
                for j in range(Sudoku.GRID_NUM):
                    if i // Sudoku.SCALE == grid[0] // Sudoku.SCALE and j // Sudoku.SCALE == grid[1] // Sudoku.SCALE:
                        result_list.append(i, j)
        return result_list


    def __check_answer(self):
        '''检查是否符合数独规则'''
        check_pass = True

        for i in range(Sudoku.GRID_NUM):
            for j in range(Sudoku.GRID_NUM):
                if self.__answer_sudoku[i][j] > 0:
                    for grid in self.__get_affect((i, j)):
                        if grid != (i, j):
                            if self.__answer_sudoku[grid[0]][grid[1]] == self.__answer_sudoku[i][j]:
                                if i == grid[0]:
                                    print "数字[%d, %d]与[%d, %d]行内冲突!" % (i, j, grid[0], grid[1])
                                elif j == grid[1]:
                                    print "数字[%d, %d]与[%d, %d]列内冲突!" % (i, j, grid[0], grid[1])
                                else:
                                    print "数字[%d, %d]与[%d, %d]区内冲突!" % (i, j, grid[0], grid[1])
                                check_pass = False
                                return

        if check_pass:
            all_fill = True
            for i in range(len(self.__answer_sudoku)):
                if 0 in self.__answer_sudoku[i]:
                    all_fill = False
                    break
            if all_fill:
                print "答案符合规则,检查通过!"


    def paint(self, dc):
        '''绘制数独'''
        self.__paint_affected(dc)
        self.__paint_actived(dc)
        self.__paint_grid(dc)
        self.__paint_current_grid(dc)
        self.__paint_puzzle(dc)
        self.__paint_answer(dc)
        self.__paint_draft(dc)


    def __paint_affected(self, dc):
        '''绘制被影响的区域'''
        dc.SetBrush(wx.Brush("#EEEEEE"))
        dc.SetPen(wx.Pen("#EEEEEE"));
        for grid in self.__affected_grids:
            dc.DrawRectangle(self.__anchor_pos[0] + grid[1] * Sudoku.GRID_WIDTH, self.__anchor_pos[1] + grid[0] * Sudoku.GRID_WIDTH, Sudoku.GRID_WIDTH, Sudoku.GRID_WIDTH)

        #for i in range(Sudoku.GRID_NUM):        # Y轴循环
            #for j in range(Sudoku.GRID_NUM):    # X轴循环
                #if self.__affected_area[i][j] > 0:
                    #dc.DrawRectangle(self.__anchor_pos[0] + j * Sudoku.GRID_WIDTH, self.__anchor_pos[1] + i * Sudoku.GRID_WIDTH, Sudoku.GRID_WIDTH, Sudoku.GRID_WIDTH)

    def __paint_actived(self, dc):
        '''绘制当前激活与可能激活的数字区域'''
        if self.__actived_num > 0:
            dc.SetBrush(wx.Brush("#D4FFD4"))
            for i in range(Sudoku.GRID_NUM):        # Y轴循环
                for j in range(Sudoku.GRID_NUM):    # X轴循环
                    if self.__answer_sudoku[i][j] == self.__actived_num:
                        dc.SetPen(wx.Pen("#D4FFD4"))
                        dc.DrawRectangle(self.__anchor_pos[0] + j * Sudoku.GRID_WIDTH, self.__anchor_pos[1] + i * Sudoku.GRID_WIDTH, Sudoku.GRID_WIDTH, Sudoku.GRID_WIDTH)
                    elif self.__actived_num in self.__draft_sudoku[i][j]:
                        idx = self.__draft_sudoku[i][j].index(self.__actived_num)
                        x = j * Sudoku.GRID_WIDTH + self.__anchor_pos[0] + (idx % Sudoku.SCALE) * Sudoku.GRID_WIDTH / Sudoku.SCALE
                        y = i * Sudoku.GRID_WIDTH + self.__anchor_pos[1] + (idx // Sudoku.SCALE) * Sudoku.GRID_WIDTH / Sudoku.SCALE
                        dc.SetPen(wx.Pen("Gray"))
                        dc.DrawRectangle(x, y, Sudoku.GRID_WIDTH / Sudoku.SCALE, Sudoku.GRID_WIDTH / Sudoku.SCALE)


    def __paint_current_grid(self, dc):
        if self.__actived_grid >= (0, 0):
            #dc.SetBrush(wx.Brush("#BBBBBB"))
            dc.SetPen(wx.Pen("#89BDE5", 3, wx.SOLID));
            dc.DrawRectangle(self.__anchor_pos[0] + self.__actived_grid[1] * Sudoku.GRID_WIDTH + 2, self.__anchor_pos[1] + self.__actived_grid[0] * Sudoku.GRID_WIDTH + 2, Sudoku.GRID_WIDTH - 3, Sudoku.GRID_WIDTH - 3)
            pass


    def __paint_grid(self, dc):
        '''绘制框架'''
        myPen = wx.Pen("Black", 1, wx.SOLID)

        for i in range(0, Sudoku.GRID_NUM + 1):
            if i % Sudoku.SCALE == 0:
                myPen.SetWidth(3)
            else:
                myPen.SetWidth(1)
            dc.SetPen(myPen)

            # 横线
            dc.DrawLine(self.__anchor_pos[0], self.__anchor_pos[1] + i * Sudoku.GRID_WIDTH, self.__anchor_pos[0] + Sudoku.GRID_NUM * Sudoku.GRID_WIDTH, self.__anchor_pos[1] + i * Sudoku.GRID_WIDTH)
            # 竖线
            dc.DrawLine(self.__anchor_pos[0] + i * Sudoku.GRID_WIDTH, self.__anchor_pos[1], self.__anchor_pos[0] + i * Sudoku.GRID_WIDTH, self.__anchor_pos[1] + Sudoku.GRID_NUM * Sudoku.GRID_WIDTH)


    def __draw_num(self, dc, row, col, num, tp = 1, idx = 0):
        '''在指定位置绘制数字

        num     要绘制的数字
        tp      数字类型 1:原始数字 2:答案 3:备注
        idx     备注数字的位置'''
        offset_x = 0
        offset_y = 0
        if tp == 1 or tp == 2:
            # 绘制原始数字或答案
            myFont = wx.Font(Sudoku.FONT_SIZE, wx.SWISS, wx.NORMAL, wx.BOLD)
            dc.SetFont(myFont)
            if tp == 1:
                # 谜题数字颜色
                dc.SetTextForeground("Black");
            else:
                if self.__is_unique_all(self.__answer_sudoku, row, col):
                    # 答案颜色
                    dc.SetTextForeground("#097AD1");
                else:
                    # 冲突答案颜色
                    dc.SetTextForeground("Red");

            offset_x = (Sudoku.GRID_WIDTH - dc.GetTextExtent(str(num))[0]) / 2
            offset_y = (Sudoku.GRID_WIDTH - dc.GetTextExtent(str(num))[1]) / 2 + 1     # Y轴上向下偏移一个像素, 避免太过靠上
        else:
            # 绘制备注数字
            myFont = wx.Font(Sudoku.FONT_SIZE / 2, wx.SWISS, wx.NORMAL, wx.NORMAL)
            dc.SetFont(myFont)
            dc.SetTextForeground("#A1A1A1");

            offset_x = (Sudoku.GRID_WIDTH / Sudoku.SCALE - dc.GetTextExtent(str(num))[0]) / 2
            offset_x += (idx % Sudoku.SCALE) * Sudoku.GRID_WIDTH / Sudoku.SCALE
            offset_y = (Sudoku.GRID_WIDTH / Sudoku.SCALE - dc.GetTextExtent(str(num))[1]) / 2 + 1  # Y轴上向下偏移一个像素, 避免太过靠上
            offset_y += (idx // Sudoku.SCALE) * Sudoku.GRID_WIDTH / Sudoku.SCALE

        dc.DrawText(str(num), self.__anchor_pos[0] + col * Sudoku.GRID_WIDTH + offset_x, self.__anchor_pos[1] + row * Sudoku.GRID_WIDTH + offset_y)


    def __paint_puzzle(self, dc):
        '''绘制初始数字'''
        for i in range(Sudoku.GRID_NUM):        # Y轴循环
            for j in range(Sudoku.GRID_NUM):    # X轴循环
                if self.__puzzle_sudoku[i][j] > 0:
                    self.__draw_num(dc, i, j, self.__puzzle_sudoku[i][j], 1)


    def __paint_answer(self, dc):
        '''绘制答案数字'''
        for i in range(Sudoku.GRID_NUM):        # Y轴循环
            for j in range(Sudoku.GRID_NUM):    # X轴循环
                if self.__puzzle_sudoku[i][j] == 0 and self.__answer_sudoku[i][j] > 0:
                    self.__draw_num(dc, i, j, self.__answer_sudoku[i][j], 2)


    def __paint_draft(self, dc):
        '''绘制草稿'''
        for i in range(Sudoku.GRID_NUM):        # Y轴循环
            for j in range(Sudoku.GRID_NUM):    # X轴循环
                if self.__answer_sudoku[i][j] <= 0:
                    for k in range(len(self.__draft_sudoku[i][j])):
                        self.__draw_num(dc, i, j, self.__draft_sudoku[i][j][k], 3, k)


    def active_grid(self, pos = (0, 0)):
        '''处理左键点击事件

        计算当前激活数字以及受影响区域'''
        if pos > (0, 0):
            row = (pos[1] - self.__anchor_pos[1]) // Sudoku.GRID_WIDTH
            col = (pos[0] - self.__anchor_pos[0]) // Sudoku.GRID_WIDTH
        else:
            row = self.__actived_grid[0]
            col = self.__actived_grid[1]
        if row in range(Sudoku.GRID_NUM) and col in range(Sudoku.GRID_NUM) and (row, col) != self.__actived_grid:
            # 点击落在有效范围内
            self.__actived_grid = (row, col)
            self.__actived_num = self.__answer_sudoku[row][col]    # 激活数字
            self.__affected_grids = self.__get_affect(self.__actived_grid)


    def input_num(self, num):
        '''在当前激活格输入数字'''
        if num in range(1, Sudoku.GRID_NUM + 1) and self.__actived_grid >= (0, 0):
            if self.__puzzle_sudoku[self.__actived_grid[0]][self.__actived_grid[1]] == 0:
                self.__answer_sudoku[self.__actived_grid[0]][self.__actived_grid[1]] = num
                self.__actived_num = num
                self.__progress += 1

                for grid in self.__affected_grids:
                    self.__fill_draft(grid)

                #self.__check_answer()


    def cancel_num(self, pos = (0, 0)):
        '''清除当前激活格答案'''
        if pos > (0, 0):
            row = (pos[1] - self.__anchor_pos[1]) // Sudoku.GRID_WIDTH
            col = (pos[0] - self.__anchor_pos[0]) // Sudoku.GRID_WIDTH
        else:
            row = self.__actived_grid[0]
            col = self.__actived_grid[1]

        if self.__puzzle_sudoku[row][col] <= 0:
            self.__answer_sudoku[row][col] = 0
            self.__actived_num = 0
            self.__progress -= 1

            for grid in self.__affected_grids:
                self.__fill_draft(grid)


if __name__ == "__main__":
    print "I'm Sudoku class."

