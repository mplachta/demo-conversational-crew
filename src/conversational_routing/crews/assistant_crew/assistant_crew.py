from crewai import Agent, Crew, Process, Task
from crewai.knowledge.knowledge_config import KnowledgeConfig
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.project import CrewBase, agent, crew, task

from conversational_routing.models.vertex import embedder_configuration, llm


@CrewBase
class AssistantCrew:
    """Assistant Crew"""

    # Crew Files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def benefits_expert_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["benefits_expert_agent"],
            knowledge_sources=[
                PDFKnowledgeSource(
                    file_paths=["freedom_benefits.pdf"],
                )
            ],
            knowledge_config=KnowledgeConfig(results_limit=5, score_threshold=0.7),
            embedder=embedder_configuration,
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
            embedder=embedder_configuration,
            verbose=False,
        )
