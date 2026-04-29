from typing import Annotated, ClassVar, cast

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_together import ChatTogether
from pydantic import BaseModel, ConfigDict, Field

from logging_utils import get_logger

logger = get_logger()

ABSTAIN_SYSTEM_PROMPT = """
You are a revenue operations agent deciding whether a sales transcript contains
enough actionable signal to draft CRM updates.

Score transcript_value from 0 to 1 based on actionable CRM signal such as stage
movement, amount, close date, decision criteria, next steps, buyer roles, risks,
or MEDDPICC details. Score confidence from 0 to 1 based on how clearly the
transcript supports that assessment.

Return only the structured AbstainEvaluation. Do not extract the CRM fields here.
""".strip()


class AbstainEvaluation(BaseModel):
    """Assessment of whether a transcript contains enough signal to extract CRM updates."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    transcript_value: Annotated[
        float,
        Field(
            ge=0,
            le=1,
            description=(
                "Estimated usefulness of the transcript for CRM extraction, where 0 is "
                "no actionable deal signal and 1 is highly actionable."
            ),
        ),
    ]
    confidence: Annotated[
        float,
        Field(
            ge=0,
            le=1,
            description=(
                "Confidence in the transcript_value score, based on clarity, specificity, "
                "and amount of supporting evidence."
            ),
        ),
    ]
    justification: Annotated[
        str,
        Field(
            max_length=300,
            description="Brief explanation for the abstain decision and score assignment.",
        ),
    ]


async def invoke_abstain_agent(transcript_text: str) -> AbstainEvaluation:
    """Assess whether a transcript contains enough actionable CRM signal."""

    logger.info("Invoking abstain agent")
    agent = cast(
        Runnable[list[BaseMessage], AbstainEvaluation],
        ChatTogether(
            model="openai/gpt-oss-120b",
            temperature=0,
            top_p=1,
            max_tokens=500,
            max_retries=2,
        ).with_structured_output(AbstainEvaluation),
    )

    result = await agent.ainvoke(
        [
            SystemMessage(ABSTAIN_SYSTEM_PROMPT),
            HumanMessage(content=f"Transcript:\n{transcript_text}"),
        ]
    )
    logger.info(
        "Abstain agent finished: transcript_value=%.2f confidence=%.2f",
        result.transcript_value,
        result.confidence,
    )
    return result
