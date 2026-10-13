from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from job_agent.integrations.gmail import (
    GmailAuthorizationRequiredError,
    GmailConfigurationError,
    GmailEmailSource,
    GmailIntegrationError,
    connect_gmail,
    get_connected_gmail_email,
    has_saved_gmail_token,
    is_gmail_connected,
    switch_gmail_account,
)
from job_agent.models.opportunity import UserDecision
from job_agent.models.preference import CandidatePreferenceProfile
from job_agent.services.agent_run_service import run_agent
from job_agent.services.ui_service import (
    add_supporting_material,
    finish_setup_and_run_agent,
    get_background_state,
    get_opportunity_detail,
    get_preferences,
    get_setup_completed,
    list_needs_review,
    list_reviewed,
    replace_resume,
    save_preferences,
    set_user_decision,
)
from job_agent.storage.database import initialize_database
from job_agent.ui.presenters import (
    decision_label,
    format_created_at,
    join_values,
    preference_label,
    priority_label,
    priority_tone,
    split_csv_values,
    support_label,
    support_tone,
)


APP_NAME = "AI Job Search Assistant"
NAV_ITEMS = ("Opportunities", "Background & Evidence", "Preferences")
WORK_MODE_OPTIONS = ("Remote", "Hybrid", "On-site")
EMPLOYMENT_TYPE_OPTIONS = (
    "Full-Time",
    "Part-Time",
    "Contract",
    "Internship",
    "Temporary",
)


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


