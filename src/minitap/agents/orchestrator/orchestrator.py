from pathlib import Path

from jinja2 import Template
from langchain_core.messages import SystemMessage

from minitap.agents.orchestrator.types import OrchestratorOutput, OrchestratorStatus
from minitap.agents.planner.utils import (
    all_completed,
    complete_current_subgoal,
    fail_current_subgoal,
    get_current_subgoal,
    nothing_started,
    start_next_subgoal,
)
from minitap.context import get_device_context
from minitap.graph.state import State
from minitap.services.llm import get_llm
from minitap.utils.decorators import wrap_with_callbacks
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


@wrap_with_callbacks(
    before=lambda: logger.info("Starting Orchestrator Agent..."),
    on_success=lambda _: logger.info("Orchestrator Agent ✅"),
    on_failure=lambda _: logger.info("Orchestrator Agent ❌"),
)
async def orchestrator_node(state: State):
    if nothing_started(state.subgoal_plan):
        state.subgoal_plan = start_next_subgoal(state.subgoal_plan)
        logger.info("No subgoal started yet, starting the first one.")
        return {
            "agents_thoughts": ["No subgoal started yet, starting the first one."],
            "subgoal_plan": state.subgoal_plan,
        }

    current_subgoal = get_current_subgoal(state.subgoal_plan)

    if not current_subgoal:
        return {"agents_thoughts": ["No subgoal to plan for."]}

    device_context = get_device_context()
    system_message = Template(
        Path(__file__).parent.joinpath("orchestrator.md").read_text(encoding="utf-8")
    ).render(
        platform=device_context.mobile_platform,
        initial_goal=state.initial_goal,
        subgoal_plan="\n".join(str(s) for s in state.subgoal_plan),
        current_subgoal=str(current_subgoal),
        agent_thoughts="\n".join(state.agents_thoughts),
    )
    messages = [
        SystemMessage(content=system_message),
    ]

    llm = get_llm(override_provider="openai", override_model="gpt-4o", override_temperature=0.4)
    llm = llm.with_structured_output(OrchestratorOutput)
    response: OrchestratorOutput = await llm.ainvoke(messages)  # type: ignore

    if response.status == OrchestratorStatus.CONTINUE:
        state.subgoal_plan = complete_current_subgoal(state.subgoal_plan)
        thoughts = [f"Subgoal '{str(current_subgoal)}' completed. {response.reason}"]

        if all_completed(state.subgoal_plan):
            thoughts.append("All subgoals completed, the goal is achieved.")
            return {
                "subgoal_plan": state.subgoal_plan,
                "agents_thoughts": thoughts,
            }
        state.subgoal_plan = start_next_subgoal(state.subgoal_plan)
        new_subgoal = get_current_subgoal(state.subgoal_plan)
        thoughts.append(f"Starting next subgoal '{str(new_subgoal)}'. {response.reason}")
        thoughts.append("==== NEXT SUBGOAL ====")
        return {
            "agents_thoughts": thoughts,
            "subgoal_plan": state.subgoal_plan,
        }

    elif response.status == OrchestratorStatus.REPLAN:
        thoughts = [f"Subgoal '{str(current_subgoal)}' failed. {response.reason}"]
        state.subgoal_plan = fail_current_subgoal(state.subgoal_plan)
        thoughts.append("==== END OF PLAN, REPLANNING ====")
        return {
            "agents_thoughts": thoughts,
            "subgoal_plan": state.subgoal_plan,
        }

    elif response.status == OrchestratorStatus.RESUME:
        return {
            "agents_thoughts": [
                f"Let's continue the current subgoal. {response.reason}",
            ],
        }

    return {
        "agents_thoughts": [
            f"Orchestrator Agent completed with {response.status.value}. {response.reason}",
        ],
    }
