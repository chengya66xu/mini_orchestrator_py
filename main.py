import argparse
from orchestrator.orchestrator import Orchestrator


def parse_args():
    parser = argparse.ArgumentParser(
        description="A lightweight terminal-first orchestration runtime"
    )
    parser.add_argument("--task", required=True, help="User task to execute")
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace directory for command execution"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=8,
        help="Maximum number of orchestration steps"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    orchestrator = Orchestrator(
        task=args.task,
        workspace=args.workspace,
        max_steps=args.max_steps
    )

    result = orchestrator.run()

    print("\n================ FINAL SUMMARY ================\n")
    print(result["final_summary"])
    print(f"\nTrace written to: {result['trace_path']}")


if __name__ == "__main__":
    main()