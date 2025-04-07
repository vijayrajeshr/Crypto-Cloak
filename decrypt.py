import os
import pyperclip
from tkinter import Tk, filedialog
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from kivy.uix.anchorlayout import AnchorLayout  # Import AnchorLayout
from kivy.core.window import Window  # Import the Window module
from kivy.utils import get_color_from_hex
from kivy.graphics import Rectangle, Color

class BaseScreen(Screen):  # Base screen to include the banner
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
            bold=True, # Make the title bold
        )
        self.banner_title.color = get_color_from_hex('#FFFFFF')
        self.banner_layout.add_widget(self.banner_title)
        self.banner_layout.add_widget(Label(size_hint_x=1))  # Spacer
        self.anchor_layout.add_widget(self.banner_layout)
        self.add_widget(self.anchor_layout)

    def update_banner_position(self):
        # Update the banner position when the screen is entered.
        self.banner_layout.pos[1] = Window.height - 50
        self.banner_rect.pos = (0, Window.height - 50)



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
            text="Secure File Decryption By CryptoCloak. Click Below Button To Continue...",
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
        import time
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
        self.manager.current = "decrypt"

    def on_pre_enter(self):
        super().on_pre_enter()
        self.update_banner_position()



class DecryptScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Remove the widgets added in BaseScreen and add them again.
        self.anchor_layout.clear_widgets()
        self.anchor_layout.add_widget(self.banner_layout)
        # Main content of DecryptScreen
        main_content = BoxLayout(orientation='vertical', padding=20, spacing=25, size_hint_x=None, width=400, pos_hint={'center_x': 0.5, 'center_y': 0.5}) # Center main content

        self.title = Label(text="Decrypt the File", font_size=20, halign='center')
        main_content.add_widget(self.title)

        button_layout = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint=(None, None), width=400) # Removed centering from here
        self.file_btn = Button(text="Select Encrypted File", size_hint=(None, None), size=(200, 50),
                                    on_press=self.select_file, background_color=(0.2, 0.5, 1, 1))
        button_layout.add_widget(self.file_btn)

        self.selected_file_label = Label(text="No file selected", font_size=16, halign='center')
        button_layout.add_widget(self.selected_file_label)

        self.key_input = TextInput(hint_text="Enter Encryption Key", size_hint=(None, None), size=(200, 40))
        button_layout.add_widget(self.key_input)

        self.decrypt_btn = Button(text="Decrypt File", background_color=(0.2, 0.5, 1, 1), size_hint=(None, None),
                                     size=(200, 50), on_press=self.decrypt_file, disabled=True)
        button_layout.add_widget(self.decrypt_btn)

        main_content.add_widget(button_layout)

        button_layout_bottom = BoxLayout(orientation='horizontal', spacing=15, padding=[10, 25, 10, 10],
                                            size_hint_x=None, size_hint_y=None, pos_hint={'center_x': 0.5}) # Center bottom buttons.  Remove the x,y
        self.back_btn = Button(text="Back", size_hint=(None, None), size=(100, 40), on_press=self.go_back)
        button_layout_bottom.add_widget(self.back_btn)
        main_content.add_widget(button_layout_bottom)

        self.anchor_layout.add_widget(main_content) # Add main_content, not layout
        #self.add_widget(self.anchor_layout)  # Removed this line
        self.decryption_key = ""
        self.selected_file = None
        self.decrypted_file_path = None

    def on_pre_enter(self):
        super().on_pre_enter()
        self.update_banner_position()

    def select_file(self, instance):
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Encrypted Files", "*.enc")])  # Only show .enc files
        if file_path:
            self.selected_file = file_path
            self.selected_file_label.text = f"Selected File: {os.path.basename(file_path)}"
            self.decrypt_btn.disabled = False

    def decrypt_file(self, instance):
        if not self.selected_file or not self.key_input.text:
            return

        self.decryption_key = self.key_input.text.encode()
        self.show_progress_popup()
        Clock.schedule_once(self.perform_decryption, 0.01)  # Reduced delay for smoother progress

    def show_progress_popup(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text="Decrypting, please wait..."))
        self.progress_bar = ProgressBar(max=100)
        content.add_widget(self.progress_bar)

        self.progress_popup = Popup(title="Processing", content=content,
                                     size_hint=(None, None), size=(300, 150), auto_dismiss=False)
        self.progress_popup.open()

    def perform_decryption(self, dt):
        try:
            with open(self.selected_file, 'rb') as f:
                encrypted_data = f.read()
                total_length = len(encrypted_data)
                chunk_size = 8192  # Process in chunks

            iv = encrypted_data[:16]
            encrypted_data = encrypted_data[16:]

            cipher = Cipher(algorithms.AES(self.decryption_key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_chunks = b""
            decrypted_length = 0

            with open(self.selected_file, 'rb') as infile:
                infile.seek(16)  # Skip the IV
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        break
                    decrypted_chunk = decryptor.update(chunk)
                    decrypted_chunks += decrypted_chunk
                    decrypted_length += len(decrypted_chunk)
                    if total_length > 0:
                        self.progress_bar.value = (decrypted_length / (total_length - 16)) * 100
                    else:
                        self.progress_bar.value = 0  # Avoid division by zero

            final_decrypted_data = decrypted_chunks + decryptor.finalize()

            unpadder = padding.PKCS7(128).unpadder()
            unpadded_data = unpadder.update(final_decrypted_data) + unpadder.finalize()

            self.decrypted_file_path = self.selected_file.replace(".enc", ".dec")

            with open(self.decrypted_file_path, 'wb') as outfile:
                outfile.write(unpadded_data)

            if self.progress_popup:
                self.progress_popup.dismiss()

            self.manager.transition.direction = 'left'
            self.manager.current = "final_decrypt"
        except Exception as e:
            if self.progress_popup:
                self.progress_popup.dismiss()
            popup = Popup(title='Decryption Error',
                          content=Label(text=f'An error occurred during decryption: {e}', text_size=(380, None)),
                          size_hint=(None, None), size=(400, 200))
            popup.open()

    def go_back(self, instance):
        self.manager.transition.direction = 'right'  # Set transition direction to right
        self.manager.current = "welcome"



class FinalDecryptScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Remove the widgets added in BaseScreen and add them again.
        self.anchor_layout.clear_widgets()
        self.anchor_layout.add_widget(self.banner_layout)
        # Main content
        main_content = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_x=None, width=400)

        self.title = Label(text="Decryption Successful!", font_size=20, halign='center')
        main_content.add_widget(self.title)

        self.decrypted_file_label = Label(text="Decrypted File: Not Generated", font_size=16, halign='center')
        main_content.add_widget(self.decrypted_file_label)

        button_layout = BoxLayout(orientation='horizontal', spacing=30, padding=[20, 25, 20, 10],
                                    size_hint_x=None, size_hint_y=None, pos_hint={'center_x': 0.5}) # Center
        self.show_file_btn = Button(text="Show Decrypted File Location", size_hint=(None, None), size=(200, 50),
                                         on_press=self.show_decrypted_file)
        self.copy_key_btn = Button(text="Copy Key", size_hint=(None, None), size=(150, 50),
                                        on_press=self.copy_decryption_key)
        self.finish_btn = Button(text="Finish", background_color=(0.1, 0.7, 0.1, 1), size_hint=(None, None),
                                   size=(100, 50), on_press=self.finish)

        button_layout.add_widget(self.show_file_btn)
        button_layout.add_widget(self.copy_key_btn)
        button_layout.add_widget(self.finish_btn)

        main_content.add_widget(button_layout)
        self.anchor_layout.add_widget(main_content) # Add main_content, not layout.
        #self.add_widget(self.anchor_layout) # Remove this line
        

    def on_pre_enter(self):
        super().on_pre_enter()
        self.update_banner_position()
        decrypt_screen = self.manager.get_screen("decrypt")
        if decrypt_screen.decrypted_file_path:
            self.decrypted_file_label.text = f"Decrypted File: {decrypt_screen.decrypted_file_path}"
        else:
            self.decrypted_file_label.text = "Decrypted File: Error generating file"

    def show_decrypted_file(self, instance):
        decrypt_screen = self.manager.get_screen("decrypt")
        if decrypt_screen.decrypted_file_path:
            try:
                os.startfile(os.path.dirname(decrypt_screen.decrypted_file_path))
            except AttributeError:
                popup = Popup(title='Error', content=Label(text='Decrypted file path not found.'),
                              size_hint=(None, None), size=(300, 150))
                popup.open()
            except OSError:
                popup = Popup(title='Error', content=Label(text='Could not open file explorer.'),
                              size_hint=(None, None), size=(300, 150))
                popup.open()
        else:
            popup = Popup(title='Error', content=Label(text='No file has been decrypted yet.'),
                          size_hint=(None, None), size=(300, 150))
            popup.open()

    def copy_decryption_key(self, instance):
        decrypt_screen = self.manager.get_screen("decrypt")
        if decrypt_screen.decryption_key:
            pyperclip.copy(decrypt_screen.decryption_key.decode())
            popup = Popup(title='Key Copied', content=Label(text='Decryption key copied to clipboard.'),
                          size_hint=(None, None), size=(300, 150))
            popup.open()
        else:
            popup = Popup(title='Error', content=Label(text='Decryption key is not available.'),
                          size_hint=(None, None), size=(300, 150))
            popup.open()

    def finish(self, instance):
        App.get_running_app().stop()

class FileDecryptorApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition())  # Use SlideTransition
        sm.add_widget(WelcomeScreen(name="welcome"))
        sm.add_widget(DecryptScreen(name="decrypt"))
        sm.add_widget(FinalDecryptScreen(name="final_decrypt"))
        return sm

if __name__ == "__main__":
    import math
    FileDecryptorApp().run()
