from agency_swarm.agents import Agent


class DataManager(Agent):
    def __init__(self):
        super().__init__(
            name="Data Manager Agent",
            description="This agent collects extracted information and stores it in an appropriate data mode.",
            instructions="./instructions.md",
            tools=[],
            tools_folder="./tools",
            model="gpt-4o-mini",
            #model="groq/llama-3.2-90b-text-preview",
            temperature=0.1,
            max_prompt_tokens=25000,
        )
