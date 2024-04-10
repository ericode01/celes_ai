import json
from typing import Annotated

from semantic_kernel.functions import kernel_function
import pandas as pd


class ExcelPlugin:
    @kernel_function(
        description="Load an Excel file and convert its rows to JSON",
        name="ExcelFileToJsonList",
    )
    def excel_file_to_json_list(
            self,
            full_file_path: Annotated[str, "The full path to a Excel file."],
    ) -> Annotated[
        list, "A converted list in JSON in which each element is a JSON object representing a row in Excel."]:
        # Load Excel data into a DataFrame
        df = pd.read_excel(full_file_path, engine='openpyxl')

        # Convert DataFrame to JSON string
        json_data_str = df.to_json(orient='records', indent=4)
        print(json_data_str)

        json_data = json.loads(json_data_str)

        # extra metadata
        #
        return json_data

    @kernel_function(
        description="Save a list with JSON data to an Excel file.",
        name="JsonListToExcelFile",
    )
    def json_list_to_excel_file(
            self,
            json_data: Annotated[list, "The JSON data list to save."],
            full_file_path: Annotated[str, "The full path including the full file name to save the Excel file to."],
    ) -> Annotated[bool, "True if successfully saved the file. Else False."]:
        try:
            json_data_str = json.dumps(json_data)
            df = pd.read_json(json_data_str)
            df.to_excel(full_file_path)
            return True
        except Exception:
            return False

# if __name__ == "__main__":
#     excelPlugin = ExcelPlugin()
#     excelPlugin.excel_file_to_json_list("/Users/eric/development/ai_employee/sample_files/Project-Management-Sample-Data.xlsx")
