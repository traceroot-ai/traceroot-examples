import os
from typing import Any, TypedDict

import traceroot
from code_agent import create_code_agent
from dotenv import load_dotenv
from execution_agent import create_execution_agent
from langgraph.graph import END, StateGraph
from plan_agent import create_plan_agent
from summarize_agent import create_summarize_agent

load_dotenv()

logger = traceroot.get_logger()


class AgentState(TypedDict):
    query: str
    is_coding: bool
    plan: str
    code: str
    execution_result: dict[str, Any]
    response: str | None = None
    retry_count: int
    max_retries: int
    previous_attempts: list[dict[str, Any]]


class MultiAgentSystem:

    def __init__(self):
        self.plan_agent = create_plan_agent()
        self.code_agent = create_code_agent()
        self.execution_agent = create_execution_agent()
        self.summarize_agent = create_summarize_agent()

        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("planning", self.plan_node)
        workflow.add_node("coding", self.code_node)
        workflow.add_node("execute", self.execute_node)
        workflow.add_node("summarize", self.summarize_node)

        # Add edges
        workflow.set_entry_point("planning")
        workflow.add_conditional_edges("planning", self.should_code, {
            "code": "coding",
            "end": "summarize"
        })

        workflow.add_edge("coding", "execute")
        workflow.add_edge("execute", "summarize")
        workflow.add_conditional_edges("summarize", self.should_retry, {
            "retry": "planning",
            "end": END
        })

        return workflow.compile()

    def plan_node(self, state: AgentState) -> AgentState:
        # existing plan_node implementation unchanged
        ...

    def _build_retry_context(self, state: AgentState) -> str:
        """Build context string from previous failed attempts"""
        context_parts = []
        for i, attempt in enumerate(state["previous_attempts"], 1):
            context_parts.append(f"Attempt {i}:")
            context_parts.append(f"  Plan: {attempt.get('plan', 'N/A')}")
            context_parts.append(f"  Code: {attempt.get('code', 'N/A')}")
            if attempt.get('execution_result'):
                exec_result = attempt['execution_result']
                context_parts.append(
                    f"  Execution Success: {exec_result.get('success', False)}"
                )
                if not exec_result.get('success', False):
                    context_parts.append(
                        f"  Error: {exec_result.get('error', 'Unknown error')}"
                    )
                    context_parts.append(
                        f"  Stderr: {exec_result.get('stderr', '')}")
            if attempt.get('summary'):
                context_parts.append(
                    f"  Previous Summary: {attempt.get('summary', 'N/A')}"
                )
            context_parts.append("")
        return "\n".join(context_parts)

    def code_node(self, state: AgentState) -> AgentState:
        # Use full historical context for retry
        historical_context = self._build_retry_context(state)
        code = self.code_agent.generate_code(
            state["query"], state["plan"], historical_context
        )
        return {**state, "code": code}

    def execute_node(self, state: AgentState) -> AgentState:
        # Pass full historical context to execution
        historical_context = self._build_retry_context(state)
        execution_result = self.execution_agent.execute_code(
            state["query"], state["plan"], state["code"], historical_context
        )
        return {**state, "execution_result": execution_result}

    def summarize_node(self, state: AgentState) -> AgentState:
        if state["is_coding"]:
            # Provide full retry context for summary
            historical_context = self._build_retry_context(state)
            response = self.summarize_agent.create_summary(
                state["query"], state["plan"], state["code"],
                state["execution_result"], state["retry_count"], historical_context
            )
        else:
            response = state["response"]

        return {**state, "response": response}

    def should_code(self, state: AgentState) -> str:
        return "code" if state["is_coding"] else "end"

    @traceroot.trace()
    def should_retry(self, state: AgentState) -> str:
        """Determine if we should retry after a failed execution"""
        ...

    @traceroot.trace()
    def process_query(self, query: str) -> str:
        logger.info(f"Processing query: {query}")
        # remaining process_query implementation unchanged
        ...


def main():
    ...

if __name__ == "__main__":
    main()
