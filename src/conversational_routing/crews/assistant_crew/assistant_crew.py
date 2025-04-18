import os
import glob
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

# Define base path to current file
knowledge_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../knowledge"))

knowledge_enterprise_kb = CSVKnowledgeSource(
    file_paths=["enterprise_kb.csv"],
    metadata={
        "category": "Enterprise Platform",
    },
)

print(os.path.join(knowledge_base_path, "oss-docs/**/*.mdx"))

# Prepare the knowledge base for the OSS Framework
files = glob.glob(os.path.join(knowledge_base_path, "oss-docs/**/*.mdx"), recursive=True)
files = [os.path.relpath(file, knowledge_base_path) for file in files]

oss_framework_kb = TextFileKnowledgeSource(
    file_paths=files,
    metadata={
        "category": "CrewAI Open Source Framework",
    },
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
            knowledge_sources=[knowledge_enterprise_kb, oss_framework_kb],
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
            verbose=True,
        )
