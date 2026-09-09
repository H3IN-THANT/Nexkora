import os

from google import genai


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

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_response(
        self,
        user_input: str,
        system_instruction: str,
    ) -> str:
        """
        Send a structured prompt to Gemini.

        The system instruction controls assistant behavior,
        while user_input contains the task-specific user content.
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