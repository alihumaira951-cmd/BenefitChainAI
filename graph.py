"""BenefitChain AI — spacious, accessible NetworkX / Plotly graph preview.

Preview only: leave the existing graph.py unchanged.
"""
from math import hypot
import networkx as nx
import plotly.graph_objects as go
from engine import LifelineStatus

_NODE_POSITIONS = {
    'SNAP': (0.0, 1.35),
    'Medicaid': (0.0, -1.35),
    'Lifeline': (2.6, 0.0),
    'SER': (5.15, 0.0),
}

_STATE_STYLES = {
    'qualifies': {'color': '#18a67d', 'text': 'Potential pathway'},
    'already_receiving': {'color': '#438bd4', 'text': 'Already receiving'},
    'not_indicated': {'color': '#aeb9c6', 'text': 'Not indicated'},
}

_EDGES = [
    ('SNAP', 'Lifeline', 'Proof of SNAP participation may be required'),
    ('Medicaid', 'Lifeline', 'Proof of Medicaid enrollment may be required'),
]


def _node_state(node, household, results):
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
        if len(results) > 2 and results[2].status == 'urgent_referral':
            return 'qualifies'
        return 'not_indicated'
    return 'not_indicated'


def build_benefit_graph(household, results):
    """Return an nx.DiGraph with the same four programs and two pathways."""
    graph = nx.DiGraph()
    for node, pos in _NODE_POSITIONS.items():
        graph.add_node(node, pos=pos, state=_node_state(node, household, results))
    for src, dst, label in _EDGES:
        graph.add_edge(src, dst, label=label, pathway=True)
    return graph


def render_benefit_graph(household, results):
    """Draw an uncluttered, interactive map; descriptions remain in hover text."""
    if not results:
        return go.Figure()

    graph = build_benefit_graph(household, results)
    figure = go.Figure()

    # Pale lanes behind the source -> Lifeline connections.
    for src, dst, label in _EDGES:
        x0, y0 = _NODE_POSITIONS[src]
        x1, y1 = _NODE_POSITIONS[dst]
        length = hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        # Arrows stop outside the 78 px node markers, leaving labels legible.
        start = 0.36
        finish = 0.42
        active = bool(getattr(household, src.lower(), False))
        color = '#159a8c' if active else '#aab7c5'
        figure.add_annotation(
            x=x1 - ux * finish, y=y1 - uy * finish,
            ax=x0 + ux * start, ay=y0 + uy * start,
            xref='x', yref='y', axref='x', ayref='y',
            text='', showarrow=True, arrowhead=2, arrowsize=1.25,
            arrowwidth=3 if active else 2.1, arrowcolor=color,
            opacity=1 if active else 0.65,
        )
        # Invisible wide hover target carries the full explanation.
        figure.add_trace(go.Scatter(
            x=[x0 + (x1-x0)*0.35, x0 + (x1-x0)*0.65],
            y=[y0 + (y1-y0)*0.35, y0 + (y1-y0)*0.65],
            mode='lines', line={'color': 'rgba(0,0,0,0)', 'width': 18},
            hovertemplate=f'{src} → {dst}<br>{label}<br>Separate application required<extra></extra>',
            showlegend=False,
        ))

    for node, (x, y) in _NODE_POSITIONS.items():
        state = graph.nodes[node]['state']
        style = _STATE_STYLES[state]
        figure.add_trace(go.Scatter(
            x=[x], y=[y], mode='markers',
            marker={'size': 76, 'color': style['color'],
                    'line': {'color': '#ffffff', 'width': 4}},
            hovertemplate=f'<b>{node}</b><br>{style["text"]}<extra></extra>',
            showlegend=False,
        ))
        figure.add_annotation(x=x, y=y + 0.60, text=f'<b>{node}</b>',
                              showarrow=False, font={'size': 17, 'color': '#143658'})
        figure.add_annotation(x=x, y=y - 0.58, text=style['text'],
                              showarrow=False, font={'size': 12, 'color': '#4a6078'},
                              bgcolor='#f5f9fc', borderpad=3)

    # Text labels are placed away from the connecting lines, not across them.
    figure.add_annotation(x=1.15, y=1.18, text='SNAP pathway', showarrow=False,
                          font={'size': 12, 'color': '#356579'}, bgcolor='#f5f9fc', borderpad=3)
    figure.add_annotation(x=1.15, y=-1.18, text='Medicaid pathway', showarrow=False,
                          font={'size': 12, 'color': '#356579'}, bgcolor='#f5f9fc', borderpad=3)
    figure.add_annotation(x=3.9, y=-0.78, showarrow=False,
                          text='SER is a separate<br>emergency referral',
                          font={'size': 12, 'color': '#62768b'}, align='center')
    figure.update_layout(
        height=480,
        margin={'l': 16, 'r': 16, 't': 24, 'b': 14},
        paper_bgcolor='#ffffff', plot_bgcolor='#f8fbff',
        xaxis={'range': [-0.85, 5.95], 'visible': False, 'fixedrange': True},
        yaxis={'range': [-2.15, 2.18], 'visible': False, 'fixedrange': True,
               'scaleanchor': 'x', 'scaleratio': 0.9},
        hovermode='closest', dragmode=False,
    )
    return figure
