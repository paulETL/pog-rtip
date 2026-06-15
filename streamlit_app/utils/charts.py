"""utils/charts.py — shared Plotly theme + helpers."""
import plotly.graph_objects as go
import plotly.express as px

DARK_BG    = "#060d1f"
CARD_BG    = "#0f172a"
BORDER     = "rgba(255,165,0,0.15)"
ORANGE     = "#f97316"
BLUE       = "#3b82f6"
GREEN      = "#22c55e"
RED        = "#ef4444"
AMBER      = "#f59e0b"
PURPLE     = "#a855f7"
CYAN       = "#06b6d4"
TEXT_MAIN  = "#f8fafc"
TEXT_MUTED = "#64748b"

PLOTLY_LAYOUT = dict(
    paper_bgcolor=CARD_BG,
    plot_bgcolor=CARD_BG,
    font=dict(family="Inter, sans-serif", color=TEXT_MAIN, size=12),
    margin=dict(l=12, r=12, t=36, b=12),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=BORDER,
        borderwidth=1,
        font=dict(color=TEXT_MAIN, size=11),
    ),
    hoverlabel=dict(
        bgcolor="#1e293b",
        bordercolor=BORDER,
        font=dict(color=TEXT_MAIN, size=12),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.08)",
        tickfont=dict(color=TEXT_MUTED, size=11),
        title_font=dict(color=TEXT_MUTED),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.08)",
        tickfont=dict(color=TEXT_MUTED, size=11),
        title_font=dict(color=TEXT_MUTED),
    ),
)

PALETTE_ORANGE_BLUE = [ORANGE, BLUE, GREEN, RED, AMBER, PURPLE, CYAN,
                        "#ec4899", "#14b8a6", "#8b5cf6"]

COLOR_SCALE_HEAT = [
    [0.0, "#0c1a3d"],
    [0.25, "#1e3a6e"],
    [0.5, "#c2410c"],
    [0.75, "#ea580c"],
    [1.0, "#f97316"],
]


def apply_dark(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    layout = dict(PLOTLY_LAYOUT)
    layout["title"] = dict(text=title, font=dict(size=14, color=TEXT_MAIN), x=0.01)
    layout["height"] = height
    fig.update_layout(**layout)
    return fig


def fmt_naira(v: float) -> str:
    if v >= 1_000_000_000:
        return f"₦{v/1_000_000_000:.2f}B"
    if v >= 1_000_000:
        return f"₦{v/1_000_000:.2f}M"
    if v >= 1_000:
        return f"₦{v/1_000:.1f}K"
    return f"₦{v:,.0f}"


def fmt_liters(v: float) -> str:
    if v >= 1_000_000:
        return f"{v/1_000_000:.2f}M L"
    if v >= 1_000:
        return f"{v/1_000:.1f}K L"
    return f"{v:,.0f} L"
