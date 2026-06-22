import json
import time

from groq import AsyncGroq

from app.config import settings
from app.schemas.contract import OptimizeMetrics, OptimizeRequest, OptimizeResponse


class GroqService:
    def __init__(self):
        # The AsyncGroq client will pick up GROQ_API_KEY from the environment or settings.
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def optimize_prompt(self, request: OptimizeRequest) -> OptimizeResponse:
        start_time = time.perf_counter()

        system_prompt = (
            "You are an expert Prompt Engineer specializing in maximizing LLM capabilities.\n"
            "Analyze the user's raw prompt and rewrite it to make it highly effective.\n"
            "Apply best-practice techniques: specify an expert persona/role, add structural context, "
            "define clear constraints/rules, request step-by-step reasoning where applicable, and "
            "provide explicit formatting instructions.\n\n"
            f"Requirements based on user inputs:\n"
            f"- Tone: {request.tone}\n"
            f"- Detail Level: {request.detail_level}\n"
        )
        if request.target_audience:
            system_prompt += f"- Target Audience: {request.target_audience}\n"

        system_prompt += (
            "\nYou MUST output your response strictly as a JSON object with the following schema:\n"
            "{\n"
            '  "optimized_prompt": "The complete, optimized prompt including formatting schemas, instructions, and structure.",\n'
            '  "explanation": "A bulleted markdown list explaining each improvement you made and why (e.g., - Specified developer persona...)"\n'
            "}\n"
            "Do not include any pre-text or post-text. Return only the JSON object."
        )

        user_content = f'Raw Prompt to Optimize: \n"""\n{request.prompt}\n"""'

        # Make the async API call using Groq JSON Mode
        response = await self.client.chat.completions.create(
            model=request.groq_model or "llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response received from Groq API")

        # Parse JSON response
        data = json.loads(content)
        optimized_prompt = data.get("optimized_prompt", "").strip()
        explanation = data.get("explanation", "").strip()

        # Rough token estimation (4 chars per token)
        tokens_before = len(request.prompt) // 4
        tokens_after = len(optimized_prompt) // 4

        processing_time_ms = (time.perf_counter() - start_time) * 1000

        metrics = OptimizeMetrics(
            tokens_before=max(1, tokens_before),
            tokens_after=max(1, tokens_after),
            processing_time_ms=round(processing_time_ms, 2),
        )

        return OptimizeResponse(
            raw_prompt=request.prompt,
            optimized_prompt=optimized_prompt,
            explanation=explanation,
            metrics=metrics,
        )


# Dependency injection helper
async def get_groq_service() -> GroqService:
    return GroqService()
