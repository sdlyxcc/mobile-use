from minitap.agents.planner.types import Subgoal, SubgoalStatus


def get_current_subgoal(subgoals: list[Subgoal]) -> Subgoal | None:
    return next((s for s in subgoals if s.status.value == SubgoalStatus.PENDING.value), None)


def get_next_subgoal(subgoals: list[Subgoal]) -> Subgoal | None:
    return next((s for s in subgoals if s.status.value == SubgoalStatus.NOT_STARTED.value), None)


def nothing_started(subgoals: list[Subgoal]) -> bool:
    return all(s.status.value == SubgoalStatus.NOT_STARTED.value for s in subgoals)


def complete_current_subgoal(subgoals: list[Subgoal]) -> list[Subgoal]:
    current_subgoal = get_current_subgoal(subgoals)
    if not current_subgoal:
        return subgoals
    current_subgoal.status = SubgoalStatus.SUCCESS
    return subgoals


def fail_current_subgoal(subgoals: list[Subgoal]) -> list[Subgoal]:
    current_subgoal = get_current_subgoal(subgoals)
    if not current_subgoal:
        return subgoals
    current_subgoal.status = SubgoalStatus.FAILURE
    return subgoals


def all_completed(subgoals: list[Subgoal]) -> bool:
    return all(s.status.value == SubgoalStatus.SUCCESS.value for s in subgoals)


def one_of_them_is_failure(subgoals: list[Subgoal]) -> bool:
    return any(s.status.value == SubgoalStatus.FAILURE.value for s in subgoals)


def start_next_subgoal(subgoals: list[Subgoal]) -> list[Subgoal]:
    next_subgoal = get_next_subgoal(subgoals)
    if not next_subgoal:
        return subgoals
    next_subgoal.status = SubgoalStatus.PENDING
    return subgoals
