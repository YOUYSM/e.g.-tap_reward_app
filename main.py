
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class TapRewardApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        label = Label(text='Tap Reward APK Ready!', font_size='24sp')
        btn = Button(text='Tap Me', font_size='20sp')
        layout.add_widget(label)
        layout.add_widget(btn)
        return layout

if __name__ == '__main__':
    TapRewardApp().run()
