import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from database import get_connection

# Colors matching the application design system
THEME_COLORS = {
    "dark": {
        "bg": "#1e293b",       # Slate 800
        "fg": "#f8fafc",       # Slate 50
        "accent": "#10b981",   # Emerald Green
        "accent_2": "#6366f1", # Indigo
        "grid": "#475569",     # Slate 600
        "palette": ["#10b981", "#6366f1", "#f59e0b", "#ec4899", "#3b82f6", "#8b5cf6"]
    },
    "light": {
        "bg": "#ffffff",       # White
        "fg": "#0f172a",       # Slate 900
        "accent": "#059669",   # Green Accent
        "accent_2": "#4f46e5", # Indigo Accent
        "grid": "#cbd5e1",     # Slate 300
        "palette": ["#059669", "#4f46e5", "#d97706", "#db2777", "#2563eb", "#7c3aed"]
    }
}

def get_category_data():
    """Queries categories and counts from the database."""
    conn = get_connection()
    query = """
    SELECT category, COUNT(*) as donation_count 
    FROM donations 
    GROUP BY category
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_monthly_data():
    """Queries monthly donation volumes from the database."""
    conn = get_connection()
    # Format: YYYY-MM
    query = """
    SELECT substr(created_at, 1, 7) as month, COUNT(*) as donation_count 
    FROM donations 
    GROUP BY month 
    ORDER BY month ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def create_category_pie_chart(theme="dark"):
    """
    Generates a Matplotlib Pie Chart representing food category distribution.
    Returns a Figure object.
    """
    df = get_category_data()
    
    # Initialize a figure
    fig = Figure(figsize=(4, 3.5), dpi=100)
    fig.patch.set_facecolor(THEME_COLORS[theme]["bg"])
    
    ax = fig.add_subplot(111)
    ax.set_facecolor(THEME_COLORS[theme]["bg"])

    if df.empty:
        ax.text(0.5, 0.5, "No data available", 
                horizontalalignment='center', verticalalignment='center',
                color=THEME_COLORS[theme]["fg"], fontsize=12)
        ax.axis('off')
        return fig

    # Plot pie
    wedges, texts, autotexts = ax.pie(
        df["donation_count"], 
        labels=df["category"], 
        autopct='%1.1f%%',
        startangle=140, 
        colors=THEME_COLORS[theme]["palette"][:len(df)],
        textprops=dict(color=THEME_COLORS[theme]["fg"]),
        wedgeprops=dict(edgecolor=THEME_COLORS[theme]["bg"], linewidth=1.5)
    )

    # Styling labels/autotexts
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')

    ax.set_title("Donations by Food Category", color=THEME_COLORS[theme]["fg"], fontsize=12, pad=10)
    
    return fig

def create_monthly_bar_chart(theme="dark"):
    """
    Generates a Matplotlib Bar Chart representing monthly donation trends.
    Returns a Figure object.
    """
    df = get_monthly_data()
    
    # Initialize figure
    fig = Figure(figsize=(4.5, 3.5), dpi=100)
    fig.patch.set_facecolor(THEME_COLORS[theme]["bg"])
    
    ax = fig.add_subplot(111)
    ax.set_facecolor(THEME_COLORS[theme]["bg"])

    if df.empty:
        ax.text(0.5, 0.5, "No data available", 
                horizontalalignment='center', verticalalignment='center',
                color=THEME_COLORS[theme]["fg"], fontsize=12)
        ax.axis('off')
        return fig

    # Plot bar
    colors = [THEME_COLORS[theme]["accent"] if i % 2 == 0 else THEME_COLORS[theme]["accent_2"] for i in range(len(df))]
    bars = ax.bar(
        df["month"], 
        df["donation_count"], 
        color=colors, 
        edgecolor=THEME_COLORS[theme]["bg"],
        width=0.5
    )

    # Style axes
    ax.spines['bottom'].set_color(THEME_COLORS[theme]["fg"])
    ax.spines['left'].set_color(THEME_COLORS[theme]["fg"])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.tick_params(colors=THEME_COLORS[theme]["fg"], labelsize=9)
    ax.set_xlabel("Month", color=THEME_COLORS[theme]["fg"], fontsize=10, labelpad=8)
    ax.set_ylabel("Donation Volume", color=THEME_COLORS[theme]["fg"], fontsize=10, labelpad=8)
    ax.set_title("Monthly Donation Trends", color=THEME_COLORS[theme]["fg"], fontsize=12, pad=10)
    
    # Add grid
    ax.grid(axis='y', linestyle='--', alpha=0.5, color=THEME_COLORS[theme]["grid"])
    
    # Value labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.0, 
            yval + 0.1, 
            str(int(yval)), 
            ha='center', 
            va='bottom', 
            color=THEME_COLORS[theme]["fg"], 
            fontsize=8, 
            weight='bold'
        )

    # Adjust layout
    fig.tight_layout()
    return fig
