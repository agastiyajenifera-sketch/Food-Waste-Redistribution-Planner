import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from database import get_connection

# Colors matching the unique design system
THEME_COLORS = {
    "dark": {
        "bg": "#0a0f1d",       # Deep Space Blue (bg_dark)
        "fg": "#f8fafc",       # Slate 50
        "accent": "#ff6b6b",   # Vibrant Coral
        "accent_2": "#8b5cf6", # Vibrant Purple
        "grid": "#1e293b",     # Dark Slate grid lines
        "palette": ["#ff6b6b", "#8b5cf6", "#10b981", "#3b82f6", "#f59e0b", "#ec4899"]
    },
    "light": {
        "bg": "#f1f5f9",       # Light Slate (bg_light)
        "fg": "#0f172a",       # Slate 900
        "accent": "#ee5253",   # Deep Coral
        "accent_2": "#7c3aed", # Deep Purple
        "grid": "#cbd5e1",     # Light Slate grid lines
        "palette": ["#ee5253", "#7c3aed", "#059669", "#2563eb", "#d97706", "#db2777"]
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
    query = """
    SELECT substr(created_at, 1, 7) as month, COUNT(*) as donation_count 
    FROM donations 
    GROUP BY month 
    ORDER BY month ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def apply_font_settings():
    """Applies clean geometric typography settings to matplotlib global properties."""
    plt.rcParams['font.sans-serif'] = 'Century Gothic'
    plt.rcParams['font.family'] = 'sans-serif'

def create_category_pie_chart(theme="dark"):
    """
    Generates a Matplotlib Pie Chart representing food category distribution.
    """
    apply_font_settings()
    df = get_category_data()
    
    # Initialize a figure
    fig = Figure(figsize=(4.5, 3.8), dpi=100)
    fig.patch.set_facecolor(THEME_COLORS[theme]["bg"])
    
    ax = fig.add_subplot(111)
    ax.set_facecolor(THEME_COLORS[theme]["bg"])

    if df.empty:
        ax.text(0.5, 0.5, "No data available", 
                horizontalalignment='center', verticalalignment='center',
                color=THEME_COLORS[theme]["fg"], fontsize=12)
        ax.axis('off')
        return fig

    # Plot pie chart with vibrant custom color palette
    wedges, texts, autotexts = ax.pie(
        df["donation_count"], 
        labels=df["category"], 
        autopct='%1.1f%%',
        startangle=140, 
        colors=THEME_COLORS[theme]["palette"][:len(df)],
        textprops=dict(color=THEME_COLORS[theme]["fg"], weight="bold", size=9),
        wedgeprops=dict(edgecolor=THEME_COLORS[theme]["bg"], linewidth=1.8)
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')
        autotext.set_size(8)

    ax.set_title("DONATIONS BY CATEGORY", color=THEME_COLORS[theme]["fg"], fontsize=12, pad=10, weight="bold")
    
    return fig

def create_monthly_bar_chart(theme="dark"):
    """
    Generates a Matplotlib Bar Chart representing monthly donation trends.
    """
    apply_font_settings()
    df = get_monthly_data()
    
    # Initialize figure
    fig = Figure(figsize=(5, 3.8), dpi=100)
    fig.patch.set_facecolor(THEME_COLORS[theme]["bg"])
    
    ax = fig.add_subplot(111)
    ax.set_facecolor(THEME_COLORS[theme]["bg"])

    if df.empty:
        ax.text(0.5, 0.5, "No data available", 
                horizontalalignment='center', verticalalignment='center',
                color=THEME_COLORS[theme]["fg"], fontsize=12)
        ax.axis('off')
        return fig

    # Plot bar with colorful gradients
    colors = [THEME_COLORS[theme]["palette"][i % len(THEME_COLORS[theme]["palette"])] for i in range(len(df))]
    bars = ax.bar(
        df["month"], 
        df["donation_count"], 
        color=colors, 
        edgecolor=THEME_COLORS[theme]["bg"],
        width=0.45
    )

    # Style axes
    ax.spines['bottom'].set_color(THEME_COLORS[theme]["fg"])
    ax.spines['left'].set_color(THEME_COLORS[theme]["fg"])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.tick_params(colors=THEME_COLORS[theme]["fg"], labelsize=9)
    ax.set_xlabel("MONTH", color=THEME_COLORS[theme]["fg"], fontsize=10, labelpad=8, weight="bold")
    ax.set_ylabel("DONATIONS", color=THEME_COLORS[theme]["fg"], fontsize=10, labelpad=8, weight="bold")
    ax.set_title("MONTHLY DONATION TRENDS", color=THEME_COLORS[theme]["fg"], fontsize=12, pad=10, weight="bold")
    
    # Add grid
    ax.grid(axis='y', linestyle='--', alpha=0.3, color=THEME_COLORS[theme]["grid"])
    
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
