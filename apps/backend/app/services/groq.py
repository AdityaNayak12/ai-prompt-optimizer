import json
import time

from groq import AsyncGroq

from app.config import settings
from app.schemas.contract import (
    OptimizeMetrics,
    OptimizeRequest,
    OptimizeResponse,
    OptimizationResult,
)


class GroqService:
    def __init__(self):
        # The AsyncGroq client will pick up GROQ_API_KEY from the environment or settings.
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def optimize_prompt(self, request: OptimizeRequest) -> OptimizeResponse:
        start_time = time.perf_counter()

        mode = request.optimization_mode or "balanced"

        # Determine base system prompt based on the optimization mode
        if mode == "save_tokens":
            base_prompt = (
                "You are a prompt compression engine.\n\n"
                "Your goal is to achieve the same user intent using the fewest possible tokens.\n\n"
                "Rules:\n"
                "* Remove redundant words.\n"
                "* Remove unnecessary context.\n"
                "* Remove filler language.\n"
                "* Prefer short instructions.\n"
                "* Preserve intent.\n"
                "* If the prompt is already efficient, return it unchanged.\n"
                "* Never expand the prompt unless expansion is required for task success.\n\n"
                "Return only the optimized prompt."
            )
        elif mode == "max_quality":
            base_prompt = (
                "You are an expert Prompt Engineer specializing in maximizing LLM capabilities.\n"
                "Analyze the user's raw prompt and rewrite it to make it extremely effective. "
                "Optimize for the absolute best output quality, even if it significantly increases the token count.\n\n"
                "Apply best-practice techniques: specify an expert persona/role, add detailed structural context, "
                "define comprehensive constraints/rules, request step-by-step reasoning where applicable, "
                "provide detailed formatting instructions, and include few-shot examples if necessary.\n\n"
                f"Requirements based on user inputs:\n"
                f"- Tone: {request.tone}\n"
                f"- Detail Level: detailed\n"
            )
            if request.target_audience:
                base_prompt += f"- Target Audience: {request.target_audience}\n"
        else:  # balanced
            base_prompt = (
                "You are an expert Prompt Engineer specializing in maximizing LLM capabilities while maintaining token efficiency.\n"
                "Analyze the user's raw prompt and rewrite it to make it highly effective by balancing quality improvements and token usage.\n\n"
                "Apply best-practice techniques: specify an expert persona/role, add structural context, "
                "define clear constraints/rules, request step-by-step reasoning where applicable, and "
                "provide explicit formatting instructions. Avoid excessive wordiness or redundant details that do not add value.\n\n"
                f"Requirements based on user inputs:\n"
                f"- Tone: {request.tone}\n"
                f"- Detail Level: {request.detail_level or 'balanced'}\n"
            )
            if request.target_audience:
                base_prompt += f"- Target Audience: {request.target_audience}\n"

        # Append quality rating instruction and JSON schema formatting
        system_prompt = base_prompt + (
            "\n\nIn addition, evaluate the quality of both the original prompt and the optimized prompt on a scale of 1 to 100.\n"
            "You MUST output your response strictly as a JSON object with the following schema:\n"
            "{\n"
            '  "optimized_prompt": "The optimized or compressed prompt content.",\n'
            '  "explanation": "A bulleted markdown list explaining each improvement or compression made and why.",\n'
            '  "original_quality_score": <number from 1 to 100 reflecting the estimated quality/effectiveness of the original prompt>,\n'
            '  "optimized_quality_score": <number from 1 to 100 reflecting the estimated quality/effectiveness of the optimized prompt>\n'
            "}\n"
            "Do not include any pre-text or post-text. Return only the JSON object."
        )

        user_content = f'Raw Prompt to Optimize: \n"""\n{request.prompt}\n"""'

        def estimate_tokens(text: str) -> int:
            return max(1, len(text) // 4)

        original_tokens = estimate_tokens(request.prompt)

        async def call_groq(prompt_system: str, prompt_user: str) -> str:
            response = await self.client.chat.completions.create(
                model=request.groq_model or "llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": prompt_system},
                    {"role": "user", "content": prompt_user},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            return response.choices[0].message.content or ""

        # Fetch optimized response once
        content = await call_groq(system_prompt, user_content)
        if not content:
            raise ValueError("Empty response received from Groq API")

        # Parse fields directly
        data = json.loads(content)
        optimized_prompt = str(data.get("optimized_prompt", "")).strip()
        explanation = str(data.get("explanation", "")).strip()

        try:
            original_quality_score = float(data.get("original_quality_score", 50.0))
        except (ValueError, TypeError):
            original_quality_score = 50.0

        try:
            optimized_quality_score = float(data.get("optimized_quality_score", 50.0))
        except (ValueError, TypeError):
            optimized_quality_score = 50.0

        optimized_tokens = estimate_tokens(optimized_prompt)
        token_delta = optimized_tokens - original_tokens
        if original_tokens > 0:
            token_savings_percent = round(((original_tokens - optimized_tokens) / original_tokens) * 100, 2)
        else:
            token_savings_percent = 0.0

        efficiency_score_original = round(original_quality_score / original_tokens, 4)
        efficiency_score_optimized = round(optimized_quality_score / optimized_tokens, 4)

        # Check acceptance
        if mode == "save_tokens" and optimized_tokens > original_tokens:
            optimization_accepted = False
            status = "Rejected"
            recommendation = "Use Original Prompt"
            pct_inc = round(((optimized_tokens - original_tokens) / original_tokens) * 100)
            reason = f"{pct_inc}% token increase"
            # Fallback to original
            optimized_prompt = request.prompt
            optimized_tokens = original_tokens
            token_delta = 0
            token_savings_percent = 0.0
            efficiency_score_optimized = efficiency_score_original
        elif efficiency_score_optimized < efficiency_score_original:
            optimization_accepted = False
            status = "Rejected"
            recommendation = "Use Original Prompt"
            if optimized_tokens > original_tokens:
                pct_inc = round(((optimized_tokens - original_tokens) / original_tokens) * 100)
                reason = f"{pct_inc}% token increase"
            else:
                reason = "Optimized prompt has lower token efficiency."
        else:
            optimization_accepted = True
            status = "Accepted"
            recommendation = "Use Optimized Prompt"
            reason = None

        processing_time_ms = (time.perf_counter() - start_time) * 1000

        metrics = OptimizeMetrics(
            tokens_before=original_tokens,
            tokens_after=optimized_tokens,
            processing_time_ms=round(processing_time_ms, 2),
        )

        opt_result = OptimizationResult(
            originalTokens=original_tokens,
            optimizedTokens=optimized_tokens,
            tokenDelta=token_delta,
            tokenSavingsPercent=token_savings_percent,
            optimizationAccepted=optimization_accepted,
            optimizationMode=mode,
            status=status,
            reason=reason,
            recommendation=recommendation,
            efficiencyScoreOriginal=efficiency_score_original,
            efficiencyScoreOptimized=efficiency_score_optimized,
        )

        return OptimizeResponse(
            raw_prompt=request.prompt,
            optimized_prompt=optimized_prompt,
            explanation=explanation,
            metrics=metrics,
            optimizationResult=opt_result,
        )


# Dependency injection helper
async def get_groq_service() -> GroqService:
    return GroqService()

