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
    '''数独游戏画布类'''
    __parent = None

    def __init__(self, parent, ID):
        # 初始化面板
        wx.Window.__init__(self, parent, ID)
        self.__parent = parent
        self.SetBackgroundColour("White")
        self.color = "Black"
        self.thickness = 1
        self.pen = wx.Pen(self.color, self.thickness, wx.SOLID)

        # 添加数独游戏
        self.margin = margin = 20
        self.sudoku = sudoku = c_sudoku.Sudoku((margin, margin))

        # 根据游戏大小重新设定窗体大小
        self.SetClientSizeWH(sudoku.get_width() + 2 * margin + 160, sudoku.get_height() + 2 * margin)

        # 计时器
        self.elapsed_time = 0

        # 定时器
        self.timer = wx.Timer(self)

        # 添加计时文字
        self.textTimer = textTimer = wx.StaticText(self)
        textTimer.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
        textTimer.SetForegroundColour("Gray")

        self.textProgress = textProgress = wx.StaticText(self)
        textProgress.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD))
        textProgress.SetForegroundColour("Gray")

        self.textFile = textFile = wx.StaticText(self)
        textFile.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        #textTimer.SetForegroundColour("Gray")

        # 添加按钮
        bitmap = wx.Bitmap(os.path.normpath("random.png"), wx.BITMAP_TYPE_PNG)
        self.btn_random = GB.GradientButton(self, -1, bitmap, "随机游戏", (self.sudoku.get_width() + 2 * self.margin, self.margin + self.sudoku.GRID_WIDTH * 3 + (self.sudoku.GRID_WIDTH - 40) / 2), (120, 40))
        bitmap = wx.Bitmap(os.path.normpath("calc.png"), wx.BITMAP_TYPE_PNG)
        self.btn_auto_calc = GB.GradientButton(self, -1, bitmap, "自动计算", (self.sudoku.get_width() + 2 * self.margin, self.margin + self.sudoku.GRID_WIDTH * 7 + (self.sudoku.GRID_WIDTH - 40) / 2), (120, 40))
        bitmap = wx.Bitmap(os.path.normpath("restart.png"), wx.BITMAP_TYPE_PNG)
        self.btn_restart = GB.GradientButton(self, -1, bitmap, "重新开始", (self.sudoku.get_width() + 2 * self.margin, self.margin + self.sudoku.GRID_WIDTH * 8 + (self.sudoku.GRID_WIDTH - 40) / 2), (120, 40))


        self.file_cmb = file_cmb = wx.ComboBox(self, wx.NewId(), size = (100, 24), style = wx.CB_READONLY)
        for file_name in os.listdir("."):
            if file_name.endswith("pzl"):
                file_cmb.Append(file_name)
                file_cmb.SetValue(file_name)


        # 绑定事件
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

        # 开始游戏
        self.InitGame("030500001050600002000802035010200706002000080704010200000100300006380000000006000")
        #self.InitGame()
        self.ReBuffer()


    def InitGame(self, puzzle = ''):
        '''初始化游戏'''
        self.elapsed_time = 0
        self.timer.Stop()
        self.timer.Start(1000)

        self.textTimer.SetLabel("00:00:00")
        self.textTimer.SetPosition((self.sudoku.get_width() + 2 * self.margin, self.margin + (48 - self.textTimer.GetSize()[1]) / 2)) # 这是为了让控件对齐左边的格子

        self.textProgress.SetLabel("完成度:")
        self.textProgress.SetPosition((self.sudoku.get_width() + 2 * self.margin, self.margin + 48 + (48 - self.textProgress.GetSize()[1]) / 2)) # 这是为了让控件对齐左边的格子

        self.textFile.SetLabel("题库：")
        self.textFile.SetPosition((self.sudoku.get_width() + 2 * self.margin, self.margin + 106 + (48 - self.textProgress.GetSize()[1]) / 2)) # 这是为了让控件对齐左边的格子
        self.file_cmb.SetPosition((self.sudoku.get_width() + 2 * self.margin + 40, self.margin + 100 + (48 - self.textProgress.GetSize()[1]) / 2)) # 这是为了让控件对齐左边的格子

        self.sudoku.init_sudoku(puzzle, self.file_cmb.GetValue())

        self.__parent.SetTitle("Sudoku - 第" + str(self.sudoku.get_puzzle_num()) + "题")


    def ReBuffer(self):
        #3 创建一个缓存的设备上下文
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
        #12 空闲时的处理
        #print "OnIdle"
        if self.reReBuffer:
            self.ReBuffer()
            self.Refresh(False)

    def OnPaint(self, event):
        #13 处理一个paint（描绘）请求
        #print "OnPaint"
        self.textProgress.SetLabel("完成度:" + str(self.sudoku.get_progress()) + "/" + str(self.sudoku.GRID_NUM ** 2))
        wx.BufferedPaintDC(self, self.__buffer_bitmap)

    def OnKeyDown(self, event):
        '''处理键盘事件'''
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
        '''复制题局'''
        self.do = wx.TextDataObject()
        self.do.SetText(self.sudoku.get_puzzle_str())
        # 复制当局到剪贴板
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(self.do)
            wx.TheClipboard.Close()
            wx.MessageBox("已将此题导出到剪贴板", "导出提示")


    def OnPaste(self):
        '''通过粘贴导入题局'''
        do = wx.TextDataObject()
        if wx.TheClipboard.Open():
            paste_ok = wx.TheClipboard.GetData(do)
            wx.TheClipboard.Close()
            if paste_ok:
                puzzle_str = do.GetText()
                if puzzle_str.isdigit()                                         \
                        and len(puzzle_str) == c_sudoku.Sudoku.GRID_NUM ** 2:
                    dlg = wx.MessageDialog(self, "确定要导入剪贴板中的题局吗?", "导入确认", wx.YES_NO)
                    if dlg.ShowModal() == wx.ID_YES:
                        self.InitGame(puzzle_str)
                        self.SetFocus()     # 处理完按钮事件后必须将focus交给canvas, 否则无法响应键盘事件
                        self.reReBuffer = True
                    dlg.Destroy()


    def OnLeftDown(self, event):
        #print 'LeftDown'
        pos = event.GetPositionTuple()
        self.sudoku.active_grid(pos)
        self.reReBuffer = True


    def OnTimer(self, event):
        # 计时器+1， 并提示当前已使用的时间
        self.elapsed_time += 1
        self.textTimer.SetLabel(time.strftime('%H:%M:%S', time.gmtime(self.elapsed_time)))


    def OnRestartButton(self, event):
        '''点击重新开始按钮事件'''
        self.InitGame(self.sudoku.get_puzzle_str())
        self.SetFocus()     # 处理完按钮事件后必须将focus交给canvas, 否则无法响应键盘事件
        self.reReBuffer = True


    def OnAutoCalcButton(self, event):
        '''点击自动计算按钮事件'''
        self.sudoku.ai_calc()
        self.SetFocus()     # 处理完按钮事件后必须将focus交给canvas, 否则无法响应键盘事件
        self.reReBuffer = True


    def OnRandomButton(self, event):
        self.InitGame()
        self.SetFocus()     # 处理完按钮事件后必须将focus交给canvas, 否则无法响应键盘事件
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
    app = SudokuApp(False)  # 设置成False可以在命令行窗口输出调试信息
    app.MainLoop()


