import random
import threading
import wx
import res


class AppFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(
            self, None, style=wx.NO_BORDER | wx.FRAME_SHAPED | wx.STAY_ON_TOP)

        # UI初期化
        self.init_ui()
        # キーバインド
        self.key_binding()
        # 初期動作
        self.timer_draw_start()

    # 初期UI
    def init_ui(self):
        # 画面解像度
        screen = (1366, 768)
        size_window = (500, 500)
        self.pos_window = [screen[0] - size_window[0],
                           screen[1] - size_window[1]]
        self.SetBackgroundColour(wx.Colour(255, 255, 255, 0))
        self.SetPosition(self.pos_window)
        self.SetSize(size_window)

        # メニュー
        menu_view = wx.Menu()
        view = menu_view.Append(1, '入力ボックス 表示/非表示')
        self.Bind(wx.EVT_MENU, self.input_view, view)

        menu_bar = wx.MenuBar()
        menu_bar.Append(menu_view, '表示')
        self.SetMenuBar(menu_bar)

        # 画像読み込み
        bmp_voice = wx.Image('assets/ui/voice.png').ConvertToBitmap()
        bmp_char = wx.Image('assets/ui/balloon_char.png').ConvertToBitmap()
        bmp_me = wx.Image('assets/ui/balloon_me.png').ConvertToBitmap()
        bmp_box = wx.Image('assets/ui/box.png').ConvertToBitmap()

        # パネル定義
        pnl_main = wx.Panel(self, -1, pos=(0, 0), size=(500, 500))
        self.pnl_char = wx.Panel(
            pnl_main, -1, pos=(280, 60), size=(220, 440))
        self.pnl_char.SetBackgroundColour(wx.Colour(255, 255, 255, 0))
        self.pnl_msg_char = wx.Panel(
            pnl_main, -1, pos=(130, 50), size=(150, 100))
        self.pnl_msg_me = wx.Panel(
            pnl_main, -1, pos=(30, 365), size=(120, 80))
        self.pnl_input = wx.Panel(
            pnl_main, -1, pos=(10, 450), size=(260, 40))
        self.pnl_msg_char.Hide()
        self.pnl_msg_me.Hide()
        self.pnl_char.Bind(wx.EVT_LEFT_DOWN, self.motion_random)

        # 画像表示
        wx.StaticBitmap(self.pnl_input, -1, bmp_box, (0, 0), (260, 40))
        wx.StaticBitmap(self.pnl_msg_char, -1, bmp_char, (0, 0), (150, 100))
        wx.StaticBitmap(self.pnl_msg_me, -1, bmp_me, (0, 0), (120, 80))

        # ラベル
        self.lbl_char = wx.StaticText(self.pnl_msg_char, -1, '', pos=(20, 25),
                                      size=(110, 50), style=wx.TE_LEFT)
        self.lbl_me = wx.StaticText(self.pnl_msg_me, -1, '', pos=(20, 25),
                                    size=(80, 50), style=wx.TE_LEFT)

        # テキストボックス
        self.txt_me = wx.TextCtrl(
            self.pnl_input, -1, pos=(5, 8), size=(215, 24),
            style=wx.TE_PROCESS_ENTER)
        self.txt_me.Bind(wx.EVT_TEXT_ENTER, self.entered)

        # ボタン
        btn_voice = wx.BitmapButton(
            self.pnl_input, -1, bmp_voice, pos=(224, 4), size=(32, 32))
        btn_voice.Bind(wx.EVT_BUTTON, self.clicked)

        # Timer/thread定義
        self.timer_draw = wx.Timer(self)
        self.flag_draw = True
        self.index_draw = 0
        self.name_dir = 'wait'
        self.mode_timer = 'draw'
        self.Bind(wx.EVT_TIMER, self.timer)

        # 会話モード
        self.mode = 'dialog'

        # モーション群
        self.name_motion = ['wait', 'POSITIVE', 'NEGATIVE', 'patapata']

        # キークリック

    # キーバインド内容
    def key_binding(self):
        self.flag_shift = False
        self.pnl_char.Bind(wx.EVT_KEY_DOWN, self.key_down)
        self.pnl_char.Bind(wx.EVT_KEY_UP, self.key_up)

    # タイマー
    def timer_draw_start(self):
        rate_draw = 1000 / 60

        self.timer_draw.Stop()
        self.index_draw = 0
        self.timer_draw.Start(rate_draw)

    def timer(self, event):
        img_path = 'assets/motion/{0}/{1:0>3}.png'.format(
            self.name_dir, self.index_draw)
        bmp = wx.Image(img_path).ConvertToBitmap()
        self.draw_char(bmp)
        if self.index_draw == 179:
            self.name_dir = 'wait'
            self.timer_draw_start()
        else:
            self.index_draw += 1

    # 会話返答
    def response(self, input_word):
        self.txt_me.Clear()
        self.lbl_me.SetLabel(res.convText(input_word, 7))
        self.pnl_msg_me.Show()
        th_me = threading.Timer(3, self.show_me)
        th_me.start()
        response = res.response(input_word, self.mode)
        self.lbl_char.SetLabel(res.convText(response['utt'], 9))
        self.pnl_msg_char.Show()
        th_char = threading.Timer(5, self.show_char)
        th_char.start()
        self.mode = response['mode']
        self.name_dir = response['emotion']
        self.timer_draw_start()

    # 音声入力
    def clicked(self, event):
        input_word = res.recWord()
        if self.mode == 'srtr':
            input_word = input_word.replace('、', '').replace('。', '')
        self.response(input_word)

    # テキストボックス
    def entered(self, event):
        input_word = self.txt_me.GetValue()
        self.response(input_word)

    # キャラ描画
    def draw_char(self, bmp):
        cd_char = wx.ClientDC(self.pnl_char)
        cd_char.Clear()
        cd_char.DrawBitmap(bmp, 0, 0)

    # 吹き出しを消す
    def show_me(self):
        self.pnl_msg_me.Hide()

    def show_char(self):
        self.pnl_msg_char.Hide()

    # 入力ボックス表示切り替え
    def input_view(self, event):
        if self.pnl_input.IsShown():
            self.pnl_input.Hide()
        else:
            self.pnl_input.Show()

    def motion_random(self, event):
        self.name_dir = random.choice(self.name_motion)
        self.timer_draw_start()

    def key_down(self, event):
        if event.GetKeyCode() == wx.WXK_SHIFT:
            self.flag_shift = True
        if event.GetKeyCode() == wx.WXK_LEFT:
            if self.flag_shift:
                self.pos_window[0] -= 10
            else:
                self.pos_window[0] -= 1
            self.SetPosition(self.pos_window)
        elif event.GetKeyCode() == wx.WXK_UP:
            if self.flag_shift:
                self.pos_window[1] -= 10
            else:
                self.pos_window[1] -= 1
            self.SetPosition(self.pos_window)
        elif event.GetKeyCode() == wx.WXK_DOWN:
            if self.flag_shift:
                self.pos_window[1] += 10
            else:
                self.pos_window[1] += 1
            self.SetPosition(self.pos_window)
        elif event.GetKeyCode() == wx.WXK_RIGHT:
            if self.flag_shift:
                self.pos_window[0] += 10
            else:
                self.pos_window[0] += 1
            self.SetPosition(self.pos_window)

    def key_up(self, event):
        if event.GetKeyCode() == wx.WXK_SHIFT:
            self.flag_shift = False


app = wx.App()
frame = AppFrame()
frame.Show()

# 起動時メッセージ
announce = wx.Frame(None, -1, title='ようこそ！', size=(400, 300))
txt_announce = ''
with open('announce.txt') as f:
    txt_announce = f.read()
wx.StaticText(
    announce, -1, txt_announce, style=wx.TE_LEFT)
announce.Show()

app.MainLoop()
