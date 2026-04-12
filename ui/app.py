from __future__ import annotations

import json
from datetime import datetime, timezone

import streamlit as st

from env.environment import Action, WorkplaceEnv, generate_kpi
from tasks.graders import grade_context_switching, grade_crisis_management, grade_prioritization

APP_BUILD = "2026-04-08.3"


def _ui_heuristic(state: dict) -> tuple[str, str, float]:
    pending = state.get("pending") or [t for t in state.get("tasks", []) if t not in state.get("completed", [])]
    if state.get("interruption") and "bug" in pending:
        return "bug", "Outage incident: prioritize the bug to restore service quickly.", 0.85
    if "email" in pending:
        return "email", "Deadline risk: send the email now and include a follow-up plan.", 0.85
    if "bug" in pending:
        return "bug", "Fix properly: root cause analysis + regression tests to prevent recurrence.", 0.8
    return "meeting", "Align with stakeholders after urgent work is complete.", 0.75


def _default_reason(action: str) -> str:
    if action == "email":
        return "Send email first to meet the deadline and align stakeholders."
    if action == "bug":
        return "Fix the bug now to restore service and reduce impact."
    return "Attend the meeting after urgent deliverables are handled."


def main() -> None:
    st.set_page_config(page_title="AI Workplace Failure Simulator", layout="centered")
    st.title("AI Workplace Failure Simulator")
    st.caption("Test if an agent survives a real job — not just tasks.")
    st.caption(f"Build: {APP_BUILD}")

    with st.sidebar:
        st.subheader("Scenario")
        role = st.selectbox(
            "Role",
            ["Software Engineer", "Customer Support", "Product Manager"],
            index=0,
        )
        mode = st.selectbox("Mode", ["normal", "stress"], index=0)
        st.divider()
        st.subheader("Controls")
        auto_run = st.toggle("Auto-run baseline agent", value=False)
        auto_steps = st.slider("Auto-run steps", 1, 6, 6, 1)

    if "env" not in st.session_state:
        st.session_state.env = WorkplaceEnv(role=role, mode=mode)
        st.session_state.obs = st.session_state.env.reset()
        st.session_state.actions = []
        st.session_state.rewards = []
        st.session_state.events = []
        st.session_state.errors = []
        st.session_state.confidences = []
        st.session_state.mistakes = []
        st.session_state.infos = []
        st.session_state.done = False

    env: WorkplaceEnv = st.session_state.env
    obs = st.session_state.obs
    state = env.state()
    if "pending" not in state:
        st.session_state.env = WorkplaceEnv(role=role, mode=mode)
        st.session_state.obs = st.session_state.env.reset()
        st.session_state.actions = []
        st.session_state.rewards = []
        st.session_state.events = []
        st.session_state.errors = []
        st.session_state.confidences = []
        st.session_state.mistakes = []
        st.session_state.infos = []
        st.session_state.done = False
        env = st.session_state.env
        obs = st.session_state.obs
        state = env.state()

    tab_play, tab_analytics, tab_about = st.tabs(["Play", "Analytics", "About"])

    with tab_play:
        kpi = generate_kpi(state)
        top1, top2, top3, top4, top5 = st.columns(5)
        top1.metric("Completed", kpi["tasks_completed"])
        top2.metric("Pending", len(state.get("pending", [])))
        top3.metric("Efficiency", kpi["efficiency"])
        top4.metric("Mood", state["mood"])
        total_score = sum(st.session_state.rewards) / max(1, len(st.session_state.rewards))
        top5.metric("Avg reward", f"{total_score:.2f}")

        st.progress(min(1.0, kpi["tasks_completed"] / 3))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Observation")
            st.write(obs.message)
            st.json(obs.model_dump())
        with col2:
            st.subheader("State")
            pending = state.get("pending")
            if pending is None:
                pending = [t for t in state.get("tasks", []) if t not in state.get("completed", [])]
            st.json(
                {
                    "time": state.get("time"),
                    "role": state.get("role"),
                    "mode": state.get("mode"),
                    "deadline_step": state.get("deadline_step"),
                    "pending": pending,
                    "completed": state.get("completed"),
                    "urgency": state.get("urgency"),
                    "interruption": state.get("interruption"),
                    "mood": state.get("mood"),
                    "last_action": state.get("last_action"),
                    "last_action_error": state.get("last_action_error"),
                    "last_confidence": state.get("last_confidence"),
                }
            )

        st.divider()
        st.subheader("Take an action")
        action = st.selectbox("Action", ["email", "bug", "meeting"], index=0)
        reason = st.text_area("Reason", value=_default_reason(action), height=80)
        confidence = st.slider(
            "Confidence (0–1)",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            step=0.05,
        )

        c1, c2, c3 = st.columns(3)
        do_step = c1.button("Step", type="primary", disabled=bool(st.session_state.done))
        do_reset = c2.button("Reset")
        do_autorun = c3.button("Auto-run", disabled=bool(st.session_state.done) or (not auto_run))

        if do_step:
            obs, r, done, info = env.step(Action(action=action, reason=reason, confidence=confidence))
            st.session_state.obs = obs
            st.session_state.actions.append(action)
            st.session_state.rewards.append(float(r))
            st.session_state.events.append(str(info.get("event", "normal")))
            st.session_state.errors.append(str(env.state().get("last_action_error") or "null"))
            st.session_state.confidences.append(float(confidence))
            st.session_state.mistakes.append(str(info.get("mistake") or "null"))
            st.session_state.infos.append(info)
            st.session_state.done = bool(done)
            st.toast(
                f"reward={r:.2f} event={info.get('event')} error={env.state().get('last_action_error') or 'null'}"
            )

        if do_autorun:
            n = 0
            while (not st.session_state.done) and n < int(auto_steps):
                st_now = env.state()
                a, rsn, conf = _ui_heuristic(st_now)
                obs, r, done, info = env.step(Action(action=a, reason=rsn, confidence=conf))
                st.session_state.obs = obs
                st.session_state.actions.append(a)
                st.session_state.rewards.append(float(r))
                st.session_state.events.append(str(info.get("event", "normal")))
                st.session_state.errors.append(str(env.state().get("last_action_error") or "null"))
                st.session_state.confidences.append(float(conf))
                st.session_state.mistakes.append(str(info.get("mistake") or "null"))
                st.session_state.infos.append(info)
                st.session_state.done = bool(done)
                n += 1
            st.rerun()

        if do_reset:
            st.session_state.env = WorkplaceEnv(role=role, mode=mode)
            st.session_state.obs = st.session_state.env.reset()
            st.session_state.actions = []
            st.session_state.rewards = []
            st.session_state.events = []
            st.session_state.errors = []
            st.session_state.confidences = []
            st.session_state.mistakes = []
            st.session_state.infos = []
            st.session_state.done = False
            st.rerun()

        st.divider()
        st.subheader("Episode timeline")
        actions = list(st.session_state.actions)
        rows = []
        for i in range(len(actions)):
            rows.append(
                {
                    "step": i + 1,
                    "action": actions[i],
                    "reward": round(float(st.session_state.rewards[i]), 2),
                    "event": st.session_state.events[i],
                    "error": st.session_state.errors[i],
                    "confidence": (
                        round(float(st.session_state.confidences[i]), 2)
                        if i < len(st.session_state.confidences)
                        else None
                    ),
                    "mistake": (
                        st.session_state.mistakes[i]
                        if i < len(st.session_state.mistakes)
                        else None
                    ),
                }
            )
        st.dataframe(rows, width="stretch", hide_index=True)

        if rows:
            st.line_chart(
                [{"step": r["step"], "reward": r["reward"]} for r in rows],
                x="step",
                y="reward",
                height=160,
            )

        st.subheader("Graders")
        st.json(
            {
                "easy": grade_prioritization(actions),
                "medium": grade_context_switching(actions),
                "hard": grade_crisis_management(env.state()),
            }
        )
        st.caption(f"Performance status: {generate_kpi(env.state())['status']}")

        with st.expander("Per-step debug (reward breakdown + multi-objective)"):
            for idx, info in enumerate(st.session_state.infos):
                st.markdown(f"**Step {idx + 1}**")
                st.json(info)

        st.subheader("Export")
        export = {
            "meta": {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "role": role,
                "mode": mode,
                "build": APP_BUILD,
            },
            "final_state": env.state(),
            "timeline": rows,
            "infos": st.session_state.infos,
        }
        st.download_button(
            "Download episode JSON",
            data=json.dumps(export, indent=2),
            file_name="episode_export.json",
            mime="application/json",
        )

    with tab_analytics:
        st.subheader("Analytics")
        st.write("This tab summarizes multi-objective signals and calibration indicators.")
        if not st.session_state.infos:
            st.info("Run a few steps to populate analytics.")
        else:
            blends = []
            emo = []
            te = []
            ts = []
            for i, info in enumerate(st.session_state.infos):
                mo = info.get("multi_objective") or {}
                blends.append({"step": i + 1, "blend": mo.get("blend")})
                emo.append({"step": i + 1, "emotional_score": mo.get("emotional_score")})
                te.append({"step": i + 1, "time_efficiency": mo.get("time_efficiency")})
                ts.append({"step": i + 1, "task_score": mo.get("task_score")})

            st.line_chart(blends, x="step", y="blend", height=140)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.line_chart(ts, x="step", y="task_score", height=140)
            with c2:
                st.line_chart(te, x="step", y="time_efficiency", height=140)
            with c3:
                st.line_chart(emo, x="step", y="emotional_score", height=140)

    with tab_about:
        st.subheader("About")
        st.write(
            "This environment evaluates workplace competence under dynamic constraints: "
            "prioritization, outages, deadlines, emotional stakeholders, memory, recovery, and calibrated confidence."
        )
        st.write("Key API methods: `reset()`, `step(Action)`, `state()`.")
        st.write("Scenarios: role-based expectations + optional stress mode.")


if __name__ == "__main__":
    main()

