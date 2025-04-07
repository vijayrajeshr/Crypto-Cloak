import os
import random
import string
import pyperclip
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
# Add this import for Calendar
from tkcalendar import Calendar
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Rectangle, Color, RoundedRectangle, Line
from kivy.clock import Clock
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
        self.banner_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)

        with self.banner_layout.canvas.before:
            Color(rgba=get_color_from_hex('#0F162A'))
            self.banner_rect = Rectangle(size=(Window.width, 50), pos=(0, Window.height - 50))

        def update_banner_rect(instance, width, height):
            self.banner_rect.size = (width, 50)
            self.banner_rect.pos = (0, height - 50)

        Window.bind(on_resize=update_banner_rect)

        self.banner_title = Label(
            text="CryptoCloak",
            font_size=24,
            halign='left',
            valign='middle',
            font_name='Roboto',
            size_hint_x=None,
            width=200,
            bold=True,
        )
        self.banner_title.color = get_color_from_hex('#FFFFFF')
        self.banner_layout.add_widget(self.banner_title)
        self.banner_layout.add_widget(Label(size_hint_x=1))  # Spacer
        self.anchor_layout.add_widget(self.banner_layout)
        self.add_widget(self.anchor_layout)

    def update_banner_position(self):
        # Update the banner position when the screen is entered
        self.banner_layout.pos[1] = Window.height - 50
        self.banner_rect.pos = (0, Window.height - 50)

class TimePicker(ModalView):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.6)
        self.callback = callback
        self.auto_dismiss = False
        
        # Main layout
        layout = BoxLayout(orientation='vertical', spacing=20, padding=15)
        
        # Add title
        title_label = Label(
            text="Select Time",
            font_size=22,
            bold=True,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(title_label)
        
        # Time selection layout
        selection_layout = GridLayout(cols=2, spacing=15, padding=10)
        
        # Hour column
        hour_layout = BoxLayout(orientation='vertical', spacing=5)
        hour_label = Label(
            text="Hour",
            font_size=18,
            size_hint_y=None,
            height=30
        )
        hour_layout.add_widget(hour_label)
        
        # Hour selector with up/down buttons
        hour_selector = BoxLayout(orientation='vertical')
        
        # Up button
        hour_up = Button(
            text="▲",
            background_color=(0.3, 0.6, 0.9, 1),
            size_hint_y=None,
            height=40
        )
        
        # Hour display
        self.hour_input = TextInput(
            text="12",
            multiline=False,
            halign='center',
            font_size=24,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=50,
            input_filter='int',
            padding=[10, 10, 10, 0]
        )
        
        # Down button
        hour_down = Button(
            text="▼",
            background_color=(0.3, 0.6, 0.9, 1),
            size_hint_y=None,
            height=40
        )
        
        # Bind events
        hour_up.bind(on_press=lambda x: self.increment_hour())
        hour_down.bind(on_press=lambda x: self.decrement_hour())
        
        hour_selector.add_widget(hour_up)
        hour_selector.add_widget(self.hour_input)
        hour_selector.add_widget(hour_down)
        
        hour_layout.add_widget(hour_selector)
        selection_layout.add_widget(hour_layout)
        
        # Minute column
        minute_layout = BoxLayout(orientation='vertical', spacing=5)
        minute_label = Label(
            text="Minute",
            font_size=18,
            size_hint_y=None,
            height=30
        )
        minute_layout.add_widget(minute_label)
        
        # Minute selector with up/down buttons
        minute_selector = BoxLayout(orientation='vertical')
        
        # Up button
        minute_up = Button(
            text="▲",
            background_color=(0.3, 0.6, 0.9, 1),
            size_hint_y=None,
            height=40
        )
        
        # Minute display
        self.minute_input = TextInput(
            text="00",
            multiline=False,
            halign='center',
            font_size=24,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=50,
            input_filter='int',
            padding=[10, 10, 10, 0]
        )
        
        # Down button
        minute_down = Button(
            text="▼",
            background_color=(0.3, 0.6, 0.9, 1),
            size_hint_y=None,
            height=40
        )
        
        # Bind events
        minute_up.bind(on_press=lambda x: self.increment_minute())
        minute_down.bind(on_press=lambda x: self.decrement_minute())
        
        minute_selector.add_widget(minute_up)
        minute_selector.add_widget(self.minute_input)
        minute_selector.add_widget(minute_down)
        
        minute_layout.add_widget(minute_selector)
        selection_layout.add_widget(minute_layout)
        
        layout.add_widget(selection_layout)
        
        # Button layout
        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=20,
            padding=[10, 20, 10, 10],
            size_hint_y=None,
            height=70
        )
        
        # Cancel button
        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.5,
            background_color=(0.8, 0.2, 0.2, 1),
            font_size=18
        )
        cancel_btn.bind(on_press=self.dismiss)
        
        # Confirm button
        confirm_btn = Button(
            text="Confirm",
            size_hint_x=0.5,
            background_color=(0.1, 0.7, 0.1, 1),
            font_size=18
        )
        confirm_btn.bind(on_press=self.on_confirm)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        
        layout.add_widget(btn_layout)
        self.add_widget(layout)
        
        # Add canvas background
        with self.canvas.before:
            Color(0.2, 0.2, 0.3, 1)  # Dark blue-gray background
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15,])
            
        # Update background size when window resizes
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    def validate_and_format(self):
        # Get hour and ensure it's within 0-23
        try:
            hour = int(self.hour_input.text)
            hour = min(max(hour, 0), 23)
            self.hour_input.text = f"{hour:02d}"
        except ValueError:
            self.hour_input.text = "00"
        
        # Get minute and ensure it's within 0-59
        try:
            minute = int(self.minute_input.text)
            minute = min(max(minute, 0), 59)
            self.minute_input.text = f"{minute:02d}"
        except ValueError:
            self.minute_input.text = "00"
    
    def increment_hour(self):
        try:
            hour = int(self.hour_input.text)
            hour = (hour + 1) % 24
            self.hour_input.text = f"{hour:02d}"
        except ValueError:
            self.hour_input.text = "00"
    
    def decrement_hour(self):
        try:
            hour = int(self.hour_input.text)
            hour = (hour - 1) % 24
            self.hour_input.text = f"{hour:02d}"
        except ValueError:
            self.hour_input.text = "23"
    
    def increment_minute(self):
        try:
            minute = int(self.minute_input.text)
            minute = (minute + 1) % 60
            self.minute_input.text = f"{minute:02d}"
        except ValueError:
            self.minute_input.text = "00"
    
    def decrement_minute(self):
        try:
            minute = int(self.minute_input.text)
            minute = (minute - 1) % 60
            self.minute_input.text = f"{minute:02d}"
        except ValueError:
            self.minute_input.text = "59"
    
    def on_confirm(self, instance):
        self.validate_and_format()
        time_str = f"{self.hour_input.text}:{self.minute_input.text}"
        self.callback(time_str)
        self.dismiss()

