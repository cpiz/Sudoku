#coding=gbk
import sys
import wx
import time
import os
import c_sudoku

try:
    from agw import gradientbutton as GB
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.gradientbutton as GB

class SudokuCanvas(wx.Panel):
    '''������Ϸ������'''
    __parent = None

    def __init__(self, parent, ID):
        # ��ʼ�����
        wx.Window.__init__(self, parent, ID)
        self.__parent = parent
        self.SetBackgroundColour("White")
        self.color = "Black"
        self.thickness = 1
        self.pen = wx.Pen(self.color, self.thickness, wx.SOLID)

        # ���������Ϸ
        self.margin = margin = 20
        self.sudoku = sudoku = c_sudoku.Sudoku((margin, margin))

        # ������Ϸ��С�����趨�����С
        self.SetClientSizeWH(sudoku.get_width() + 2 * margin + 160, sudoku.get_height() + 2 * margin)

        # ��ʱ��
        self.elapsed_time = 0

        # ��ʱ��
        self.timer = wx.Timer(self)

        # ��Ӽ�ʱ����
        self.textTimer = textTimer = wx.StaticText(self)
        textTimer.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
        textTimer.SetForegroundColour("Gray")

        self.textProgress = textProgress = wx.StaticText(self)
        textProgress.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD))
        textProgress.SetForegroundColour("Gray")

        self.textFile = textFile = wx.StaticText(self)
        textFile.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        #textTimer.SetForegroundColour("Gray")

        # ��Ӱ�ť
        bitmap = wx.Bitmap(os.path.normpath("random.png"), wx.BITMAP_TYPE_PNG)
        self.btn_random = GB.GradientButton(self, -1, bitmap, "�����Ϸ", (self.sudoku.get_width() + 2 * self.margin, self.margin + self.sudoku.GRID_WIDTH * 3 + (self.sudoku.GRID_WIDTH - 40) / 2), (120, 40))
        bitmap = wx.Bitmap(os.path.normpath("calc.png"), wx.BITMAP_TYPE_PNG)
        self.btn_auto_calc = GB.GradientButton(self, -1, bitmap, "�Զ�����", (self.sudoku.get_width() + 2 * self.margin, self.margin + self.sudoku.GRID_WIDTH * 7 + (self.sudoku.GRID_WIDTH - 40) / 2), (120, 40))
        bitmap = wx.Bitmap(os.path.normpath("restart.png"), wx.BITMAP_TYPE_PNG)
        self.btn_restart = GB.GradientButton(self, -1, bitmap, "���¿�ʼ", (self.sudoku.get_width() + 2 * self.margin, self.margin + self.sudoku.GRID_WIDTH * 8 + (self.sudoku.GRID_WIDTH - 40) / 2), (120, 40))


        self.file_cmb = file_cmb = wx.ComboBox(self, wx.NewId(), size = (100, 24), style = wx.CB_READONLY)
        for file_name in os.listdir("."):
            if file_name.endswith("pzl"):
                file_cmb.Append(file_name)
                file_cmb.SetValue(file_name)


        # ���¼�
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_CHAR, self.OnKeyDown)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_BUTTON, self.OnRestartButton, self.btn_restart)
        self.Bind(wx.EVT_BUTTON, self.OnAutoCalcButton, self.btn_auto_calc)
        self.Bind(wx.EVT_BUTTON, self.OnRandomButton, self.btn_random)

        # ��ʼ��Ϸ
        self.InitGame("030500001050600002000802035010200706002000080704010200000100300006380000000006000")
        #self.InitGame()
        self.ReBuffer()


    def InitGame(self, puzzle = ''):
        '''��ʼ����Ϸ'''
        self.elapsed_time = 0
        self.timer.Stop()
        self.timer.Start(1000)

        self.textTimer.SetLabel("00:00:00")
        self.textTimer.SetPosition((self.sudoku.get_width() + 2 * self.margin, self.margin + (48 - self.textTimer.GetSize()[1]) / 2)) # ����Ϊ���ÿؼ�������ߵĸ���

        self.textProgress.SetLabel("��ɶ�:")
        self.textProgress.SetPosition((self.sudoku.get_width() + 2 * self.margin, self.margin + 48 + (48 - self.textProgress.GetSize()[1]) / 2)) # ����Ϊ���ÿؼ�������ߵĸ���

        self.textFile.SetLabel("��⣺")
        self.textFile.SetPosition((self.sudoku.get_width() + 2 * self.margin, self.margin + 106 + (48 - self.textProgress.GetSize()[1]) / 2)) # ����Ϊ���ÿؼ�������ߵĸ���
        self.file_cmb.SetPosition((self.sudoku.get_width() + 2 * self.margin + 40, self.margin + 100 + (48 - self.textProgress.GetSize()[1]) / 2)) # ����Ϊ���ÿؼ�������ߵĸ���

        self.sudoku.init_sudoku(puzzle, self.file_cmb.GetValue())

        self.__parent.SetTitle("Sudoku - ��" + str(self.sudoku.get_puzzle_num()) + "��")


    def ReBuffer(self):
        #3 ����һ��������豸������
        #print "ReBuffer"
        size = self.GetClientSize()
        self.__buffer_bitmap = wx.EmptyBitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.__buffer_bitmap)
        dc.Clear()

        self.sudoku.paint(dc)
        self.reReBuffer = False

    def OnSize(self, event):
        #print "OnSize"
        self.ReBuffer()


    def OnLeftUp(self, event):
        #print "OnLeftUp"
        #self.reReBuffer = True
        pass

    def OnIdle(self, event):
        #12 ����ʱ�Ĵ���
        #print "OnIdle"
        if self.reReBuffer:
            self.ReBuffer()
            self.Refresh(False)

    def OnPaint(self, event):
        #13 ����һ��paint����棩����
        #print "OnPaint"
        self.textProgress.SetLabel("��ɶ�:" + str(self.sudoku.get_progress()) + "/" + str(self.sudoku.GRID_NUM ** 2))
        wx.BufferedPaintDC(self, self.__buffer_bitmap)

    def OnKeyDown(self, event):
        '''��������¼�'''
        keycode = event.GetKeyCode()
        #print keycode
        if keycode == wx.WXK_ESCAPE:
            # esc
            sys.exit()
        if keycode == wx.WXK_DELETE:
            # delete
            self.sudoku.cancel_num()
            self.reReBuffer = True
        elif keycode in range(49, 58):
            # 1 ~ 9
            self.sudoku.input_num(keycode - 48)
            #self.sudoku.ai_calc()
            self.reReBuffer = True
        elif keycode == 3:
            # ctrl + c
            self.OnCopy()
        elif keycode == 22:
            # ctrl + v
            self.OnPaste()
        else:
            event.Skip()

    def OnCopy(self):
        '''�������'''
        self.do = wx.TextDataObject()
        self.do.SetText(self.sudoku.get_puzzle_str())
        # ���Ƶ��ֵ�������
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(self.do)
            wx.TheClipboard.Close()
            wx.MessageBox("�ѽ����⵼����������", "������ʾ")


    def OnPaste(self):
        '''ͨ��ճ���������'''
        do = wx.TextDataObject()
        if wx.TheClipboard.Open():
            paste_ok = wx.TheClipboard.GetData(do)
            wx.TheClipboard.Close()
            if paste_ok:
                puzzle_str = do.GetText()
                if puzzle_str.isdigit()                                         \
                        and len(puzzle_str) == c_sudoku.Sudoku.GRID_NUM ** 2:
                    dlg = wx.MessageDialog(self, "ȷ��Ҫ����������е������?", "����ȷ��", wx.YES_NO)
                    if dlg.ShowModal() == wx.ID_YES:
                        self.InitGame(puzzle_str)
                        self.SetFocus()     # �����갴ť�¼�����뽫focus����canvas, �����޷���Ӧ�����¼�
                        self.reReBuffer = True
                    dlg.Destroy()


    def OnLeftDown(self, event):
        #print 'LeftDown'
        pos = event.GetPositionTuple()
        self.sudoku.active_grid(pos)
        self.reReBuffer = True


    def OnTimer(self, event):
        # ��ʱ��+1�� ����ʾ��ǰ��ʹ�õ�ʱ��
        self.elapsed_time += 1
        self.textTimer.SetLabel(time.strftime('%H:%M:%S', time.gmtime(self.elapsed_time)))


    def OnRestartButton(self, event):
        '''������¿�ʼ��ť�¼�'''
        self.InitGame(self.sudoku.get_puzzle_str())
        self.SetFocus()     # �����갴ť�¼�����뽫focus����canvas, �����޷���Ӧ�����¼�
        self.reReBuffer = True


    def OnAutoCalcButton(self, event):
        '''����Զ����㰴ť�¼�'''
        self.sudoku.ai_calc()
        self.SetFocus()     # �����갴ť�¼�����뽫focus����canvas, �����޷���Ӧ�����¼�
        self.reReBuffer = True


    def OnRandomButton(self, event):
        self.InitGame()
        self.SetFocus()     # �����갴ť�¼�����뽫focus����canvas, �����޷���Ӧ�����¼�
        self.reReBuffer = True


    def OnKeyUp(self, event):
        pass

class SudokuFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Sudoku", pos = (600, 200), size = (200, 200))
        self.sketch = SudokuCanvas(self, -1)
        self.SetClientSize(self.sketch.GetClientSize())

class SudokuApp(wx.App):
    def OnInit(self):
        frame = SudokuFrame(None)
        frame.Show()
        return True

if __name__ == "__main__":
    app = SudokuApp(False)  # ���ó�False�����������д������������Ϣ
    app.MainLoop()