CSS = """
<style>
:root {
  --ink: #14213d;
  --muted: #64748b;
  --line: #e5eaf2;
  --soft: #f6f8fc;
  --blue: #1769e0;
  --green-bg: #eaf8ef;
  --green: #18794e;
  --amber-bg: #fff6df;
  --amber: #9a6700;
  --gray-bg: #f1f4f8;
  --gray: #5b6577;
}
.block-container {padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1180px;}
[data-testid="stSidebar"] {border-right: 1px solid var(--line); background: #fbfcfe;}
[data-testid="stSidebar"] .block-container {padding-top: 1.6rem;}
h1, h2, h3 {color: var(--ink); letter-spacing: -0.02em;}
.small-muted {color: var(--muted); font-size: .92rem;}
.eyebrow {color: var(--blue); font-weight: 700; font-size: .78rem; text-transform: uppercase; letter-spacing: .08em;}
.card {border: 1px solid var(--line); border-radius: 14px; padding: 18px 20px; background: white; margin-bottom: 10px;}
.metric-card {border: 1px solid var(--line); border-radius: 12px; padding: 16px; background: #fff; min-height: 104px;}
.metric-label {font-size: .82rem; color: var(--muted); margin-bottom: 6px;}
.metric-value {font-size: 1.25rem; color: var(--ink); font-weight: 750;}
.pill {display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: .78rem; font-weight: 700;}
.pill-positive {background: var(--green-bg); color: var(--green);}
.pill-caution {background: var(--amber-bg); color: var(--amber);}
.pill-muted, .pill-neutral {background: var(--gray-bg); color: var(--gray);}
.source-quote {border-left: 3px solid #cbd5e1; background: #f8fafc; padding: 10px 12px; border-radius: 0 8px 8px 0; color: #334155; margin-top: 6px; white-space: pre-wrap;}
.evidence-card {border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px; margin: 9px 0; background: #fbfcfe;}
.empty-state {border: 1px solid var(--line); border-radius: 16px; padding: 50px 24px; text-align: center; background: #fff;}
.setup-shell {max-width: 760px; margin: 0 auto;}
.stepbar {display:flex; gap:8px; margin-bottom: 26px;}
.step {flex:1; padding:10px 12px; border-radius:10px; background:#f1f4f8; color:#64748b; text-align:center; font-size:.86rem; font-weight:650;}
.step-active {background:#e8f1ff; color:#1769e0;}
.step-done {background:#eaf8ef; color:#18794e;}
hr {border-color: var(--line)!important;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def _esc(value) -> str:
    return html.escape("" if value is None else str(value))


def _set_flash(kind: str, message: str) -> None:
    st.session_state["flash"] = (kind, message)


def _show_flash() -> None:
    flash = st.session_state.pop("flash", None)
    if not flash:
        return
    kind, message = flash
    getattr(st, kind, st.info)(message)


def _navigate(page: str, opportunity_id: str | None = None) -> None:
    st.session_state["page"] = page
    st.session_state["opportunity_id"] = opportunity_id
    st.rerun()


def _priority_pill(priority) -> str:
    tone = priority_tone(priority)
    return (
        f'<span class="pill pill-{tone}">'
        f'{_esc(priority_label(priority))}</span>'
    )


def _support_pill(level: str) -> str:
    tone = support_tone(level)
    return (
        f'<span class="pill pill-{tone}">'
        f'{_esc(support_label(level))}</span>'
    )


def _render_stepbar(active_macro: int) -> None:
    labels = ("1  Background", "2  Preferences", "3  Ready")
    parts = []
    for index, label in enumerate(labels, start=1):
        if index < active_macro:
            css_class = "step step-done"
        elif index == active_macro:
            css_class = "step step-active"
        else:
            css_class = "step"
        parts.append(f'<div class="{css_class}">{label}</div>')
    st.markdown(
        '<div class="stepbar">' + "".join(parts) + "</div>",
        unsafe_allow_html=True,
    )


def _current_onboarding_macro(stage: str) -> int:
    if stage in {"welcome", "resume", "supporting"}:
        return 1
    if stage == "preferences":
        return 2
    return 3


def _safe_gmail_connected() -> bool:
    try:
        return is_gmail_connected()
    except GmailConfigurationError as error:
        st.session_state["gmail_configuration_error"] = str(error)
        return False


def _safe_connected_gmail_email() -> str | None:
    try:
        return get_connected_gmail_email()
    except GmailIntegrationError:
        return None


def _connect_gmail_from_ui(*, change_account: bool = False) -> str | None:
    try:
        with st.spinner("Opening Google authorization..."):
            email_address = (
                switch_gmail_account()
                if change_account
                else connect_gmail()
            )
    except GmailIntegrationError as error:
        st.error(str(error))
        return None

    st.session_state.pop("gmail_recovery_required", None)
    st.session_state.pop("gmail_recovery_message", None)
    st.session_state.pop("gmail_configuration_error", None)
    return email_address


@st.dialog("Change Gmail account")
def _render_change_gmail_account_dialog() -> None:
    current_email = _safe_connected_gmail_email()
    st.write(
        "Your current Gmail connection will be replaced. Existing "
        "opportunities, preferences, and background materials will stay "
        "unchanged. Future Agent runs will read job-alert emails from the "
        "new Gmail account."
    )
    if current_email:
        st.markdown(f"**Current email:** {_esc(current_email)}")

    cancel_col, continue_col = st.columns(2)
    with cancel_col:
        if st.button("Cancel", use_container_width=True):
            st.session_state["show_change_gmail_dialog"] = False
            st.rerun()
    with continue_col:
        if st.button("Continue", type="primary", use_container_width=True):
            new_email = _connect_gmail_from_ui(change_account=True)
            if new_email:
                st.session_state["show_change_gmail_dialog"] = False
                _set_flash(
                    "success",
                    "Gmail account updated. Future Agent runs will use "
                    f"{new_email}.",
                )
                st.rerun()


def _render_gmail_recovery_banner() -> bool:
    recovery_required = bool(st.session_state.get("gmail_recovery_required"))
    connected = _safe_gmail_connected()
    if connected and not recovery_required:
        return True

    has_token = has_saved_gmail_token()
    if recovery_required or has_token:
        message = st.session_state.get(
            "gmail_recovery_message",
            "We couldn’t access Gmail. Reconnect Gmail to continue.",
        )
        action_label = "Reconnect Gmail"
    else:
        message = (
            "Gmail is not connected yet. Connect Gmail to import job-alert "
            "emails when you run the agent."
        )
        action_label = "Connect Gmail"

    st.warning(message)
    configuration_error = st.session_state.get("gmail_configuration_error")
    if configuration_error:
        st.caption(configuration_error)

    if st.button(action_label, key="gmail_recovery_action"):
        email_address = _connect_gmail_from_ui()
        if email_address:
            _set_flash(
                "success",
                f"Gmail connected successfully: {email_address}",
            )
            st.rerun()

    return False


def _run_agent_from_ui(*, first_setup: bool) -> None:
    status = st.status("Running Job Search Agent", expanded=True)
    checking_line = status.empty()
    processing_line = status.empty()
    complete_line = status.empty()

    checking_line.markdown("⏳ **Checking recent emails...**")
    processing_line.markdown("○ **Processing opportunities**")
    complete_line.markdown("○ **Complete**")

    progress_state = {
        "emails_found": None,
        "current": 0,
        "total": 0,
    }

    def on_progress(progress) -> None:
        phase = str(progress.phase)

        if phase == "FINDING_JOB_ALERTS":
            if progress.current is not None:
                progress_state["emails_found"] = progress.current
                email_word = "email" if progress.current == 1 else "emails"
                checking_line.markdown(
                    "✓ **Checking recent emails** — "
                    f"Found {progress.current} {email_word}"
                )
            else:
                checking_line.markdown("⏳ **Checking recent emails...**")
            return

        if phase == "ANALYZING_OPPORTUNITIES":
            if progress.current is not None:
                progress_state["current"] = progress.current
            if progress.total is not None:
                progress_state["total"] = progress.total

            current = progress_state["current"]
            total = progress_state["total"]
            if total:
                processing_line.markdown(
                    f"⏳ **Processing opportunity {current} / {total}**"
                )
            else:
                processing_line.markdown("⏳ **Processing opportunities...**")
            return

        if phase == "COMPLETE":
            current = progress.current or progress_state["current"]
            total = progress.total or progress_state["total"]
            if total:
                processing_line.markdown(
                    f"✓ **Processing opportunities** — {current} / {total}"
                )
            else:
                processing_line.markdown(
                    "✓ **Processing opportunities** — No new opportunities"
                )
            complete_line.markdown("✓ **Complete**")

    try:
        email_source = GmailEmailSource()
        if first_setup:
            result = finish_setup_and_run_agent(
                email_source=email_source,
                progress_callback=on_progress,
            )
        else:
            result = run_agent(
                email_source=email_source,
                progress_callback=on_progress,
            )
    except GmailAuthorizationRequiredError as error:
        status.update(
            label="Gmail access needs attention",
            state="error",
            expanded=False,
        )
        complete_line.markdown("✕ **Run stopped**")
        st.session_state["gmail_recovery_required"] = True
        st.session_state["gmail_recovery_message"] = str(error)
        if first_setup and get_setup_completed():
            st.session_state["page"] = "Opportunities"
            st.session_state["opportunity_id"] = None
        st.rerun()
    except Exception as error:
        status.update(
            label="Agent run could not complete",
            state="error",
            expanded=True,
        )
        complete_line.markdown("✕ **Run stopped**")
        status.write(str(error))
        if first_setup and get_setup_completed():
            _set_flash(
                "warning",
                "Setup was saved, but the first Agent Run did not complete. "
                "You can run it again from Opportunities.",
            )
            st.session_state["page"] = "Opportunities"
            st.session_state["opportunity_id"] = None
            st.rerun()
        return

    status.update(label="Agent run complete", state="complete", expanded=False)
    st.session_state.pop("gmail_recovery_required", None)
    st.session_state.pop("gmail_recovery_message", None)
    _set_flash(
        "success",
        f"Agent run complete. Added {len(result.new_opportunities)} new "
        "opportunities.",
    )
    st.session_state["page"] = "Opportunities"
    st.session_state["opportunity_id"] = None
    st.rerun()


def _render_onboarding() -> None:
    stage = st.session_state.setdefault("onboarding_stage", "welcome")
    background = get_background_state()

    st.markdown('<div class="setup-shell">', unsafe_allow_html=True)
    st.markdown(f"## {APP_NAME}")
    if stage != "welcome":
        _render_stepbar(_current_onboarding_macro(stage))

    if stage == "welcome":
        st.markdown("### Welcome")
        st.write(
            "Set up your background and optional job preferences once, then "
            "run the agent to find and analyze opportunities."
        )
        st.markdown(
            """
            <div class="card">
              <strong>What you’ll do</strong><br><br>
              1. Upload your background<br>
              2. Set optional preferences<br>
              3. Connect Gmail<br>
              4. Run the agent and review opportunities
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Start Setup", type="primary", use_container_width=True):
            st.session_state["onboarding_stage"] = "resume"
            st.rerun()

    elif stage == "resume":
        st.markdown("### Upload Your Resume")
        st.caption("Upload your resume in Markdown (.md) format.")

        if background.current_resume is not None:
            st.success(f"Current resume: {background.current_resume.filename}")

        upload = st.file_uploader(
            "Resume (.md)",
            type=["md"],
            key="onboarding_resume_upload",
            label_visibility="collapsed",
        )
        if upload is not None:
            if st.button("Upload Resume", type="primary", use_container_width=True):
                try:
                    with st.spinner("Processing your resume..."):
                        replace_resume(filename=upload.name, content=upload.getvalue())
                except Exception as error:
                    st.error(f"Resume upload failed. {error}")
                else:
                    st.session_state["onboarding_stage"] = "supporting"
                    st.rerun()

        if background.current_resume is not None:
            if st.button("Continue", use_container_width=True):
                st.session_state["onboarding_stage"] = "supporting"
                st.rerun()

    elif stage == "supporting":
        st.markdown("### Add Supporting Materials")
        st.caption(
            "Optional. Add .md documents such as project writeups, technical "
            "notes, or other relevant materials."
        )

        background = get_background_state()
        for source in background.supporting_materials:
            st.markdown(
                f'<div class="card"><strong>{_esc(source.filename)}</strong>'
                '<br><span class="small-muted">Added and ready for future runs</span></div>',
                unsafe_allow_html=True,
            )

        support_upload_version = st.session_state.setdefault(
            "onboarding_support_upload_version", 0
        )
        support = st.file_uploader(
            "Supporting material (.md)",
            type=["md"],
            key=f"onboarding_support_upload_{support_upload_version}",
            label_visibility="collapsed",
        )
        if support is not None and st.button(
            "Add Supporting Material",
            use_container_width=True,
        ):
            try:
                with st.spinner("Processing supporting material..."):
                    add_supporting_material(
                        filename=support.name,
                        content=support.getvalue(),
                    )
            except Exception as error:
                st.error(f"Supporting material upload failed. {error}")
            else:
                st.session_state["onboarding_support_upload_version"] = (
                    support_upload_version + 1
                )
                st.rerun()

        if st.button("Continue to Preferences", type="primary", use_container_width=True):
            st.session_state["onboarding_stage"] = "preferences"
            st.rerun()

    elif stage == "preferences":
        st.markdown("### Set Your Preferences")
        st.caption("All preferences are optional. You can update them later.")
        _render_preferences_form(onboarding=True)

    else:
        st.markdown("### Ready to run")
        st.write("Your background and preferences have been saved.")
        background = get_background_state()
        preferences = get_preferences()
        st.markdown(
            f"""
            <div class="card">
              <strong>Background & Evidence</strong><br>
              <span class="small-muted">Resume: {_esc(background.current_resume.filename if background.current_resume else 'Not uploaded')} · {_esc(len(background.supporting_materials))} supporting material(s)</span>
              <br><br>
              <strong>Preferences</strong><br>
              <span class="small-muted">Saved for future Agent runs</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("#### Email connection")
        gmail_connected = _safe_gmail_connected()
        if gmail_connected:
            current_email = _safe_connected_gmail_email()
            if current_email:
                st.success(f"Gmail connected: {current_email}")
            else:
                st.success(
                    "Gmail connected. The agent can read job-alert emails when you run it."
                )
            if st.button(
                "Change Gmail account",
                key="onboarding_change_gmail",
                use_container_width=True,
            ):
                new_email = _connect_gmail_from_ui(change_account=True)
                if new_email:
                    st.rerun()
        else:
            st.info(
                "Connect Gmail once. Normal daily use will run in the background "
                "without showing a connection status."
            )
            configuration_error = st.session_state.get("gmail_configuration_error")
            if configuration_error:
                st.caption(configuration_error)
            if st.button(
                "Connect Gmail",
                key="onboarding_connect_gmail",
                use_container_width=True,
            ):
                if _connect_gmail_from_ui():
                    st.rerun()

        st.caption(
            "Your settings and Gmail authorization are stored locally. "
            "You can update background and preferences later."
        )
        if st.button(
            "Finish Setup & Run Agent",
            type="primary",
            use_container_width=True,
            disabled=not gmail_connected,
        ):
            _run_agent_from_ui(first_setup=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _sidebar() -> str:
    with st.sidebar:
        st.markdown(f"### {APP_NAME}")
        st.caption("Local personal tool")
        current = st.session_state.get("page", "Opportunities")
        if current not in NAV_ITEMS:
            current = "Opportunities"
        selected = st.radio(
            "Navigation",
            NAV_ITEMS,
            index=NAV_ITEMS.index(current),
            label_visibility="collapsed",
        )
        if selected != current:
            st.session_state["page"] = selected
            st.session_state["opportunity_id"] = None
            st.rerun()
        st.markdown("---")
        st.caption("Runs locally · Your data stays on this machine")
    return selected


def _render_opportunity_row(item, *, prefix: str) -> None:
    with st.container(border=True):
        left, middle, right = st.columns([5.2, 2.2, 1.4])
        with left:
            if st.button(
                item.title,
                key=f"{prefix}_{item.opportunity_id}",
                use_container_width=False,
            ):
                _navigate("Opportunities", item.opportunity_id)
            meta = item.company
            if item.location:
                meta += f" · {item.location}"
            st.caption(meta)
        with middle:
            st.markdown(_priority_pill(item.pursuit_priority), unsafe_allow_html=True)
            st.caption(
                f"Fit {item.requirement_fit_score:.0f}% · "
                f"{preference_label(item.preference_matched_count, item.preference_configured_count)}"
            )
        with right:
            if item.user_decision is not None:
                st.markdown(f"**{decision_label(item.user_decision)}**")
            created = format_created_at(item.created_at)
            if created:
                st.caption(created)


def _render_opportunities() -> None:
    detail_id = st.session_state.get("opportunity_id")
    if detail_id:
        _render_job_detail(detail_id)
        return

    needs = list_needs_review()
    reviewed = list_reviewed()

    header_left, header_run, header_menu = st.columns([6, 1.4, 0.45])
    with header_left:
        st.title("Opportunities")
        st.caption("Find and analyze job opportunities from your email.")
    with header_run:
        st.write("")
        st.write("")
        gmail_ready = _safe_gmail_connected() and not bool(
            st.session_state.get("gmail_recovery_required")
        )
        if st.button(
            "Run Agent",
            type="primary",
            use_container_width=True,
            disabled=not gmail_ready,
        ):
            _run_agent_from_ui(first_setup=False)
    with header_menu:
        st.write("")
        st.write("")
        with st.popover("⋯"):
            st.caption("Agent settings")
            if st.button(
                "Change Gmail account",
                key="open_change_gmail_account",
                use_container_width=True,
            ):
                st.session_state["show_change_gmail_dialog"] = True

    if st.session_state.get("show_change_gmail_dialog"):
        _render_change_gmail_account_dialog()

    if not gmail_ready:
        _render_gmail_recovery_banner()

    needs_tab, reviewed_tab = st.tabs(
        [f"Needs Review ({len(needs)})", f"Reviewed ({len(reviewed)})"]
    )

    with needs_tab:
        if not needs:
            st.markdown(
                """
                <div class="empty-state">
                  <div style="font-size:42px">⌕</div>
                  <h3>No opportunities yet</h3>
                  <div class="small-muted">Run the agent to find and analyze jobs from your email.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for item in needs:
                _render_opportunity_row(item, prefix="needs")

    with reviewed_tab:
        filter_label = st.radio(
            "Reviewed filter",
            ("All", "Pursuing", "Saved", "Passed"),
            horizontal=True,
            label_visibility="collapsed",
        )
        decision_map = {
            "Pursuing": UserDecision.PURSUE_NOW,
            "Saved": UserDecision.SAVE_FOR_LATER,
            "Passed": UserDecision.PASS,
        }
        filtered = (
            reviewed
            if filter_label == "All"
            else list_reviewed(decision=decision_map[filter_label])
        )
        if not filtered:
            st.info("No reviewed opportunities in this category yet.")
        for item in filtered:
            _render_opportunity_row(item, prefix=f"reviewed_{filter_label}")


def _render_decision_buttons(opportunity_id: str, current) -> None:
    st.caption("Your decision")
    pursue_col, save_col, pass_col = st.columns(3)
    actions = (
        (pursue_col, "Pursue", UserDecision.PURSUE_NOW),
        (save_col, "Save for later", UserDecision.SAVE_FOR_LATER),
        (pass_col, "Pass", UserDecision.PASS),
    )
    for column, label, decision in actions:
        with column:
            is_current = current == decision
            button_label = f"✓ {label}" if is_current else label
            if st.button(
                button_label,
                key=f"decision_{opportunity_id}_{decision.value}",
                type="primary" if is_current else "secondary",
                use_container_width=True,
            ):
                set_user_decision(opportunity_id, decision)
                _set_flash("success", f"Decision saved: {decision_label(decision)}")
                st.rerun()


def _render_job_detail(opportunity_id: str) -> None:
    try:
        detail = get_opportunity_detail(opportunity_id)
    except KeyError:
        _set_flash("error", "That opportunity could not be found.")
        _navigate("Opportunities", None)
        return

    opportunity = detail.opportunity
    if st.button("← Back to Opportunities"):
        _navigate("Opportunities", None)

    top_left, top_right = st.columns([6, 1.4])
    with top_left:
        st.title(opportunity.title)
        meta = opportunity.company
        if opportunity.location:
            meta += f" · {opportunity.location}"
        st.caption(meta)
    with top_right:
        st.write("")
        st.markdown(_priority_pill(opportunity.pursuit_priority), unsafe_allow_html=True)

    _show_flash()
    _render_decision_buttons(opportunity_id, opportunity.user_decision)
    st.write("")

    overview_tab, analysis_tab = st.tabs(["Overview", "Requirement Analysis"])

    with overview_tab:
        st.subheader("Job Overview")
        attrs = opportunity.job_attributes
        values = (
            ("Location", attrs.location or opportunity.location),
            ("Work Mode", attrs.work_mode),
            ("Employment Type", attrs.employment_type),
            ("Industry", attrs.industry),
            ("Company Size", attrs.company_size),
        )
        columns = st.columns(3)
        for index, (label, value) in enumerate(values):
            with columns[index % 3]:
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">{_esc(label)}</div>'
                    f'<div class="metric-value" style="font-size:1rem">{_esc(value or "Not provided")}</div></div>',
                    unsafe_allow_html=True,
                )
                st.write("")

        st.link_button("Open Original Posting", opportunity.posting_url)
        with st.expander("Job Description", expanded=False):
            st.markdown(
                f'<div class="card" style="white-space:pre-wrap">{_esc(opportunity.jd_text)}</div>',
                unsafe_allow_html=True,
            )

    with analysis_tab:
        st.markdown("### Pursuit Priority")
        st.markdown(_priority_pill(opportunity.pursuit_priority), unsafe_allow_html=True)
        st.write("")

        fit_col, pref_col = st.columns(2)
        with fit_col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Requirement Fit</div>'
                f'<div class="metric-value">{opportunity.requirement_fit_score:.0f}%</div>'
                f'<div class="small-muted">Based on {len(detail.requirements)} job requirements</div></div>',
                unsafe_allow_html=True,
            )
        with pref_col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Preferences</div>'
                f'<div class="metric-value">{_esc(preference_label(detail.preference_matched_count, detail.preference_configured_count))}</div>'
                '<div class="small-muted">Based on preferences configured when this job was analyzed</div></div>',
                unsafe_allow_html=True,
            )

        st.write("")
        summary_left, summary_right = st.columns(2)
        with summary_left:
            st.markdown("#### Strong Matches")
            if opportunity.strong_matches:
                for match in opportunity.strong_matches:
                    st.markdown(f"- {match}")
            else:
                st.caption("No strong matches were summarized.")
        with summary_right:
            st.markdown("#### Main Gaps")
            if opportunity.main_gaps:
                for gap in opportunity.main_gaps:
                    st.markdown(f"- {gap}")
            else:
                st.caption("No main gaps were summarized.")

        st.markdown("### All Requirements")
        for requirement in detail.requirements:
            title = f"{support_label(requirement.support_level)} · {requirement.requirement}"
            with st.expander(title, expanded=False):
                st.markdown(_support_pill(requirement.support_level), unsafe_allow_html=True)
                if requirement.requirement_level:
                    st.caption(
                        f"{requirement.requirement_level.replace('_', ' ').title()} · "
                        f"{requirement.category.replace('_', ' ').title()}"
                    )
                st.markdown("**Match Reason**")
                st.write(requirement.match_reason)
                st.markdown("**Supporting Evidence**")
                if not requirement.evidence:
                    st.caption("No grounded evidence was found for this requirement.")
                for evidence in requirement.evidence:
                    st.markdown(
                        f'<div class="evidence-card"><strong>{_esc(evidence.claim)}</strong>'
                        f'<br><span class="small-muted">Source: {_esc(evidence.source_document)}</span>'
                        f'<div class="source-quote">{_esc(evidence.source_text)}</div></div>',
                        unsafe_allow_html=True,
                    )


