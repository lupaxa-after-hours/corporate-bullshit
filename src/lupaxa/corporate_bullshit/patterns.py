"""Sentence templates. Placeholders name vocabulary categories or specials.

Specials filled by the engine, not by vocabulary: ``{company}``, ``{percent}``.
Square brackets mark an optional clause. Nothing in a template is executed.
"""

from __future__ import annotations

PATTERNS: dict[str, dict[int, tuple[str, ...]]] = {
    "statement": {
        1: (
            "We should {verb} the {noun} so the team can {verb} {outcome}.",
            "The {noun} needs a {adjective} look before we {verb} the next step.",
            "Please {verb} the {noun} and {verb} {outcome} with {stakeholder}.",
        ),
        2: (
            "We must {verb} our {adjective} {noun} to {verb} {outcome}.",
            "By aligning {stakeholder} around the {noun}, we can {verb} {outcome}.",
            "Our {adjective} {noun} will {verb} {outcome} [ {expression}].",
        ),
        3: (
            ("We must {verb} our {phrase} [ {expression}] to {verb} {outcome} [ in service of {cliche}]."),
            ("It is imperative that we {verb} the {adjective} {noun} so {stakeholder} can {verb} {outcome} [ while we {verb} {management}]."),
            ("Going forward, we will {verb} our {phrase} [ through {technical}] in order to {verb} {outcome}."),
        ),
    },
    "phrase": {
        1: ("{adjective} {noun}", "{noun}"),
        2: ("{adjective} {noun}", "{stakeholder} view of the {noun}"),
        3: ("{adjective} {noun}", "{adjective} path to {outcome}"),
    },
    "meeting_agreement": {
        1: (
            "I agree with the direction, and we can {verb} the details later.",
            "Yes, that sounds right. Let's {verb} the {noun} and move on.",
        ),
        2: (
            ("I think we're broadly aligned on the {noun}, but we should circle back with {stakeholder} before committing to the next phase."),
            ("I'm supportive. We should {verb} the {adjective} {noun} and keep {stakeholder} in the loop."),
        ),
        3: (
            ("I am fully aligned, directionally, with the {phrase}, and I propose we {verb} {outcome} [ {expression}] before we {meeting}."),
            ("Broadly, yes. Let us {verb} our {adjective} {noun} and socialise {outcome} with {stakeholder} [ in honour of {cliche}]."),
        ),
    },
    "meeting_avoidance": {
        1: (
            "That is a fair question. I need to {verb} the {noun} before I answer it.",
            "Can we {verb} that after I have checked the {noun}?",
        ),
        2: (
            "I want to {verb} that properly once we {verb} the {adjective} {noun}.",
            "Let's {meeting} and {verb} the {noun} with {stakeholder} before we answer.",
        ),
        3: (
            ("I want to honour the question by a plan to {verb} it through the {phrase} [ {expression}] rather than answering it in the room."),
            ("The responsible path is to {verb} the {adjective} {noun} with {stakeholder} before we commit a position on {outcome}."),
        ),
    },
    "meeting_deflection": {
        1: (
            "That one sits with {stakeholder}. They can {verb} the {noun}.",
            "I think {stakeholder} can {verb} this more cleanly.",
        ),
        2: (
            "This sits more naturally with {stakeholder}, who can {verb} the {adjective} {noun}.",
            "I'll ask {stakeholder} to {verb} the {noun} so we stay in our lane.",
        ),
        3: (
            ("Ownership of the {phrase} clearly resides with {stakeholder}, who can {verb} {outcome} [ {expression}]."),
            ("In the interest of {noun}, {stakeholder} should {verb} this while we {verb} the wider {management}."),
        ),
    },
    "meeting_followup": {
        1: (
            "Let's set up a short follow-up to {verb} the {noun}.",
            "We should {verb} this in a smaller group and report back.",
        ),
        2: (
            "Let's take this offline and schedule time to {verb} the {adjective} {noun}.",
            "I'll book a working session so we can {verb} {outcome} with {stakeholder}.",
        ),
        3: (
            ("I propose a follow-up forum to {verb} the {phrase} and {verb} {outcome} [ before we {meeting}]."),
            ("We should spin up a focused session [ {expression}] so {stakeholder} can {verb} the {adjective} {noun}."),
        ),
    },
    "meeting_strategy": {
        1: (
            "If we {verb} the {noun}, the rest of the plan gets easier.",
            "The useful move is to {verb} {outcome} and keep the {noun} simple.",
        ),
        2: (
            "If we {verb} our {adjective} {noun}, we can unlock {outcome}.",
            "Strategically, we should {verb} the {noun} so {stakeholder} see {outcome}.",
        ),
        3: (
            ("Strategically, we must {verb} the {phrase} [ {expression}] so that {stakeholder} experience {outcome}."),
            ("The play is to {verb} our {adjective} {noun} through {management} and {verb} {outcome} [ in keeping with {cliche}]."),
        ),
    },
    "meeting_objection": {
        1: (
            "I'm not sure we should {verb} that until the {noun} is clearer.",
            "I have a concern. Can we {verb} the {noun} before we agree?",
        ),
        2: (
            ("I'm not sure we're ready to {verb} that until the {noun} has been discussed with {stakeholder}."),
            "I'd challenge the pace. We should {verb} the {adjective} {noun} first.",
        ),
        3: (
            ("I have a directional concern: we should not {verb} the {phrase} until {stakeholder} can {verb} {outcome}."),
            ("I'm hesitant. The {adjective} {noun} is not yet socialised [ {expression}], so {outcome} would be premature."),
        ),
    },
    "meeting_summary": {
        1: (
            "So, we will {verb} the {noun} and {verb} {outcome} afterwards.",
            "To summarise, {stakeholder} will {verb} the {noun}.",
        ),
        2: (
            ("So, to summarise, we are going to {verb} the {adjective} {noun} and revisit {outcome} later."),
            "The short version is that {stakeholder} will {verb} the {noun} [ {expression}].",
        ),
        3: (
            ("Summarising the summary, we will {verb} our {phrase} [ {expression}] and {verb} {outcome} with {stakeholder}."),
            ("Net-net, we will {verb} the {adjective} {noun} so we can {verb} {outcome} [ in the spirit of {cliche}]."),
        ),
    },
    "excuse_deadline": {
        1: (
            "The date slipped because we had to {verb} the {noun} again.",
            "We need a little more time to {verb} the {noun} properly.",
        ),
        2: (
            ("Due to evolving {adjective} dependencies, we've had to {verb} our delivery expectations to stay aligned with the {noun}."),
            "An upstream change means we must {verb} the {project} before the date can hold.",
        ),
        3: (
            ("Due to evolving {adjective} dependencies [ {expression}], we've had to {verb} our delivery expectations to maintain alignment with {outcome}."),
            ("The {project} encountered {excuse}, so the committed date has been moved in favour of {outcome}."),
        ),
    },
    "excuse_budget": {
        1: (
            "The {financial} no longer covers the {noun}, so the timing has to change.",
            "We need to {verb} the numbers before we can {verb} the {noun}.",
        ),
        2: (
            ("The {financial} is now tied to a {adjective} review, so we need to {verb} spend before we proceed with the {noun}."),
            "A funding check means we should {verb} the {noun} rather than start it.",
        ),
        3: (
            ("The {financial} now has to {verb} {outcome}, which requires us to {verb} the {phrase} [ {expression}]."),
            ("Pending a {adjective} investment review, the {noun} is paused so we can {verb} {outcome} for {stakeholder}."),
        ),
    },
    "excuse_technical": {
        1: (
            "We hit a snag in the {technical} and need to {verb} it before continuing.",
            "The {technical} needs a fix, so the {noun} is waiting.",
        ),
        2: (
            ("A constraint in the {technical} means we have to {verb} the {adjective} {noun} before delivery can continue."),
            "The {technical} surfaced {excuse}, so the team is working to {verb} it.",
        ),
        3: (
            ("The {technical} introduced {excuse}, requiring us to {verb} the {phrase} [ before we can {verb} {outcome}]."),
            ("Until we {verb} the {technical} [ {expression}], the {adjective} {noun} remains in a holding pattern."),
        ),
    },
    "excuse_meeting": {
        1: (
            "The meeting moved, so we could not {verb} the {noun} with everyone there.",
            "We ran out of time to {verb} the {noun} and will pick it up next time.",
        ),
        2: (
            ("The forum was rescheduled, which delayed our chance to {verb} the {adjective} {noun} with {stakeholder}."),
            "Without the right people in the room we could not {verb} {outcome}.",
        ),
        3: (
            ("The alignment forum was resequenced, so {stakeholder} have not yet been able to {verb} the {phrase}."),
            ("A cadence clash [ {expression}] prevented us from a plan to {verb} the {adjective} {noun} in the agreed window."),
        ),
    },
    "excuse_report": {
        1: (
            "The {noun} is still being checked, so I don't want to send a wrong version.",
            "I need to {verb} one figure in the {noun} before it goes out.",
        ),
        2: (
            ("The {noun} is with {stakeholder} for a {adjective} review, so the issue date has moved."),
            "We are still trying to {verb} the commentary so the {noun} tells one story.",
        ),
        3: (
            ("The {noun} is undergoing a {adjective} narrative review so we can {verb} {outcome} [ {expression}]."),
            ("Issuing the {noun} now would get ahead of {stakeholder}, who still need to {verb} the {phrase}."),
        ),
    },
    "excuse_project": {
        1: (
            "The {project} changed, so the {noun} needs another pass.",
            "A dependency on the {project} means we cannot {verb} this yet.",
        ),
        2: (
            "The {project} picked up {excuse}, and we have had to {verb} the {adjective} {noun}.",
            "Until the {project} is stable we should not {verb} {outcome}.",
        ),
        3: (
            "The {project} is absorbing {excuse}, which has forced us to {verb} the {phrase}.",
            ("Cross-workstream {excuse} [ {expression}] means the {noun} cannot yet {verb} {outcome}."),
        ),
    },
    "excuse_performance": {
        1: (
            "The result is behind where we wanted, and we are working to {verb} the {noun}.",
            "We did not hit the figure. The next step is to {verb} the {noun}.",
        ),
        2: (
            ("Performance against the {noun} is below the plan, so we are going to {verb} the approach with {stakeholder}."),
            ("The numbers need context. We should {verb} the {adjective} {noun} before drawing a conclusion."),
        ),
        3: (
            ("The {kpi} is tracking shy of the aspirational range, so we will {verb} the {phrase} [ {expression}]."),
            ("Rather than treat the variance as final, we will {verb} {outcome} through a {adjective} recovery narrative."),
        ),
    },
    "excuse_communication": {
        1: (
            "The note didn't reach everyone, so the {noun} was not picked up.",
            "I should have been clearer. I'll {verb} the {noun} again today.",
        ),
        2: (
            "The update did not land with {stakeholder}, which delayed the {noun}.",
            "A gap in the handover meant we had to {verb} the {adjective} {noun} late.",
        ),
        3: (
            ("A breakdown in stakeholder communication [ {expression}] meant the {phrase} did not {verb} {outcome} in time."),
            ("The message architecture failed to {verb} {outcome}, so {stakeholder} were not carrying the same {noun}."),
        ),
    },
    "strategy_objective": {
        1: (
            "{verb} the {noun} so the team can {verb} {outcome}.",
            "Make the {noun} {adjective} enough that {stakeholder} can use it.",
        ),
        2: (
            "{verb} {adjective} {noun} across the team.",
            "Enable {stakeholder} to {verb} {outcome} through the {noun}.",
        ),
        3: (
            "{verb} enterprise-facing {phrase} in pursuit of {outcome}.",
            ("Institutionalise a {adjective} {noun} that lets {stakeholder} {verb} {outcome} [ {expression}]."),
        ),
    },
    "strategy_rationale": {
        1: (
            "This keeps the work understandable and helps us {verb} {outcome}.",
            "Without it, the {noun} stays harder than it needs to be.",
        ),
        2: (
            ("This enables {adjective} progress across the {noun} and gives {stakeholder} a clearer path to {outcome}."),
            "It reduces friction in the {noun} so we can {verb} {outcome}.",
        ),
        3: (
            "This unlocks {adjective} synergies across the evolving {phrase} [ {expression}].",
            "It positions {stakeholder} to {verb} {outcome} while we {verb} the {management}.",
        ),
    },
    "strategy_kpi": {
        1: ("Increase {kpi} by {percent}%.",),
        2: ("Increase {kpi} by {percent}%.",),
        3: ("Increase {kpi} by {percent}% through {adjective} {noun}.",),
    },
    "mission_mission": {
        1: (
            "{company} exists to {verb} {outcome} for {stakeholder}.",
            "Our mission is to {verb} the {noun} and {verb} {outcome}.",
        ),
        2: (
            "{company} exists to {verb} {adjective} {outcome} for {stakeholder}.",
            "The mission of {company} is to {verb} a {adjective} {noun} so {outcome} follows.",
        ),
        3: (
            ("{company} exists to {verb} {outcome} by a promise to {verb} a {phrase} [ {expression}] for {stakeholder}."),
            "The mission of {company} is to {verb} a {adjective} {noun} in service of {outcome}.",
        ),
    },
    "mission_vision": {
        1: (
            "We picture {company} as a place where people can {verb} the {noun} without fuss.",
            "{company} is somewhere {stakeholder} can {verb} {outcome}.",
        ),
        2: (
            ("We envision {company} as a place in which {stakeholder} {verb} {adjective} {outcome} as a matter of course."),
            "A future where the {noun} is so {adjective} that {outcome} feels inevitable.",
        ),
        3: (
            ("We envision {company} as a place in which {stakeholder} inhabit a {phrase} and {verb} {outcome} [ {expression}]."),
            "A horizon where {adjective} {noun} and {outcome} are the same sentence.",
        ),
    },
    "mission_values": {
        1: (
            "{adjective} work: we {verb} the {noun} so {stakeholder} get {outcome}.",
            "Plain dealing: we {verb} the {noun} and say what it means.",
        ),
        2: (
            "{adjective} {noun}: we {verb} {outcome} with {stakeholder} watching.",
            "Stewardship of the {noun}: we {verb} it so {outcome} survives contact with a Tuesday.",
        ),
        3: (
            ("{adjective} {noun}: we {verb} {outcome} [ {expression}] even when {stakeholder} have not asked twice."),
            "Radical {noun}: a commitment to {verb} {outcome} through the {phrase}.",
        ),
    },
    "mission_purpose": {
        1: (
            "The purpose of {company} is to {verb} {outcome} for {stakeholder}.",
            "{company} is here to {verb} the {noun} and then stop talking about it.",
        ),
        2: (
            "{company} exists so {stakeholder} can {verb} {adjective} {outcome}.",
            "Our purpose is to {verb} the {noun} until {outcome} is boringly reliable.",
        ),
        3: (
            ("The purpose of {company} is to {verb} a {phrase} that can {verb} {outcome} for {stakeholder} [ {expression}]."),
            ("{company} pursues {outcome} by a decision to {verb} the {adjective} {noun} into something {stakeholder} can almost explain."),
        ),
    },
    "email_subject_update": {
        1: ("Update on the {noun}",),
        2: ("Update: how we {verb} our {adjective} {noun}",),
        3: ("Update: how we {verb} the {phrase} to {verb} {outcome}",),
    },
    "email_subject_followup": {
        1: ("Follow-up on the {noun}",),
        2: ("Follow-up: next step on the {adjective} {noun}",),
        3: ("Follow-up: how we {verb} {outcome} with {stakeholder}",),
    },
    "email_subject_apology": {
        1: ("Sorry about the {noun}",),
        2: ("Apology: delay to the {adjective} {noun}",),
        3: ("Apology: we will {verb} the {phrase}",),
    },
    "email_subject_announcement": {
        1: ("News: a change to the {noun}",),
        2: ("Announcement: we will {verb} the {adjective} {noun}",),
        3: ("Announcement: {company} will {verb} {outcome}",),
    },
    "email_subject_request": {
        1: ("Please {verb} the {noun}",),
        2: ("Request: {verb} the {adjective} {noun}",),
        3: ("Request: {stakeholder} to {verb} the {phrase}",),
    },
    "email_subject_escalation": {
        1: ("Help needed with the {noun}",),
        2: ("Escalation: the {adjective} {noun} needs a decision",),
        3: ("Escalation: {verb} {outcome} before the {noun} stalls",),
    },
    "email_subject_reminder": {
        1: ("Reminder: the {noun}",),
        2: ("Reminder: please {verb} the {adjective} {noun}",),
        3: ("Reminder: {stakeholder} still need to {verb} {outcome}",),
    },
    "email_body_update": {
        1: (
            "A short update: we are going to {verb} the {noun} so we can {verb} {outcome}.",
            "The {noun} is on track. The next step is to {verb} it with {stakeholder}.",
        ),
        2: (
            "We continue to {verb} the {adjective} {noun} so {stakeholder} can {verb} {outcome}.",
            ("Progress on the {noun} is steady [ {expression}]. We will {verb} the next step with {stakeholder}."),
        ),
        3: (
            ("We continue to {verb} our {phrase} [ {expression}] in order to {verb} {outcome} for {stakeholder}."),
            "The {adjective} {noun} continues to {verb} {outcome} [ through {management}].",
        ),
    },
    "email_body_followup": {
        1: (
            "Following up on the {noun}. Could you {verb} it when you have a moment?",
            "Just checking where the {noun} landed, so we can {verb} {outcome}.",
        ),
        2: (
            "I am following up so we can {verb} the {adjective} {noun} with {stakeholder}.",
            "A nudge on the {noun}: once we {verb} it, we can move toward {outcome}.",
        ),
        3: (
            ("Circling back, with intent, so we can {verb} the {phrase} and {verb} {outcome} [ {expression}]."),
            ("This is the follow-up that pretends not to be a chase: please {verb} the {adjective} {noun} for {stakeholder}."),
        ),
    },
    "email_body_apology": {
        1: (
            "Sorry the {noun} was late. We are working to {verb} it properly.",
            "Apologies for the confusion on the {noun}. I will {verb} a clearer version.",
        ),
        2: (
            ("Apologies that the {adjective} {noun} did not land as planned. We will {verb} {outcome} with {stakeholder}."),
            "I am sorry for the delay. The next version of the {noun} will {verb} the open points.",
        ),
        3: (
            ("Please accept an apology for the friction on the {phrase}. We are a plan to {verb} {outcome} [ {expression}] so {stakeholder} are not left guessing."),
            ("The {adjective} {noun} should have been clearer. We will {verb} it and {verb} the lesson into {management}."),
        ),
    },
    "email_body_announcement": {
        1: (
            "From today we will {verb} the {noun}. {stakeholder} will get a short note.",
            "A small change: the {noun} now has a named owner who will {verb} it.",
        ),
        2: (
            "We are announcing a {adjective} change to the {noun} so we can {verb} {outcome}.",
            "{stakeholder} should know that we will {verb} the {noun} [ {expression}].",
        ),
        3: (
            ("{company} will {verb} the {phrase} [ {expression}] in order to {verb} {outcome} for {stakeholder}."),
            ("Please cascade this: the {adjective} {noun} is now the path by which we {verb} {outcome}."),
        ),
    },
    "email_body_request": {
        1: (
            "Could you {verb} the {noun} and send it back to {stakeholder}?",
            "Please {verb} the {noun} this week so we can {verb} {outcome}.",
        ),
        2: (
            "Please {verb} the {adjective} {noun} and share it with {stakeholder}.",
            "I need a {adjective} view of the {noun} so we can {verb} {outcome}.",
        ),
        3: (
            ("Please {verb} the {phrase} [ {expression}] and return a view that helps us {verb} {outcome}."),
            ("Requesting that {stakeholder} {verb} the {adjective} {noun} before the next forum attempts to {verb} {outcome}."),
        ),
    },
    "email_body_escalation": {
        1: (
            "We are stuck on the {noun} and need help to {verb} it.",
            "The {noun} needs a decision from {stakeholder} before we can continue.",
        ),
        2: (
            ("I am escalating the {adjective} {noun} because we cannot {verb} {outcome} without a decision."),
            "The {noun} is blocked. {stakeholder} need to {verb} it so the team can move.",
        ),
        3: (
            ("Escalating the {phrase} [ {expression}]: without a decision we cannot {verb} {outcome} for {stakeholder}."),
            ("The {adjective} {noun} has exhausted the local options. We need {stakeholder} to {verb} it."),
        ),
    },
    "email_body_reminder": {
        1: (
            "A reminder to {verb} the {noun} before the next conversation.",
            "Gentle reminder: the {noun} is still open with {stakeholder}.",
        ),
        2: (
            "Reminding the group to {verb} the {adjective} {noun} so we protect {outcome}.",
            "The {noun} is still outstanding [ {expression}]. Please {verb} it.",
        ),
        3: (
            ("A strategically gentle reminder to {verb} the {phrase} before {stakeholder} {verb} {outcome} without us."),
            ("The {adjective} {noun} remains unresolved [ {expression}]. {stakeholder} are waiting to {verb} it."),
        ),
    },
    "document": {
        1: (
            ("The {noun} is in good enough shape to {verb}, provided {stakeholder} {verb} {outcome}."),
            "We recommend a {adjective} pass over the {noun} before the next step.",
        ),
        2: (
            ("The {adjective} {noun} gives {stakeholder} a practical way to {verb} {outcome} [ {expression}]."),
            ("Progress depends on our ability to {verb} the {noun} without adding another layer of {management}."),
        ),
        3: (
            ("The {phrase} [ {expression}] positions {stakeholder} to {verb} {outcome} while we still {verb} the {noun}."),
            ("In keeping with {cliche}, the {adjective} {noun} will {verb} {outcome} through {management}."),
        ),
    },
    "initiative": {
        1: (
            "{verb} the {noun} and tell {stakeholder} what changed.",
            "Give the {noun} an owner and a date.",
        ),
        2: (
            "{verb} the {adjective} {noun} with {stakeholder}.",
            "Stand up a short effort to {verb} {outcome} via the {noun}.",
        ),
        3: (
            "{verb} a {phrase} [ {expression}] so {stakeholder} can {verb} {outcome}.",
            "Launch a {adjective} workstream to {verb} the {noun} through {management}.",
        ),
    },
    "recommendation": {
        1: (
            "{verb} the {noun} this month and {verb} {outcome} in the open.",
            "Ask {stakeholder} to {verb} the {noun} before adding more scope.",
        ),
        2: (
            "{verb} the {adjective} {noun} and report {outcome} to {stakeholder}.",
            "Pause new work until we {verb} the {noun} [ {expression}].",
        ),
        3: (
            "{verb} the {phrase} [ {expression}] and only then {verb} {outcome}.",
            "Commission {stakeholder} to {verb} a {adjective} {noun} in service of {outcome}.",
        ),
    },
    "outcome_item": {
        1: ("{stakeholder} can {verb} {outcome}.",),
        2: ("{stakeholder} {verb} {outcome} through the {adjective} {noun}.",),
        3: (("{stakeholder} experience {outcome} [ {expression}] because the {phrase} is ready for us to {verb}."),),
    },
}
