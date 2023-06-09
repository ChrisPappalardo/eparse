from tempfile import SpooledTemporaryFile
from typing import IO, BinaryIO, List, Optional, Union, cast

from eparse.core import get_df_from_file
import lxml.html
import pandas as pd

from unstructured.documents.elements import (
    DataSourceMetadata,
    Element,
    ElementMetadata,
    Table,
    process_metadata,
)
from unstructured.file_utils.filetype import FileType, add_metadata_with_filetype
from unstructured.partition.common import exactly_one, spooled_to_bytes_io_if_needed


@process_metadata()
@add_metadata_with_filetype(FileType.XLSX)
def partition_xlsx(
    filename: Optional[str] = None,
    file: Optional[Union[IO, SpooledTemporaryFile]] = None,
    metadata_filename: Optional[str] = None,
    include_metadata: bool = True,
    **kwargs,
) -> List[Element]:
    """Partitions Microsoft Excel Documents in .xlsx format into its document elements.

    Parameters
    ----------
    filename
        A string defining the target filename path.
    file
        A file-like object using "rb" mode --> open(filename, "rb").
    metadata_filename
        The filename to use for the metadata.
    include_metadata
        Determines whether or not metadata is included in the output.
    """
    exactly_one(filename=filename, file=file)

    if filename:
        tables = get_df_from_file(filename)
    else:
        f = spooled_to_bytes_io_if_needed(cast(Union[BinaryIO, SpooledTemporaryFile], file))
        tables = get_df_from_file(f)

    metadata_filename = filename or metadata_filename

    elements: List[Element] = []
    table_number = 0
    for table, excel_RC, table_name, sheet_name in tables:
        table_number += 1
        html_text = table.to_html(index=False, header=False, na_rep="")
        text = lxml.html.document_fromstring(html_text).text_content()

        if include_metadata:
            datasource_metadata = DataSourceMetadata(
                record_locator={
                    "excel_RC": excel_RC,
                    "table_name": table_name,
                },
            )
            metadata = ElementMetadata(
                text_as_html=html_text,
                page_name=sheet_name,
                page_number=table_number,
                filename=metadata_filename,
                data_source=datasource_metadata,
            )
        else:
            metadata = ElementMetadata()

        table = Table(text=text, metadata=metadata)
        elements.append(table)

    return elements


if __name__ == "__main__":
    try:
        partition_xlsx("tests/eparse_unit_test_data.xlsx")
    except Exception as e:
        print(f"xlsx failed with {e}")
