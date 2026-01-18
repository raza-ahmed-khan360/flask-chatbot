
import os
import asyncio
from agents import Agent, Runner, FileSearchTool
from agents.extensions.memory import AdvancedSQLiteSession
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from my_gaurdrail import document_scope_input_guardrail
from agents.exceptions import InputGuardrailTripwireTriggered

load_dotenv()
vector_store_id= os.getenv("VECTOR_STORE_ID")

# FileSearchTool with OpenAI vector store ID
file_search = FileSearchTool(vector_store_ids=[vector_store_id])

INSTRUCTIONS = """
You are a retrieval-augmented assistant.

You MUST follow these rules strictly:

1. Use the file_search tool to retrieve relevant information from the provided documents whenever the user asks a factual, explanatory, or knowledge-based question.

2. Base your answer ONLY on the content returned by the file_search tool.
   - Do NOT use prior knowledge.
   - Do NOT guess or infer beyond the retrieved text.

3. If the file_search tool returns no relevant results, respond clearly that the requested information is not available in the documents.

4. When answering:
   - Be concise, clear, and accurate.
   - Rephrase the retrieved content in your own words.
   - Do not mention internal tools, embeddings, vector stores, or retrieval mechanics.

5. Do NOT answer questions that are unrelated to the document content.
   Politely state that the question is outside the scope of the available documents.

6. Do NOT hallucinate, fabricate details, or complete missing information.

Your goal is to provide reliable answers strictly grounded in the retrieved document context.
"""

retrieval_agent = Agent(
    name="File Retrieval Chatbot",
    instructions=INSTRUCTIONS,
    tools=[file_search],
    input_guardrails=[document_scope_input_guardrail],
)

# Helper function to stream asynchronously for Flask
def stream_agent_response(user_message: str, history: list = None):
    """
    Streams the agent response. 
    'history' is expected to be a list of {"role": "user"|"assistant", "content": "..."}
    """
    async def async_stream():
        try:
            # We use an in-memory session because we are now stateless server-side.
            # The client provides the full history context.
            current_session = AdvancedSQLiteSession(
                session_id="temp_session",
                db_path=":memory:", 
                create_tables=True
            )

            # Construct context from history
            # format:
            # [Previous Conversation]
            # User: ...
            # Assistant: ...
            # [End Previous Conversation]
            
            context_str = ""
            if history:
                context_str += "Here is the conversation history so far:\n"
                for msg in history:
                    role = "User" if msg.get("role") == "user" else "Assistant"
                    content = msg.get("content", "")
                    context_str += f"{role}: {content}\n"
                context_str += "\nEnd of history.\n\n"

            # Prepend context to the current message
            full_input = f"{context_str}Current User Question: {user_message}"

            # Only send the specific user message to the runner? 
            # If we send full_input, the agent sees the history as one big blob of current input.
            # This is a simple way to give context for a retrieval agent.
            
            stream = Runner.run_streamed(retrieval_agent, full_input, current_session)
            
            async for event in stream.stream_events():
                if (
                    event.type == "raw_response_event"
                    and isinstance(event.data, ResponseTextDeltaEvent)
                ):
                    yield event.data.delta
            
            # We skip storing run usage permanently since we are stateless

        except InputGuardrailTripwireTriggered:
            yield "This question is outside the scope of the available documents."

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async_gen = async_stream()

    while True:
        try:
            yield loop.run_until_complete(async_gen.__anext__())
        except StopAsyncIteration:
            break
