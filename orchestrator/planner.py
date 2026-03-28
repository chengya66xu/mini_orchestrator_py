from orchestrator.types import Action, ContextState


class Planner:
    @staticmethod
    #this function takes task+state and returns next action
    def next_action(task: str, state: ContextState, step_index: int) -> Action:
        facts = state.facts
#decison tree
        #step 1:If workspace not confirmed → run pwd
        if not facts.pwd_seen:
            return Action(
                action_type="run_command",
                command="pwd",
                args=[],
                reason="Establish current workspace context"
            )

        #step 2:If files not listed → run ls -la
        if not facts.files_listed:
            return Action(
                action_type="run_command",
                command="ls",
                args=["-la"],
                reason="Inspect top-level repository structure"
            )

        #step 3:Find key metadata files and gather evidence
        #This part builds an evidence-gathering pipeline
        if not facts.key_files_scanned:
            return Action(
                action_type="run_command",
                command="find",
                args=[
                    ".",
                    "-maxdepth",
                    "2",
                    "(",
                    "-name",
                    "README*",
                    "-o",
                    "-name",
                    "requirements.txt",
                    "-o",
                    "-name",
                    "pyproject.toml",
                    "-o",
                    "-name",
                    "package.json",
                    "-o",
                    "-name",
                    "Cargo.toml",
                    ")"
                ],
                reason="Find key project metadata files"
            )

        #step 4:If README exists but not read → read preview
        if facts.readme_found and not facts.readme_attempted:
            return Action(
                action_type="run_command",
                command="head",
                args=["-n", "20", facts.readme_path],
                reason="Read README preview for usage instructions"
            )

        #If README is insufficient → read manifest
        #Priority: pyproject → requirements → package.json → Cargo.toml
        if facts.pyproject_found and not facts.manifest_attempted:
            return Action(
                action_type="run_command",
                command="head",
                args=["-n", "40", "pyproject.toml"],
                reason="Read pyproject.toml to inspect Python project metadata"
            )

        if facts.requirements_found and not facts.manifest_attempted:
            return Action(
                action_type="run_command",
                command="head",
                args=["-n", "40", facts.requirements_path],
                reason="Read requirements.txt to inspect Python dependencies"
            )

        if facts.package_json_found and not facts.manifest_attempted:
            return Action(
                action_type="run_command",
                command="head",
                args=["-n", "40", facts.package_json_path],
                reason="Read package.json to inspect Node project metadata"
            )

        if facts.cargo_toml_found and not facts.manifest_attempted:
            return Action(
                action_type="run_command",
                command="head",
                args=["-n", "40", "Cargo.toml"],
                reason="Read Cargo.toml to inspect Rust project metadata"
            )

        #step 6:If enough info → finish and summarize
        return Action(
            action_type="finish",
            reason="Enough information collected to summarize repository",
            summary=Planner.build_summary(task, state, step_index - 1)
        )

    @staticmethod
    #state → human-readable answer
    def build_summary(task: str, state: ContextState, steps_executed: int) -> str:
        facts = state.facts

        lines = [
            "Repository inspection completed.",
            "",
            f"User task: {task}",
            f"Steps executed: {steps_executed}",
            "",
            "Final assessment:",
            f"- Workspace: {facts.workspace_path or 'unknown'}",
            f"- Detected project type: {facts.project_type or 'unknown'}",
        ]

        #Collect evidence → explainability
        evidence = []
        if facts.readme_found:
            evidence.append("README")
        if facts.requirements_found:
            evidence.append("requirements.txt")
        if facts.pyproject_found:
            evidence.append("pyproject.toml")
        if facts.package_json_found:
            evidence.append("package.json")
        if facts.cargo_toml_found:
            evidence.append("Cargo.toml")

        lines.append(f"- Evidence used: {', '.join(evidence) if evidence else 'none'}")

        lines.append("")
        lines.append("Observation quality:")
        if facts.readme_found:
            #Check observation quality
            if facts.readme_preview:
                lines.append("- README existed and provided useful content")
            else:
                lines.append("- README existed but did not provide useful content")

        if facts.manifest_preview:
            lines.append("- Manifest file provided useful content")
        elif any([
            facts.requirements_found,
            facts.pyproject_found,
            facts.package_json_found,
            facts.cargo_toml_found
        ]):
            lines.append("- Manifest file existed and was inspected")

        lines.append("")
        lines.append("Recommended way to run this repository:")
        #Suggest how to run based on project type
        if facts.project_type == "python":
            if facts.pyproject_found:
                lines.append("- python3 -m pip install -e .")
            elif facts.requirements_found:
                lines.append("- python3 -m pip install -r requirements.txt")
            else:
                lines.append("- Check README for Python setup steps")
        elif facts.project_type == "node":
            lines.append("- Try: npm install")
            lines.append("- Then inspect package.json scripts to determine the correct run command")
        elif facts.project_type == "rust":
            lines.append("- cargo build / cargo run / cargo test")
        else:
            lines.append("- Manual inspection needed")

        if facts.manifest_preview:
            lines.append("")
            lines.append("Manifest preview:")
            lines.append(facts.manifest_preview.strip())

        lines.append("")
        lines.append("Execution notes:")
        for note in state.notes:
            lines.append(f"- {note}")

        return "\n".join(lines)