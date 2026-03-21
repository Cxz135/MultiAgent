#tools_and_schemas.py


from typing import List
from pydantic import BaseModel, Field

class SearchQueryList(BaseModel):
    query: List[str] = Field(
        description="A list of search queries to be used for web research.")

    rationale: str = Field(
        description="A brief explanation of why these queries are relevant to the research topic.")


class Reflection(BaseModel):
    is_sufficient: bool = Field(
        description="Whether the provided summary is sufficient to answer the user's question."
    )

    knowledge_gap: str = Field(
        description="A description of what information is missing or needs clarification."
    )

    follow_up_queries: List[str] = Field(
        description="A list of follow_up queries to address knowledge gap."
    )
