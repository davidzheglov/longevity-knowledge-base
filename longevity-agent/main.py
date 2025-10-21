import asyncio
from agents import Agent, AgentBase, RunContextWrapper, Runner, trace, gen_trace_id

from context import RunContext
from tools.genome import build_gene_alias_map, normalize_gene

orchestrator = Agent(
    name="orchestrator",
    instructions=(
        "You are a longevity researcher. You use the tools given to you to respond to users. "
    ),
    tools=[normalize_gene],
)

async def main() -> None:
    gene_alias_map = build_gene_alias_map()
    context = RunContext(gene_alias_map=gene_alias_map)
    context = RunContextWrapper(context)

    user_request = input("Ask a question about longevity:\n")

    with trace("Longevity research"):
        result = await Runner.run(
            starting_agent=orchestrator,
            input=user_request,
            context=context.context,
        )
        print(f"\nResponse:\n{result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())