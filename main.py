from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.image import AsyncImage
from kivy.uix.floatlayout import FloatLayout
import json
import arabic_reshaper
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle
import re
import random

LabelBase.register(name='Arabic', fn_regular='data/Amiri-Bold.ttf')
LabelBase.register(name='Emoji', fn_regular='data/Segoe UI Emoji.TTF')

def read_usernames_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    except Exception as e:
        print(f"Error reading usernames: {e}")
        return []

def save_last_used_user(file_path, username):
    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(username + '\n')
    except Exception as e:
        print(f"Error saving last used user: {e}")

def read_comments_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading comments: {e}")
        return []

def reshape_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return reshaped_text[::-1]

def is_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text))

def get_next_username(users_file, last_used_file):
    usernames = read_usernames_from_file(users_file)
    last_used_users = read_usernames_from_file(last_used_file)
    for username in usernames:
        if username not in last_used_users:
            return username
    return None

class CommentApp(App):
    def build(self):
        self.layout = FloatLayout()
        with self.layout.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
            self.layout.bind(size=self.update_rect, pos=self.update_rect)

        # زيادة حجم الصورة هنا
        self.header_image = AsyncImage(source='112.jpg', size_hint=(1, None), size=(2500, 1500), pos_hint={'center_x': 0.5, 'center_y': 0.8})
        self.layout.add_widget(self.header_image)

        reshaped_hint_text = reshape_text('أدخل رابط المنشور هنا')
        self.url_input = TextInput(hint_text=reshaped_hint_text, font_name='Arabic', font_size=20, size_hint=(0.8, None), height=55, pos_hint={'center_x': 0.5, 'center_y': 0.6}, halign='right')
        self.layout.add_widget(self.url_input)

        reshaped_button_text = reshape_text('تنفيذ')
        self.execute_button = Button(text=reshaped_button_text, font_name='Arabic', size_hint=(0.3, None), height=50, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.execute_button.bind(on_press=self.on_execute_button_press)
        self.layout.add_widget(self.execute_button)

        self.comment_layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(800, 350), pos_hint={'center_x': 0.5, 'center_y': 0.35}, padding=(10, 10), spacing=5)
        with self.comment_layout.canvas.before:
            Color(0, 0, 0, 1)
            self.comment_rect = Rectangle(size=self.comment_layout.size, pos=self.comment_layout.pos)
            self.comment_layout.bind(size=self.update_comment_rect, pos=self.update_comment_rect)

        self.user_info_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.username_label = Label(text="", font_size=30, halign='center', valign='middle', font_name='Arabic', size_hint_y=None, height=200)
        self.user_info_layout.add_widget(self.username_label)
        self.image = AsyncImage(size_hint=(None, None), size=(200, 250))
        self.image.opacity = 0
        self.user_info_layout.add_widget(self.image)

        self.winner_label = Label(text="", font_size=40, halign='center', valign='middle', font_name='Arabic', size_hint_y=None, height=40, pos_hint={'center_y': 0.8})
        self.comment_layout.add_widget(self.winner_label)
        self.comment_layout.add_widget(self.user_info_layout)
        self.layout.add_widget(self.comment_layout)

        return self.layout

    def update_rect(self, *args):
        self.rect.pos = self.layout.pos
        self.rect.size = self.layout.size

    def update_comment_rect(self, *args):
        self.comment_rect.pos = self.comment_layout.pos
        self.comment_rect.size = self.comment_layout.size

    def on_execute_button_press(self, instance):
        self.username_label.text = reshape_text("جاري تحميل التعليقات...")
        Clock.schedule_once(self.get_comments, 1)

    def get_comments(self, *args):
        comments = read_comments_from_json('/storage/emulated/0/Android/media/com.almnhage.app/.almnhage/comments.json')
        if comments:
            random_comments = random.sample(comments, min(10, len(comments)))
            self.selected_comments = random_comments
            self.current_comment_index = 0
            self.show_next_comment()
            self.header_image.opacity = 1
            Clock.schedule_once(self.load_next_user_comment, len(random_comments))

    def load_next_user_comment(self, *args):
        while True:
            next_username = get_next_username('/storage/emulated/0/Android/media/com.almnhage.app/.almnhage/users.txt', 
                                              '/storage/emulated/0/Android/media/com.almnhage.app/.almnhage/last_used_users.txt')
            if not next_username:
                return

            comments = read_comments_from_json('/storage/emulated/0/Android/media/com.almnhage.app/.almnhage/comments.json')
            if comments:
                user_comments = [comment for comment in comments if comment['username'] == next_username]
                if user_comments:
                    self.selected_comments = user_comments[:1]
                    self.current_comment_index = 0
                    self.show_next_comment()
                    save_last_used_user('/storage/emulated/0/Android/media/com.almnhage.app/.almnhage/last_used_users.txt', next_username)
                    break

    def show_next_comment(self, *args):
        if self.current_comment_index >= len(self.selected_comments):
            return
        comment = self.selected_comments[self.current_comment_index]
        full_text = comment['text']
        username = comment['username']
        profile_pic_url = comment['profile_pic_url']

        self.comment_layout.clear_widgets()
        self.comment_layout.add_widget(self.winner_label)
        self.comment_layout.add_widget(self.user_info_layout)

        # إعادة تشكيل النص فقط إذا كان باللغة العربية
        if is_arabic(username):
            self.username_label.text = username
        else:
            self.username_label.text = username

        comment_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=(5, 70), spacing=5)
        arabic_part = ' '.join(re.findall(r'[\u0600-\u06FF]+', full_text))
        if arabic_part:
            arabic_label = Label(text=reshape_text(arabic_part), font_name='Arabic', size_hint_y=None, height=20, font_size=30)
            comment_box.add_widget(arabic_label)
        non_arabic_part = ' '.join(re.findall(r'[^ \u0600-\u06FF]+', full_text))
        if non_arabic_part:
            non_arabic_label = Label(text=non_arabic_part, font_name='Emoji', size_hint_y=None, height=20, font_size=30)
            comment_box.add_widget(non_arabic_label)

        self.comment_layout.add_widget(comment_box)
        self.image.source = profile_pic_url
        self.image.opacity = 1
        self.current_comment_index += 1

        if self.current_comment_index < len(self.selected_comments):
            Clock.schedule_once(self.show_next_comment, 1)

if __name__ == '__main__':
    CommentApp().run()