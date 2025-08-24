import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from html_layout import create_layout

import traceroot

logger = traceroot.get_logger()


@traceroot.trace()
def generate_data() -> pd.DataFrame:
    # ... existing data generation unchanged ...
    return pd.DataFrame(data)


@traceroot.trace()
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"Starting preprocessing. Initial shape: {df.shape}")
    cleaned_df = df.dropna()
    logger.info(f"Preprocessing complete. Final shape: {cleaned_df.shape}")
    logger.info(
        f"Removed {df.shape[0] - cleaned_df.shape[0]} rows with null values")
    return cleaned_df


@traceroot.trace()
def validate_data(df: pd.DataFrame) -> bool:
    errors_found = False
    if df.isnull().any().any():
        logger.error("Found None/null values in dataset")
        errors_found = True

    for col in ['response_time', 'accuracy', 'tokens']:
        non_numeric = df[col].apply(
            lambda x: not isinstance(x, (int, float, type(None))))
        if non_numeric.any():
            # non-numeric values are flagged as warnings
            logger.warning(f"Found non-numeric values in {col} column")
            errors_found = True
            continue

        numeric_data = df[col].dropna()
        if len(numeric_data) == 0:
            logger.warning(f"No numeric values found in {col} column")
            errors_found = True
            continue

        if col == 'response_time' and (numeric_data < 0).any():
            logger.error("Found negative values in response_time column")
            errors_found = True
        elif col == 'tokens' and (numeric_data < 0).any():
            logger.error("Found negative values in tokens column")
            errors_found = True
        elif col == 'accuracy':
            invalid_acc = (numeric_data < 0) | (numeric_data > 1)
            if invalid_acc.any():
                logger.error("Found accuracy values outside valid range (0-1)")
                errors_found = True

    if errors_found:
        logger.error("Data preprocessing failed due to data quality issues")
    return errors_found


@traceroot.trace()
def update_response_chart(df):
    processed_df = preprocess_data(df)
    errors_found = validate_data(processed_df)
    if errors_found:
        logger.error("Cannot create response chart: data validation failed")
        return go.Figure().update_layout(
            title="Response Times by Model - Data Validation Failed")

    if processed_df.empty:
        logger.error(
            "Cannot create response chart: no valid data after preprocessing")
        return go.Figure().update_layout(
            title="Response Times by Model - No Valid Data")

    return px.box(
        processed_df,
        x='model',
        y='response_time',
        title='Response Times by Model'
    )


@traceroot.trace()
def update_accuracy_chart(df):
    processed_df = preprocess_data(df)
    errors_found = validate_data(processed_df)
    if errors_found:
        logger.error("Cannot create accuracy chart: data validation failed")
        return go.Figure().update_layout(
            title="Model Accuracy Over Time - Data Validation Failed")

    if processed_df.empty:
        logger.error(
            "Cannot create accuracy chart: no valid data after preprocessing")
        return go.Figure().update_layout(
            title="Model Accuracy Over Time - No Valid Data")

    fig = px.line(
        processed_df,
        x='date',
        y='accuracy',
        color='model',
        title='Model Accuracy Over Time'
    )
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
    # ensure available height is non-negative
    available_height = max(viewport_height - (header_height + 2 * padding), 0)
    # reserve a small margin, ensure positive chart height
    chart_height = max(available_height - 20, 0)
    # split into two cards side by side
    card_width = 48
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


def run_dashboard():
    app = dash.Dash(__name__)
    df = generate_data()
    styles = html_stats()
    response_fig = update_response_chart(df)
    accuracy_fig = update_accuracy_chart(df)
    app.layout = create_layout(response_fig, accuracy_fig, styles)
    app.run(host='0.0.0.0', port=8050)


if __name__ == '__main__':
    run_dashboard()
