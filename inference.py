from __future__ import annotations

import os
import sys
import json
from typing import Dict, List, Tuple, Optional

from openai import OpenAI

from env.environment import Action, WorkplaceEnv
from tasks.graders import grade_context_switching, grade_crisis_management, grade_prioritization


def _heuristic_policy(obs: Dict, state: Dict) -> Tuple[str, str, float]:
    remaining = [t for t in state["tasks"] if t not in state["completed"]]
    if not remaining:
        return "meeting", "Wrapping up and documenting next steps.", 0.7

    if "email" in remaining:
        return "email", "Send email early to meet the deadline and unblock stakeholders.", 0.85
    if "bug" in remaining:
        if state.get("interruption") or state["urgency"].get("bug", 0) >= 3:
            return "bug", "Prioritize the outage bug to restore service quickly.", 0.82
        return "bug", "Fix the bug next based on urgency and impact.", 0.8
    return "meeting", "Schedule the meeting after urgent deliverables are handled.", 0.78


def _llm_policy(client: OpenAI, obs: Dict, state: Dict, model: str) -> Tuple[str, str, float | None]:
    prompt = {
        "allowed_actions": ["email", "bug", "meeting"],
        "observation": obs,
        "state": state,
        "instruction": (
            "Choose the next action and provide a brief reason and calibrated confidence. "
            "Return ONLY valid JSON: {\"action\": \"email|bug|meeting\", \"reason\": \"...\", \"confidence\": 0.0-1.0}."
        ),
    }

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a reliable workplace agent. Output only JSON."},
            {"role": "user", "content": json.dumps(prompt)},
        ],
        temperature=0,
    )
    content = (resp.choices[0].message.content or "").strip()
    data = json.loads(content)
    action = str(data.get("action", "")).strip().lower()
    reason = str(data.get("reason", "")).strip()
    conf = data.get("confidence", None)
    try:
        conf_f = float(conf) if conf is not None else None
    except Exception:
        conf_f = None
    return action, reason, conf_f


def _bool_str(v: bool) -> str:
    return "true" if v else "false"


def _fmt_rewards(rewards: List[float]) -> str:
    return ",".join(f"{r:.2f}" for r in rewards)


def _run_episode(
    *,
    task_name: str,
    env_name: str,
    model_name: str,
    client: Optional[OpenAI],
) -> None:
    env = WorkplaceEnv()
    actions: List[str] = []
    rewards: List[float] = []
    success = True
    last_error: Optional[str] = None
    steps = 0

    print(f"[START] task={task_name} env={env_name} model={model_name}")

    try:
        obs = env.reset()
        done = False
        step_n = 1

        while not done and step_n <= env.max_steps:
            st = env.state()
            obs_dict = obs.model_dump()

            action_str = ""
            reason = ""
            confidence: float | None = None
            if client is not None:
                action_str, reason, confidence = _llm_policy(client, obs_dict, st, model_name)
            else:
                action_str, reason, confidence = _heuristic_policy(obs_dict, st)

            obs, r, done, _info = env.step(
                Action(action=action_str, reason=reason, confidence=confidence)
            )
            actions.append(action_str if action_str else "invalid")
            rewards.append(float(r))

            st_after = env.state()
            err = (st_after.get("last_action_error") or "").strip()
            last_error = err or None

            print(
                f"[STEP] step={step_n} action={action_str} reward={r:.2f} done={_bool_str(bool(done))} "
                f"error={(err if err else 'null')}"
            )

            steps = step_n
            step_n += 1

        final_state = env.state()
        if task_name == "prioritization":
            score = float(grade_prioritization(actions))
        elif task_name == "context_switching":
            score = float(grade_context_switching(actions))
        elif task_name == "crisis_management":
            score = float(grade_crisis_management(final_state))
        else:
            score = 0.5  # Default middle score

        # CRITICAL: Ensure score is STRICTLY in (0, 1) range, not [0, 1]
        # Per TASK.md: "Each task's score must be strictly between 0 and 1 (not 0.0 and not 1.0)"
        score = max(0.01, min(0.99, score))
        print(
            f"[END] success={_bool_str(True)} steps={steps} score={score:.2f} rewards={_fmt_rewards(rewards)}"
        )
    except Exception as exc:
        success = False
        msg = str(exc).replace("\n", " ").strip()
        if not msg:
            msg = type(exc).__name__
        last_error = msg
        # CRITICAL: Must output score strictly in (0, 1) range, never 0.00
        print(
            f"[END] success={_bool_str(False)} steps={steps} score={0.01:.2f} rewards={_fmt_rewards(rewards)}"
        )
    finally:
        try:
            env.close()
        except Exception:
            pass


if __name__ == "__main__":
    # MANDATORY: These variables must be defined per guide_rules.md
    # API_BASE_URL   The API endpoint for the LLM.
    # MODEL_NAME     The model identifier to use for inference.
    # HF_TOKEN       Your Hugging Face / API key.
    API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
    MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
    HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

    client: Optional[OpenAI] = None
    api_key = HF_TOKEN or OPENAI_API_KEY
    if api_key and API_BASE_URL:
        client = OpenAI(api_key=api_key, base_url=API_BASE_URL)

    ENV_NAME = "workplace-simulator"
    for task in ["prioritization", "context_switching", "crisis_management"]:
        _run_episode(task_name=task, env_name=ENV_NAME, model_name=MODEL_NAME, client=client)