def _render_background() -> None:
    st.title("Background & Evidence")
    st.caption("Update your background materials. Changes apply to future Agent runs only.")
    _show_flash()

    background = get_background_state()
    st.subheader("Resume")
    if background.current_resume is None:
        st.info("No managed resume is currently uploaded.")
    else:
        st.markdown(
            f'<div class="card"><strong>{_esc(background.current_resume.filename)}</strong>'
            '<br><span class="small-muted">Current resume used for future matching</span></div>',
            unsafe_allow_html=True,
        )

    resume_upload_version = st.session_state.setdefault(
        "background_resume_upload_version", 0
    )
    resume = st.file_uploader(
        "Replace Resume (.md)",
        type=["md"],
        key=f"background_resume_upload_{resume_upload_version}",
    )
    if resume is not None and st.button("Replace Resume", type="primary"):
        try:
            with st.spinner("Processing replacement resume..."):
                replace_resume(filename=resume.name, content=resume.getvalue())
        except Exception as error:
            st.error(
                "Resume replacement failed. Your current resume has not been "
                f"changed. {error}"
            )
        else:
            st.session_state["background_resume_upload_version"] = (
                resume_upload_version + 1
            )
            _set_flash("success", "Resume replaced successfully.")
            st.rerun()

    st.markdown("---")
    st.subheader("Supporting Materials")
    background = get_background_state()
    if not background.supporting_materials:
        st.caption("No supporting materials added yet.")
    for source in background.supporting_materials:
        st.markdown(
            f'<div class="card"><strong>{_esc(source.filename)}</strong>'
            '<br><span class="small-muted">Active for future matching</span></div>',
            unsafe_allow_html=True,
        )

    support_upload_version = st.session_state.setdefault(
        "background_support_upload_version", 0
    )
    support = st.file_uploader(
        "Add Supporting Material (.md)",
        type=["md"],
        key=f"background_support_upload_{support_upload_version}",
    )
    if support is not None and st.button("Add Supporting Material"):
        try:
            with st.spinner("Processing supporting material..."):
                add_supporting_material(
                    filename=support.name,
                    content=support.getvalue(),
                )
        except Exception as error:
            st.error(f"Supporting material upload failed. {error}")
        else:
            st.session_state["background_support_upload_version"] = (
                support_upload_version + 1
            )
            _set_flash("success", "Supporting material added.")
            st.rerun()

    st.info(
        "Background changes affect future Agent runs only. Existing Opportunity "
        "analyses are not recalculated."
    )


