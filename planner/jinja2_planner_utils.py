from semantic_kernel import Kernel
from semantic_kernel.functions import KernelFunctionMetadata


class Jinja2PlannerUtils:
    @staticmethod
    def get_available_function_manual(kernel: Kernel):
        excluded_plugins = []
        excluded_functions = []
        included_functions = []

        available_functions = [
            func
            for func in kernel.plugins.get_list_of_function_metadata()
            if (func.plugin_name not in excluded_plugins and func.name not in excluded_functions)
        ]

        manual = "\n\n".join([Jinja2PlannerUtils.to_manual_string(func) for func in available_functions])
        return manual

    @staticmethod
    def to_manual_string(function: KernelFunctionMetadata):
        inputs = [
            f"    - {parameter.name} ({parameter.type_}): {parameter.description}"
            + (f" (default value: {parameter.default_value})" if parameter.default_value else "")
            for parameter in function.parameters
        ]
        inputs = "\n".join(inputs)

        if function.return_parameter and function.return_parameter.type_ != "None":
            output = f"output ({function.return_parameter.type_}): {function.return_parameter.description}"
        else:
            output = "output: no output"

        fully_qualified_name = f"{function.plugin_name}___{function.name}" if function.plugin_name else function.name

        return f"{fully_qualified_name}:\n  description: {function.description}\n  inputs:\n" + f"{inputs}" + f"\n  {output}"
