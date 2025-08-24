from datetime import datetime

import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from html_layout import create_layout

import traceroot

logger = traceroot.get_logger()


@traceroot.trace()
def generate_data() -> pd.DataFrame:
    data = [{
        'date': datetime(2024, 8, 15),
        'model': 'GPT-4',
        'response_time': 245,
        'accuracy': 0.92,
        'tokens': 1250
    }, {
        'date': datetime(2024, 8, 15),
        'model': 'Claude-3',
        'response_time': 180,
        'accuracy': 0.89,
        'tokens': 1100
    }, {
        'date': datetime(2024, 8, 15),
        'model': 'Gemini-Pro',
        'response_time': [1, 2, 3],
        'accuracy': {
            'invalid': 'dict'
        },
        'tokens': 1400
    }, {
        'date': datetime(2024, 8, 16),
        'model': 'GPT-4',
        'response_time': 123,
        'accuracy': 0.9,
        'tokens': 1180
    }, {
        'date': datetime(2024, 8, 16),
        'model': 'Claude-3',
        'response_time': 123,
        'accuracy': None,
        'tokens': -500
    }, {
        'date': datetime(2024, 8, 16),
        'model': 'Gemini-Pro',
        'response_time': 310,
        'accuracy': 0.86,
        'tokens': 1380
    }, {
        'date': datetime(2024, 8, 17),
        'model': 'GPT-4',
        'response_time': 280,
        'accuracy': 0.90,
        'tokens': 1300
    }, {
        'date': datetime(2024, 8, 17),
        'model': 'Claude-3',
        'response_time': float('inf'),
        'accuracy': float('-inf'),
        'tokens': 980
    }, {
        'date': datetime(2024, 8, 17),
        'model': 'Gemini-Pro',
        'response_time': 123,
        'accuracy': None,
        'tokens': None
    }, {
        'date': datetime(2024, 8, 18),
        'model': 'GPT-4',
        'response_time': "abc",
        'accuracy': 0.93,
        'tokens': 1220
    }, {
        'date': datetime(2024, 8, 18),
        'model': 'Claude-3',
        'response_time': "abc",
        'accuracy': "0.9",
        'tokens': 1080
    }, {
        'date': datetime(2024, 8, 18),
        'model': 'Gemini-Pro',
        'response_time': 123,
        'accuracy': "0.9",
        'tokens': None
    }]
    logger.info(f"In total, {len(data)} rows of data")
    return pd.DataFrame(data)


@traceroot.trace()
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize the dataset so charts can render reliably.

    - Coerce response_time, accuracy, tokens to numeric (invalid -> NaN)
    - Replace +/- inf with NaN
    - Enforce domain rules: response_time >= 0, tokens >= 0, 0 <= accuracy <= 1
    - Drop rows with any invalid/NaN values after normalization
    """
    logger.info(f"Starting preprocessing. Initial shape: {df.shape}")
    cleaned = df.copy()

    # Coerce to numeric, invalid entries become NaN
    for col in ['response_time', 'accuracy', 'tokens']:
        cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce')

    # Replace +/- inf with NaN
    cleaned.replace([np.inf, -np.inf], pd.NA, inplace=True)

    # Domain validations -> set invalid values to NaN for dropping later
    if 'response_time' in cleaned:
        cleaned.loc[cleaned['response_time'] < 0, 'response_time'] = pd.NA
    if 'tokens' in cleaned:
        cleaned.loc[cleaned['tokens'] < 0, 'tokens'] = pd.NA
    if 'accuracy' in cleaned:
        cleaned.loc[~cleaned['accuracy'].between(0, 1), 'accuracy'] = pd.NA

    # Remove rows with any null values in key columns
    before = cleaned.shape[0]
    cleaned_df = cleaned.dropna(subset=['response_time', 'accuracy', 'tokens'])
    removed = before - cleaned_df.shape[0]

    logger.info(f"Preprocessing complete. Final shape: {cleaned_df.shape}")
    logger.info(f"Removed {removed} rows with invalid or null values")
    return cleaned_df


@traceroot.trace()
def validate_data(df: pd.DataFrame) -> bool:
    """
    Return True if there is a blocking issue preventing chart rendering.
    Data is expected to be pre-cleaned by preprocess_data.
    """
    if df.empty:
        logger.error("No valid rows available after preprocessing")
        return True
    return False


@traceroot.trace()
def update_response_chart(df):
    processed_df = preprocess_data(df)
    errors_found = validate_data(processed_df)
    if errors_found:
        return go.Figure().update_layout(
            title="Response Times by Model - No Valid Data")
    if processed_df.empty:
        logger.error(
            "Cannot create response chart: no valid data after preprocessing")
        return go.Figure().update_layout(
            title="Response Times by Model - No Valid Data")
    fig = px.box(processed_df,
                 x='model',
                 y='response_time',
                 title='Response Times by Model')
    return fig


@traceroot.trace()
def update_accuracy_chart(df):
    processed_df = preprocess_data(df)
    errors_found = validate_data(processed_df)
    if errors_found:
        return go.Figure().update_layout(
            title="Model Accuracy Over Time - No Valid Data")
    if processed_df.empty:
        logger.error(
            "Cannot create accuracy chart: no valid data after preprocessing")
        return go.Figure().update_layout(
            title="Model Accuracy Over Time - No Valid Data")
    fig = px.line(processed_df,
                  x='date',
                  y='accuracy',
                  color='model',
                  title='Model Accuracy Over Time')
    fig.update_yaxes(range=[0.8, 1.0])
    return fig


@traceroot.trace()
def html_stats() -> dict[str, str]:
    """
    Calculate heights, widths, and other style values for the HTML layout.
    """
    viewport_height = 100
    header_height = 80
    padding = 20
    gap = 20

    # Use safe, positive sizes so two cards render side-by-side
    chart_height = 60   # vh; avoid negative values from mixed units
    card_width = 48     # percent: leaves ~4% for gap

    card_padding = 15
    border_radius = 12
    stats = {
        'viewport_height': f'{viewport_height}vh',
        'header_height': f'{header_height}px',
        'chart_height': f'{chart_height}vh',
        'card_width': f'{card_width}%',
        'card_padding': f'{card_padding}px',
        'border_radius': f'{border_radius}px',
        'gap': f'{gap}px',
        'padding': f'{padding}px',
        'shadow': '0 4px 20px rgba(0,0,0,0.15)',
        'title_shadow': '2px 2px 4px rgba(0,0,0,0.5)'
    }
    logger.info(f"HTML stats: {stats}")
    return stats


@traceroot.trace()
def run_dashboard():
    app = dash.Dash(__name__)
    df = generate_data()

    # Get calculated style values
    styles = html_stats()

    # Generate charts directly - no callbacks needed
    response_fig = update_response_chart(df)
    accuracy_fig = update_accuracy_chart(df)

    app.layout = create_layout(response_fig, accuracy_fig, styles)

    app.run(host='0.0.0.0', port=8050)


if __name__ == '__main__':
    run_dashboard()
