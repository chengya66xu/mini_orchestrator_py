from orchestrator.types import (
    TaskSpec,
    ContextState,
    RunTrace,
    StepTrace,
    now_iso,
)
from orchestrator.planner import Planner
from orchestrator.executor import Executor
from orchestrator.state import update_state
from orchestrator.utils import truncate, write_json


class Orchestrator:
    def __init__(self, task: str, workspace: str, max_steps: int):
        self.task_spec = TaskSpec(
            user_goal=task,
            workspace=workspace,
            max_steps=max_steps
        )
        self.state = ContextState()
        self.trace = RunTrace(
            task=task,
            workspace=workspace,
            started_at=now_iso()
        )

#Starts the orchestration loop
    def run(self) -> dict:
        for step_index in range(1, self.task_spec.max_steps + 1):
            #step 1 : planner decides next action
            action = Planner.next_action(
                task=self.task_spec.user_goal,
                state=self.state,
                step_index=step_index
            )

            #step 2 : if planner decides to finish
            if action.action_type == "finish":
                #record final step
                step_trace = StepTrace(
                    step_index=step_index,
                    timestamp=now_iso(),
                    action=action.to_dict(),
                    observation=None,
                    status="finished"
                )
                self.trace.steps.append(step_trace.to_dict()) #append to trace
                #set finish time and summary
                self.trace.finished_at = now_iso()
                self.trace.final_summary = action.summary

                trace_path = "trace.json"
                write_json(trace_path, self.trace.to_dict())

                return {
                    "final_summary": action.summary,
                    "trace_path": trace_path
                }

            #step 3 : action
            print(f"\n[Step {step_index}] {action.reason}")

            try:
                #execute action
                observation = Executor.execute(
                    action=action,
                    workspace=self.task_spec.workspace
                )
                update_state(self.state, action, observation)

                #step 4: print the output
                print(f"Success: {observation.success}")
                if observation.stdout.strip():
                    print("--- stdout ---")
                    print(truncate(observation.stdout))
                if observation.stderr.strip():
                    print("--- stderr ---")
                    print(truncate(observation.stderr))

                #step 5: record trace
                status = "executed" if observation.success else "failed"

                step_trace = StepTrace(
                    step_index=step_index,
                    timestamp=now_iso(),
                    action=action.to_dict(),
                    observation=observation.to_dict(),
                    status=status
                )
                self.trace.steps.append(step_trace.to_dict())

            #step 6:Catch execution errors
            except Exception as e:
                error_observation = {
                    "success": False,
                    "exit_code": None,
                    "stdout": "",
                    "stderr": str(e)
                }

                print(f"Execution error: {e}")

                step_trace = StepTrace(
                    step_index=step_index,
                    timestamp=now_iso(),
                    action=action.to_dict(),
                    observation=error_observation,
                    status="failed"
                )
                self.trace.steps.append(step_trace.to_dict())

                self.trace.finished_at = now_iso()
                self.trace.final_summary = f"Run failed at step {step_index}: {e}"

                trace_path = "trace.json"
                write_json(trace_path, self.trace.to_dict())

                return {
                    "final_summary": self.trace.final_summary,
                    "trace_path": trace_path
                }

        self.trace.finished_at = now_iso()
        #fallback if no finish action
        self.trace.final_summary = "Max steps reached before finish action"
        trace_path = "trace.json"
        write_json(trace_path, self.trace.to_dict())

        return {
            "final_summary": self.trace.final_summary,
            "trace_path": trace_path
        }