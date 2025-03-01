from typing import Any, Optional

import gradio as gr
import pandas as pd

from eparse.core import get_df_from_file


# create context
class Context:
    def __init__(self) -> None:
        self.selected_file: Optional[gr.File] = None
        self.selected_sheet: Optional[str] = None
        self.selected_table: Optional[str] = None
        # df, excel_RC, name, sheet
        self._tables = list[tuple[pd.DataFrame, str, str, str]]

    def __str__(self) -> str:
        v = (self.selected_file, self.selected_sheet, self.selected_table)
        return "{} {} {}".format(*v)


context = Context()


# create gradio functions
def render_table(
    selected_file: str,
    selected_sheet: str,
    selected_table: str,
    context: Context = context,
) -> tuple[str, str, pd.DataFrame]:
    """loads and renders table from file and sheet"""

    if selected_file != context.excel_file:
        context.selected_file = selected_file
        context.selected_sheet = selected_sheet
        context.selected_table = selected_table
        context._tables = list()
        for df, excel_RC, name, sheet in get_df_from_file(excel_file):
            context._tables.append((df, excel_RC, name, sheet))
            context.selected_sheet = sheet
            context.selected_table = name

    elif selected_sheet != context.selected_sheet:
        context.selected_sheet = selected_sheet
        context.selected_table = None

    elif selected_table != context.selected_table:
        context.selected_table = selected_table

    for df, excel_RC, name, sheet in context._tables:
        if sheet == selected_sheet and name == selected_table:
            return (excel_RC, name, df)

    return ("", "", pd.DataFrame())


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
