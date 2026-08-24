import io
import base64
from typing import List, Dict, Any
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

def _encode_fig(fig) -> str:
    """Encode a matplotlib figure to a base64 png string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded

def generate_pareto_chart(data: List[Dict[str, Any]], title: str = "Pareto Chart") -> str:
    """
    Generate a base64 encoded Pareto chart.
    Expects data format: [{"loss_reason": "A", "duration_minutes": 120, "percentage_of_downtime": 40}, ...]
    """
    if not data:
        return ""
        
    labels = [item.get("loss_reason", "Unknown") for item in data]
    durations = [item.get("duration_minutes", 0) for item in data]
    
    # Calculate cumulative percentages if not perfectly provided
    total = sum(durations)
    if total == 0: return ""
    cum_percentages = []
    cum = 0
    for d in durations:
        cum += d
        cum_percentages.append((cum / total) * 100)

    fig, ax1 = plt.subplots(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    # Bar chart for absolute duration
    sns.barplot(x=labels, y=durations, ax=ax1, color='steelblue')
    ax1.set_ylabel("Duration (Minutes)")
    ax1.set_xlabel("Loss Reason")
    ax1.tick_params(axis='x', rotation=45)

    # Line chart for cumulative percentage
    ax2 = ax1.twinx()
    ax2.plot(labels, cum_percentages, color='crimson', marker='D', ms=7, linewidth=2)
    ax2.set_ylabel("Cumulative Percentage (%)")
    ax2.set_ylim(0, 110)

    plt.title(title)
    fig.tight_layout()
    
    return _encode_fig(fig)

def generate_spc_chart(data: List[Dict[str, Any]], title: str = "SPC Control Chart") -> str:
    """
    Generate a Statistical Process Control (SPC) chart.
    Expects data format: [{"date": "2026-08-01", "measure": 10.1, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5}, ...]
    Sorted by date ascending.
    """
    if not data:
        return ""
        
    dates = [item.get("date", "") for item in data]
    measures = [item.get("measure", 0) for item in data]
    
    # Use first item for reference lines
    norm = data[0].get("norm", 0)
    tol_min = data[0].get("tolerance_min", 0)
    tol_max = data[0].get("tolerance_max", 0)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    # Plot measurements
    ax.plot(dates, measures, marker='o', linestyle='-', color='indigo', label='Measurement')
    
    # Reference lines
    ax.axhline(y=norm, color='green', linestyle='--', label='Norm/Target')
    ax.axhline(y=tol_max, color='red', linestyle=':', label='Upper Control Limit')
    ax.axhline(y=tol_min, color='red', linestyle=':', label='Lower Control Limit')

    ax.set_ylabel("Measurement Value")
    ax.set_xlabel("Date")
    ax.tick_params(axis='x', rotation=45)
    
    # Add legend outside the plot
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

    plt.title(title)
    fig.tight_layout()
    
    return _encode_fig(fig)
