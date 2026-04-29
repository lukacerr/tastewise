from datetime import date
from enum import Enum
from typing import Annotated, ClassVar, Generic, TypeVar, cast

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_together import ChatTogether
from pydantic import BaseModel, ConfigDict, Field

from logging_utils import get_logger

logger = get_logger()

T = TypeVar("T")

EXTRACTION_SYSTEM_PROMPT = """
You are a Salesforce update extraction agent. Extract only information grounded
in the transcript into the AgentExtraction schema.

Every extracted attribute must include a concise justification and timestamped
quotes from the transcript when available. Do not invent missing values. For
list fields, return an empty list when there is no evidence. For scalar nullable
fields, use null values with low confidence when a field is absent or only
implied.

For dates, use ISO dates. If the transcript gives only a quarter or broad period,
normalize to the first plausible day of that period and state the assumption in
the justification.
""".strip()


class ExtractedAttribute(BaseModel, Generic[T]):
    """A single extracted CRM attribute with confidence and source evidence."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    value: Annotated[T, Field(description="Extracted value for this attribute.")]
    confidence_score: Annotated[
        float,
        Field(
            ge=0,
            le=1,
            description=(
                "Confidence that the extracted value is correct, where 0 is unsupported "
                "and 1 is directly supported by the transcript."
            ),
        ),
    ]
    justification: Annotated[
        str,
        Field(
            max_length=150,
            description="Concise reason the value was extracted or left empty.",
        ),
    ]
    timestamp_quotes: Annotated[
        list[str],
        Field(
            default=[],
            description="Transcript quotes, preferably with timestamps, that support the value.",
        ),
    ]


class Stage(str, Enum):
    """Canonical sales stages used for opportunity stage extraction."""

    prospecting = "prospecting"
    discovery = "discovery"
    solution_design = "solution_design"
    proposal = "proposal"
    negotiation = "negotiation"
    closed_won = "closed_won"
    closed_lost = "closed_lost"


class AgentExtraction(BaseModel):
    """Structured CRM updates extracted from a sales transcript."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    deal_stage_delta: Annotated[
        ExtractedAttribute[tuple[Stage, Stage]],
        Field(
            description="Previous and updated deal stage inferred from the transcript."
        ),
    ]
    amount_usd: Annotated[
        ExtractedAttribute[float | None],
        Field(description="Opportunity amount in USD, or null if not stated."),
    ]
    close_date: Annotated[
        ExtractedAttribute[date | None],
        Field(description="Expected opportunity close date, or null if not stated."),
    ]
    risks: Annotated[
        list[ExtractedAttribute[str]],
        Field(
            description="Material deal risks, blockers, objections, or warning signs.",
        ),
    ]

    next_step_description: Annotated[
        ExtractedAttribute[str | None],
        Field(
            description="Committed or recommended follow-up action from the transcript."
        ),
    ]
    next_step_owner: Annotated[
        ExtractedAttribute[str | None],
        Field(description="Person or team responsible for the next step."),
    ]
    next_step_due_date: Annotated[
        ExtractedAttribute[date | None],
        Field(description="Due date or timing commitment for the next step."),
    ]

    metrics: Annotated[
        list[ExtractedAttribute[str]],
        Field(
            description="Quantified business outcomes, success measures, or KPIs mentioned."
        ),
    ]
    economic_buyer: Annotated[
        list[ExtractedAttribute[str]],
        Field(
            description="Individuals with budget authority or final purchasing influence."
        ),
    ]
    decision_criteria: Annotated[
        list[ExtractedAttribute[str]],
        Field(description="Criteria the prospect will use to evaluate the solution."),
    ]
    decision_process: Annotated[
        list[ExtractedAttribute[str]],
        Field(description="Steps, stakeholders, or approvals in the buying decision."),
    ]
    paper_process: Annotated[
        list[ExtractedAttribute[str]],
        Field(
            description="Legal, procurement, security, or contracting process details."
        ),
    ]
    identify_pain: Annotated[
        list[ExtractedAttribute[str]],
        Field(
            description="Business pains, gaps, or motivations creating urgency to buy."
        ),
    ]
    champion: Annotated[
        list[ExtractedAttribute[str]],
        Field(description="Internal advocates who support the vendor or solution."),
    ]
    competition: Annotated[
        list[ExtractedAttribute[str]],
        Field(
            description="Competing vendors, alternatives, or incumbent solutions mentioned."
        ),
    ]
    detractors: Annotated[
        list[ExtractedAttribute[str]],
        Field(description="Stakeholders opposing, slowing, or questioning the deal."),
    ]


async def invoke_extraction_agent(transcript_text: str) -> AgentExtraction:
    """Extract structured CRM updates from a transcript."""

    logger.info("Invoking extraction agent")
    agent = cast(
        Runnable[list[BaseMessage], AgentExtraction],
        ChatTogether(
            model="zai-org/GLM-5.1",
            temperature=0,
            top_p=1,
            max_tokens=4_000,
            max_retries=2,
        ).with_structured_output(AgentExtraction),
    )

    result = await agent.ainvoke(
        [
            SystemMessage(EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(content=f"Transcript:\n{transcript_text}"),
        ]
    )
    logger.info(
        "Extraction agent finished: stage=%s->%s risks=%d",
        result.deal_stage_delta.value[0].value,
        result.deal_stage_delta.value[1].value,
        len(result.risks),
    )
    return result
