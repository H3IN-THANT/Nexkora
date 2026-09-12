from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    role: str
    task: str
    constraints: tuple[str, ...]
    output_format: str
    missing_information: str

    def build_system_prompt(self) -> str:
        constraints = "\n".join(
            f"- {item}"
            for item in self.constraints
        )

        return f"""
<role>
{self.role}
</role>

<constraints>
{constraints}
</constraints>

<output_format>
{self.output_format}
</output_format>

<missing_information>
{self.missing_information}
</missing_information>
""".strip()

    def build_user_prompt(self, context: str) -> str:
        return f"""
<task>
{self.task}
</task>

<context>
{context}
</context>
""".strip()