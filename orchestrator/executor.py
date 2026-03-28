import subprocess
from orchestrator.types import Action, Observation


class Executor:
    #safty control
    ALLOWED_COMMANDS = {"pwd", "ls", "find", "head", "cat"}

    @classmethod
    def execute(cls, action: Action, workspace: str) -> Observation:
        if action.action_type != "run_command":
            raise ValueError("Only run_command actions can be executed")

        if action.command not in cls.ALLOWED_COMMANDS:
            raise ValueError(f"Command '{action.command}' is not allowed")

        completed = subprocess.run(
            [action.command] + action.args,
            cwd=workspace,
            capture_output=True,
            text=True
        )

        return Observation(
            success=(completed.returncode == 0),
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr
        )

