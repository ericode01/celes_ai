from semantic_kernel import Kernel, KernelFunction
from semantic_kernel.exceptions import KernelPluginNotFoundError, KernelFunctionNotFoundError


class KernelExtensions:
    @staticmethod
    def func_from_fully_qualified_function_name(kernel: Kernel, fully_qualified_function_name: str) -> KernelFunction:
        plugin_name, function_name = fully_qualified_function_name.split("___")
        if plugin_name not in kernel.plugins:
            raise KernelPluginNotFoundError(f"Plugin '{plugin_name}' not found")
        if function_name not in kernel.plugins[plugin_name]:
            raise KernelFunctionNotFoundError(f"Function '{function_name}' not found in plugin '{plugin_name}'")
        return kernel.plugins[plugin_name][function_name]
