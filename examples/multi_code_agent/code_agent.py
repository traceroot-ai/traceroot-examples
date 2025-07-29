import logging

logger = logging.getLogger(__name__)

class CodeAgent:
    def __init__(self, code_prompt, llm):
        self.code_prompt = code_prompt
        self.llm = llm

    def generate_code(self, query: str, plan: str, historical_context: str = "") -> str:
        formatted_prompt = self.code_prompt.format(
            query=query, plan=plan, historical_context=historical_context
        )
        logger.info(f"CODE AGENT prompt:\n{formatted_prompt}")

        chain = self.code_prompt | self.llm
        response = chain.invoke({
            "query": query,
            "plan": plan,
            "historical_context": historical_context,
        })
        code = response

        # Remove leading markdown fence if present
        if code.startswith("```"):
            # Strip the first fence line
            fence_end = code.find("\n")
            if fence_end != -1:
                code = code[fence_end + 1:]
            else:
                code = code.lstrip("`")

        # Remove trailing markdown fence if present
        if code.endswith("```"):
            code = code[:-3]

        code = code.strip()
        logger.info(f"Generated code cleaned:\n{code}")
        return code


def create_code_agent():
    # Example factory
    from traceroot_examples.multi_code_agent.code_agent import CodeAgent
    return CodeAgent()
