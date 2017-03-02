#coding=gbk
import wx
import os
import time
import copy
import pdb
import random

class Sudoku:
    SCALE               = 3             # ��Ϸ��ģΪ scale * scale
    GRID_NUM            = SCALE ** 2    # ÿһ���еĸ���
    GRID_WIDTH          = 48            # ÿ�����ӵĿ�
    FONT_SIZE           = 20            # �����ֺ�
    __puzzle_idx        = 0             # ��ţ���������Ŀ�ļ��е���������0��ʼ
    __progress          = 0
    __anchor_pos        = (0, 0)        # ��Ϸ�����������
    __puzzle_sudoku     = []            # ���������ά����, ��һάΪ��, �ڶ�άΪ��
    __answer_sudoku     = []            # �����𰸶�ά����
    __draft_sudoku      = []            # �����ݸ���ά����, ǰһ��άͬ��, ����άΪ��Ԫ���п��ܴ��ڵ�����
    __actived_grid      = (-1, -1)      # ��ǰ�����
    __actived_num       = 0             # ��ǰ������е�����
    __affected_grids    = []            # ��ǰ�������Ӱ�쵽�ķ�Χ, ÿһ��Ԫ����һ����Ԫ���
    __puzzle_lib        = []            # �������


    def __init__(self, pos = (0, 0)):
        self.__anchor_pos       = pos
        self.__puzzle_sudoku    = [[0 for a in range(1, Sudoku.GRID_NUM + 1)] for b in range(Sudoku.GRID_NUM)]
        self.__answer_sudoku    = copy.deepcopy(self.__puzzle_sudoku)
        self.__draft_sudoku     = [[[] for a in range(1, Sudoku.GRID_NUM + 1)] for b in range(Sudoku.GRID_NUM)]


    def init_sudoku(self, init_str = "", puzzle_file = "game.pzl"):
        '''��ʼ��ָ������'''

        #���û��ָ����ʹ�������
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
            for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
                for j in range(Sudoku.GRID_NUM):    # X��ѭ��
                    self.__puzzle_sudoku[i][j] = int(init_str[i * Sudoku.GRID_NUM + j])

        # ��ʼ���ݸ�
        self.__draft_sudoku     = [[[] for a in range(1, Sudoku.GRID_NUM + 1)] for b in range(Sudoku.GRID_NUM)]

        # ��ʼ����
        self.__answer_sudoku    = copy.deepcopy(self.__puzzle_sudoku)
        self.__progress = 0
        for i in range(Sudoku.GRID_NUM):
            for j in range(Sudoku.GRID_NUM):
                if self.__answer_sudoku[i][j] != 0:
                    self.__progress += 1

        # ��ʼ��������
        self.__actived_grid     = (-1, -1)
        self.__affected_grids   = []
        self.__actived_num      = 0


    def __debug_print(self, arr):
        '''�ڿ���̨���Դ�ӡ����'''
        print "----------------------"
        for i in range(len(arr)):        # Y��ѭ��
            for j in range(len(arr[i])):    # X��ѭ��
                print arr[i][j],'|',
            print
        print "----------------------"


    def get_puzzle_str(self):
        s = ''
        for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
            for j in range(Sudoku.GRID_NUM):    # X��ѭ��
                s += str(self.__puzzle_sudoku[i][j])
        return s


    def get_answer_str(self):
        s = ''
        for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
            for j in range(Sudoku.GRID_NUM):    # X��ѭ��
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
        '''�Զ�����'''
        loop = True
        while loop:
            loop = False

            # step1.�������Կհ׸����п��ܳ��ֵ�����
            self.__fill_draft()

            # step2.�Ҳݸ���ֻ��һ�����ֵ������
            for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
                for j in range(Sudoku.GRID_NUM):    # X��ѭ��
                    if len(self.__draft_sudoku[i][j]) == 1:
                        self.__actived_grid = (i, j)
                        self.__affected_grids = self.__get_affect(self.__actived_grid)
                        self.__actived_num = self.__draft_sudoku[i][j][0]
                        print "��Ԫ��", j, i, "ֻ��һ����������", self.__draft_sudoku[i][j][0]
                        self.input_num(self.__draft_sudoku[i][j][0])
                        loop = True
                        del self.__draft_sudoku[i][j][:]
                        return


            # step3.�Ҳݸ�����������Ψһ�����������
            #self.__debug_print(self.__answer_sudoku)
            for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
                for j in range(Sudoku.GRID_NUM):    # X��ѭ��
                    for k in range(len(self.__draft_sudoku[i][j])):
                        if self.__is_unique_one(self.__draft_sudoku, i, j, self.__draft_sudoku[i][j][k]):
                            # ����´�
                            self.__actived_grid = (i, j)
                            self.__affected_grids = self.__get_affect(self.__actived_grid)
                            self.__actived_num = self.__draft_sudoku[i][j][k]
                            print "��Ԫ��", j, i, "����Ψһ����", self.__draft_sudoku[i][j][k]
                            self.input_num(self.__draft_sudoku[i][j][k])
                            loop = True
                            del self.__draft_sudoku[i][j][:]
                            return
                            break

        # ���е���˵�����ݲݸ�û�еõ�ֱ�۽⣬�Բݸ��������ų�
        self.__reduce_draft()


    def __fill_draft(self, grid = (-1, -1)):
        '''�Զ����ݸ�

        grid - ָ���ĵ�Ԫ��, ����ָ��, ��������пհ׸�'''
        if grid >= (0, 0):
            # ����ָ������
            del self.__draft_sudoku[grid[0]][grid[1]][:]    #��ոø�ݸ�
            if self.__answer_sudoku[grid[0]][grid[1]] <= 0:
                for k in range(1, Sudoku.GRID_NUM + 1):
                    if self.__is_unique_all(self.__answer_sudoku, grid[0], grid[1], k):
                        self.__draft_sudoku[grid[0]][grid[1]].append(k)
        else:
            # δָ������, ����ȫ��
            for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
                for j in range(Sudoku.GRID_NUM):    # X��ѭ��
                    self.__fill_draft((i, j))


    def __reduce_draft(self):
        '''�Բݸ���δ��������ų������ܵ�����'''
        # ѭ��9����
        for i in range(Sudoku.SCALE):       # Y
            for j in range(Sudoku.SCALE):   # X
                # ��ÿ������̽��ÿ������
                for n in range(1, Sudoku.GRID_NUM + 1):
                    x_uniq = -1
                    y_uniq = -1
                    for y in range(i * Sudoku.SCALE, (i + 1) * Sudoku.SCALE):
                        for x in range(j * Sudoku.SCALE, (j + 1) * Sudoku.SCALE):
                            if n in self.__draft_sudoku[y][x]:
                                if x_uniq == -1:
                                    x_uniq = x
                                elif x_uniq != x:
                                    # ���ʾ�˵�ǰ���ҵ����ִ�����2��x�����У�û�а���
                                    x_uniq = -2

                                if y_uniq == -1:
                                    y_uniq = y
                                elif y_uniq != y:
                                    y_uniq = -2
                    if x_uniq > 0:
                        # ��n���ڴ�����ռx_uniq�ᣬ����ͬ�е�����������x_uniq�ϲ����ܴ���n
                        for yy in range(Sudoku.GRID_NUM):
                            if (yy // Sudoku.SCALE) != i and n in self.__draft_sudoku[yy][x_uniq]:
                                print x_uniq, yy, "��Ӧ��", n, "�ѱ�", j, i, "����ռ"
                                self.__draft_sudoku[yy][x_uniq].remove(n)

                    if y_uniq > 0:
                        for xx in range(Sudoku.GRID_NUM):
                            if (xx // Sudoku.SCALE) != j and n in self.__draft_sudoku[y_uniq][xx]:
                                print xx, y_uniq, "��Ӧ��", n, "�ѱ�", j, i, "����ռ"
                                self.__draft_sudoku[y_uniq][xx].remove(n)


    def __take_draft(self):
        '''�Զ��Ƴ��ݸ�'''
        pass


    def __clear_draft(self, row, col, num):
        """���ָ������������ָ�����ֵĲݸ�"""
        for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
            for j in range(Sudoku.GRID_NUM):    # X��ѭ��
                if row == i and col == j:   # ͬ��, ����ø������вݸ�
                    del self.__draft_sudoku[i][j][:]
                    continue
                else:
                    erase = False
                    if row == i:  # ͬ��
                        erase = True
                    elif col == j:  # ͬ��
                        erase = True
                    elif row // Sudoku.SCALE == i // Sudoku.SCALE and col // Sudoku.SCALE == j // Sudoku.SCALE:     # ͬ��
                        erase = True;

                    if erase and num in self.__draft_sudoku[i][j]:  # ͬ��/��/��, ����ݸ��еĸ�����
                        self.__draft_sudoku[i][j].remove(num)


    def __is_unique_all(self, arr, row, col, var = 0):
        '''���ָ��λ�������Ƿ���������Ψһ

        arr[row][col]��������������, Ҳ������list
        ���varС��0, ��ʹ��arr[row][col]�����ж�
        Ψһ����True, ���򷵻�False'''
        return self.__is_unique_row(arr, row, col, var) and self.__is_unique_col(arr, row, col, var) and self.__is_unique_zone(arr, row, col, var)


    def __is_unique_one(self, arr, row, col, var = 0):
        '''���ָ��λ�������Ƿ��л��л�����Ψһ

        arr[row][col]��������������, Ҳ������list
        ���varС��0, ��ʹ��arr[row][col]�����ж�
        Ψһ����True, ���򷵻�False'''
        #print self.__is_unique_row(arr, row, col, var)
        #print self.__is_unique_col(arr, row, col, var)
        #print self.__is_unique_zone(arr, row, col, var)
        return self.__is_unique_row(arr, row, col, var) or self.__is_unique_col(arr, row, col, var) or self.__is_unique_zone(arr, row, col, var)


    def __is_unique_row(self, arr, row, col, var = 0):
        '''���ָ��λ�������Ƿ�����Ψһ

        arr[row][col]��������������, Ҳ������list
        ���varС��0, ��ʹ��arr[row][col]�����ж�.
        Ψһ����True, ���򷵻�False'''
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
        '''���ָ��λ�������Ƿ�����Ψһ

        arr[row][col]��������������, Ҳ������list
        ���varС��0, ��ʹ��arr[row][col]�����ж�
        Ψһ����True, ���򷵻�False'''
        if var <= 0:
            var = arr[row][col]
        if var > 0:
            for i in range(len(arr)):
                if i != row:
                    if type(0) == type(arr[i][col]):
                        if var == arr[i][col]:
                            return False    # �������ҵ��ظ�����
                    elif type([]) == type(arr[i][col]):
                        if var in arr[i][col]:
                            return False

        return True


    def __is_unique_zone(self, arr, row, col, var = 0):
        '''���ָ��λ�������Ƿ�����Ψһ

        arr[row][col]��������������, Ҳ������list
        ���varС��0, ��ʹ��arr[row][col]�����ж�
        Ψһ����True, ���򷵻�False'''
        if var <= 0:
            var = arr[row][col]
        # �ҵ������ڵ�һ�����ӵ�λ��
        if var > 0:
            start_row = (row // Sudoku.SCALE) * Sudoku.SCALE
            start_col = (col // Sudoku.SCALE) * Sudoku.SCALE
            for i in range(Sudoku.SCALE):
                for j in range(Sudoku.SCALE):
                    if start_row + i != row or start_col + j != col:
                        #print "i:",i,", j",j
                        if type(0) == type(arr[start_row + i][start_col + j]):
                            if var == arr[start_row + i][start_col + j]:
                                return False    # �������ҵ��ظ�����
                        elif type([]) == type(arr[start_row + i][start_col + j]):
                            #print var, 'in', arr[start_row + i][start_col + j]
                            if var in arr[start_row + i][start_col + j]:
                                return False    # �������ҵ��ظ�����

        return True

    def __get_affect(self, grid):
        '''������ָ������Ӱ��ĸ���'''
        result_list = []
        if grid >= (0, 0) and grid <= (Sudoku.GRID_NUM - 1, Sudoku.GRID_NUM - 1):
            for i in range(Sudoku.GRID_NUM):
                for j in range(Sudoku.GRID_NUM):
                    if i == grid[0] or j == grid[1] or (i // Sudoku.SCALE == grid[0] // Sudoku.SCALE and j // Sudoku.SCALE == grid[1] // Sudoku.SCALE):
                        result_list.append((i, j))
        return result_list


    def __get_same_row(self, grid):
        '''�����ָ����ͬһ�еĸ���'''
        result_list = []
        if grid >= (0, 0) and grid <= (Sudoku.GRID_NUM - 1, Sudoku.GRID_NUM - 1):
            for j in range(Sudoku.GRID_NUM):
                result_list.append(grid[0], j)
        return result_list


    def __get_same_col(self, grid):
        '''�����ָ����ͬһ�еĸ���'''
        result_list = []
        if grid >= (0, 0) and grid <= (Sudoku.GRID_NUM - 1, Sudoku.GRID_NUM - 1):
            for i in range(Sudoku.GRID_NUM):
                result_list.append(i, grid[1])
        return result_list


    def __get_same_area(self, grid):
        '''�����ָ����ͬһ�еĸ���'''
        result_list = []
        if grid >= (0, 0) and grid <= (Sudoku.GRID_NUM - 1, Sudoku.GRID_NUM - 1):
            for i in range(Sudoku.GRID_NUM):
                for j in range(Sudoku.GRID_NUM):
                    if i // Sudoku.SCALE == grid[0] // Sudoku.SCALE and j // Sudoku.SCALE == grid[1] // Sudoku.SCALE:
                        result_list.append(i, j)
        return result_list


    def __check_answer(self):
        '''����Ƿ������������'''
        check_pass = True

        for i in range(Sudoku.GRID_NUM):
            for j in range(Sudoku.GRID_NUM):
                if self.__answer_sudoku[i][j] > 0:
                    for grid in self.__get_affect((i, j)):
                        if grid != (i, j):
                            if self.__answer_sudoku[grid[0]][grid[1]] == self.__answer_sudoku[i][j]:
                                if i == grid[0]:
                                    print "����[%d, %d]��[%d, %d]���ڳ�ͻ!" % (i, j, grid[0], grid[1])
                                elif j == grid[1]:
                                    print "����[%d, %d]��[%d, %d]���ڳ�ͻ!" % (i, j, grid[0], grid[1])
                                else:
                                    print "����[%d, %d]��[%d, %d]���ڳ�ͻ!" % (i, j, grid[0], grid[1])
                                check_pass = False
                                return

        if check_pass:
            all_fill = True
            for i in range(len(self.__answer_sudoku)):
                if 0 in self.__answer_sudoku[i]:
                    all_fill = False
                    break
            if all_fill:
                print "�𰸷��Ϲ���,���ͨ��!"


    def paint(self, dc):
        '''��������'''
        self.__paint_affected(dc)
        self.__paint_actived(dc)
        self.__paint_grid(dc)
        self.__paint_current_grid(dc)
        self.__paint_puzzle(dc)
        self.__paint_answer(dc)
        self.__paint_draft(dc)


    def __paint_affected(self, dc):
        '''���Ʊ�Ӱ�������'''
        dc.SetBrush(wx.Brush("#EEEEEE"))
        dc.SetPen(wx.Pen("#EEEEEE"));
        for grid in self.__affected_grids:
            dc.DrawRectangle(self.__anchor_pos[0] + grid[1] * Sudoku.GRID_WIDTH, self.__anchor_pos[1] + grid[0] * Sudoku.GRID_WIDTH, Sudoku.GRID_WIDTH, Sudoku.GRID_WIDTH)

        #for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
            #for j in range(Sudoku.GRID_NUM):    # X��ѭ��
                #if self.__affected_area[i][j] > 0:
                    #dc.DrawRectangle(self.__anchor_pos[0] + j * Sudoku.GRID_WIDTH, self.__anchor_pos[1] + i * Sudoku.GRID_WIDTH, Sudoku.GRID_WIDTH, Sudoku.GRID_WIDTH)

    def __paint_actived(self, dc):
        '''���Ƶ�ǰ��������ܼ������������'''
        if self.__actived_num > 0:
            dc.SetBrush(wx.Brush("#D4FFD4"))
            for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
                for j in range(Sudoku.GRID_NUM):    # X��ѭ��
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
        '''���ƿ��'''
        myPen = wx.Pen("Black", 1, wx.SOLID)

        for i in range(0, Sudoku.GRID_NUM + 1):
            if i % Sudoku.SCALE == 0:
                myPen.SetWidth(3)
            else:
                myPen.SetWidth(1)
            dc.SetPen(myPen)

            # ����
            dc.DrawLine(self.__anchor_pos[0], self.__anchor_pos[1] + i * Sudoku.GRID_WIDTH, self.__anchor_pos[0] + Sudoku.GRID_NUM * Sudoku.GRID_WIDTH, self.__anchor_pos[1] + i * Sudoku.GRID_WIDTH)
            # ����
            dc.DrawLine(self.__anchor_pos[0] + i * Sudoku.GRID_WIDTH, self.__anchor_pos[1], self.__anchor_pos[0] + i * Sudoku.GRID_WIDTH, self.__anchor_pos[1] + Sudoku.GRID_NUM * Sudoku.GRID_WIDTH)


    def __draw_num(self, dc, row, col, num, tp = 1, idx = 0):
        '''��ָ��λ�û�������

        num     Ҫ���Ƶ�����
        tp      �������� 1:ԭʼ���� 2:�� 3:��ע
        idx     ��ע���ֵ�λ��'''
        offset_x = 0
        offset_y = 0
        if tp == 1 or tp == 2:
            # ����ԭʼ���ֻ��
            myFont = wx.Font(Sudoku.FONT_SIZE, wx.SWISS, wx.NORMAL, wx.BOLD)
            dc.SetFont(myFont)
            if tp == 1:
                # ����������ɫ
                dc.SetTextForeground("Black");
            else:
                if self.__is_unique_all(self.__answer_sudoku, row, col):
                    # ����ɫ
                    dc.SetTextForeground("#097AD1");
                else:
                    # ��ͻ����ɫ
                    dc.SetTextForeground("Red");

            offset_x = (Sudoku.GRID_WIDTH - dc.GetTextExtent(str(num))[0]) / 2
            offset_y = (Sudoku.GRID_WIDTH - dc.GetTextExtent(str(num))[1]) / 2 + 1     # Y��������ƫ��һ������, ����̫������
        else:
            # ���Ʊ�ע����
            myFont = wx.Font(Sudoku.FONT_SIZE / 2, wx.SWISS, wx.NORMAL, wx.NORMAL)
            dc.SetFont(myFont)
            dc.SetTextForeground("#A1A1A1");

            offset_x = (Sudoku.GRID_WIDTH / Sudoku.SCALE - dc.GetTextExtent(str(num))[0]) / 2
            offset_x += (idx % Sudoku.SCALE) * Sudoku.GRID_WIDTH / Sudoku.SCALE
            offset_y = (Sudoku.GRID_WIDTH / Sudoku.SCALE - dc.GetTextExtent(str(num))[1]) / 2 + 1  # Y��������ƫ��һ������, ����̫������
            offset_y += (idx // Sudoku.SCALE) * Sudoku.GRID_WIDTH / Sudoku.SCALE

        dc.DrawText(str(num), self.__anchor_pos[0] + col * Sudoku.GRID_WIDTH + offset_x, self.__anchor_pos[1] + row * Sudoku.GRID_WIDTH + offset_y)


    def __paint_puzzle(self, dc):
        '''���Ƴ�ʼ����'''
        for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
            for j in range(Sudoku.GRID_NUM):    # X��ѭ��
                if self.__puzzle_sudoku[i][j] > 0:
                    self.__draw_num(dc, i, j, self.__puzzle_sudoku[i][j], 1)


    def __paint_answer(self, dc):
        '''���ƴ�����'''
        for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
            for j in range(Sudoku.GRID_NUM):    # X��ѭ��
                if self.__puzzle_sudoku[i][j] == 0 and self.__answer_sudoku[i][j] > 0:
                    self.__draw_num(dc, i, j, self.__answer_sudoku[i][j], 2)


    def __paint_draft(self, dc):
        '''���Ʋݸ�'''
        for i in range(Sudoku.GRID_NUM):        # Y��ѭ��
            for j in range(Sudoku.GRID_NUM):    # X��ѭ��
                if self.__answer_sudoku[i][j] <= 0:
                    for k in range(len(self.__draft_sudoku[i][j])):
                        self.__draw_num(dc, i, j, self.__draft_sudoku[i][j][k], 3, k)


    def active_grid(self, pos = (0, 0)):
        '''�����������¼�

        ���㵱ǰ���������Լ���Ӱ������'''
        if pos > (0, 0):
            row = (pos[1] - self.__anchor_pos[1]) // Sudoku.GRID_WIDTH
            col = (pos[0] - self.__anchor_pos[0]) // Sudoku.GRID_WIDTH
        else:
            row = self.__actived_grid[0]
            col = self.__actived_grid[1]
        if row in range(Sudoku.GRID_NUM) and col in range(Sudoku.GRID_NUM) and (row, col) != self.__actived_grid:
            # ���������Ч��Χ��
            self.__actived_grid = (row, col)
            self.__actived_num = self.__answer_sudoku[row][col]    # ��������
            self.__affected_grids = self.__get_affect(self.__actived_grid)


    def input_num(self, num):
        '''�ڵ�ǰ�������������'''
        if num in range(1, Sudoku.GRID_NUM + 1) and self.__actived_grid >= (0, 0):
            if self.__puzzle_sudoku[self.__actived_grid[0]][self.__actived_grid[1]] == 0:
                self.__answer_sudoku[self.__actived_grid[0]][self.__actived_grid[1]] = num
                self.__actived_num = num
                self.__progress += 1

                for grid in self.__affected_grids:
                    self.__fill_draft(grid)

                #self.__check_answer()


    def cancel_num(self, pos = (0, 0)):
        '''�����ǰ������'''
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

