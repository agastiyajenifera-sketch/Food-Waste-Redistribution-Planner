import customtkinter as ctk
import os
import database
from auth import AuthFrame
from admin import AdminDashboard
from donor import DonorDashboard
from ngo import NGODashboard
from config import WINDOW_TITLE, WINDOW_SIZE, DEFAULT_THEME, COLOR_THEME

class FoodShareApp(ctk.CTk):
    """Main window class coordinating routing and user state."""
    def __init__(self):
        super().__init__()
        
        # Configure Window
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(980, 600)

        # Center on screen
        self.center_window()

        # Set CustomTkinter theme configurations
        ctk.set_appearance_mode(DEFAULT_THEME)
        ctk.set_default_color_theme(COLOR_THEME)

        # Initialize and seed database if empty
        database.initialize()

        # Track session state
        self.current_user = None
        self.current_frame = None

        # Load Authentication flow initially
        self.show_auth_screen()

    def center_window(self):
        """Calculates screen dimensions to center the app on startup."""
        self.update_idletasks()
        width = 1100
        height = 680
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_auth_screen(self):
        """Clears frame container and renders Login/Registration card."""
        if self.current_frame:
            self.current_frame.destroy()

        self.current_user = None
        self.current_frame = AuthFrame(self, on_login_success=self.login_user_session)
        self.current_frame.pack(fill="both", expand=True)

    def login_user_session(self, user):
        """Callback from AuthFrame redirecting to correct dashboard."""
        self.current_user = user
        if self.current_frame:
            self.current_frame.destroy()

        # Redirect user based on their system role
        if user.role == "Admin":
            self.current_frame = AdminDashboard(
                self, 
                user=self.current_user, 
                on_logout=self.show_auth_screen,
                change_theme_callback=self.set_theme
            )
        elif user.role == "Donor":
            self.current_frame = DonorDashboard(
                self,
                user=self.current_user,
                on_logout=self.show_auth_screen,
                change_theme_callback=self.set_theme
            )
        elif user.role == "NGO":
            self.current_frame = NGODashboard(
                self,
                user=self.current_user,
                on_logout=self.show_auth_screen,
                change_theme_callback=self.set_theme
            )

        self.current_frame.pack(fill="both", expand=True)

    def set_theme(self, theme_mode):
        """Changes the appearance mode globally (light or dark)."""
        ctk.set_appearance_mode(theme_mode)

if __name__ == "__main__":
    # Start the desktop GUI event loop
    app = FoodShareApp()
    app.mainloop()
