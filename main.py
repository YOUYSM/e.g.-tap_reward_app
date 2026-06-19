"""
main.py

Kivy app: this is the frontend that communicates with api.py (Flask server)
through HTTP requests.

English Notes:
- We are using the 'requests' library to call the Flask API.
- There are 2 screens:
    1. LoginScreen -> enter phone number, Login or Signup
    2. HomeScreen  -> shows points, "Watch Ad" button, ads watched count

Before running:
Start the Flask server first:
    python api.py

Then, in another terminal:
    python main.py
"""

import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock

# Flask server address.
# While testing on a real phone, use your computer's local IP address
# (example: "http://192.168.1.5:5000")
SERVER_URL = "http://127.0.0.1:5000"


def show_popup(title, message):
    """Helper function to show small popups (errors/success messages)."""
    popup = Popup(
        title=title,
        content=Label(text=message),
        size_hint=(0.8, 0.4)
    )
    popup.open()


class LoginScreen(Screen):
    """
    Screen for entering phone number and performing Login or Signup.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)

        layout.add_widget(Label(
            text="Ad Reward App",
            font_size=28,
            size_hint=(1, 0.3)
        ))

        self.phone_input = TextInput(
            hint_text="Enter phone number",
            multiline=False,
            input_filter="int",
            font_size=20,
            size_hint=(1, 0.15)
        )
        layout.add_widget(self.phone_input)

        login_btn = Button(text="Login", size_hint=(1, 0.15))
        login_btn.bind(on_press=self.do_login)
        layout.add_widget(login_btn)

        signup_btn = Button(
            text="Signup (Create New Account)",
            size_hint=(1, 0.15)
        )
        signup_btn.bind(on_press=self.do_signup)
        layout.add_widget(signup_btn)

        self.status_label = Label(text="", size_hint=(1, 0.2))
        layout.add_widget(self.status_label)

        self.add_widget(layout)

    def do_login(self, instance):
        phone = self.phone_input.text.strip()
        if not phone:
            self.status_label.text = "Phone number is required"
            return

        try:
            res = requests.post(
                f"{SERVER_URL}/login",
                json={"phone": phone},
                timeout=5
            )
            data = res.json()
        except requests.exceptions.RequestException:
            self.status_label.text = "Could not connect to the server"
            return

        if data.get("success"):
            self.go_to_home(data["user"])
        else:
            self.status_label.text = data.get("message", "Login failed")

    def do_signup(self, instance):
        phone = self.phone_input.text.strip()
        if not phone:
            self.status_label.text = "Phone number is required"
            return

        try:
            res = requests.post(
                f"{SERVER_URL}/signup",
                json={"phone": phone},
                timeout=5
            )
            data = res.json()
        except requests.exceptions.RequestException:
            self.status_label.text = "Could not connect to the server"
            return

        if data.get("success"):
            self.go_to_home(data["user"])
        else:
            self.status_label.text = data.get("message", "Signup failed")

    def go_to_home(self, user):
        """After successful Login/Signup, move to Home screen."""
        home_screen = self.manager.get_screen("home")
        home_screen.set_user(user)
        self.manager.current = "home"


class HomeScreen(Screen):
    """
    Main screen: shows points and a "Watch Ad" button.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None

        self.layout = BoxLayout(
            orientation="vertical",
            padding=40,
            spacing=20
        )

        self.welcome_label = Label(
            text="Welcome!",
            font_size=22,
            size_hint=(1, 0.15)
        )
        self.layout.add_widget(self.welcome_label)

        self.points_label = Label(
            text="Points: 0",
            font_size=36,
            size_hint=(1, 0.3)
        )
        self.layout.add_widget(self.points_label)

        self.ads_label = Label(
            text="Ads Watched: 0",
            font_size=16,
            size_hint=(1, 0.15)
        )
        self.layout.add_widget(self.ads_label)

        self.watch_btn = Button(
            text="Watch Ad (+10 points)",
            font_size=20,
            size_hint=(1, 0.2)
        )
        self.watch_btn.bind(on_press=self.watch_ad)
        self.layout.add_widget(self.watch_btn)

        logout_btn = Button(text="Logout", size_hint=(1, 0.15))
        logout_btn.bind(on_press=self.logout)
        self.layout.add_widget(logout_btn)

        self.add_widget(self.layout)

    def set_user(self, user):
        """Set user data after login and update the screen."""
        self.user = user
        self.welcome_label.text = f"Welcome, {user['phone']}"
        self.points_label.text = f"Points: {user['points']}"
        self.refresh_balance()

    def watch_ad(self, instance):
        if not self.user:
            return

        # Disable button temporarily to simulate ad playback
        self.watch_btn.disabled = True
        self.watch_btn.text = "Ad is playing..."

        # Simulate ad completion after 2 seconds
        Clock.schedule_once(self.complete_ad_watch, 2)

    def complete_ad_watch(self, dt):
        try:
            res = requests.post(
                f"{SERVER_URL}/watch_ad",
                json={"user_id": self.user["id"]},
                timeout=5
            )
            data = res.json()
        except requests.exceptions.RequestException:
            show_popup("Error", "Could not connect to the server")
            self.reset_watch_button()
            return

        if data.get("success"):
            self.points_label.text = f"Points: {data['total_points']}"
            show_popup(
                "Reward Received!",
                f"You earned +{data['points_earned']} points!"
            )
            self.refresh_balance()
        else:
            show_popup("Error", data.get("message", "Something went wrong"))

        self.reset_watch_button()

    def reset_watch_button(self):
        self.watch_btn.disabled = False
        self.watch_btn.text = "Watch Ad (+10 points)"

    def refresh_balance(self):
        """Fetch latest points and ads watched count from the server."""
        if not self.user:
            return

        try:
            res = requests.get(
                f"{SERVER_URL}/balance/{self.user['id']}",
                timeout=5
            )
            data = res.json()
        except requests.exceptions.RequestException:
            return

        if data.get("success"):
            self.points_label.text = f"Points: {data['points']}"
            self.ads_label.text = f"Ads Watched: {data['ads_watched']}"

    def logout(self, instance):
        self.user = None
        self.manager.current = "login"


class TapRewardApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        return sm


if __name__ == "__main__":
    TapRewardApp().run()
