import customtkinter as ctk
import tkinter as tk
from models import User, NGO
from utils import validate_email, validate_phone

class AuthFrame(ctk.CTkFrame):
    """Frame containing Login and Registration user interfaces."""
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.is_register_mode = False

        # Apply grid grid-weight for responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Card container
        self.card = ctk.CTkFrame(self, width=450, corner_radius=15)
        self.card.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        self.card.grid_columnconfigure(0, weight=1)

        # Show initial login panel
        self.show_login_view()

    def clear_card(self):
        """Helper to clear widgets inside the card before switching views."""
        for widget in self.card.winfo_children():
            widget.destroy()

    def show_login_view(self):
        self.clear_card()
        self.is_register_mode = False

        # Header Title
        title = ctk.CTkLabel(self.card, text="FoodShare Redistribution", font=ctk.CTkFont(size=22, weight="bold"))
        title.grid(row=0, column=0, padx=30, pady=(40, 5))

        subtitle = ctk.CTkLabel(self.card, text="Connecting Surplus Food With Those In Need.", 
                                font=ctk.CTkFont(size=13), text_color="gray")
        subtitle.grid(row=1, column=0, padx=30, pady=(0, 30))

        # Email entry
        self.login_email = ctk.CTkEntry(self.card, placeholder_text="Email Address", width=320, height=40)
        self.login_email.grid(row=2, column=0, padx=30, pady=10)

        # Password entry
        self.login_password = ctk.CTkEntry(self.card, placeholder_text="Password", show="*", width=320, height=40)
        self.login_password.grid(row=3, column=0, padx=30, pady=10)

        # Error text
        self.error_label = ctk.CTkLabel(self.card, text="", text_color="#ef4444", font=ctk.CTkFont(size=12))
        self.error_label.grid(row=4, column=0, padx=30, pady=(5, 5))

        # Login button
        btn_login = ctk.CTkButton(self.card, text="Sign In", command=self.handle_login, 
                                   width=320, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        btn_login.grid(row=5, column=0, padx=30, pady=15)

        # Toggle Register view button
        btn_toggle = ctk.CTkButton(self.card, text="Don't have an account? Sign Up", fg_color="transparent", 
                                    text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                                    hover=False, command=self.show_register_view, font=ctk.CTkFont(size=12, underline=True))
        btn_toggle.grid(row=6, column=0, padx=30, pady=(10, 40))

    def show_register_view(self):
        self.clear_card()
        self.is_register_mode = True

        # Wrap in scrollable frame for overflow fields
        scroll = ctk.CTkScrollableFrame(self.card, width=380, height=520, fg_color="transparent")
        scroll.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(scroll, text="Join FoodShare", font=ctk.CTkFont(size=22, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(15, 5))

        subtitle = ctk.CTkLabel(scroll, text="Create your free account today.", 
                                font=ctk.CTkFont(size=12), text_color="gray")
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Full Name
        self.reg_name = ctk.CTkEntry(scroll, placeholder_text="Full Name / Authorized Person", width=300, height=35)
        self.reg_name.grid(row=2, column=0, padx=20, pady=8)

        # Email
        self.reg_email = ctk.CTkEntry(scroll, placeholder_text="Email Address", width=300, height=35)
        self.reg_email.grid(row=3, column=0, padx=20, pady=8)

        # Password
        self.reg_password = ctk.CTkEntry(scroll, placeholder_text="Password", show="*", width=300, height=35)
        self.reg_password.grid(row=4, column=0, padx=20, pady=8)

        # Phone
        self.reg_phone = ctk.CTkEntry(scroll, placeholder_text="Contact Phone Number", width=300, height=35)
        self.reg_phone.grid(row=5, column=0, padx=20, pady=8)

        # Address
        self.reg_address = ctk.CTkEntry(scroll, placeholder_text="Address (include coordinates: (lat, lon))", width=300, height=35)
        self.reg_address.grid(row=6, column=0, padx=20, pady=8)

        # Role Selection (Segmented Control)
        role_label = ctk.CTkLabel(scroll, text="Account Role:", font=ctk.CTkFont(size=12, weight="bold"))
        role_label.grid(row=7, column=0, padx=20, pady=(10, 2), sticky="w")
        
        self.reg_role = ctk.CTkSegmentedButton(scroll, values=["Donor", "NGO", "Admin"], 
                                                command=self.toggle_role_fields, width=300)
        self.reg_role.grid(row=8, column=0, padx=20, pady=5)
        self.reg_role.set("Donor")

        # Container for NGO specific fields
        self.ngo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.ngo_frame.grid_columnconfigure(0, weight=1)

        # NGO inputs
        self.ngo_org_name = ctk.CTkEntry(self.ngo_frame, placeholder_text="Organization Name", width=300, height=35)
        self.ngo_org_name.grid(row=0, column=0, padx=0, pady=8)

        self.ngo_reg_num = ctk.CTkEntry(self.ngo_frame, placeholder_text="Government Registration No.", width=300, height=35)
        self.ngo_reg_num.grid(row=1, column=0, padx=0, pady=8)

        # Error label
        self.reg_error = ctk.CTkLabel(scroll, text="", text_color="#ef4444", font=ctk.CTkFont(size=12))
        self.reg_error.grid(row=10, column=0, padx=20, pady=5)

        # Register button
        btn_register = ctk.CTkButton(scroll, text="Create Account", command=self.handle_registration, 
                                      width=300, height=38, font=ctk.CTkFont(size=13, weight="bold"))
        btn_register.grid(row=11, column=0, padx=20, pady=15)

        # Toggle Login view button
        btn_toggle = ctk.CTkButton(scroll, text="Already have an account? Sign In", fg_color="transparent", 
                                    text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                                    hover=False, command=self.show_login_view, font=ctk.CTkFont(size=12, underline=True))
        btn_toggle.grid(row=12, column=0, padx=20, pady=(5, 15))

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
