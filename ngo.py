import os
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from config import IMAGES_DIR, FOOD_CATEGORIES
from models import Donation, Request, NGO, User, Notification
from utils import predict_expiry_risk, haversine_distance, extract_coords_from_text

class NGODashboard(ctk.CTkFrame):
    """NGO Dashboard layout with sidebar navigation and sub-panels."""
    def __init__(self, parent, user, on_logout, change_theme_callback):
        super().__init__(parent)
        self.user = user
        self.on_logout = on_logout
        self.change_theme_callback = change_theme_callback
        
        # Fetch linked NGO Profile
        self.ngo_profile = NGO.get_by_user_id(self.user.user_id)
        if not self.ngo_profile:
            # Fallback mock if not registered in NGO table
            self.ngo_profile = NGO(1, self.user.user_id, self.user.full_name, "REG-MOCK", self.user.address, self.user.phone, self.user.email)
            
        # Parse NGO coordinates
        self.ngo_lat, self.ngo_lon = extract_coords_from_text(self.ngo_profile.location)
        if self.ngo_lat is None or self.ngo_lon is None:
            # Fallback coordinates for NGO if address parsing fails
            self.ngo_lat, self.ngo_lon = 12.9715, 77.5946 

        # Grid Layout: Sidebar left, Content right
        self.grid_columnconfigure(0, minsize=200, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.current_theme = ctk.get_appearance_mode().lower()

        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(4, weight=1)  # Spacer

        # Sidebar Title
        sidebar_title = ctk.CTkLabel(self.sidebar, text="NGO Portal", font=ctk.CTkFont(size=18, weight="bold"))
        sidebar_title.grid(row=0, column=0, padx=20, pady=25)

        # Nav Buttons
        self.btn_browse = ctk.CTkButton(self.sidebar, text="Browse Food", anchor="w", fg_color="transparent",
                                         text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         command=lambda: self.switch_view("browse"))
        self.btn_browse.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.btn_claims = ctk.CTkButton(self.sidebar, text="My Collection Claims", anchor="w", fg_color="transparent",
                                         text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         command=lambda: self.switch_view("claims"))
        self.btn_claims.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.btn_notifs = ctk.CTkButton(self.sidebar, text="Notifications", anchor="w", fg_color="transparent",
                                         text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         command=lambda: self.switch_view("notifications"))
        self.btn_notifs.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Dark/Light switch
        self.theme_switch = ctk.CTkSwitch(self.sidebar, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.grid(row=5, column=0, padx=20, pady=10, sticky="w")
        if self.current_theme == "dark":
            self.theme_switch.select()

        btn_logout = ctk.CTkButton(self.sidebar, text="Log Out", fg_color="#ef4444", hover_color="#dc2626",
                                    text_color="white", command=self.on_logout)
        btn_logout.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        # Content Frame
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        # Show browse by default
        self.switch_view("browse")

    def toggle_theme(self):
        new_theme = "dark" if self.theme_switch.get() == 1 else "light"
        self.current_theme = new_theme
        self.change_theme_callback(new_theme)
        if self.current_view == "browse":
            self.show_browse_view()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def switch_view(self, view_name):
        self.current_view = view_name
        self.clear_content()

        # Update button highlight
        buttons = {
            "browse": self.btn_browse,
            "claims": self.btn_claims,
            "notifications": self.btn_notifs
        }
        for name, btn in buttons.items():
            if name == view_name:
                btn.configure(fg_color=("gray80", "gray25"), font=ctk.CTkFont(weight="bold"))
            else:
                btn.configure(fg_color="transparent", font=ctk.CTkFont(weight="normal"))

        if view_name == "browse":
            self.show_browse_view()
        elif view_name == "claims":
            self.show_claims_view()
        elif view_name == "notifications":
            self.show_notifications_view()

    # --- View 1: Browse Available Food ---
    def show_browse_view(self):
        self.content_area.grid_rowconfigure(0, weight=0)
        self.content_area.grid_rowconfigure(1, weight=0)
        self.content_area.grid_rowconfigure(2, weight=1)

        # Header Title
        title_lbl = ctk.CTkLabel(self.content_area, text="Available Surplus Food Catalog", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Search and Filters Panel
        filter_frame = ctk.CTkFrame(self.content_area, height=60)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        filter_frame.grid_columnconfigure(0, weight=2)
        filter_frame.grid_columnconfigure((1, 2), weight=1)

        # Search Entry
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_available_catalog())
        self.search_entry = ctk.CTkEntry(filter_frame, placeholder_text="🔍 Search food by name...", textvariable=self.search_var, height=35)
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Category Filter
        categories = ["All Categories"] + FOOD_CATEGORIES
        self.category_var = tk.StringVar(value="All Categories")
        self.category_filter = ctk.CTkOptionMenu(filter_frame, values=categories, variable=self.category_var, height=35, command=lambda x: self.refresh_available_catalog())
        self.category_filter.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Sort selector
        self.sort_var = tk.StringVar(value="Soonest Expiry First")
        sort_options = ["Soonest Expiry First", "Largest Quantity First", "Closest Distance First"]
        self.sort_select = ctk.CTkOptionMenu(filter_frame, values=sort_options, variable=self.sort_var, height=35, command=lambda x: self.refresh_available_catalog())
        self.sort_select.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # Catalog Cards Frame
        self.catalog_scroll = ctk.CTkScrollableFrame(self.content_area)
        self.catalog_scroll.grid(row=2, column=0, sticky="nsew")
        self.catalog_scroll.grid_columnconfigure((0, 1), weight=1)  # 2 Column layout for cards

        self.refresh_available_catalog()

    def refresh_available_catalog(self):
        for widget in self.catalog_scroll.winfo_children():
            widget.destroy()

        search_query = self.search_var.get().strip().lower()
        selected_category = self.category_var.get()
        sort_method = self.sort_var.get()

        all_available = Donation.get_available()
        filtered = []

        for d in all_available:
            # 1. Filter search
            if search_query and search_query not in d.food_name.lower():
                continue
            # 2. Filter category
            if selected_category != "All Categories" and d.category != selected_category:
                continue
            
            # Calculate distance
            dist = haversine_distance(self.ngo_lat, self.ngo_lon, d.latitude, d.longitude)
            # Add distance attribute dynamically
            d.distance_km = dist if dist != float('inf') else 999.0
            
            # Add Expiry Risk Level
            d.expiry_risk = predict_expiry_risk(d.category, d.expiry_time)
            
            filtered.append(d)

        # 3. Sort postings
        if sort_method == "Soonest Expiry First":
            filtered.sort(key=lambda x: x.expiry_time)
        elif sort_method == "Largest Quantity First":
            filtered.sort(key=lambda x: x.quantity, reverse=True)
        elif sort_method == "Closest Distance First":
            filtered.sort(key=lambda x: x.distance_km)

        if not filtered:
            lbl = ctk.CTkLabel(self.catalog_scroll, text="No food postings found matching criteria.", font=ctk.CTkFont(slant="italic"), text_color="gray")
            lbl.grid(row=0, column=0, columnspan=2, pady=50)
            return

        row_idx = 0
        col_idx = 0
        for item in filtered:
            self.create_food_card(self.catalog_scroll, row_idx, col_idx, item)
            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1

    def create_food_card(self, parent, row, col, item):
        card = ctk.CTkFrame(parent, border_width=1, border_color=("gray80", "gray70"), corner_radius=10)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        # Header Title
        title_lbl = ctk.CTkLabel(card, text=item.food_name, font=ctk.CTkFont(size=15, weight="bold"), anchor="w")
        title_lbl.pack(fill="x", padx=15, pady=(15, 2))

        # Subtitle details
        sub_lbl = ctk.CTkLabel(card, text=f"{item.category} • {item.quantity} {item.unit}", 
                               font=ctk.CTkFont(size=12), text_color="gray", anchor="w")
        sub_lbl.pack(fill="x", padx=15, pady=(0, 10))

        # Visual indicator or image
        img_frame = ctk.CTkFrame(card, height=120, fg_color=("gray90", "gray25"), corner_radius=6)
        img_frame.pack(fill="x", padx=15, pady=5)
        img_frame.pack_propagate(False)

        # Image render logic
        has_image = False
        if item.image:
            img_path = os.path.join(IMAGES_DIR, item.image)
            if os.path.exists(img_path):
                try:
                    pil_img = Image.open(img_path)
                    # Resize while keeping aspect ratio or fit frame
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(240, 110))
                    img_lbl = ctk.CTkLabel(img_frame, image=ctk_img, text="")
                    img_lbl.pack(fill="both", expand=True)
                    has_image = True
                except Exception as e:
                    print(f"Failed to load image: {e}")
        
        if not has_image:
            # Fallback text placeholder
            placeholder = ctk.CTkLabel(img_frame, text="🍲 Fresh surplus donation", font=ctk.CTkFont(slant="italic", size=12), text_color="gray")
            placeholder.pack(expand=True)

        # Metadata Details: Proximity & Expiry Risk
        meta_frame = ctk.CTkFrame(card, fg_color="transparent")
        meta_frame.pack(fill="x", padx=15, pady=(10, 5))

        dist_txt = f"📍 {item.distance_km} km away" if item.distance_km < 990 else "📍 Location unlisted"
        dist_lbl = ctk.CTkLabel(meta_frame, text=dist_txt, font=ctk.CTkFont(size=12))
        dist_lbl.pack(side="left")

        # Expiry risk level badge
        risk = item.expiry_risk
        risk_colors = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981", "Expired": "#6b7280"}
        r_color = risk_colors.get(risk, "gray")
        
        risk_lbl = ctk.CTkLabel(meta_frame, text=f"AI Expiry: {risk}", text_color=r_color, font=ctk.CTkFont(size=11, weight="bold"))
        risk_lbl.pack(side="right")

        # Address tooltip/label
        addr_lbl = ctk.CTkLabel(card, text=f"Pickup: {item.pickup_address}", font=ctk.CTkFont(size=11), text_color="gray", justify="left", anchor="w", wraplength=300)
        addr_lbl.pack(fill="x", padx=15, pady=2)

        # Claim Button
        btn_claim = ctk.CTkButton(card, text="Claim Collection", height=32, font=ctk.CTkFont(weight="bold"),
                                   command=lambda item_id=item.donation_id: self.claim_food_item(item_id))
        btn_claim.pack(fill="x", padx=15, pady=(10, 15))

    def claim_food_item(self, donation_id):
        d = Donation.get_by_id(donation_id)
        if not d:
            return

        if messagebox.askyesno("Confirm Claim", f"Confirm you want to request collection for:\n{d.food_name} ({d.quantity} {d.unit})?\nThis reserves the item."):
            req = Request.create(donation_id=donation_id, ngo_id=self.ngo_profile.ngo_id)
            if req:
                # Notify Donor
                Notification.create(
                    user_id=d.donor_id,
                    title="Collection Claim Filed",
                    message=f"NGO '{self.ngo_profile.organization_name}' has requested to collect '{d.food_name}'. Check claim dashboard to coordinate."
                )
                messagebox.showinfo("Success", "Collection request submitted! Coordination details are now in your 'Collection Claims' dashboard.")
                self.refresh_available_catalog()

    # --- View 2: My Claims ---
    def show_claims_view(self):
        self.content_area.grid_rowconfigure(0, weight=0)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Title
        title_lbl = ctk.CTkLabel(self.content_area, text="My Collection Claims Directory", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # Scrollable table container
        self.claims_table = ctk.CTkScrollableFrame(self.content_area)
        self.claims_table.grid(row=1, column=0, sticky="nsew")
        self.claims_table.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Table headers
        headers = ["Food Item", "Donor", "Contact Phone", "Pickup Location", "Claim Status", "Actions"]
        for col_idx, text in enumerate(headers):
            lbl = ctk.CTkLabel(self.claims_table, text=text, font=ctk.CTkFont(size=12, weight="bold"))
            lbl.grid(row=0, column=col_idx, padx=10, pady=10, sticky="w")

        self.refresh_claims_list()

    def refresh_claims_list(self):
        for widget in self.claims_table.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        my_reqs = Request.get_by_ngo_id(self.ngo_profile.ngo_id)
        row_idx = 1
        for r in my_reqs:
            d = Donation.get_by_id(r.donation_id)
            if not d:
                continue

            donor = User.get_by_id(d.donor_id)
            donor_name = donor.full_name if donor else "Unknown"
            donor_phone = donor.phone if donor else "Unknown"

            # Fields
            ctk.CTkLabel(self.claims_table, text=d.food_name).grid(row=row_idx, column=0, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.claims_table, text=donor_name).grid(row=row_idx, column=1, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.claims_table, text=donor_phone).grid(row=row_idx, column=2, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.claims_table, text=d.pickup_address, wraplength=200, justify="left").grid(row=row_idx, column=3, padx=10, pady=6, sticky="w")
            
            # Request status
            req_status_colors = {
                "Pending": "#f59e0b",
                "Approved": "#10b981", # Ready for collection
                "Rejected": "#ef4444",
                "Completed": "#8b5cf6"
            }
            s_color = req_status_colors.get(r.status, "gray")
            
            # Show customized label if request is approved (meaning claim is approved, collection is pending)
            display_status = "Ready for Collection" if r.status == "Approved" else r.status
            status_lbl = ctk.CTkLabel(self.claims_table, text=display_status, text_color=s_color, font=ctk.CTkFont(weight="bold"))
            status_lbl.grid(row=row_idx, column=4, padx=10, pady=6, sticky="w")

            # Actions cell
            actions_frame = ctk.CTkFrame(self.claims_table, fg_color="transparent")
            actions_frame.grid(row=row_idx, column=5, padx=10, pady=6, sticky="w")

            if r.status == "Approved":
                # Approved claim means NGO can mark collection complete after picking it up
                btn_complete = ctk.CTkButton(actions_frame, text="Picked Up ✔", width=80, height=24, fg_color="#10b981", hover_color="#059669",
                                              command=lambda req_id=r.request_id: self.mark_collection_completed(req_id))
                btn_complete.pack(side="left")
            elif r.status == "Pending":
                ctk.CTkLabel(actions_frame, text="Awaiting Donor approval", font=ctk.CTkFont(size=11, slant="italic"), text_color="gray").pack()
            else:
                ctk.CTkLabel(actions_frame, text="Closed", font=ctk.CTkFont(size=11, slant="italic"), text_color="gray").pack()

            row_idx += 1

    def mark_collection_completed(self, request_id):
        r = Request.get_by_id(request_id)
        if not r:
            return
        d = Donation.get_by_id(r.donation_id)
        if not d:
            return

        if messagebox.askyesno("Confirm Pickup", "Confirm that you have picked up this food package from the donor?"):
            pickup_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Request.update_status(request_id, "Completed", pickup_time=pickup_now)
            
            # Notify Donor
            Notification.create(
                user_id=d.donor_id,
                title="Food Collection Completed",
                message=f"Thank you! NGO '{self.ngo_profile.organization_name}' has confirmed successful collection of '{d.food_name}'."
            )
            messagebox.showinfo("Success", "Collection finalized! The donation is marked as successfully rescued.")
            self.refresh_claims_list()

    # --- View 3: Notifications ---
    def show_notifications_view(self):
        self.content_area.grid_rowconfigure(0, weight=0)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Title / Buttons
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(header_frame, text="My Platform Notifications", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, sticky="w")

        btn_mark = ctk.CTkButton(header_frame, text="Mark All Read", width=120, fg_color="transparent", text_color=("gray10", "gray90"), border_width=1, border_color=("gray50", "gray50"), hover_color=("gray80", "gray30"),
                                  command=self.mark_all_notifications_read)
        btn_mark.grid(row=0, column=1, sticky="e")

        # Scrollable Notifications list
        self.notif_scroll = ctk.CTkScrollableFrame(self.content_area)
        self.notif_scroll.grid(row=1, column=0, sticky="nsew")
        self.notif_scroll.grid_columnconfigure(0, weight=1)

        self.refresh_notifications_list()

    def refresh_notifications_list(self):
        for widget in self.notif_scroll.winfo_children():
            widget.destroy()

        notifs = Notification.get_by_user_id(self.user.user_id)
        if not notifs:
            lbl = ctk.CTkLabel(self.notif_scroll, text="You have no notifications.", font=ctk.CTkFont(slant="italic"), text_color="gray")
            lbl.pack(pady=40)
            return

        for n in notifs:
            card_border = "#4f46e5" if n.status == "Unread" else "transparent"
            card = ctk.CTkFrame(self.notif_scroll, corner_radius=8, border_width=1 if n.status == "Unread" else 0, border_color=card_border)
            card.pack(fill="x", padx=10, pady=6)
            card.grid_columnconfigure(0, weight=1)

            title_lbl = ctk.CTkLabel(card, text=n.title, font=ctk.CTkFont(size=13, weight="bold"))
            title_lbl.grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")

            msg_lbl = ctk.CTkLabel(card, text=n.message, font=ctk.CTkFont(size=12), text_color=("gray20", "gray80"), justify="left", wraplength=700)
            msg_lbl.grid(row=1, column=0, padx=15, pady=(2, 10), sticky="w")

            date_lbl = ctk.CTkLabel(card, text=n.created_at, font=ctk.CTkFont(size=10), text_color="gray")
            date_lbl.grid(row=0, column=1, rowspan=2, padx=15, pady=10, sticky="e")

            if n.status == "Unread":
                Notification.mark_as_read(n.notification_id)

    def mark_all_notifications_read(self):
        Notification.mark_all_read(self.user.user_id)
        self.refresh_notifications_list()
