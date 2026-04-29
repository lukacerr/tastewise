from typing import Annotated, ClassVar, cast

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_together import ChatTogether
from pydantic import BaseModel, ConfigDict, Field

from logging_utils import get_logger

logger = get_logger()

SUMMARY_SYSTEM_PROMPT = """
You are a Salesforce activity logging agent. Summarize the latest transcript
touchpoint in one concise sentence under 300 characters.
""".strip()


class SummaryResult(BaseModel):
    """Structured last-touch summary for Salesforce activity logging."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    summary: Annotated[
        str,
        Field(
            max_length=300,
            description="Brief summary of the latest transcript touchpoint.",
        ),
    ]


async def invoke_summary_agent(transcript_text: str) -> SummaryResult:
    """Summarize the latest transcript touchpoint."""

    logger.info("Invoking summary agent")
    agent = cast(
        Runnable[list[BaseMessage], SummaryResult],
        ChatTogether(
            model="openai/gpt-oss-120b",
            temperature=0,
            top_p=1,
            max_tokens=300,
            max_retries=2,
        ).with_structured_output(SummaryResult),
    )

    result = await agent.ainvoke(
        [
            SystemMessage(SUMMARY_SYSTEM_PROMPT),
            HumanMessage(content=f"Transcript:\n{transcript_text}"),
        ]
    )
    logger.info("Summary agent finished")
    return result