# Calendar Popup for Windows
class WindowsCalendarPopup(Popup):
    def __init__(self, parent, callback, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.8)
        self.title = "Select Date"
        self.callback = callback
        
        def select_date():
            root = tk.Tk()
            root.withdraw()
            top = tk.Toplevel(root)
            top.title("Calendar")
            
            cal = Calendar(top, selectmode='day')
            cal.pack(fill="both", expand=True)
            
            def ok_button():
                selected_date = cal.get_date()
                # Format date as month/day/year
                self.callback(selected_date)
                top.destroy()
                root.destroy()
                self.dismiss()
            
            ok_btn = tk.Button(top, text="OK", command=ok_button)
            ok_btn.pack()
            
            top.mainloop()
        
        threading.Thread(target=select_date, daemon=True).start()

# Welcome Screen
class WelcomeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Remove the banner widgets added in BaseScreen
        self.anchor_layout.clear_widgets()
        self.anchor_layout.add_widget(self.banner_layout)  # Add the banner back
        # Instructions Label
        instructions_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        instructions_box = BoxLayout(orientation='vertical', padding=20, spacing=25, size_hint_x=None, width=400)

        self.instructions = Label(
            text="Secure File Encryption By CryptoCloak. Click Below Button To Continue...",
            font_size=18,
            halign='center',
            font_name='Roboto'
        )
        self.instructions.color = get_color_from_hex('#FFFFFF')  # White
        instructions_box.add_widget(self.instructions)

        button_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), spacing=15,
                                    pos_hint={'center_x': 0.5, 'center_y': 0.5}) # Center the button
        self.next_btn = Button(
            text="Get Started",
            size_hint=(None, None),
            size=(150, 50),
            on_press=self.go_next,
            # Use a gradient background with black and azure
            background_color=(0, 0, 0, 0),  # Make the button background transparent
            background_normal='',
        )
        # Define the gradient in the style
        self.next_btn.background_color = [0, 0, 0, 1]
        button_layout.add_widget(self.next_btn)
        instructions_box.add_widget(button_layout)
        instructions_layout.add_widget(instructions_box)
        self.add_widget(instructions_layout)

        self.apply_gradient_effect(self.next_btn)

    def apply_gradient_effect(self, button):
        import math
        def update_gradient(dt):
            r, g, b, a = button.background_color
            phase = time.time() * 0.5  # Adjust speed here
            r = 0.1 + (0.3 * (1 + math.sin(phase)))
            g = 0.3 + (0.3 * (1 + math.cos(phase)))
            b = 0.5 + (0.5 * (1 + math.sin(phase * 1.2)))
            button.background_color = [r, g, b, a]
        Clock.schedule_interval(update_gradient, 0.02)
    
    def go_next(self, instance):
        self.manager.transition.direction = 'left'  # Set transition direction to left
        self.manager.current = "encrypt"
    
    def on_pre_enter(self):
        super().on_pre_enter()
        self.update_banner_position()

