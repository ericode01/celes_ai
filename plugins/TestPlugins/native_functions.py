from typing import Annotated

from semantic_kernel.functions import kernel_function


class TestPlugin:
    @kernel_function(
        description="Search coursera courses",
        name="SearchCoursera",
    )
    def search_coursera(
            self,
            query: Annotated[str, "The search query"],
    ) -> Annotated[dict, "The search results."]:
        return {
            'hits': [
                {
                    'name': 'course1',
                    'entityType': 'type1'
                },
                {
                    'name': 'course2',
                    'entityType': 'type2'
                }
            ]
        }
