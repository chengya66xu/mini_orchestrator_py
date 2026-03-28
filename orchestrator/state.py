from orchestrator.types import Action, Observation, ContextState


def update_state(state: ContextState, action: Action, observation: Observation) -> None:
    if action.action_type != "run_command":
        return

    facts = state.facts

    if action.command == "pwd" and observation.success:
        facts.pwd_seen = True
        facts.workspace_path = observation.stdout.strip()
        state.notes.append(f"Workspace confirmed: {facts.workspace_path}")

    elif action.command == "ls" and observation.success:
        facts.files_listed = True
        state.notes.append("Top-level files listed")

    elif action.command == "find" and observation.success:
        facts.key_files_scanned = True
        output = observation.stdout
        lines = [line.strip() for line in output.splitlines() if line.strip()]

        for line in lines:
            if line.endswith("README.md") or line.endswith("README"):
                facts.readme_found = True
                if facts.readme_path is None:
                    facts.readme_path = line

            if line.endswith("requirements.txt"):
                facts.requirements_found = True
                facts.project_type = "python"
                if facts.requirements_path is None:
                    facts.requirements_path = line

            if line.endswith("pyproject.toml"):
                facts.pyproject_found = True
                facts.project_type = "python"
                if facts.pyproject_path is None:
                    facts.pyproject_path = line

            if line.endswith("package.json"):
                facts.package_json_found = True
                facts.project_type = "node"
                if facts.package_json_path is None:
                    facts.package_json_path = line

            if line.endswith("Cargo.toml"):
                facts.cargo_toml_found = True
                facts.project_type = "rust"
                if facts.cargo_toml_path is None:
                    facts.cargo_toml_path = line

        state.notes.append("Key metadata files scanned")

    elif action.command == "head" and observation.success:
        joined_args = " ".join(action.args)

        # raw observation → structured facts → higher-level inference
        if "README.md" in joined_args or "README" in joined_args:
            facts.readme_attempted = True
            if observation.stdout.strip():
                facts.readme_preview = observation.stdout
                state.notes.append("README preview captured")
            else:
                state.notes.append("README exists but is empty")

        elif "pyproject.toml" in joined_args:
            facts.manifest_attempted = True
            facts.project_type = "python"
            if observation.stdout.strip():
                facts.manifest_preview = observation.stdout
                state.notes.append("pyproject.toml preview captured")
            else:
                state.notes.append("pyproject.toml exists but preview is empty")

        elif "requirements.txt" in joined_args:
            facts.manifest_attempted = True
            facts.project_type = "python"
            if observation.stdout.strip():
                facts.manifest_preview = observation.stdout
                state.notes.append("requirements.txt preview captured")
            else:
                state.notes.append("requirements.txt exists but preview is empty")

        elif "package.json" in joined_args:
            facts.manifest_attempted = True
            facts.project_type = "node"
            if observation.stdout.strip():
                facts.manifest_preview = observation.stdout
                state.notes.append("package.json preview captured")
            else:
                state.notes.append("package.json exists but preview is empty")

        elif "Cargo.toml" in joined_args:
            facts.manifest_attempted = True
            facts.project_type = "rust"
            if observation.stdout.strip():
                facts.manifest_preview = observation.stdout
                state.notes.append("Cargo.toml preview captured")
            else:
                state.notes.append("Cargo.toml exists but preview is empty")