# Encryption Screen
class EncryptScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Remove the widgets added in BaseScreen and add them again
        self.anchor_layout.clear_widgets()
        self.anchor_layout.add_widget(self.banner_layout)
        
        # Main content of EncryptScreen
        main_content = BoxLayout(orientation='vertical', padding=20, spacing=25, size_hint_x=None, width=400, pos_hint={'center_x': 0.5, 'center_y': 0.5})

        self.title = Label(text="", font_size=20, halign='center')
        main_content.add_widget(self.title)

        button_layout = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint=(None, None), width=400)
        
        self.file_btn = Button(
            text="Choose File to Encrypt", 
            size_hint=(None, None), 
            size=(200, 50),
            on_press=self.select_file, 
            background_color=(0.2, 0.5, 1, 1)
        )
        button_layout.add_widget(self.file_btn)
        
        self.selected_file_label = Label(text="No file selected", font_size=16, halign='center')
        button_layout.add_widget(self.selected_file_label)
        
        self.save_btn = Button(
            text="Select Save Location", 
            size_hint=(None, None), 
            size=(200, 50),
            on_press=self.select_save_location, 
            background_color=(0.2, 0.5, 1, 1)
        )
        button_layout.add_widget(self.save_btn)
        
        # Date and Time selection
        date_time_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(None, None), width=400, height=100)
        
        # Date Selection
        date_layout = BoxLayout(orientation='vertical', size_hint_x=0.3)
        date_layout.add_widget(Label(text="Self-destruct date", halign='center'))
        self.date_btn = Button(
            text="Select Date", 
            size_hint=(None, None), 
            size=(140, 40),
            pos_hint={'center_x': 0.5},
            on_press=self.show_date_picker,
            background_color=(0.2, 0.5, 1, 1)
        )
        date_layout.add_widget(self.date_btn)
        self.date_label = Label(text="No date selected", font_size=14, halign='center')
        date_layout.add_widget(self.date_label)
        date_time_layout.add_widget(date_layout)
        
        # Time Selection
        time_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        time_layout.add_widget(Label(text="Self-destruct time", halign='center'))
        self.time_btn = Button(
            text="Select Time", 
            size_hint=(None, None), 
            size=(140, 40),
            pos_hint={'center_x': 0.5},
            on_press=self.show_time_picker,
            background_color=(0.2, 0.5, 1, 1)
        )
        time_layout.add_widget(self.time_btn)
        self.time_label = Label(text="No time selected", font_size=14, halign='center')
        time_layout.add_widget(self.time_label)
        date_time_layout.add_widget(time_layout)
        
        button_layout.add_widget(date_time_layout)
        
        # Progress
        self.progress_bar = ProgressBar(max=100, size_hint=(None, None), width=380, height=20, pos_hint={'center_x': 0.5})
        button_layout.add_widget(self.progress_bar)
        self.progress_label = Label(text="Ready", font_size=14, halign='center')
        button_layout.add_widget(self.progress_label)
        
        # Encryption button
        self.encrypt_btn = Button(
            text="Encrypt", 
            size_hint=(None, None), 
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.5, 1, 1),
            on_press=self.start_encryption
        )
        self.encrypt_btn.disabled = True
        button_layout.add_widget(self.encrypt_btn)
        
        # Encryption key display
        key_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(None, None), width=380, height=150)
        key_layout.add_widget(Label(
            text="Encryption Key (copied to clipboard):",
            font_size=16,
            halign='center',
            size_hint=(1, None),
            height=30
        ))
        
        self.encryption_key_box = TextInput(
            text="", 
            readonly=True, 
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            font_size=18,
            size_hint=(None, None),
            width=380,
            height=40,
            padding=[10, 10]
        )
        key_layout.add_widget(self.encryption_key_box)
        
        copy_btn = Button(
            text="Copy Key Again",
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={'center_x': 0.5},
            background_color=(0.3, 0.5, 0.8, 1),
            on_press=self.copy_key
        )
        key_layout.add_widget(copy_btn)
        button_layout.add_widget(key_layout)
        
        # Bottom buttons
        bottom_btn_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), width=380, height=50, spacing=10)
        
        self.back_btn = Button(
            text="Back",
            size_hint=(None, None),
            size=(100, 40),
            on_press=self.go_back
        )
        bottom_btn_layout.add_widget(self.back_btn)
        
        self.quit_btn = Button(
            text="Quit",
            size_hint=(None, None),
            size=(100, 40),
            on_press=self.quit_app
        )
        bottom_btn_layout.add_widget(self.quit_btn)
        
        button_layout.add_widget(bottom_btn_layout)
        main_content.add_widget(button_layout)
        
        self.anchor_layout.add_widget(main_content)
        
        # Initialize variables
        self.selected_file = None
        self.save_location = None
        self.encryption_progress = 0
        self.encryption_key = ""

    def show_date_picker(self, instance):
        def callback(date_str):
            self.date_label.text = date_str
            self.check_encrypt_button()
        WindowsCalendarPopup(self, callback).open()

    def show_time_picker(self, instance):
        def callback(time_str):
            self.time_label.text = time_str
            self.check_encrypt_button()
        TimePicker(callback).open()

    def copy_key(self, instance):
        if self.encryption_key:
            pyperclip.copy(self.encryption_key)
            self.update_progress_label("Key copied to clipboard!")

    def check_encrypt_button(self):
        if (self.selected_file and 
            self.save_location and 
            self.date_label.text != "No date selected" and 
            self.time_label.text != "No time selected"):
            self.encrypt_btn.disabled = False
        else:
            self.encrypt_btn.disabled = True

    def select_file(self, instance):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        root.destroy()
        if file_path:
            self.selected_file = file_path
            self.selected_file_label.text = f"Selected: {os.path.basename(file_path)}"
            self.check_encrypt_button()

    def select_save_location(self, instance):
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory()
        root.destroy()
        if folder_path:
            self.save_location = folder_path
            self.check_encrypt_button()

    def validate_datetime(self):
        try:
            # Validate date
            date_text = self.date_label.text
            if date_text == "No date selected":
                raise ValueError("Please select a destruction date")
            
            month, day, year = map(int, date_text.split('/'))
            
            # Handle 2-digit years
            if year < 100:
                current_year = datetime.now().year
                century = current_year // 100 * 100
                year += century
                if year < current_year:
                    year += 100
            
            # Validate time
            time_text = self.time_label.text
            if time_text == "No time selected":
                raise ValueError("Please select a destruction time")
            
            if ':' in time_text:
                hour_str, minute_str = time_text.split(':')
                hour = int(hour_str)
                minute = int(minute_str)
            else:
                raise ValueError("Invalid time format")
            
            # Validate ranges
            if not (1 <= day <= 31):
                raise ValueError("Invalid day")
            if not (1 <= month <= 12):
                raise ValueError("Invalid month")
            if year < datetime.now().year:
                raise ValueError("Year must be current or future")
            if not (0 <= hour <= 23):
                raise ValueError("Hour must be between 00 and 23")
            if not (0 <= minute <= 59):
                raise ValueError("Minute must be between 00 and 59")
                
            destroy_time = datetime(year, month, day, hour, minute)
            
            if destroy_time <= datetime.now():
                raise ValueError("Destruction time must be in the future")
                
            return destroy_time
            
        except ValueError as e:
            self.update_progress_label(str(e))
            return None

    def start_encryption(self, instance):
        destroy_time = self.validate_datetime()
        if destroy_time:
            self.show_progress_popup("Encrypting...")
            self.encrypt_btn.disabled = True
            threading.Thread(target=self.encrypt_file, args=(destroy_time,), daemon=True).start()

    def show_progress_popup(self, message):
        self.progress_label.text = message
        self.progress_bar.value = 0

    def encrypt_file(self, destroy_time):
        error_msg = None
        try:
            # Generate encryption key
            key = ''.join(random.choices(string.ascii_letters + string.digits, k=32)).encode()
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()

            # Read and encrypt file
            file_size = os.path.getsize(self.selected_file)
            chunk_size = 1024 * 1024  # 1MB chunks
            
            encrypted_file_path = os.path.join(
                self.save_location, 
                os.path.basename(self.selected_file) + ".enc"
            )
            
            padder = padding.PKCS7(128).padder()
            bytes_processed = 0
            
            with open(self.selected_file, 'rb') as infile, open(encrypted_file_path, 'wb') as outfile:
                outfile.write(iv)
                
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        break
                    
                    if len(chunk) < chunk_size:
                        padded = padder.update(chunk) + padder.finalize()
                    else:
                        padded = padder.update(chunk)
                    
                    encrypted = encryptor.update(padded)
                    outfile.write(encrypted)
                    
                    # Update progress
                    bytes_processed += len(chunk)
                    progress = (bytes_processed / file_size) * 100
                    self.update_progress(progress)
            
            # Finalize encryption
            final = encryptor.finalize()
            if final:
                with open(encrypted_file_path, 'ab') as outfile:
                    outfile.write(final)
            
            # Set up self-destruct
            self.setup_self_destruct(destroy_time, encrypted_file_path)
            
            # Display key in the white box
            self.encryption_key = key.decode()
            Clock.schedule_once(lambda dt: pyperclip.copy(self.encryption_key))
            self.update_ui_after_encryption()
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
        finally:
            if error_msg:
                self.update_progress_label(error_msg)
            self.enable_encrypt_button()

    def setup_self_destruct(self, destroy_time, file_path):
        def run_timer():
            while datetime.now() < destroy_time:
                time.sleep(1)
            
            # Time's up - securely delete encrypted file
            try:
                with open(file_path, 'ba+') as f:
                    length = f.tell()
                    for _ in range(3):
                        f.seek(0)
                        f.write(os.urandom(length))
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
        
        timer_thread = threading.Thread(target=run_timer, daemon=True)
        timer_thread.start()
        
        # Show timer popup
        self.show_destruct_popup(destroy_time)

    # Thread-safe UI update methods
    def update_progress(self, value):
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', value))

    def update_progress_label(self, text):
        Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', text))

    def update_ui_after_encryption(self):
        Clock.schedule_once(lambda dt: (
            setattr(self.encryption_key_box, 'text', self.encryption_key),
            setattr(self.progress_label, 'text', "Encryption Complete! Key copied to clipboard.")
        ))

    def enable_encrypt_button(self):
        Clock.schedule_once(lambda dt: setattr(self.encrypt_btn, 'disabled', False))

    def show_destruct_popup(self, destroy_time):
        Clock.schedule_once(lambda dt: Popup(
            title='Self-Destruct Timer',
            content=Label(text=f"Encrypted file will self-destruct at:\n{destroy_time.strftime('%Y-%m-%d %H:%M:%S')}"),
            size_hint=(0.8, 0.5)
        ).open())

    def go_back(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = "welcome"
    
    def quit_app(self, instance):
        App.get_running_app().stop()
        
    def on_pre_enter(self):
        super().on_pre_enter()
        self.update_banner_position()

# Main App
class CryptoCloakApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)  # Set background color to black
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(WelcomeScreen(name="welcome"))
        sm.add_widget(EncryptScreen(name="encrypt"))
        return sm

if __name__ == "__main__":
    CryptoCloakApp().run()