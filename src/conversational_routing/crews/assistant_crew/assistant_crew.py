import os
import glob
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.knowledge.knowledge_config import KnowledgeConfig
from pathlib import Path

@CrewBase
class AssistantCrew:
    """Assistant Crew"""

    # Crew Files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # LLM Configuration
    llm = LLM(
        model="gpt-4o",
        temperature=0.1,
    )

    @agent
    def crewai_expert_agent(self) -> Agent:
        # Knowledge Configuration
        # Define base path to current file
        knowledge_base_path = Path(__file__).parent / "knowledge"
        print("Knowledge base path (lorenze):", knowledge_base_path)

        # Prepare the knowledge base for the OSS Framework
        files = glob.glob(os.path.join(knowledge_base_path, "oss-docs/**/*.mdx"), recursive=True)
        print("Files (lorenze):", files)
        # Convert file strings to Path objects
        knowledge_file_paths = [Path(file) for file in files]

        print("Knowledge paths (lorenze):", knowledge_file_paths)

        return Agent(
            config=self.agents_config["crewai_expert_agent"],
            knowledge_sources=[TextFileKnowledgeSource(
                file_paths=knowledge_file_paths,
                metadata={
                    "category": "CrewAI",
                },
            )],
            knowledge_config=KnowledgeConfig(results_limit=5, score_threshold=0.7),
            llm=self.llm,
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
            memory=True,
        )
