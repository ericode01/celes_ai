import json
from typing import Annotated

import pandas as pd
from semantic_kernel.functions import kernel_function


class JsonPlugin:
    @kernel_function(
        description="Filters the list of objects with the given query and returns the filtered result as a new list.",
        name="QueryJsonData",
    )
    def query_json_data(
            self,
            json_data: Annotated[
                list, "The JSON data to query against. Is a list of objects. All objects have the same set of keys."],
            query: Annotated[str, '''The query parameter is a string that specifies the condition(s) for filtering objects from a list of objects. It should be constructed using the objects' key names, comparison operators (`>`, `<`, `>=`, `<=`, `==`, `!=`), logical operators (`&` for AND, `|` for OR, `~` for NOT), and values to compare against. When writing complex expressions, consider the following guidelines:
1. Keys: Directly reference keys by their names. Always enclose them in backticks (\` \`). Example: \`Key Name\`.
2. Operators: Utilize comparison operators to evaluate conditions between key values and specified values or other key values. Combine multiple conditions with logical operators to refine your query. Parentheses can be used to group conditions and control the evaluation order.
3. Values: Incorporate values directly in the expression. String values must be enclosed in quotes. For conditions involving key value comparisons, simply use the key names.
4. Complex Conditions: For expressions combining multiple conditions, use parentheses to group them logically. This ensures the desired precedence and clarity in conditions that use a mix of logical operators.
5. Special Considerations: Strings and column names that conflict with Python syntax or contain special characters should be appropriately quoted or backticked. The expression should be written as a single string, maintaining readability and clarity even in complex scenarios.
Example expressions might look like "Age > 30" for a simple condition, or "((A > B) | (B == \`Complex Column\`)) & (A == 1) | (\`Another Column\` == 'value')" for a more complex query, illustrating the use of logical and comparison operators, special character handling in column names, and grouping of conditions.'''],
    ) -> Annotated[list, "A new list of the filtered result objects."]:
        df = pd.DataFrame(json_data)
        result_df = df.query(query)

        # Convert DataFrame to JSON string
        json_data_str = result_df.to_json(orient='records', indent=4)
        print(json_data_str)

        json_data = json.loads(json_data_str)

        return json_data

    @kernel_function(
        description="From the list find the objects containing the given key_value_pair_to_check and for these filtered object(s), if an object contains the key in the given key_value_pair_to_upsert, update its value; if an object doesn't contain the given key, insert the given key_value_pair_to_upsert.",
        name="UpsertObjectKeyValueWithConditionInList",
    )
    def upsert_object_key_value_with_condition_in_list(
            self,
            json_data: Annotated[
                list, "The JSON data to work against. Is a list of objects."],
            key_value_pair_to_check: Annotated[
                tuple, "From the list find the objects containing the given (key, value) pair."],
            key_value_pair_to_upsert: Annotated[
                tuple, "The (key, value) pair to update or insert."]
    ) -> Annotated[bool, "True: successfully insert or updated. False: failed to insert or update."]:
        for obj in json_data:
            if key_value_pair_to_check[0] in obj and obj[key_value_pair_to_check[0]] == key_value_pair_to_check[1]:
                print("updating\n" + json.dumps(obj))
                obj[key_value_pair_to_upsert[0]] = key_value_pair_to_upsert[1]
                print("updated\n" + json.dumps(obj))

        return True

    @kernel_function(
        description="Serialize a JSON data and print it to the console.",
        name="PrintJson",
    )
    def print_json(
            self,
            json_data: Annotated[
                list, "The JSON data to print."]
    ):
        print(json.dumps(json_data))

# if __name__ == "__main__":
#     df = pd.DataFrame({'A': range(1, 6),
#                        'B': range(10, 0, -2),
#                        'C C': range(10, 5, -1)})
#     result = df.query('((A > B | B == `C C`) & ~(A == 1)) | (`C C` == 7 )')
#     print(result)
