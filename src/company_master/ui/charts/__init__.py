# -*- coding: utf-8 -*-
"""Charts module for Huginn UI.

Provides helper functions to create Plotly charts that can be rendered
in Streamlit or exported as JSON.

Example:
    from company_master.ui.charts import line_chart

    fig = line_chart(data, x='date', y='value', title='Sales Trend')
    st.plotly_chart(fig, use_container_width=True)
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


def line_chart(
    data: Union[pd.DataFrame, Dict, List],
    x: str,
    y: str,
    color: Optional[str] = None,
    title: Optional[str] = None,
    template: str = "plotly_white",
    **px_kwargs: Any,
) -> go.Figure:
    """Create a line chart.

    Args:
        data: DataFrame or dict/list convertible to DataFrame.
        x: Column name for x-axis.
        y: Column name for y-axis.
        color: Optional column name for color encoding.
        title: Chart title.
        template: Plotly template.
        **px_kwargs: Additional arguments passed to px.line.

    Returns:
        Plotly Figure object.
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    fig = px.line(data, x=x, y=y, color=color, title=title, template=template, **px_kwargs)
    fig.update_layout(legend_title_text="")
    return fig


def bar_chart(
    data: Union[pd.DataFrame, Dict, List],
    x: str,
    y: Union[str, List[str]],
    color: Optional[str] = None,
    title: Optional[str] = None,
    template: str = "plotly_white",
    orientation: str = "v",
    **px_kwargs: Any,
) -> go.Figure:
    """Create a bar chart.

    Args:
        data: DataFrame or dict/list convertible to DataFrame.
        x: Column name for x-axis.
        y: Column name(s) for y-axis.
        color: Optional column name for color encoding.
        title: Chart title.
        template: Plotly template.
        orientation: 'v' for vertical, 'h' for horizontal.
        **px_kwargs: Additional arguments passed to px.bar.

    Returns:
        Plotly Figure object.
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    fig = px.bar(data, x=x, y=y, color=color, title=title, template=template,
                 orientation=orientation, **px_kwargs)
    fig.update_layout(legend_title_text="")
    return fig


def pie_chart(
    data: Union[pd.DataFrame, Dict, List],
    names: str,
    values: str,
    title: Optional[str] = None,
    template: str = "plotly_white",
    **px_kwargs: Any,
) -> go.Figure:
    """Create a pie chart.

    Args:
        data: DataFrame or dict/list convertible to DataFrame.
        names: Column name for slice labels.
        values: Column name for slice values.
        title: Chart title.
        template: Plotly template.
        **px_kwargs: Additional arguments passed to px.pie.

    Returns:
        Plotly Figure object.
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    fig = px.pie(data, names=names, values=values, title=title,
                 template=template, **px_kwargs)
    return fig


def scatter_chart(
    data: Union[pd.DataFrame, Dict, List],
    x: str,
    y: str,
    color: Optional[str] = None,
    size: Optional[str] = None,
    title: Optional[str] = None,
    template: str = "plotly_white",
    **px_kwargs: Any,
) -> go.Figure:
    """Create a scatter chart.

    Args:
        data: DataFrame or dict/list convertible to DataFrame.
        x: Column name for x-axis.
        y: Column name for y-axis.
        color: Optional column name for color encoding.
        size: Optional column name for point size.
        title: Chart title.
        template: Plotly template.
        **px_kwargs: Additional arguments passed to px.scatter.

    Returns:
        Plotly Figure object.
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    fig = px.scatter(data, x=x, y=y, color=color, size=size,
                     title=title, template=template, **px_kwargs)
    fig.update_layout(legend_title_text="")
    return fig


def fig_to_json(fig: go.Figure) -> Dict[str, Any]:
    """Convert a Plotly figure to a JSON-serializable dict.

    Useful for embedding in web dashboards or passing through APIs.

    Args:
        fig: Plotly Figure.

    Returns:
        Dict representing the figure (JSON-serializable).
    """
    return json.loads(pio.to_json(fig))


__all__ = [
    "line_chart",
    "bar_chart",
    "pie_chart",
    "scatter_chart",
    "fig_to_json",
]
