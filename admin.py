import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from database import get_connection
from models import User, Donation, Request, Notification
from utils import get_food_waste_insights
from analytics import create_category_pie_chart, create_monthly_bar_chart
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import FONT_FAMILY, THEME_COLORS

class AdminDashboard(ctk.CTkFrame):
    """Admin Dashboard layout with sidebar navigation, custom typography, and vibrant cards."""
    def __init__(self, parent, user, on_logout, change_theme_callback):
        super().__init__(parent)
        self.user = user
        self.on_logout = on_logout
        self.change_theme_callback = change_theme_callback
        
        # Grid layout: left sidebar, right main content area
        self.grid_columnconfigure(0, minsize=210, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.current_theme = ctk.get_appearance_mode().lower()

        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color=("#f1f5f9", "#111827"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(6, weight=1)  # Spacer row

        # Sidebar Title (ALL CAPS bold unique font)
        sidebar_title = ctk.CTkLabel(self.sidebar, text="ADMIN CONSOLE", 
                                     font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
                                     text_color=THEME_COLORS["primary"])
        sidebar_title.grid(row=0, column=0, padx=20, pady=25)

        # Navigation Buttons (uses custom fonts)
        self.btn_overview = ctk.CTkButton(self.sidebar, text="Overview", anchor="w", fg_color="transparent",
                                           text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                           font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                                           command=lambda: self.switch_view("overview"))
        self.btn_overview.grid(row=1, column=0, padx=12, pady=5, sticky="ew")

        self.btn_donations = ctk.CTkButton(self.sidebar, text="Donation Audit", anchor="w", fg_color="transparent",
                                            text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                                            command=lambda: self.switch_view("donations"))
        self.btn_donations.grid(row=2, column=0, padx=12, pady=5, sticky="ew")

        self.btn_users = ctk.CTkButton(self.sidebar, text="User Manager", anchor="w", fg_color="transparent",
                                        text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                        font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                                        command=lambda: self.switch_view("users"))
        self.btn_users.grid(row=3, column=0, padx=12, pady=5, sticky="ew")

        self.btn_analytics = ctk.CTkButton(self.sidebar, text="Visual Analytics", anchor="w", fg_color="transparent",
                                            text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                                            command=lambda: self.switch_view("analytics"))
        self.btn_analytics.grid(row=4, column=0, padx=12, pady=5, sticky="ew")

        self.btn_reports = ctk.CTkButton(self.sidebar, text="Generate Reports", anchor="w", fg_color="transparent",
                                          text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                          font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                                          command=lambda: self.switch_view("reports"))
        self.btn_reports.grid(row=5, column=0, padx=12, pady=5, sticky="ew")

        # Dark/Light Mode switch
        self.theme_switch = ctk.CTkSwitch(self.sidebar, text="Dark Mode", command=self.toggle_theme,
                                           progress_color=THEME_COLORS["primary"],
                                           font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.theme_switch.grid(row=7, column=0, padx=20, pady=10, sticky="w")
        if self.current_theme == "dark":
            self.theme_switch.select()

        btn_logout = ctk.CTkButton(self.sidebar, text="LOG OUT", fg_color=THEME_COLORS["primary"], hover_color=THEME_COLORS["primary"],
                                    text_color="white", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                                    command=self.on_logout)
        btn_logout.grid(row=8, column=0, padx=20, pady=20, sticky="ew")

        # Content Frame
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        # Show overview by default
        self.switch_view("overview")

    def toggle_theme(self):
        """Toggle app theme via callback to parent window."""
        new_theme = "dark" if self.theme_switch.get() == 1 else "light"
        self.current_theme = new_theme
        self.change_theme_callback(new_theme)
        
        # Redraw current frame to match theme colors if on analytics
        if self.current_view_name == "analytics":
            self.show_analytics_view()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def switch_view(self, view_name):
        self.current_view_name = view_name
        self.clear_content()

        # Update sidebar button highlight colors (Vibrant Purple Active Color)
        buttons = {
            "overview": self.btn_overview,
            "donations": self.btn_donations,
            "users": self.btn_users,
            "analytics": self.btn_analytics,
            "reports": self.btn_reports
        }
        for name, btn in buttons.items():
            if name == view_name:
                btn.configure(fg_color=THEME_COLORS["accent"], text_color="white", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"))
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"), font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="normal"))

        # Render corresponding view
        if view_name == "overview":
            self.show_overview_view()
        elif view_name == "donations":
            self.show_donations_view()
        elif view_name == "users":
            self.show_users_view()
        elif view_name == "analytics":
            self.show_analytics_view()
        elif view_name == "reports":
            self.show_reports_view()

    # --- View 1: Overview ---
    def show_overview_view(self):
        self.content_area.grid_rowconfigure(0, weight=0)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Title (ALL CAPS bold unique font)
        header = ctk.CTkLabel(self.content_area, text=f"WELCOME BACK, {self.user.full_name.upper()}", 
                               font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"))
        header.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Query metrics
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE role = 'Donor'")
        total_donors = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE role = 'NGO'")
        total_ngos = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM donations WHERE status = 'Approved'")
        active_donations = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM requests WHERE status = 'Completed'")
        rescued_food = c.fetchone()[0]
        conn.close()

        # Stats Cards container
        cards_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="new", pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Create cards with distinct unique background and border colors
        self.create_stat_card(cards_frame, 0, "Total Donors", str(total_donors), "card_donors")
        self.create_stat_card(cards_frame, 1, "Total NGOs", str(total_ngos), "card_ngos")
        self.create_stat_card(cards_frame, 2, "Active Items", str(active_donations), "card_active")
        self.create_stat_card(cards_frame, 3, "Rescued Food Items", str(rescued_food), "card_rescued")

        # AI Insights Panel
        insights_card = ctk.CTkFrame(self.content_area, corner_radius=12, border_width=1, border_color=THEME_COLORS["primary"])
        insights_card.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        insights_card.grid_columnconfigure(0, weight=1)
        
        insights_title = ctk.CTkLabel(insights_card, text="🧠 AI WASTE INSIGHTS ENGINE", 
                                      font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
                                      text_color=THEME_COLORS["primary"])
        insights_title.pack(anchor="w", padx=20, pady=(15, 5))

        insights = get_food_waste_insights()
        for idx, insight in enumerate(insights):
            lbl = ctk.CTkLabel(insights_card, text=insight, font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                               wraplength=700, justify="left", anchor="w")
            lbl.pack(anchor="w", padx=30, pady=6)

    def create_stat_card(self, parent, col, title, value, theme_key):
        """Helper to create a colorful themed metric card."""
        card_theme = THEME_COLORS[theme_key]  # (light_bg, dark_bg, border_color)
        bg = (card_theme[0], card_theme[1])
        border_color = card_theme[2]

        card = ctk.CTkFrame(parent, height=110, corner_radius=12, border_width=2, border_color=border_color, fg_color=bg)
        card.grid(row=0, column=col, padx=8, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_propagate(False)

        val_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(family=FONT_FAMILY, size=28, weight="bold"),
                               text_color=("#0f172a", "#ffffff"))
        val_lbl.grid(row=0, column=0, padx=15, pady=(15, 0), sticky="w")

        title_lbl = ctk.CTkLabel(card, text=title.upper(), font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
                                 text_color=("#475569", "#cbd5e1"))
        title_lbl.grid(row=1, column=0, padx=15, pady=(2, 10), sticky="w")

    # --- View 2: Donation Audit ---
    def show_donations_view(self):
        self.content_area.grid_rowconfigure(0, weight=0)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Title (ALL CAPS bold unique font)
        title_lbl = ctk.CTkLabel(self.content_area, text="PENDING DONATIONS AUDIT", 
                                 font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"))
        title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # Table container
        self.donations_table = ctk.CTkScrollableFrame(self.content_area)
        self.donations_table.grid(row=1, column=0, sticky="nsew")
        self.donations_table.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        # Table headers
        headers = ["Food Item", "Category", "Quantity", "Expiry Date", "Donor", "Status", "Actions"]
        for col_idx, text in enumerate(headers):
            lbl = ctk.CTkLabel(self.donations_table, text=text.upper(), font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color="gray")
            lbl.grid(row=0, column=col_idx, padx=10, pady=10, sticky="w")

        self.refresh_donations_list()

    def refresh_donations_list(self):
        # Clear existing rows (keep headers)
        for widget in self.donations_table.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        donations = Donation.get_all()
        row_idx = 1
        for d in donations:
            donor = User.get_by_id(d.donor_id)
            donor_name = donor.full_name if donor else "Unknown"

            # Create row fields
            ctk.CTkLabel(self.donations_table, text=d.food_name, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=0, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.donations_table, text=d.category, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=1, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.donations_table, text=f"{d.quantity} {d.unit}", font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=2, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.donations_table, text=d.expiry_time, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=3, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.donations_table, text=donor_name, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=4, padx=10, pady=6, sticky="w")
            
            # Status Badge color styling (Pill tags)
            status_themes = {
                "Pending": (("#fef3c7", "#d97706"), ("#78350f", "#fde68a")),
                "Approved": (("#d1fae5", "#059669"), ("#064e3b", "#a7f3d0")),
                "Rejected": (("#fee2e2", "#ef4444"), ("#7f1d1d", "#fca5a5")),
                "Requested": (("#dbeafe", "#1e40af"), ("#1e3a8a", "#bfdbfe")),
                "Collected": (("#f3e8ff", "#7e22ce"), ("#581c87", "#e9d5ff")),
                "Expired": (("#f3f4f6", "#4b5563"), ("#111827", "#9ca3af"))
            }
            theme = status_themes.get(d.status, (("#f3f4f6", "#4b5563"), ("#111827", "#9ca3af")))
            light_colors, dark_colors = theme[0], theme[1]
            
            badge_lbl = ctk.CTkLabel(self.donations_table, text=d.status, font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                                     fg_color=(light_colors[0], dark_colors[0]), text_color=(light_colors[1], dark_colors[1]),
                                     corner_radius=10, height=20, padx=8)
            badge_lbl.grid(row=row_idx, column=5, padx=10, pady=6, sticky="w")

            # Actions cell
            actions_frame = ctk.CTkFrame(self.donations_table, fg_color="transparent")
            actions_frame.grid(row=row_idx, column=6, padx=10, pady=6, sticky="w")

            if d.status == "Pending":
                btn_approve = ctk.CTkButton(actions_frame, text="Approve", width=55, height=24, fg_color=THEME_COLORS["secondary"], hover_color=THEME_COLORS["secondary"],
                                             font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                                             command=lambda item_id=d.donation_id: self.audit_donation(item_id, "Approved"))
                btn_approve.pack(side="left", padx=2)

                btn_reject = ctk.CTkButton(actions_frame, text="Reject", width=50, height=24, fg_color=THEME_COLORS["primary"], hover_color=THEME_COLORS["primary"],
                                            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                                            command=lambda item_id=d.donation_id: self.audit_donation(item_id, "Rejected"))
                btn_reject.pack(side="left", padx=2)
            else:
                btn_del = ctk.CTkButton(actions_frame, text="Delete", width=50, height=24, fg_color="transparent", text_color="#ef4444", border_width=1, border_color="#ef4444", hover_color=("#fee2e2", "#450a0a"),
                                         font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                                         command=lambda item_id=d.donation_id: self.delete_donation_record(item_id))
                btn_del.pack(side="left", padx=2)

            row_idx += 1

    def audit_donation(self, donation_id, decision):
        d = Donation.update(donation_id, status=decision)
        if d:
            Notification.create(
                user_id=d.donor_id,
                title=f"Donation Posting {decision}",
                message=f"Your posting for '{d.food_name}' has been {decision.lower()} by the system admin."
            )
            if decision == "Approved":
                ngos = User.get_all_by_role("NGO")
                for ngo in ngos:
                    Notification.create(
                        user_id=ngo.user_id,
                        title="New Surplus Food Available",
                        message=f"'{d.food_name}' ({d.quantity} {d.unit}) is available for pickup. Hurry and claim it!"
                    )
            
            messagebox.showinfo("Success", f"Donation successfully {decision.lower()}.")
            self.refresh_donations_list()

    def delete_donation_record(self, donation_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this donation record?"):
            Donation.delete(donation_id)
            self.refresh_donations_list()

    # --- View 3: User Manager ---
    def show_users_view(self):
        self.content_area.grid_rowconfigure(0, weight=0)
        self.content_area.grid_rowconfigure(1, weight=0)
        self.content_area.grid_rowconfigure(2, weight=1)

        # Title (ALL CAPS bold unique font)
        title_lbl = ctk.CTkLabel(self.content_area, text="PLATFORM USER DIRECTORY", 
                                 font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"))
        title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Search Bar
        search_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        search_frame.grid_columnconfigure(0, weight=1)

        self.user_search_var = tk.StringVar()
        self.user_search_var.trace_add("write", lambda *args: self.refresh_users_list())
        
        search_input = ctk.CTkEntry(search_frame, placeholder_text="Search users by name, email, or role...", 
                                     font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                                     textvariable=self.user_search_var, height=35)
        search_input.grid(row=0, column=0, sticky="ew")

        # Scrollable Users Table
        self.users_table = ctk.CTkScrollableFrame(self.content_area)
        self.users_table.grid(row=2, column=0, sticky="nsew")
        self.users_table.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Headers
        headers = ["Full Name", "Email Address", "Contact", "Account Role", "Actions"]
        for col_idx, text in enumerate(headers):
            lbl = ctk.CTkLabel(self.users_table, text=text.upper(), font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color="gray")
            lbl.grid(row=0, column=col_idx, padx=10, pady=10, sticky="w")

        self.refresh_users_list()

    def refresh_users_list(self):
        # Clear existing
        for widget in self.users_table.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        search_query = self.user_search_var.get().strip().lower()

        # Connect and search
        conn = get_connection()
        cursor = conn.cursor()
        if search_query:
            cursor.execute("""
            SELECT * FROM users 
            WHERE (lower(full_name) LIKE ? OR lower(email) LIKE ? OR lower(role) LIKE ?)
            AND user_id != ?
            ORDER BY role ASC, full_name ASC
            """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", self.user.user_id))
        else:
            cursor.execute("SELECT * FROM users WHERE user_id != ? ORDER BY role ASC, full_name ASC", (self.user.user_id,))
        
        rows = cursor.fetchall()
        conn.close()

        row_idx = 1
        for row in rows:
            u = User.from_row(row)
            
            ctk.CTkLabel(self.users_table, text=u.full_name, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=0, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.users_table, text=u.email, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=1, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(self.users_table, text=u.phone, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).grid(row=row_idx, column=2, padx=10, pady=6, sticky="w")
            
            role_colors = {"Admin": THEME_COLORS["accent"], "Donor": THEME_COLORS["secondary"], "NGO": THEME_COLORS["warning"]}
            r_color = role_colors.get(u.role, "gray")
            badge = ctk.CTkLabel(self.users_table, text=u.role, text_color=r_color, font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"))
            badge.grid(row=row_idx, column=3, padx=10, pady=6, sticky="w")

            btn_del = ctk.CTkButton(self.users_table, text="Delete", width=60, height=24, fg_color="#ef4444", hover_color="#dc2626",
                                     font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                                     command=lambda u_id=u.user_id: self.delete_user(u_id))
            btn_del.grid(row=row_idx, column=4, padx=10, pady=6, sticky="w")

            row_idx += 1

    def delete_user(self, user_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this user? All their postings and details will be deleted permanently."):
            User.delete(user_id)
            self.refresh_users_list()

    # --- View 4: Visual Analytics (Dynamic & Colorful) ---
    def show_analytics_view(self):
        self.content_area.grid_rowconfigure(0, weight=0)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Title (ALL CAPS bold unique font)
        title_lbl = ctk.CTkLabel(self.content_area, text="PLATFORM VISUAL ANALYTICS DASHBOARD", 
                                 font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
                                 text_color=THEME_COLORS["primary"])
        title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # Chart frames container (Horizontal Layout)
        charts_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        charts_frame.grid(row=1, column=0, sticky="nsew")
        charts_frame.grid_columnconfigure((0, 1), weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)

        # Container for Pie Chart
        pie_container = ctk.CTkFrame(charts_frame, border_width=1, border_color=THEME_COLORS["primary"])
        pie_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        fig_pie = create_category_pie_chart(theme=self.current_theme)
        canvas_pie = FigureCanvasTkAgg(fig_pie, master=pie_container)
        canvas_pie.draw()
        canvas_pie.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Container for Bar Chart
        bar_container = ctk.CTkFrame(charts_frame, border_width=1, border_color=THEME_COLORS["accent"])
        bar_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        fig_bar = create_monthly_bar_chart(theme=self.current_theme)
        canvas_bar = FigureCanvasTkAgg(fig_bar, master=bar_container)
        canvas_bar.draw()
        canvas_bar.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # --- View 5: Report Generator ---
    def show_reports_view(self):
        self.content_area.grid_rowconfigure(0, weight=0)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Title (ALL CAPS bold unique font)
        title_lbl = ctk.CTkLabel(self.content_area, text="REPORT GENERATION PANEL", 
                                 font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"))
        title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Configuration frame
        config_box = ctk.CTkFrame(self.content_area, width=500, height=350, border_width=1, border_color=THEME_COLORS["primary"])
        config_box.grid(row=1, column=0, sticky="n", pady=20)
        config_box.grid_columnconfigure(0, weight=1)
        config_box.grid_propagate(False)

        info_lbl = ctk.CTkLabel(config_box, text="COMPILE PLATFORM ACTIVITY REPORT", 
                                font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
                                text_color=THEME_COLORS["primary"])
        info_lbl.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="w")

        desc_lbl = ctk.CTkLabel(config_box, text="This tool generates a comprehensive summary file (.csv)\ncontaining database listings for Users, Donations, and NGO request audits.",
                                font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color="gray", justify="left")
        desc_lbl.grid(row=1, column=0, padx=30, pady=10, sticky="w")

        # Select scope
        scope_lbl = ctk.CTkLabel(config_box, text="Report Format Options:", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"))
        scope_lbl.grid(row=2, column=0, padx=30, pady=(15, 2), sticky="w")

        self.report_option = ctk.CTkSegmentedButton(config_box, values=["CSV Format", "Plain Text Summary"],
                                                     selected_color=THEME_COLORS["primary"][1],
                                                     font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.report_option.grid(row=3, column=0, padx=30, pady=5, sticky="ew")
        self.report_option.set("CSV Format")

        btn_export = ctk.CTkButton(config_box, text="GENERATE AND EXPORT REPORT", height=40, 
                                   fg_color=THEME_COLORS["primary"], hover_color=THEME_COLORS["primary"],
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                                   command=self.compile_and_save_report)
        btn_export.grid(row=4, column=0, padx=30, pady=35, sticky="ew")

    def compile_and_save_report(self):
        file_type = "csv" if self.report_option.get() == "CSV Format" else "txt"
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{file_type}",
            filetypes=[("CSV Files", "*.csv")] if file_type == "csv" else [("Text Files", "*.txt")],
            title="Save Activity Report As"
        )
        if not file_path:
            return

        try:
            conn = get_connection()
            
            # Fetch summary stats
            users_df = pd.read_sql_query("SELECT user_id, full_name, email, role, created_at FROM users", conn)
            donations_df = pd.read_sql_query("SELECT donation_id, food_name, category, quantity, unit, status, created_at FROM donations", conn)
            requests_df = pd.read_sql_query("SELECT request_id, donation_id, ngo_id, status, request_date FROM requests", conn)
            conn.close()

            if file_type == "csv":
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=== FOODSHARE PLATFORM METRICS SUMMARY ===\n")
                    f.write(f"Report Generated On: {pd.Timestamp.now()}\n\n")
                    
                    f.write("--- PLATFORM USERS LIST ---\n")
                    users_df.to_csv(f, index=False)
                    
                    f.write("\n--- SURPLUS FOOD DONATIONS LIST ---\n")
                    donations_df.to_csv(f, index=False)
                    
                    f.write("\n--- NGO COLLECTION REQUESTS LIST ---\n")
                    requests_df.to_csv(f, index=False)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("==================================================\n")
                    f.write("        FOODSHARE REDISTRIBUTION PLANNER\n")
                    f.write("             ADMIN SUMMARY REPORT\n")
                    f.write("==================================================\n")
                    f.write(f"Generated on: {pd.Timestamp.now()}\n\n")
                    
                    f.write("1. SYSTEM METRICS OVERVIEW\n")
                    f.write("--------------------------\n")
                    f.write(f"Total Users Registered: {len(users_df)}\n")
                    f.write(f"  - Donors: {len(users_df[users_df['role']=='Donor'])}\n")
                    f.write(f"  - NGOs: {len(users_df[users_df['role']=='NGO'])}\n")
                    f.write(f"  - Admins: {len(users_df[users_df['role']=='Admin'])}\n\n")
                    
                    f.write(f"Total Donations Registered: {len(donations_df)}\n")
                    f.write(f"  - Approved: {len(donations_df[donations_df['status']=='Approved'])}\n")
                    f.write(f"  - Collected/Completed: {len(donations_df[donations_df['status']=='Collected'])}\n")
                    f.write(f"  - Expired: {len(donations_df[donations_df['status']=='Expired'])}\n\n")
                    
                    f.write(f"Total NGO Requests Filed: {len(requests_df)}\n")
                    f.write(f"  - Pending Audit: {len(requests_df[requests_df['status']=='Pending'])}\n")
                    f.write(f"  - Approved: {len(requests_df[requests_df['status']=='Approved'])}\n")
                    f.write(f"  - Completed: {len(requests_df[requests_df['status']=='Completed'])}\n\n")
                    
                    f.write("2. AI WASTE ENGINE INSIGHTS\n")
                    f.write("----------------------------\n")
                    for insight in get_food_waste_insights():
                        f.write(f"- {insight}\n")
                    f.write("\n")
                    f.write("==================================================\n")
                    f.write("                 REPORT END\n")
                    f.write("==================================================\n")

            messagebox.showinfo("Success", f"Activity report exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report:\n{str(e)}")
