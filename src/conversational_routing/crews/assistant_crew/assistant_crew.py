import os
import glob
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.knowledge.knowledge_config import KnowledgeConfig
from pathlib import Path

# Define base path to current file
knowledge_base_path = Path(__file__).parent / "knowledge"

# Prepare the knowledge base for the OSS Framework
files = glob.glob(os.path.join(knowledge_base_path, "oss-docs/**/*.mdx"), recursive=True)
# Convert file strings to Path objects
file_paths = [Path(file) for file in files]

print("file_paths", file_paths)

oss_framework_kb = TextFileKnowledgeSource(
    file_paths=file_paths,
    metadata={
        "category": "CrewAI",
    },
)

llm = LLM(
    model="gpt-4o",
    temperature=0.1,
)

@CrewBase
class AssistantCrew:
    """Assistant Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def crewai_expert_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["crewai_expert_agent"],
            knowledge_sources=[oss_framework_kb],
            knowledge_config=KnowledgeConfig(results_limit=5, score_threshold=0.7),
            llm=llm,
        )

    @task
    def answer_crewai_questions_task(self) -> Task:
        return Task(
            config=self.tasks_config["answer_crewai_questions_task"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=False,
            memory=True,
        )
