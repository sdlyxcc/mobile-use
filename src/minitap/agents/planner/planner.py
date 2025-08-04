from pathlib import Path

from jinja2 import Template
from langchain_core.messages import AIMessage, SystemMessage

from minitap.agents.planner.types import PlannerOutput, Subgoal, SubgoalStatus
from minitap.agents.planner.utils import one_of_them_is_failure
from minitap.context import get_device_context
from minitap.graph.state import State
from minitap.services.llm import get_llm
from minitap.utils.decorators import wrap_with_callbacks
from minitap.utils.logger import get_logger

logger = get_logger(__name__)


@wrap_with_callbacks(
    before=lambda: logger.info("Starting Planner Agent..."),
    on_success=lambda _: logger.info("Planner Agent ✅"),
    on_failure=lambda _: logger.info("Planner Agent ❌"),
)
async def planner_node(state: State):
    device_context = get_device_context()

    needs_replan = one_of_them_is_failure(state.subgoal_plan)

    system_message = Template(
        Path(__file__).parent.joinpath("planner.md").read_text(encoding="utf-8")
    ).render(
        platform=device_context.mobile_platform,
        action="replan" if needs_replan else "plan",
        initial_goal=state.initial_goal,
        previous_plan="\n".join(str(s) for s in state.subgoal_plan),
        agent_thoughts="\n".join(state.agents_thoughts),
    )
    messages = [
        SystemMessage(content=system_message),
    ]

    llm = get_llm(override_provider="openai", override_model="gpt-4o", override_temperature=0.4)
    llm = llm.with_structured_output(PlannerOutput)
    response: PlannerOutput = await llm.ainvoke(messages)  # type: ignore

    subgoals_plan = [
        Subgoal(
            description=subgoal,
            status=SubgoalStatus.NOT_STARTED,
            completion_reason=None,
        )
        for subgoal in response.subgoals
    ]

    return {
        "messages": [AIMessage(content="A new plan has been generated.")],
        "needs_replan": False,
        "subgoal_plan": subgoals_plan,
    }
