from kivy.app import App
from kivy.uix.label import Label

class TapRewardApp(App):
    def build(self):
        return Label(text='Tap Reward APK Ready!')

if __name__ == '__main__':
    TapRewardApp().run()