def _render_preferences_form(*, onboarding: bool) -> None:
    current = get_preferences()
    with st.form("preferences_form"):
        location = st.text_input(
            "Location (optional)",
            value=join_values(current.preferred_locations),
            placeholder="San Francisco, CA, Remote",
            help="Separate multiple accepted values with commas.",
        )
        work_modes = st.multiselect(
            "Work Mode (optional)",
            WORK_MODE_OPTIONS,
            default=[v for v in WORK_MODE_OPTIONS if v in current.accepted_work_modes],
        )
        industry = st.text_input(
            "Industry (optional)",
            value=join_values(current.preferred_industries),
            placeholder="AI / Machine Learning, Software",
            help="Separate multiple accepted values with commas.",
        )
        company_size = st.text_input(
            "Company Size (optional)",
            value=join_values(current.preferred_company_sizes),
            placeholder="100 - 1,000",
            help="Use the labels you want to match from job postings; separate multiple values with commas.",
        )
        employment_types = st.multiselect(
            "Employment Type (optional)",
            EMPLOYMENT_TYPE_OPTIONS,
            default=[
                v
                for v in EMPLOYMENT_TYPE_OPTIONS
                if v in current.accepted_employment_types
            ],
        )
        submitted = st.form_submit_button(
            "Save Preferences" if not onboarding else "Save & Continue",
            type="primary",
            use_container_width=onboarding,
        )

    if submitted:
        profile = CandidatePreferenceProfile(
            preferred_locations=split_csv_values(location),
            accepted_work_modes=set(work_modes),
            accepted_employment_types=set(employment_types),
            minimum_compensation=None,
            preferred_industries=split_csv_values(industry),
            preferred_company_sizes=split_csv_values(company_size),
        )
        save_preferences(profile)
        if onboarding:
            st.session_state["onboarding_stage"] = "ready"
            st.rerun()
        else:
            _set_flash("success", "Preferences saved.")
            st.rerun()


def _render_preferences() -> None:
    st.title("Preferences")
    st.caption("Update your job-search preferences. All fields are optional.")
    _show_flash()
    _render_preferences_form(onboarding=False)
    st.info(
        "Preference changes apply to future Agent runs only. Existing analyses "
        "are not recalculated."
    )


def main() -> None:
    initialize_database()
    if not get_setup_completed():
        _render_onboarding()
        return

    st.session_state.setdefault("page", "Opportunities")
    _sidebar()
    _show_flash()

    page = st.session_state.get("page", "Opportunities")
    if page == "Background & Evidence":
        _render_background()
    elif page == "Preferences":
        _render_preferences()
    else:
        _render_opportunities()


if __name__ == "__main__":
    main()
