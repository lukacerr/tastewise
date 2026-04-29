"""CLI agent for extracting Salesforce opportunity updates from transcripts."""

import asyncio
import json
import uuid
from pathlib import Path
from typing import (
    Annotated,
    Literal,
    NotRequired,
    Required,
    TypedDict,
    cast,
)

import typer
from dotenv import load_dotenv
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from langgraph.graph.state import CompiledStateGraph
from pydantic import Field

from agents.abstain import AbstainEvaluation, invoke_abstain_agent
from agents.extraction import AgentExtraction, Stage, invoke_extraction_agent
from agents.summary import invoke_summary_agent
from logging_utils import configure_logging, get_logger

_ = load_dotenv()
logger = get_logger()


class Opportunity(AgentExtraction):
    """Final consolidated opportunity update produced from agent extraction results."""

    # Intentionally hardcoded as per task definition
    opportunity_id: Annotated[
        uuid.UUID,
        Field(
            default=uuid.uuid4(),
            description="Unique identifier for the opportunity record being updated.",
        ),
    ]
    stage: Annotated[
        Stage | None,
        Field(
            default=Stage.prospecting,
            description="Current consolidated opportunity stage after applying the stage delta.",
        ),
    ]

    average_confidence: Annotated[
        float,
        Field(
            ge=0,
            le=1,
            description="Average confidence across extracted attributes used in the opportunity.",
        ),
    ]
    abstainReasoning: Annotated[
        AbstainEvaluation,
        Field(
            description="Signal-quality evaluation used to decide whether extraction should run."
        ),
    ]
    last_touch_summary: Annotated[
        str,
        Field(
            max_length=300,
            description="Short human-readable summary of the latest transcript touchpoint.",
        ),
    ]


class AgentState(TypedDict):
    """Shared state passed between transcript-processing graph nodes."""

    transcript_path: Required[Path]
    """Path to the transcript file being processed."""
    threshold: Required[float]
    """Minimum value_index required to extract opportunity updates."""
    transcript_text: NotRequired[str]
    """Raw transcript text read from disk."""
    abstain_evaluation: NotRequired[AbstainEvaluation]
    """Structured signal-quality evaluation."""
    value_index: NotRequired[float]
    """Computed transcript_value multiplied by confidence."""
    agent_extraction: NotRequired[AgentExtraction]
    """Structured CRM extraction from the transcript."""
    last_touch_summary: NotRequired[str]
    """Brief summary of the transcript touchpoint."""
    opportunity: NotRequired[Opportunity]
    """Final consolidated opportunity update."""
    abstained: NotRequired[bool]
    """Whether the agent skipped CRM extraction."""


def require_transcript_text(state: AgentState) -> str:
    """Return transcript text or raise when graph state is incomplete."""

    transcript_text = state.get("transcript_text")
    if transcript_text is None:
        raise ValueError("Transcript text is missing from graph state.")
    return transcript_text


def read_transcript(state: AgentState) -> dict[str, str]:
    """Read the transcript file into graph state."""

    transcript_path = state["transcript_path"]
    logger.info("Reading transcript: %s", transcript_path)
    transcript_text = transcript_path.read_text(encoding="utf-8")
    logger.info("Transcript loaded: %d characters", len(transcript_text))
    return {"transcript_text": transcript_text}


async def evaluate_abstain(
    state: AgentState,
) -> dict[str, AbstainEvaluation | float | bool]:
    """Evaluate transcript signal and decide whether extraction should run."""

    logger.info("Evaluating whether to abstain")
    evaluation = await invoke_abstain_agent(require_transcript_text(state))
    value_index = evaluation.transcript_value * evaluation.confidence
    abstained = value_index < state["threshold"]
    logger.info(
        "Abstain decision: value_index=%.2f threshold=%.2f abstained=%s",
        value_index,
        state["threshold"],
        abstained,
    )

    return {
        "abstain_evaluation": evaluation,
        "value_index": value_index,
        "abstained": abstained,
    }


def route_after_abstain(
    state: AgentState,
) -> Literal["summarize_touch", "extract_updates"]:
    """Route graph execution based on the abstain decision."""
    route = "summarize_touch" if state.get("abstained", False) else "extract_updates"
    logger.info("Routing after abstain evaluation: %s", route)
    return route


def route_after_summary(state: AgentState) -> Literal["create_opportunity", "__end__"]:
    """Finish abstained runs or continue to opportunity creation."""
    route = "__end__" if state.get("abstained", False) else "create_opportunity"
    logger.info("Routing after summary: %s", route)
    return route


async def extract_updates(state: AgentState) -> dict[str, AgentExtraction]:
    """Extract structured CRM updates from the transcript."""

    logger.info("Extracting opportunity updates")
    return {
        "agent_extraction": await invoke_extraction_agent(
            require_transcript_text(state)
        )
    }


async def summarize_touch(state: AgentState) -> dict[str, str]:
    """Summarize the transcript for last-touch logging."""

    logger.info("Summarizing last touch")
    summary = await invoke_summary_agent(require_transcript_text(state))
    return {"last_touch_summary": summary.summary}


