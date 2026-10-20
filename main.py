from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.core.text import LabelBase
import os
import requests

# ==================== 配置 ====================

# 后端 API 地址（改成运行 server.py 那台电脑的 IP）
API_URL = 'http://10.10.10.235:8000'

# 中文字体（相对路径，与 main.py 放在同一目录）
FONT = 'msyh.ttf'

# 如果字体文件不存在，给出友好提示
if not os.path.exists(FONT):
    print(f'⚠️ 找不到字体文件: {os.path.abspath(FONT)}')
    print('请执行: copy C:\\Windows\\Fonts\\simsun.ttc 到本目录并命名为 msyh.ttf')

# 全局注册字体，之后的 Label/Button 默认使用它
LabelBase.register(name='msyh', fn_regular=FONT)


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(20), spacing=dp(10), **kwargs)

        # ---------- 标题 ----------
        self.title = Label(text='SQL Server 数据管理',
                           font_name=FONT, font_size='22sp',
                           size_hint_y=None, height=dp(50))

        # ---------- 输入框 ----------
        self.input = TextInput(hint_text='请输入内容',
                               font_name=FONT, font_size='16sp',
                               size_hint_y=None, height=dp(50),
                               multiline=False)

        # ---------- 结果显示 ----------
        self.result = Label(text='等待操作...',
                            font_name=FONT, font_size='14sp',
                            color=(0.9, 0.9, 0.9, 1))

        # ---------- 按钮 ----------
        self.btn_add = Button(text='添加数据',
                              font_name=FONT, font_size='16sp',
                              size_hint_y=None, height=dp(50),
                              background_color=(0.2, 0.6, 0.9, 1),
                              on_press=self.add_data)

        self.btn_query = Button(text='查询数据',
                                font_name=FONT, font_size='16sp',
                                size_hint_y=None, height=dp(50),
                                background_color=(0.3, 0.7, 0.4, 1),
                                on_press=self.query_data)

        self.btn_delete = Button(text='删除最新一条',
                                 font_name=FONT, font_size='16sp',
                                 size_hint_y=None, height=dp(50),
                                 background_color=(0.9, 0.3, 0.3, 1),
                                 on_press=self.delete_data)

        # ---------- 添加到界面 ----------
        for w in [self.title, self.input, self.btn_add,
                  self.btn_query, self.btn_delete, self.result]:
            self.add_widget(w)

    # ==================== 添加数据 ====================
    def add_data(self, instance):
        content = self.input.text.strip()
        if not content:
            self.result.text = '请先输入内容'
            return
        try:
            r = requests.post(f'{API_URL}/notes',
                              json={'content': content}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                self.result.text = f'保存成功，ID = {data["id"]}'
                self.input.text = ''
            else:
                self.result.text = f'失败，状态码: {r.status_code}'
        except requests.exceptions.ConnectionError:
            self.result.text = '连接失败，请检查服务器地址和网络'
        except Exception as e:
            self.result.text = f'错误: {e}'

    # ==================== 查询数据 ====================
    def query_data(self, instance):
        try:
            r = requests.get(f'{API_URL}/notes', timeout=10)
            print(r)
            if r.status_code == 200:
                notes = r.json()
                if not notes:
                    self.result.text = '数据库是空的'
                    return
                lines = [f"{n['id']}. {n['content']}  ({str(n['created_at'])[:16]})"
                         for n in notes[:10]]  # 最多显示10条
                self.result.text = '\n'.join(lines) + f'\n\n共 {len(notes)} 条'
            else:
                self.result.text = f'查询失败，状态码: {r.status_code}'
        except Exception as e:
            self.result.text = f'错误: {e}'

    # ==================== 删除数据 ====================
    def delete_data(self, instance):
        try:
            r = requests.get(f'{API_URL}/notes', timeout=10)
            notes = r.json()
            if not notes:
                self.result.text = '没有可删除的数据'
                return
            newest_id = notes[0]['id']
            r = requests.delete(f'{API_URL}/notes/{newest_id}', timeout=10)
            if r.status_code == 200:
                self.result.text = f'已删除 ID={newest_id} 的数据'
            else:
                self.result.text = f'删除失败，状态码: {r.status_code}'
        except Exception as e:
            self.result.text = f'错误: {e}'


class MyApp(App):
    def build(self):
        self.title = 'SQL Server 管理助手'
        return MainScreen()


if __name__ == '__main__':
    MyApp().run()
