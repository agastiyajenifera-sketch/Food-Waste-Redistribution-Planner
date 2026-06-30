import os
import shutil
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
from PIL import Image
from config import IMAGES_DIR, FOOD_CATEGORIES, FOOD_UNITS, FONT_FAMILY, THEME_COLORS
from models import Donation, User, Notification
from utils import parse_datetime, predict_expiry_risk, extract_coords_from_text

class DonorDashboard(ctk.CTkFrame):
    """Donor Dashboard layout with sidebar navigation, custom typography, and visual previews."""
    def __init__(self, parent, user, on_logout, change_theme_callback):
        super().__init__(parent)
        self.user = user
        self.on_logout = on_logout
        self.change_theme_callback = change_theme_callback
        self.editing_donation_id = None  # Track if editing an item
        self.selected_image_path = None  # Track uploaded image path

        # Layout: Left sidebar, right content area
        self.grid_columnconfigure(0, minsize=200, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.current_theme = ctk.get_appearance_mode().lower()

        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=("#f1f5f9", "#111827"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(4, weight=1)  # Spacer

        # Sidebar Title (ALL CAPS bold unique font)
        sidebar_title = ctk.CTkLabel(self.sidebar, text="DONOR PORTAL", 
                                     font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
                                     text_color=THEME_COLORS["primary"])
        sidebar_title.grid(row=0, column=0, padx=20, pady=25)

        # Nav Buttons
        self.btn_my_donations = ctk.CTkButton(self.sidebar, text="My Donations", anchor="w", fg_color="transparent",
                                              text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                              font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                                              command=lambda: self.switch_view("my_donations"))
        self.btn_my_donations.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.btn_new_donation = ctk.CTkButton(self.sidebar, text="Donate Food", anchor="w", fg_color="transparent",
                                              text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                              font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                                              command=lambda: self.switch_view("new_donation"))
        self.btn_new_donation.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.btn_notifs = ctk.CTkButton(self.sidebar, text="Notifications", anchor="w", fg_color="transparent",
                                         text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                                         command=lambda: self.switch_view("notifications"))
        self.btn_notifs.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Dark/Light Mode switch
        self.theme_switch = ctk.CTkSwitch(self.sidebar, text="Dark Mode", command=self.toggle_theme,
                                           progress_color=THEME_COLORS["primary"],
                                           font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.theme_switch.grid(row=5, column=0, padx=20, pady=10, sticky="w")
        if self.current_theme == "dark":
            self.theme_switch.select()

        btn_logout = ctk.CTkButton(self.sidebar, text="LOG OUT", fg_color=THEME_COLORS["primary"], hover_color=THEME_COLORS["primary"],
                                    text_color="white", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                                    command=self.on_logout)
        btn_logout.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        # Content Frame
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        # Switch to default
        self.switch_view("my_donations")

    def toggle_theme(self):
        new_theme = "dark" if self.theme_switch.get() == 1 else "light"
        self.current_theme = new_theme
        self.change_theme_callback(new_theme)

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def switch_view(self, view_name):
        self.current_view = view_name
        self.clear_content()

        # Update sidebar button highlight
        buttons = {
            "my_donations": self.btn_my_donations,
            "new_donation": self.btn_new_donation,
            "notifications": self.btn_notifs
        }
        for name, btn in buttons.items():
            if name == view_name:
                btn.configure(fg_color=THEME_COLORS["accent"], text_color="white", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"))
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"), font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="normal"))

        if view_name == "my_donations":
            self.show_my_donations_view()
        elif view_name == "new_donation":
            self.show_donation_form()
        elif view_name == "notifications":
            self.show_notifications_view()

    # --- View 1: My Donations ---
    def show_my_donations_view(self):
        self.content_area.grid_rowconfigure(0, weight=0)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Title / Buttons
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)

        # Bold ALL CAPS header
        title = ctk.CTkLabel(header_frame, text="MY REGISTERED SURPLUS DONATIONS", 
                             font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"))
        title.grid(row=0, column=0, sticky="w")

        btn_add = ctk.CTkButton(header_frame, text="+ DONATE FOOD", width=130, 
                                 fg_color=THEME_COLORS["primary"], hover_color=THEME_COLORS["primary"],
                                 font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                                 command=lambda: self.switch_view("new_donation"))
        btn_add.grid(row=0, column=1, sticky="e")

        # Table scroll view
        self.donations_table = ctk.CTkScrollableFrame(self.content_area)
        self.donations_table.grid(row=1, column=0, sticky="nsew")
        self.donations_table.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        # Table headers
        headers = ["Food Name", "Category", "Quantity", "Expiry Time", "AI Expiry Risk", "Status", "Actions"]
        for col_idx, text in enumerate(headers):
            lbl = ctk.CTkLabel(self.donations_table, text=text.upper(), font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color="gray")
            lbl.grid(row=0, column=col_idx, padx=10, pady=10, sticky="w")

        self.refresh_donations_list()

    def refresh_donations_list(self):
        for widget in self.donations_table.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        my_items = Donation.get_by_donor_id(self.user.user_id)
        row_idx = 1
        for d in my_items:
            # Predict Expiry Risk locally
            risk = predict_expiry_risk(d.category, d.expiry_time)
            
            ctk.CTkLabel(self.donations_table, text=d.food_name, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=0, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.donations_table, text=d.category, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=1, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.donations_table, text=f"{d.quantity} {d.unit}", font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=2, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.donations_table, text=d.expiry_time, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=3, padx=10, pady=6, sticky="w")
            
            # Risk Tag Styling (Pill tag)
            risk_bg_fg = {
                "High": (("#fee2e2", "#ef4444"), ("#7f1d1d", "#fca5a5")),
                "Medium": (("#fef3c7", "#d97706"), ("#78350f", "#fde68a")),
                "Low": (("#d1fae5", "#059669"), ("#064e3b", "#a7f3d0")),
                "Expired": (("#e5e7eb", "#4b5563"), ("#1f2937", "#d1d5db")),
                "Unknown": (("#f3f4f6", "#6b7280"), ("#111827", "#9ca3af"))
            }
            theme = risk_bg_fg.get(risk, (("#f3f4f6", "#6b7280"), ("#111827", "#9ca3af")))
            light_colors, dark_colors = theme[0], theme[1]
            risk_lbl = ctk.CTkLabel(self.donations_table, text=risk, font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                                    fg_color=(light_colors[0], dark_colors[0]), text_color=(light_colors[1], dark_colors[1]),
                                    corner_radius=10, height=20, padx=8)
            risk_lbl.grid(row=row_idx, column=4, padx=10, pady=6, sticky="w")

            # Status Badge color styling (Pill tags)
            status_themes = {
                "Pending": (("#fef3c7", "#d97706"), ("#78350f", "#fde68a")),
                "Approved": (("#d1fae5", "#059669"), ("#064e3b", "#a7f3d0")),
                "Rejected": (("#fee2e2", "#ef4444"), ("#7f1d1d", "#fca5a5")),
                "Requested": (("#dbeafe", "#1e40af"), ("#1e3a8a", "#bfdbfe")),
                "Collected": (("#f3e8ff", "#7e22ce"), ("#581c87", "#e9d5ff")),
                "Expired": (("#f3f4f6", "#4b5563"), ("#111827", "#9ca3af"))
            }
            theme_s = status_themes.get(d.status, (("#f3f4f6", "#4b5563"), ("#111827", "#9ca3af")))
            light_s, dark_s = theme_s[0], theme_s[1]
            
            status_lbl = ctk.CTkLabel(self.donations_table, text=d.status, font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                                      fg_color=(light_s[0], dark_s[0]), text_color=(light_s[1], dark_s[1]),
                                      corner_radius=10, height=20, padx=8)
            status_lbl.grid(row=row_idx, column=5, padx=10, pady=6, sticky="w")

            # Actions Frame (Edit/Delete)
            act_frame = ctk.CTkFrame(self.donations_table, fg_color="transparent")
            act_frame.grid(row=row_idx, column=6, padx=10, pady=6, sticky="w")

            if d.status not in ["Collected", "Expired"]:
                btn_edit = ctk.CTkButton(act_frame, text="Edit", width=45, height=24, fg_color=THEME_COLORS["info"], hover_color=THEME_COLORS["info"],
                                          font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                                          command=lambda item_id=d.donation_id: self.edit_donation(item_id))
                btn_edit.pack(side="left", padx=2)

                btn_del = ctk.CTkButton(act_frame, text="Delete", width=50, height=24, fg_color=THEME_COLORS["primary"], hover_color=THEME_COLORS["primary"],
                                         font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                                         command=lambda item_id=d.donation_id: self.delete_donation(item_id))
                btn_del.pack(side="left", padx=2)
            else:
                ctk.CTkLabel(act_frame, text="Closed", text_color="gray", font=ctk.CTkFont(family=FONT_FAMILY, size=11, slant="italic")).pack()

            row_idx += 1

    # --- View 2: Add / Edit Donation Form ---
    def show_donation_form(self, donation_obj=None):
        self.content_area.grid_rowconfigure(0, weight=0)
        self.content_area.grid_rowconfigure(1, weight=1)

        title_text = "EDIT FOOD DONATION DETAILS" if donation_obj else "REGISTER NEW FOOD DONATION"
        self.editing_donation_id = donation_obj.donation_id if donation_obj else None
        self.selected_image_path = donation_obj.image if donation_obj else None

        # Title (ALL CAPS bold unique font)
        title_lbl = ctk.CTkLabel(self.content_area, text=title_text, font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"))
        title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # Form scroll frame
        form = ctk.CTkScrollableFrame(self.content_area)
        form.grid(row=1, column=0, sticky="nsew")
        form.grid_columnconfigure((0, 1), weight=1)

        # Field 1: Food Name
        ctk.CTkLabel(form, text="Food Item Name:", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).grid(row=0, column=0, padx=20, pady=(15, 2), sticky="w")
        self.entry_name = ctk.CTkEntry(form, placeholder_text="e.g. Mixed Vegetable Rice, Wheat Bread", height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.entry_name.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="ew")

        # Field 2: Category & Unit
        ctk.CTkLabel(form, text="Food Category:", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).grid(row=2, column=0, padx=20, pady=(10, 2), sticky="w")
        self.combo_category = ctk.CTkOptionMenu(form, values=FOOD_CATEGORIES, height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.combo_category.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(form, text="Unit of Measure:", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).grid(row=2, column=1, padx=20, pady=(10, 2), sticky="w")
        self.combo_unit = ctk.CTkOptionMenu(form, values=FOOD_UNITS, height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.combo_unit.grid(row=3, column=1, padx=20, pady=5, sticky="ew")

        # Field 3: Quantity & Type
        ctk.CTkLabel(form, text="Quantity:", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).grid(row=4, column=0, padx=20, pady=(10, 2), sticky="w")
        self.entry_quantity = ctk.CTkEntry(form, placeholder_text="e.g. 15.5, 30", height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.entry_quantity.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(form, text="Food Package/Prep Type:", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).grid(row=4, column=1, padx=20, pady=(10, 2), sticky="w")
        self.seg_type = ctk.CTkSegmentedButton(form, values=["Cooked", "Packaged", "Fresh"], height=35,
                                               selected_color=THEME_COLORS["primary"][1],
                                               font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.seg_type.grid(row=5, column=1, padx=20, pady=5, sticky="ew")
        self.seg_type.set("Cooked")

        # Field 4: Expiry Time
        default_expiry = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
        ctk.CTkLabel(form, text="Expiration Date & Time (YYYY-MM-DD HH:MM):", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).grid(row=6, column=0, padx=20, pady=(10, 2), sticky="w")
        self.entry_expiry = ctk.CTkEntry(form, placeholder_text="YYYY-MM-DD HH:MM", height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.entry_expiry.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        self.entry_expiry.insert(0, default_expiry)

        # Field 5: Pickup Location & Contact
        ctk.CTkLabel(form, text="Pickup Address Location:", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).grid(row=8, column=0, padx=20, pady=(10, 2), sticky="w")
        self.entry_location = ctk.CTkEntry(form, placeholder_text="Pickup address (lat, lon)", height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.entry_location.grid(row=9, column=0, padx=20, pady=5, sticky="ew")
        self.entry_location.insert(0, self.user.address if self.user.address else "")

        ctk.CTkLabel(form, text="Donor Contact Number:", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).grid(row=8, column=1, padx=20, pady=(10, 2), sticky="w")
        self.entry_phone = ctk.CTkEntry(form, placeholder_text="Phone number", height=35, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.entry_phone.grid(row=9, column=1, padx=20, pady=5, sticky="ew")
        self.entry_phone.insert(0, self.user.phone if self.user.phone else "")

        # Field 6: Image Upload frame (Clickable preview frame)
        ctk.CTkLabel(form, text="Food Item Photograph (Optional):", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).grid(row=10, column=0, padx=20, pady=(10, 2), sticky="w")
        
        self.upload_card = ctk.CTkFrame(form, height=150, width=320, border_width=2, border_color=THEME_COLORS["primary"], corner_radius=10)
        self.upload_card.grid(row=11, column=0, columnspan=2, padx=20, pady=8, sticky="w")
        self.upload_card.grid_propagate(False)
        self.upload_card.bind("<Button-1>", lambda e: self.upload_donation_image())
        
        self.render_image_preview()

        # Submit button (styled with colorful primary)
        btn_submit = ctk.CTkButton(form, text="SUBMIT DONATION REQUEST", height=40, 
                                   fg_color=THEME_COLORS["primary"], hover_color=THEME_COLORS["primary"],
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
                                   command=self.submit_donation_form)
        btn_submit.grid(row=13, column=0, columnspan=2, padx=20, pady=30, sticky="ew")

        # Populate fields if editing
        if donation_obj:
            self.entry_name.insert(0, donation_obj.food_name)
            self.combo_category.set(donation_obj.category)
            self.combo_unit.set(donation_obj.unit)
            self.entry_quantity.insert(0, str(donation_obj.quantity))
            self.seg_type.set(donation_obj.cooked_or_packaged)
            self.entry_expiry.delete(0, "end")
            self.entry_expiry.insert(0, donation_obj.expiry_time)
            self.entry_location.delete(0, "end")
            self.entry_location.insert(0, donation_obj.pickup_address)
            self.entry_phone.delete(0, "end")
            self.entry_phone.insert(0, donation_obj.phone if hasattr(donation_obj, "phone") else self.user.phone)
            btn_submit.configure(text="SAVE MODIFICATIONS")
            self.render_image_preview()

    def render_image_preview(self):
        """Displays image preview inside upload frame."""
        for widget in self.upload_card.winfo_children():
            widget.destroy()

        if self.selected_image_path:
            img_path = self.selected_image_path
            if not os.path.isabs(img_path):
                img_path = os.path.join(IMAGES_DIR, img_path)

            if os.path.exists(img_path):
                try:
                    pil_img = Image.open(img_path)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(310, 140))
                    
                    lbl_preview = ctk.CTkLabel(self.upload_card, image=ctk_img, text="")
                    lbl_preview.pack(fill="both", expand=True, padx=4, pady=4)
                    lbl_preview.bind("<Button-1>", lambda e: self.upload_donation_image())
                    
                    hint_lbl = ctk.CTkLabel(lbl_preview, text="Click to replace photo", fg_color=("#1e293b", "#0f172a"), text_color="white", font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"))
                    hint_lbl.place(relx=0.5, rely=0.85, anchor="center")
                    return
                except Exception as e:
                    print(f"Failed to show preview: {e}")
        
        placeholder_lbl = ctk.CTkLabel(self.upload_card, text="📷\nClick here to select a photograph\n(PNG, JPG, WEBP)", 
                                       font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="normal"), justify="center")
        placeholder_lbl.pack(expand=True)
        placeholder_lbl.bind("<Button-1>", lambda e: self.upload_donation_image())

    def upload_donation_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp")]
        )
        if file_path:
            self.selected_image_path = file_path
            self.render_image_preview()

    def submit_donation_form(self):
        name = self.entry_name.get().strip()
        category = self.combo_category.get()
        unit = self.combo_unit.get()
        quantity_str = self.entry_quantity.get().strip()
        prep_type = self.seg_type.get()
        expiry_str = self.entry_expiry.get().strip()
        address = self.entry_location.get().strip()
        phone = self.entry_phone.get().strip()

        # Validations
        if not all([name, quantity_str, expiry_str, address, phone]):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive number.")
            return

        expiry_time = parse_datetime(expiry_str)
        if not expiry_time:
            messagebox.showerror("Error", "Invalid Date/Time format. Use YYYY-MM-DD HH:MM")
            return
            
        if expiry_time <= datetime.now():
            messagebox.showerror("Error", "Expiration time must be in the future.")
            return

        lat, lon = extract_coords_from_text(address)

        final_image_name = None
        if self.selected_image_path and os.path.exists(self.selected_image_path):
            if not self.selected_image_path.startswith(IMAGES_DIR):
                ext = os.path.splitext(self.selected_image_path)[1]
                filename = f"donation_{int(datetime.now().timestamp())}{ext}"
                dest_path = os.path.join(IMAGES_DIR, filename)
                try:
                    shutil.copy(self.selected_image_path, dest_path)
                    final_image_name = filename
                except Exception as e:
                    print(f"Error copying image: {e}")
            else:
                final_image_name = os.path.basename(self.selected_image_path)

        if self.editing_donation_id:
            d = Donation.update(
                donation_id=self.editing_donation_id,
                food_name=name,
                category=category,
                quantity=quantity,
                unit=unit,
                cooked_or_packaged=prep_type,
                expiry_time=expiry_time.strftime("%Y-%m-%d %H:%M:%S"),
                pickup_address=address,
                latitude=lat,
                longitude=lon,
                status="Pending",
                image=final_image_name
            )
            msg = "Donation modifications saved. It has been queued for Admin audit."
        else:
            d = Donation.create(
                donor_id=self.user.user_id,
                food_name=name,
                category=category,
                quantity=quantity,
                unit=unit,
                cooked_or_packaged=prep_type,
                expiry_time=expiry_time.strftime("%Y-%m-%d %H:%M:%S"),
                pickup_address=address,
                latitude=lat,
                longitude=lon,
                status="Pending",
                image=final_image_name
            )
            admins = User.get_all_by_role("Admin")
            for admin in admins:
                Notification.create(
                    user_id=admin.user_id,
                    title="New Donation Pending Audit",
                    message=f"'{d.food_name}' posted by {self.user.full_name} is waiting for audit approval."
                )
            msg = "Donation successfully registered! Waiting for Admin audit approval."

        messagebox.showinfo("Success", msg)
        self.switch_view("my_donations")

    def edit_donation(self, donation_id):
        d = Donation.get_by_id(donation_id)
        if d:
            self.show_donation_form(d)

    def delete_donation(self, donation_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this donation?"):
            Donation.delete(donation_id)
            self.refresh_donations_list()

    # --- View 3: Notifications ---
    def show_notifications_view(self):
        self.content_area.grid_rowconfigure(0, weight=0)
        self.content_area.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(header_frame, text="MY SYSTEM NOTIFICATIONS", font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"))
        title.grid(row=0, column=0, sticky="w")

        btn_mark = ctk.CTkButton(header_frame, text="MARK ALL READ", width=120, fg_color="transparent", text_color=THEME_COLORS["primary"], border_width=1, border_color=THEME_COLORS["primary"], hover_color=("#fee2e2", "#450a0a"),
                                  font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                                  command=self.mark_all_notifications_read)
        btn_mark.grid(row=0, column=1, sticky="e")

        self.notif_scroll = ctk.CTkScrollableFrame(self.content_area)
        self.notif_scroll.grid(row=1, column=0, sticky="nsew")
        self.notif_scroll.grid_columnconfigure(0, weight=1)

        self.refresh_notifications_list()

    def refresh_notifications_list(self):
        for widget in self.notif_scroll.winfo_children():
            widget.destroy()

        notifs = Notification.get_by_user_id(self.user.user_id)
        if not notifs:
            lbl = ctk.CTkLabel(self.notif_scroll, text="You have no notifications.", font=ctk.CTkFont(family=FONT_FAMILY, size=12, slant="italic"), text_color="gray")
            lbl.pack(pady=40)
            return

        for n in notifs:
            card_border = THEME_COLORS["primary"] if n.status == "Unread" else "transparent"
            card = ctk.CTkFrame(self.notif_scroll, corner_radius=8, border_width=1 if n.status == "Unread" else 0, border_color=card_border)
            card.pack(fill="x", padx=10, pady=6)
            card.grid_columnconfigure(0, weight=1)

            title_lbl = ctk.CTkLabel(card, text=n.title.upper(), font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"))
            title_lbl.grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")

            msg_lbl = ctk.CTkLabel(card, text=n.message, font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=("gray20", "gray80"), justify="left", wraplength=700)
            msg_lbl.grid(row=1, column=0, padx=15, pady=(2, 10), sticky="w")

            date_lbl = ctk.CTkLabel(card, text=n.created_at, font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color="gray")
            date_lbl.grid(row=0, column=1, rowspan=2, padx=15, pady=10, sticky="e")

            if n.status == "Unread":
                Notification.mark_as_read(n.notification_id)

    def mark_all_notifications_read(self):
        Notification.mark_all_read(self.user.user_id)
        self.refresh_notifications_list()
