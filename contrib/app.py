import gradio as gr
import pandas as pd


# create context
class Context:
    def __init__(self) -> None:
        self.excel_file = None


context = Context()


# create gradio functions
def render_table(
    excel_file: str,
    selected_sheet: str,
    selected_table: str,
    context: Context = context,
) -> pd.DataFrame:
    """loads and renders table from file and sheet"""
    return pd.DataFrame()


with gr.Blocks(
    title="eparse: Excel Data Extraction",
    analytics_enabled=False,
) as demo:
    # gradio app
    with gr.Tab("eparse"):
        with gr.Row():
            excel_file = gr.File(label="Excel File")
            selected_sheet = gr.Dropdown(label="Selected Sheet")
            selected_table = gr.Dropdown(label="Selected Table")
        table_view = gr.DataFrame(label="Table View")
    with gr.Tab("Settings"):
        with gr.Tab("Metadata"):
            metadata = gr.Textbox(
                label="Metadata",
                value=str(context),
                lines=15,
            )

    # listeners
    excel_file.select(
        render_table,
        [excel_file, selected_sheet, selected_table],
        [selected_sheet, selected_table, table_view],
    )
    selected_sheet.change(
        render_table,
        [excel_file, selected_sheet, selected_table],
        [selected_sheet, selected_table, table_view],
    )
    selected_table.change(
        render_table,
        [excel_file, selected_sheet, selected_table],
        [selected_sheet, selected_table, table_view],
    )

demo.queue()
demo.launch(
    server_name="0.0.0.0",
    server_port=8000,
)
