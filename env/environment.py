from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple

from pydantic import BaseModel, Field


ALLOWED_ACTIONS = ["email", "bug", "meeting"]


class Observation(BaseModel):
    message: str
    time: int
    tasks: List[str]
    urgency: Dict[str, int]
    mood: str


class Action(BaseModel):
    action: str = Field(..., description="One of: email, bug, meeting")
    reason: str
    confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Optional calibrated confidence (0.0-1.0)"
    )


class Reward(BaseModel):
    score: float


def generate_kpi(state: dict) -> dict:
    completed = len(state["completed"])
    efficiency = completed / 3
    return {
        "tasks_completed": completed,
        "efficiency": round(efficiency, 2),
        "status": "Excellent" if efficiency > 0.8 else "Needs Improvement",
    }


@dataclass
class _Internal:
    step_idx: int
    state: dict


class WorkplaceEnv:
    max_steps: int = 6

    def __init__(
        self,
        *,
        role: Literal["Software Engineer", "Customer Support", "Product Manager"] = "Software Engineer",
        mode: Literal["normal", "stress"] = "normal",
    ):
        self._i: _Internal | None = None
        self._role = role
        self._mode = mode

    def reset(self) -> Observation:
        deadline_step = 3 if self._mode == "normal" else 2
        self._i = _Internal(
            step_idx=0,
            state={
                "time": 0,
                "tasks": ["email", "bug", "meeting"],
                "urgency": {"email": 3, "bug": 2, "meeting": 1},
                "completed": [],
                "pending": ["email", "bug", "meeting"],
                "mood": "normal",
                "interruption": False,
                "last_action": "",
                "last_action_error": "",
                "loop_count": 0,
                "role": self._role,
                "mode": self._mode,
                "deadline_step": deadline_step,
                "trap_active": True,
                "client_preference": "Client prefers quick replies.",
                "memory_test_step": 4 if self._mode == "normal" else 3,
                "needs_recovery": False,
                "mistake_type": "",
                "recovery_used": False,
                "last_confidence": None,
            },
        )
        return self._observe(event="normal")

    def close(self) -> None:
        self._i = None

    def state(self) -> dict:
        if self._i is None:
            _ = self.reset()
        assert self._i is not None
        pending = [t for t in self._i.state["tasks"] if t not in self._i.state["completed"]]
        self._i.state["pending"] = pending
        kpi = generate_kpi(self._i.state)
        return {
            "time": int(self._i.state["time"]),
            "tasks": list(self._i.state["tasks"]),
            "urgency": dict(self._i.state["urgency"]),
            "completed": list(self._i.state["completed"]),
            "pending": pending,
            "mood": str(self._i.state["mood"]),
            "interruption": bool(self._i.state["interruption"]),
            "last_action": str(self._i.state["last_action"]),
            "last_action_error": str(self._i.state.get("last_action_error", "")),
            "loop_count": int(self._i.state["loop_count"]),
            "role": str(self._i.state.get("role", "")),
            "mode": str(self._i.state.get("mode", "")),
            "deadline_step": int(self._i.state.get("deadline_step", 3)),
            "trap_active": bool(self._i.state.get("trap_active", False)),
            "client_preference": str(self._i.state.get("client_preference", "")),
            "memory_test_step": int(self._i.state.get("memory_test_step", 4)),
            "needs_recovery": bool(self._i.state.get("needs_recovery", False)),
            "mistake_type": str(self._i.state.get("mistake_type", "")),
            "recovery_used": bool(self._i.state.get("recovery_used", False)),
            "last_confidence": self._i.state.get("last_confidence"),
            "kpi": kpi,
        }

    def step(self, action: Action) -> Tuple[Observation, float, bool, dict]:
        if self._i is None:
            _ = self.reset()
        assert self._i is not None

        info = {"event": "normal", "step": self._i.step_idx}
        s = self._i.state
        s["last_action_error"] = ""
        info["reward_breakdown"] = {}
        info["mistake"] = None
        info["recovery"] = None

        is_interrupt = (self._mode == "normal" and self._i.step_idx == 2) or (
            self._mode == "stress" and self._i.step_idx in (1, 2)
        )
        if is_interrupt:
            s["interruption"] = True
            info["event"] = "interruption"
            s["urgency"]["bug"] = 3
            s["urgency"]["email"] = 2
            s["urgency"]["meeting"] = 1
        else:
            s["interruption"] = False

        angry_step = 3 if self._mode == "normal" else 2
        if self._i.step_idx == angry_step:
            s["mood"] = "angry_client"

        reward = 0.0
        rb = info["reward_breakdown"]

        act = (action.action or "").strip().lower()
        reason = (action.reason or "").strip()
        conf = action.confidence
        s["last_confidence"] = conf
        if act not in ALLOWED_ACTIONS:
            reward -= 0.5
            rb["invalid_action"] = -0.5
            s["last_action_error"] = "invalid_action"
            act = ""

        if act and act in s["completed"]:
            reward -= 0.15
            rb["already_completed"] = -0.15
            if not s["last_action_error"]:
                s["last_action_error"] = "already_completed"

        if not reason:
            reward -= 0.2
            rb["empty_reason"] = -0.2
            if not s["last_action_error"]:
                s["last_action_error"] = "empty_reason"

        if act and act == s["last_action"]:
            s["loop_count"] += 1
            reward -= 0.3
            rb["loop_detected"] = -0.3
            if not s["last_action_error"]:
                s["last_action_error"] = "loop_detected"
        else:
            s["loop_count"] = 0

        pending = [t for t in s["tasks"] if t not in s["completed"]]
        best_action = self._best_action(pending, s)

        if conf is not None and act:
            if conf >= 0.8 and act == best_action:
                reward += 0.08
                rb["confidence_correct_bonus"] = 0.08
            elif conf >= 0.8 and act != best_action:
                reward -= 0.12
                rb["confidence_wrong_penalty"] = -0.12

        if s["mood"] == "angry_client":
            if "apolog" in reason.lower() or "sorry" in reason.lower():
                s["mood"] = "recovered"
                reward += 0.3
                rb["emotional_bonus"] = 0.3

        if s.get("trap_active") and self._i.step_idx in (0, 1):
            if act == "email" and (
                "contradict" in reason.lower()
                or "despite" in reason.lower()
                or "urgency" in reason.lower()
                or "priority" in reason.lower()
            ):
                reward += 0.15
                rb["trap_detected_bonus"] = 0.15
                s["trap_active"] = False

        if act and act in s["tasks"] and act not in s["completed"]:
            s["completed"].append(act)
            reward += 0.4
            rb["task_completed"] = rb.get("task_completed", 0.0) + 0.4

            if self._respected_urgency(act, s):
                reward += 0.3
                rb["urgency_respected"] = 0.3
            else:
                s["needs_recovery"] = True
                s["mistake_type"] = "urgency_violated"
                info["mistake"] = "urgency_violated"

        if reason:
            tokens = reason.lower()
            if len(reason.split()) >= 3:
                reward += 0.12
                rb["reasoning_basic"] = 0.12
            if any(k in tokens for k in ["deadline", "due", "asap"]):
                reward += 0.06
                rb["reasoning_deadline"] = 0.06
            if any(k in tokens for k in ["outage", "incident", "server"]):
                reward += 0.06
                rb["reasoning_outage"] = 0.06
            if any(k in tokens for k in ["priority", "prioritize", "urgent", "urgency"]):
                reward += 0.04
                rb["reasoning_priority"] = 0.04
            if any(k in tokens for k in ["follow-up", "follow up", "update", "plan"]):
                reward += 0.04
                rb["reasoning_followup"] = 0.04
            if any(k in tokens for k in ["just because", "idk", "whatever", "random"]):
                reward -= 0.15
                rb["reasoning_low_quality"] = -0.15
                if not s["last_action_error"]:
                    s["last_action_error"] = "low_quality_reason"

        if self._i.step_idx == int(s.get("memory_test_step", 4)):
            if any(k in reason.lower() for k in ["quick", "fast", "prompt", "reply"]):
                reward += 0.3
                rb["memory_recall_bonus"] = 0.3
            else:
                reward -= 0.2
                rb["memory_recall_penalty"] = -0.2
                if not s["last_action_error"]:
                    s["last_action_error"] = "memory_forget"

        if act == "bug" and act not in s["completed"]:
            pass
        if act == "bug" and "quick fix" in reason.lower():
            reward -= 0.08
            rb["tradeoff_quick_fix_penalty"] = -0.08
        if act == "bug" and any(k in reason.lower() for k in ["proper", "root cause", "tests", "regression"]):
            reward += 0.08
            rb["tradeoff_quality_bonus"] = 0.08
            s["time"] = int(s["time"]) + 1

        if s.get("needs_recovery") and not s.get("recovery_used"):
            if any(k in reason.lower() for k in ["correct", "recover", "fix my mistake", "undo"]) and act == best_action:
                reward += 0.5
                rb["recovery_bonus"] = 0.5
                s["needs_recovery"] = False
                s["mistake_type"] = ""
                s["recovery_used"] = True
                info["recovery"] = "successful"
            elif self._i.step_idx >= 1:
                reward -= 0.1
                rb["recovery_ignored_penalty"] = -0.1

        deadline_step = int(s.get("deadline_step", 3))
        if self._i.step_idx >= deadline_step and "email" not in s["completed"]:
            reward -= 1.0
            rb["deadline_missed"] = -1.0
            info["event"] = "deadline_missed"
            s["needs_recovery"] = True
            s["mistake_type"] = "deadline_missed"
            info["mistake"] = info["mistake"] or "deadline_missed"
            if not s["last_action_error"]:
                s["last_action_error"] = "deadline_missed"

        s["time"] = int(s["time"]) + 1
        s["last_action"] = act
        for t in s["completed"]:
            s["urgency"][t] = 0
        s["pending"] = [t for t in s["tasks"] if t not in s["completed"]]

        task_score = min(1.0, len(s["completed"]) / 3)
        time_eff = max(0.0, 1.0 - (self._i.step_idx / max(1, self.max_steps - 1)))
        emotional = 1.0 if s["mood"] == "recovered" else (0.5 if s["mood"] == "normal" else 0.0)
        blended = (task_score * 0.5) + (time_eff * 0.2) + (emotional * 0.3)
        info["multi_objective"] = {
            "task_score": round(task_score, 2),
            "time_efficiency": round(time_eff, 2),
            "emotional_score": round(emotional, 2),
            "blend": round(blended, 2),
        }

        done = False
        if len(s["completed"]) == 3:
            done = True
        if self._i.step_idx >= (self.max_steps - 1):
            done = True

        reward = float(max(0.0, min(1.0, reward)))
        obs = self._observe(event=info["event"])

        self._i.step_idx += 1
        return obs, reward, done, info

    def _observe(self, event: str) -> Observation:
        assert self._i is not None
        s = self._i.state
        base = "You are an AI employee starting your workday."
        if self._i.step_idx == 0:
            msg = (
                f"{base} Today you are acting as a {s.get('role')}. "
                f"Client note: {s.get('client_preference')}\n"
                "Note from colleague: “Email is NOT urgent.” (Double-check urgency vs messages.)\n"
                "Prioritize tasks and explain why."
            )
        elif event == "interruption":
            msg = "🔥 Server outage! Customers are impacted. Bug must be prioritized now."
        elif event == "deadline_missed":
            msg = "Deadline missed: email follow-up was not sent in time."
        elif self._i.step_idx == int(s.get("memory_test_step", 4)):
            msg = "Reminder: the client had a preference earlier. What is it, and how will you honor it?"
        elif s["mood"] == "angry_client":
            msg = "Client is angry about delays. Respond professionally and consider an apology."
        elif s["mood"] == "recovered":
            msg = "Client has calmed down. Provide a clear follow-up plan."
        else:
            msg = "Continue your workday: choose the next task and justify your decision."

        return Observation(
            message=msg,
            time=int(s["time"]),
            tasks=list(s["tasks"]),
            urgency=dict(s["urgency"]),
            mood=str(s["mood"]),
        )

    @staticmethod
    def _respected_urgency(chosen: str, s: dict) -> bool:
        remaining = [t for t in s["tasks"] if t not in s["completed"]]
        if not remaining:
            return True
        max_u = max(s["urgency"].get(t, 0) for t in remaining)
        return s["urgency"].get(chosen, 0) >= max_u

    @staticmethod
    def _best_action(pending: List[str], s: dict) -> str:
        if s.get("interruption") and "bug" in pending:
            return "bug"
        if not pending:
            return "meeting"
        urg = s.get("urgency", {})
        return max(pending, key=lambda t: (urg.get(t, 0), t))