def iter_confidence_scores(extraction: AgentExtraction):
    """Yield every confidence score from an extraction result."""

    direct_attributes = (
        extraction.deal_stage_delta,
        extraction.amount_usd,
        extraction.close_date,
        extraction.next_step_description,
        extraction.next_step_owner,
        extraction.next_step_due_date,
    )
    for attribute in direct_attributes:
        yield attribute.confidence_score

    attribute_lists = (
        extraction.risks,
        extraction.metrics,
        extraction.economic_buyer,
        extraction.decision_criteria,
        extraction.decision_process,
        extraction.paper_process,
        extraction.identify_pain,
        extraction.champion,
        extraction.competition,
        extraction.detractors,
    )
    for attributes in attribute_lists:
        for attribute in attributes:
            yield attribute.confidence_score


def create_opportunity(state: AgentState) -> dict[str, Opportunity]:
    """Create the final opportunity update from extraction and summary state."""

    logger.info("Creating final opportunity payload")
    extraction = state.get("agent_extraction")
    if extraction is None:
        raise ValueError("Agent extraction is missing from graph state.")
    last_touch_summary = state.get("last_touch_summary")
    if last_touch_summary is None:
        raise ValueError("Last-touch summary is missing from graph state.")
    abstain_evaluation = state.get("abstain_evaluation")
    if abstain_evaluation is None:
        raise ValueError("Abstain evaluation is missing from graph state.")

    confidence_scores = list(iter_confidence_scores(extraction))
    average_confidence = (
        sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    )

    opportunity = Opportunity(
        opportunity_id=uuid.uuid4(),
        deal_stage_delta=extraction.deal_stage_delta,
        amount_usd=extraction.amount_usd,
        close_date=extraction.close_date,
        risks=extraction.risks,
        next_step_description=extraction.next_step_description,
        next_step_owner=extraction.next_step_owner,
        next_step_due_date=extraction.next_step_due_date,
        metrics=extraction.metrics,
        economic_buyer=extraction.economic_buyer,
        decision_criteria=extraction.decision_criteria,
        decision_process=extraction.decision_process,
        paper_process=extraction.paper_process,
        identify_pain=extraction.identify_pain,
        champion=extraction.champion,
        competition=extraction.competition,
        detractors=extraction.detractors,
        stage=extraction.deal_stage_delta.value[1],
        average_confidence=average_confidence,
        abstainReasoning=abstain_evaluation,
        last_touch_summary=last_touch_summary,
    )

    logger.info(
        "Opportunity payload created: stage=%s average_confidence=%.2f",
        opportunity.stage.value if opportunity.stage else None,
        opportunity.average_confidence,
    )
    return {"opportunity": opportunity}


def build_graph() -> CompiledStateGraph[AgentState, None, AgentState, AgentState]:
    """Build the transcript-processing LangGraph workflow."""

    graph = StateGraph(AgentState)

    _ = graph.add_node("read_transcript", read_transcript)
    _ = graph.add_node("evaluate_abstain", evaluate_abstain)
    _ = graph.add_node("extract_updates", extract_updates)
    _ = graph.add_node("summarize_touch", summarize_touch)
    _ = graph.add_node("create_opportunity", create_opportunity)

    _ = graph.add_edge(START, "read_transcript")
    _ = graph.add_edge("read_transcript", "evaluate_abstain")
    _ = graph.add_conditional_edges("evaluate_abstain", route_after_abstain)
    _ = graph.add_edge("extract_updates", "summarize_touch")
    _ = graph.add_conditional_edges("summarize_touch", route_after_summary)
    _ = graph.add_edge("create_opportunity", END)

    return graph.compile()


async def run_agent(transcript_path: Path, threshold: float) -> AgentState:
    """Run the transcript graph asynchronously."""

    logger.info("Starting transcript agent: threshold=%.2f", threshold)
    graph = build_graph()
    result = cast(
        AgentState,
        await graph.ainvoke(
            {"transcript_path": transcript_path, "threshold": threshold},
            config={
                "run_name": "tastewise_transcript_agent",
                "tags": ["tastewise", "cli"],
            },
        ),
    )
    logger.info("Transcript agent finished")
    return result


def main(
    transcript_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to the transcript .txt file to process.",
        ),
    ],
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            min=0,
            max=1,
            help="Minimum value_index required to extract opportunity updates.",
        ),
    ] = 0.6,
) -> None:
    """Run the transcript agent and print structured JSON output."""

    configure_logging()
    result = asyncio.run(run_agent(transcript_path, threshold))

    if result.get("abstained", False):
        abstain_evaluation = result.get("abstain_evaluation")
        value_index = result.get("value_index")
        if abstain_evaluation is None or value_index is None:
            raise ValueError("Abstain evaluation is missing from graph state.")
        typer.echo(
            json.dumps(
                {
                    "abstained": True,
                    "transcript_value": abstain_evaluation.transcript_value,
                    "confidence": abstain_evaluation.confidence,
                    "value_index": value_index,
                    "justification": abstain_evaluation.justification,
                    "last_touch_summary": result.get("last_touch_summary"),
                },
                indent=2,
            )
        )
        logger.info("Printed abstain result")
        return

    opportunity = result.get("opportunity")
    if opportunity is None:
        raise ValueError("Opportunity is missing from graph state.")
    typer.echo(opportunity.model_dump_json(indent=2))
    logger.info("Printed opportunity result")


if __name__ == "__main__":
    typer.run(main)
