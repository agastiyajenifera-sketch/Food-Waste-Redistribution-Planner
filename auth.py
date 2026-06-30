import customtkinter as ctk
import tkinter as tk
import os
from PIL import Image
from config import IMAGES_DIR, FONT_FAMILY, THEME_COLORS
from models import User, NGO
from utils import validate_email, validate_phone

class AuthFrame(ctk.CTkFrame):
    """Frame containing Login and Registration user interfaces with password show/hide eye toggles."""
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.is_register_mode = False

        # Apply grid weight for responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Card container (Split Layout: Left = Banner, Right = Forms)
        self.card = ctk.CTkFrame(self, width=900, height=560, corner_radius=20, border_width=2, border_color=THEME_COLORS["primary"])
        self.card.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        
        self.card.grid_columnconfigure(0, weight=1, minsize=450)  # Left (Banner)
        self.card.grid_columnconfigure(1, weight=1, minsize=450)  # Right (Forms)
        self.card.grid_rowconfigure(0, weight=1)
        self.card.grid_propagate(False)

        # Show initial login panel
        self.show_login_view()

    def clear_card(self):
        """Helper to clear widgets inside the card before switching views."""
        for widget in self.card.winfo_children():
            widget.destroy()

    def show_banner(self):
        """Renders the left side project banner illustration."""
        banner_frame = ctk.CTkFrame(self.card, fg_color=("gray95", "gray15"), corner_radius=0)
        banner_frame.grid(row=0, column=0, sticky="nsew")
        banner_frame.grid_columnconfigure(0, weight=1)
        banner_frame.grid_rowconfigure((0, 1, 2), weight=1)

        # Load login_banner.jpg from assets
        img_path = os.path.join(IMAGES_DIR, "login_banner.jpg")
        if os.path.exists(img_path):
            try:
                pil_img = Image.open(img_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(360, 360))
                img_lbl = ctk.CTkLabel(banner_frame, image=ctk_img, text="")
                img_lbl.grid(row=1, column=0, padx=20, pady=20)
            except Exception as e:
                print(f"Error loading login banner: {e}")
        else:
            # Fallback text logo (ALL CAPS bold unique font)
            fallback_lbl = ctk.CTkLabel(banner_frame, text="FOODSHARE\nREDISTRIBUTION\nPLANNER", 
                                        font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"))
            fallback_lbl.grid(row=1, column=0, padx=20, pady=20)
            
        # Add slogan at the bottom of the left banner
        slogan_lbl = ctk.CTkLabel(banner_frame, text="REDISTRIBUTE SURPLUS. FEED COMMUNITIES. REDUCE WASTE.", 
                                  font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=THEME_COLORS["primary"])
        slogan_lbl.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="s")

    def show_login_view(self):
        self.clear_card()
        self.is_register_mode = False
        
        # Redraw left banner
        self.show_banner()

        # Right container frame (Column 1)
        right_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=35, pady=35)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        # Header Title (Bold, ALL CAPS unique font)
        title = ctk.CTkLabel(right_frame, text="SIGN IN TO FOODSHARE", font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(15, 2), sticky="ew")

        subtitle = ctk.CTkLabel(right_frame, text="Connecting surplus food with those in need.", 
                                font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color="gray")
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Email entry (uses custom font)
        self.login_email = ctk.CTkEntry(right_frame, placeholder_text="Email Address", width=300, height=40, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.login_email.grid(row=2, column=0, padx=20, pady=8)

        # Password frame to house entry + eye toggle button
        password_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        password_frame.grid(row=3, column=0, padx=20, pady=8, sticky="ew")
        password_frame.grid_columnconfigure(0, weight=1)

        self.login_password = ctk.CTkEntry(password_frame, placeholder_text="Password", show="*", height=40, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.login_password.grid(row=0, column=0, sticky="ew")

        self.btn_show_pass = ctk.CTkButton(password_frame, text="👁️", width=35, height=36, fg_color="transparent", hover=False, text_color="gray", command=self.toggle_login_password)
        self.btn_show_pass.grid(row=0, column=1, padx=(5, 0))

        # Error text
        self.error_label = ctk.CTkLabel(right_frame, text="", text_color="#ef4444", font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.error_label.grid(row=4, column=0, padx=20, pady=2)

        # Login button (styled with primary color)
        btn_login = ctk.CTkButton(right_frame, text="SIGN IN", command=self.handle_login, 
                                   width=300, height=40, fg_color=THEME_COLORS["primary"], hover_color=THEME_COLORS["primary"],
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"))
        btn_login.grid(row=5, column=0, padx=20, pady=10)

        # Toggle Register view button
        btn_toggle = ctk.CTkButton(right_frame, text="Don't have an account? Sign Up", fg_color="transparent", 
                                    text_color=THEME_COLORS["primary"],
                                    hover=False, command=self.show_register_view, font=ctk.CTkFont(family=FONT_FAMILY, size=12, underline=True))
        btn_toggle.grid(row=6, column=0, padx=20, pady=(5, 20))

    def show_register_view(self):
        self.clear_card()
        self.is_register_mode = True
        
        # Redraw left banner
        self.show_banner()

        # Right container frame (Column 1)
        right_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)

        # Wrap in scrollable frame for overflow fields
        scroll = ctk.CTkScrollableFrame(right_frame, width=380, height=480, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Bold ALL CAPS unique font
        title = ctk.CTkLabel(scroll, text="JOIN FOODSHARE", font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(10, 2))

        subtitle = ctk.CTkLabel(scroll, text="Create your free account today.", 
                                font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color="gray")
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 15))

        # Full Name
        self.reg_name = ctk.CTkEntry(scroll, placeholder_text="Full Name / Authorized Person", width=300, height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.reg_name.grid(row=2, column=0, padx=20, pady=6)

        # Email
        self.reg_email = ctk.CTkEntry(scroll, placeholder_text="Email Address", width=300, height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.reg_email.grid(row=3, column=0, padx=20, pady=6)

        # Registration password frame + eye button
        reg_pass_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        reg_pass_frame.grid(row=4, column=0, padx=20, pady=6, sticky="ew")
        reg_pass_frame.grid_columnconfigure(0, weight=1)

        self.reg_password = ctk.CTkEntry(reg_pass_frame, placeholder_text="Password", show="*", width=300, height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.reg_password.grid(row=0, column=0, sticky="ew")

        self.btn_show_reg_pass = ctk.CTkButton(reg_pass_frame, text="👁️", width=35, height=32, fg_color="transparent", hover=False, text_color="gray", command=self.toggle_reg_password)
        self.btn_show_reg_pass.grid(row=0, column=1, padx=(5, 0))

        # Phone
        self.reg_phone = ctk.CTkEntry(scroll, placeholder_text="Contact Phone Number", width=300, height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.reg_phone.grid(row=5, column=0, padx=20, pady=6)

        # Address
        self.reg_address = ctk.CTkEntry(scroll, placeholder_text="Address (include coordinates: (lat, lon))", width=300, height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.reg_address.grid(row=6, column=0, padx=20, pady=6)

        # Role Selection (Segmented Control)
        role_label = ctk.CTkLabel(scroll, text="Account Role:", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"))
        role_label.grid(row=7, column=0, padx=20, pady=(8, 2), sticky="w")
        
        self.reg_role = ctk.CTkSegmentedButton(scroll, values=["Donor", "NGO", "Admin"], 
                                                command=self.toggle_role_fields, width=300,
                                                selected_color=THEME_COLORS["primary"][1],
                                                font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.reg_role.grid(row=8, column=0, padx=20, pady=5)
        self.reg_role.set("Donor")

        # Container for NGO specific fields
        self.ngo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.ngo_frame.grid_columnconfigure(0, weight=1)

        # NGO inputs
        self.ngo_org_name = ctk.CTkEntry(self.ngo_frame, placeholder_text="Organization Name", width=300, height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.ngo_org_name.grid(row=0, column=0, padx=0, pady=6)

        self.ngo_reg_num = ctk.CTkEntry(self.ngo_frame, placeholder_text="Government Registration No.", width=300, height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.ngo_reg_num.grid(row=1, column=0, padx=0, pady=6)

        # Error label
        self.reg_error = ctk.CTkLabel(scroll, text="", text_color="#ef4444", font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.reg_error.grid(row=10, column=0, padx=20, pady=3)

        # Register button
        btn_register = ctk.CTkButton(scroll, text="CREATE ACCOUNT", command=self.handle_registration, 
                                      width=300, height=38, fg_color=THEME_COLORS["primary"], hover_color=THEME_COLORS["primary"],
                                      font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"))
        btn_register.grid(row=11, column=0, padx=20, pady=10)

        # Toggle Login view button
        btn_toggle = ctk.CTkButton(scroll, text="Already have an account? Sign In", fg_color="transparent", 
                                    text_color=THEME_COLORS["primary"],
                                    hover=False, command=self.show_login_view, font=ctk.CTkFont(family=FONT_FAMILY, size=12, underline=True))
        btn_toggle.grid(row=12, column=0, padx=20, pady=(3, 10))

    def toggle_login_password(self):
        """Toggles login password visibility."""
        if self.login_password.cget("show") == "*":
            self.login_password.configure(show="")
            self.btn_show_pass.configure(text="🙈")
        else:
            self.login_password.configure(show="*")
            self.btn_show_pass.configure(text="👁️")

    def toggle_reg_password(self):
        """Toggles registration password visibility."""
        if self.reg_password.cget("show") == "*":
            self.reg_password.configure(show="")
            self.btn_show_reg_pass.configure(text="🙈")
        else:
            self.reg_password.configure(show="*")
            self.btn_show_reg_pass.configure(text="👁️")

    def toggle_role_fields(self, role):
        """Displays NGO specific input fields only if 'NGO' role is selected."""
        if role == "NGO":
            self.ngo_frame.grid(row=9, column=0, padx=20, pady=5, sticky="ew")
        else:
            self.ngo_frame.grid_forget()

    def handle_login(self):
        email = self.login_email.get().strip()
        password = self.login_password.get().strip()

        if not email or not password:
            self.error_label.configure(text="Please fill in all fields.")
            return

        user = User.authenticate(email, password)
        if user:
            self.error_label.configure(text="")
            # Redirect to app.py container view
            self.on_login_success(user)
        else:
            self.error_label.configure(text="Invalid email or password.")

    def handle_registration(self):
        full_name = self.reg_name.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get().strip()
        phone = self.reg_phone.get().strip()
        address = self.reg_address.get().strip()
        role = self.reg_role.get()

        # Validations
        if not all([full_name, email, password, phone, address]):
            self.reg_error.configure(text="All primary fields are required.")
            return

        if not validate_email(email):
            self.reg_error.configure(text="Please enter a valid email address.")
            return

        if len(password) < 6:
            self.reg_error.configure(text="Password must be at least 6 characters.")
            return

        if not validate_phone(phone):
            self.reg_error.configure(text="Contact phone must be at least 10 digits.")
            return

        # NGO Specific Validations
        if role == "NGO":
            org_name = self.ngo_org_name.get().strip()
            reg_num = self.ngo_reg_num.get().strip()
            if not org_name or not reg_num:
                self.reg_error.configure(text="Please fill NGO Organization and Registration fields.")
                return

        # Try to create User
        user = User.create(full_name, email, password, phone, address, role)
        if not user:
            self.reg_error.configure(text="User email already registered.")
            return

        # Save NGO details if applicable
        if role == "NGO":
            ngo = NGO.create(
                user_id=user.user_id,
                organization_name=org_name,
                registration_number=reg_num,
                location=address,
                phone=phone,
                email=email
            )
            if not ngo:
                # Cleanup user if NGO fails (e.g. duplicate reg num)
                User.delete(user.user_id)
                self.reg_error.configure(text="Registration number already registered.")
                return

        # Success - Auto Login
        self.reg_error.configure(text="")
        self.on_login_success(user)
