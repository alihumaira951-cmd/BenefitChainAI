"""Benefit Domino Effect graph — NetworkX + Plotly. No Streamlit imports."""
import networkx as nx
import plotly.graph_objects as go
from engine import Household, ScreeningResult, LifelineStatus

# Fixed node positions
_NODE_POSITIONS = {
    'SNAP':     (0.0, 1.0),
    'Medicaid': (0.0, 0.0),
    'Lifeline': (1.0, 0.5),
    'SER':      (2.0, 0.5),
}

# Visual properties by node state: color and text label suffix
_STATE_STYLES = {
    'qualifies':         {'color': '#2ecc71', 'suffix': '(Potential Pathway)'},
    'already_receiving': {'color': '#4a90d9', 'suffix': '(Already Receiving)'},
    'not_indicated':     {'color': '#aaaaaa', 'suffix': '(Not Indicated)'},
}

_EDGES = [
    ('SNAP',     'Lifeline', 'Proof of SNAP participation required'),
    ('Medicaid', 'Lifeline', 'Proof of Medicaid enrollment required'),
]


def _node_state(node, household, results):
    """Return the state string for a graph node."""
    if node == 'SNAP':
        return 'already_receiving' if household.snap else 'not_indicated'
    if node == 'Medicaid':
        return 'already_receiving' if household.medicaid else 'not_indicated'
    if node == 'Lifeline':
        if not results:
            return 'not_indicated'
        status = results[0].status
        if status in (LifelineStatus.LIKELY_QUALIFIES_INCOME,
                      LifelineStatus.LIKELY_QUALIFIES_PROGRAM):
            return 'qualifies'
        if status == LifelineStatus.ALREADY_RECEIVING:
            return 'already_receiving'
        return 'not_indicated'
    if node == 'SER':
        if not results or len(results) < 3:
            return 'not_indicated'
        return 'qualifies' if results[2].status == 'urgent_referral' else 'not_indicated'
    return 'not_indicated'


def build_benefit_graph(household, results):
    """Build the benefit relationship DiGraph.

    Args:
        household: Household with snap/medicaid participation flags.
        results: list of ScreeningResult from screen() — index 0=Lifeline, 2=SER.

    Returns:
        nx.DiGraph with nodes SNAP, Medicaid, Lifeline, SER and two directed edges.
    """
    G = nx.DiGraph()
    for node in _NODE_POSITIONS:
        state = _node_state(node, household, results)
        G.add_node(node, state=state, pos=_NODE_POSITIONS[node])
    for src, dst, label in _EDGES:
        G.add_edge(src, dst, label=label, pathway=True)
    return G


def render_benefit_graph(household, results):
    """Build and render the benefit graph as a Plotly figure with arrows."""
    if not results:
        return go.Figure()

    try:
        G = build_benefit_graph(household, results)
    except Exception:
        return go.Figure()

    pos = _NODE_POSITIONS
    traces = []

    # Node traces — markers with color AND text state label for accessibility
    for node in list(_NODE_POSITIONS.keys()):
        x, y = pos[node]
        state = G.nodes[node]['state']
        style = _STATE_STYLES.get(state, _STATE_STYLES['not_indicated'])
        traces.append(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(
                size=52,
                color=style['color'],
                line=dict(color='#222222', width=2),
            ),
            text=[node],
            textposition='top center',
            textfont=dict(size=13, color='#111111'),
            hovertemplate='<b>' + node + '</b><br>' + style['suffix'] + '<extra></extra>',
            showlegend=False,
        ))
        # State label below node
        traces.append(go.Scatter(
            x=[x], y=[y - 0.2],
            mode='text',
            text=[style['suffix']],
            textfont=dict(size=10, color='#444444'),
            hoverinfo='none',
            showlegend=False,
        ))

    fig = go.Figure(
        data=traces,
        layout=go.Layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       range=[-0.6, 2.8]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       range=[-0.6, 1.6]),
            plot_bgcolor='#fafafa',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=20, b=20),
            height=360,
        ),
    )

    # Arrows via annotations
    import math
    for src, dst, label in _EDGES:
        x0, y0 = pos[src]
        x1, y1 = pos[dst]
        dx, dy = x1 - x0, y1 - y0
        dist = math.sqrt(dx * dx + dy * dy)
        ux, uy = dx / dist, dy / dist
        offset = 0.14
        ax0 = x0 + ux * offset
        ay0 = y0 + uy * offset
        ax1 = x1 - ux * offset
        ay1 = y1 - uy * offset

        fig.add_annotation(
            x=ax1, y=ay1,
            ax=ax0, ay=ay0,
            xref='x', yref='y',
            axref='x', ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.3,
            arrowwidth=2.5,
            arrowcolor='#555555',
            text='',
        )
        # Edge label at midpoint, slightly above the line
        fig.add_annotation(
            x=(x0 + x1) / 2,
            y=(y0 + y1) / 2 + 0.1,
            text='<i>' + label + '</i>',
            showarrow=False,
            font=dict(size=10, color='#555555'),
            bgcolor='rgba(255,255,255,0.85)',
            borderpad=3,
        )

    return fig
