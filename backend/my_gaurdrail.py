
import os
from dotenv import load_dotenv
from agents import (
    Agent,
    FileSearchTool,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from pydantic import BaseModel

load_dotenv()
vector_store_id = os.getenv("VECTOR_STORE_ID")

class DocumentCheckOutput(BaseModel):
    is_document_related: bool

# Tool to search the documents
file_search = FileSearchTool(vector_store_ids=[vector_store_id])

document_guardrail_agent = Agent(
    name="Document Scope Guardrail",
    instructions=(
        "You are a guardrail agent responsible for ensuring user questions are related to the provided documents.\n"
        "1. Use the `file_search` tool to search for keywords from the user's question in the vector store.\n"
        "2. If the search returns relevant results (even if partial), consider the question related.\n"
        "3. If the search returns NO relevant results, or if the question is clearly off-topic (e.g., about cooking, celebrities not mentioned), consider it unrelated.\n"
        "4. Return true if related, false if unrelated.\n\n"
        "Respond ONLY using the output schema."
    ),
    tools=[file_search],
    output_type=DocumentCheckOutput,
)


@input_guardrail
async def document_scope_input_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:

    result = await Runner.run(
        document_guardrail_agent,
        input,
        context=ctx.context,
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        # Trip when NOT document-related
        tripwire_triggered=not result.final_output.is_document_related,
    )
