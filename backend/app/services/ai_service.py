import os

from google import genai

from app.prompts.rag_qa import (
    SYSTEM_PROMPT as RAG_QA_SYSTEM_PROMPT,
    build_prompt as build_rag_qa_prompt,
)
from app.prompts.registry import get_prompt


class AIService:
    """Service responsible for communicating with Gemini."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        )

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    def generate_response(
        self,
        user_input: str,
        system_instruction: str,
    ) -> str:
        """
        Send a structured prompt to Gemini.

        The system instruction controls assistant behavior,
        while user_input contains the task-specific content.
        """

        interaction = self.client.interactions.create(
            model=self.model,
            system_instruction=system_instruction,
            input=user_input,
        )

        response_text = interaction.output_text

        if not response_text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response_text

    def generate_developer_response(
        self,
        mode: str,
        message: str,
    ) -> str:
        """Generate a response using a registered developer prompt."""

        system_prompt, prompt_builder = get_prompt(mode)

        user_prompt = prompt_builder(message)

        return self.generate_response(
            user_input=user_prompt,
            system_instruction=system_prompt,
        )

    def answer_document_question(
        self,
        question: str,
        context: str,
    ) -> str:
        """Answer a question using selected document context."""

        prompt = build_rag_qa_prompt(
            question=question,
            context=context,
        )

        return self.generate_response(
            user_input=prompt,
            system_instruction=RAG_QA_SYSTEM_PROMPT,
        )