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
        model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.2,
    )

    knowledge_sources = []

    def __init__(self):
        self.knowledge_files = []

        # Knowledge Configuration
        # Define base path to current file
        knowledge_base_path = Path(__file__).parent / "knowledge"

        # Prepare the knowledge base for the OSS Framework
        files = glob.glob(os.path.join(knowledge_base_path, "oss-docs/**/*.mdx"), recursive=True)

        for file in files:
            url = ""
            first_line = open(file).readline()
            if "URL:" in first_line:
                url = first_line.replace("URL:", "").strip()
            
            file_path = Path(file)
            category = file_path.parent.name
            # print(file_path)
            
            knowledge_source = TextFileKnowledgeSource(
                file_paths=[file_path],
                metadata={
                    "url": url,
                    "category": category,
                },
            )
            self.knowledge_sources.append(knowledge_source)

    @agent
    def crewai_expert_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["crewai_expert_agent"],
            knowledge_sources=self.knowledge_sources,
            knowledge_config=KnowledgeConfig(results_limit=5),
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
