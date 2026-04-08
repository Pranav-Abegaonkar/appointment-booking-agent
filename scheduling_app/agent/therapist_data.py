"""
Talk Your Heart Out (TYHO) — Therapist directory and availability data.

This module provides the therapist roster, their specializations,
available time slots, and helper functions used by the voice agent
to match patients with the right therapist.
"""

THERAPISTS = [
    {
        "name": "Dr. Priya Menon",
        "title": "Clinical Psychologist",
        "qualifications": "M.Phil Clinical Psychology, RCI Licensed",
        "specializations": ["Anxiety", "Depression", "Trauma (EMDR)", "OCD"],
        "approaches": ["CBT", "EMDR", "ACT"],
        "languages": ["English", "Hindi"],
        "session_formats": ["Online", "In-Person (Tanjong Pagar)"],
        "client_types": ["Adults", "Older Adults"],
        "available_days": ["Monday", "Wednesday", "Friday", "Saturday"],
        "slots": {
            "Monday": ["10:00", "11:00", "14:00", "15:00", "18:00", "19:00"],
            "Wednesday": ["10:00", "11:00", "14:00", "15:00", "18:00", "19:00"],
            "Friday": ["10:00", "11:00", "14:00", "15:00"],
            "Saturday": ["10:00", "11:00", "12:00"],
        },
    },
    {
        "name": "Ms. Rachel Tan",
        "title": "Senior Counsellor",
        "qualifications": "Master's in Counselling Psychology",
        "specializations": ["Relationship Issues", "Self-Esteem", "Life Transitions", "Grief & Loss"],
        "approaches": ["Narrative Therapy", "Schema Therapy", "Person-Centred"],
        "languages": ["English", "Mandarin"],
        "session_formats": ["Online", "In-Person (City Hall)"],
        "client_types": ["Adults", "Couples"],
        "available_days": ["Tuesday", "Thursday", "Saturday"],
        "slots": {
            "Tuesday": ["11:00", "12:00", "16:00", "17:00", "18:00", "19:00"],
            "Thursday": ["11:00", "12:00", "16:00", "17:00", "18:00", "19:00"],
            "Saturday": ["10:00", "11:00", "12:00", "14:00", "15:00"],
        },
    },
    {
        "name": "Dr. Arun Kapoor",
        "title": "Clinical Psychologist",
        "qualifications": "Doctorate in Clinical Psychology",
        "specializations": ["Work-Related Stress", "Burnout", "Anxiety", "Identity Concerns"],
        "approaches": ["CBT", "DBT", "ACT"],
        "languages": ["English", "Hindi", "Tamil"],
        "session_formats": ["Online"],
        "client_types": ["Adults", "Older Adults"],
        "available_days": ["Monday", "Tuesday", "Thursday", "Friday"],
        "slots": {
            "Monday": ["18:00", "19:00", "20:00"],
            "Tuesday": ["18:00", "19:00", "20:00"],
            "Thursday": ["18:00", "19:00", "20:00"],
            "Friday": ["18:00", "19:00", "20:00"],
        },
    },
    {
        "name": "Ms. Sarah Lim",
        "title": "Counsellor & Play Therapist",
        "qualifications": "Master's in Counselling, Certified Play Therapist",
        "specializations": ["Children & Adolescents", "Family Therapy", "Behavioural Issues", "School Stress"],
        "approaches": ["Play Therapy", "CBT", "Family Systems Therapy"],
        "languages": ["English", "Mandarin", "Malay"],
        "session_formats": ["Online", "In-Person (Tanjong Pagar)"],
        "client_types": ["Children", "Adolescents", "Families"],
        "available_days": ["Monday", "Wednesday", "Thursday", "Saturday"],
        "slots": {
            "Monday": ["10:00", "11:00", "14:00", "15:00"],
            "Wednesday": ["10:00", "11:00", "14:00", "15:00", "16:00"],
            "Thursday": ["14:00", "15:00", "16:00"],
            "Saturday": ["10:00", "11:00", "12:00"],
        },
    },
    {
        "name": "Dr. Mei Ling Chen",
        "title": "Senior Clinical Psychologist",
        "qualifications": "Ph.D. Psychology, Board Certified",
        "specializations": ["Depression", "Trauma", "Grief & Loss", "Chronic Illness"],
        "approaches": ["EMDR", "Schema Therapy", "Narrative Therapy"],
        "languages": ["English", "Mandarin", "Cantonese"],
        "session_formats": ["Online", "In-Person (City Hall)"],
        "client_types": ["Adults", "Couples", "Older Adults"],
        "available_days": ["Tuesday", "Wednesday", "Friday", "Saturday"],
        "slots": {
            "Tuesday": ["10:00", "11:00", "14:00", "15:00"],
            "Wednesday": ["16:00", "17:00", "18:00", "19:00"],
            "Friday": ["10:00", "11:00", "16:00", "17:00", "18:00"],
            "Saturday": ["10:00", "11:00", "12:00", "14:00"],
        },
    },
]


SESSION_TYPES = ["Initial Consultation", "Follow-Up Session"]

SESSION_DURATION = {
    "Initial Consultation": "50 minutes",
    "Follow-Up Session": "50 minutes",
}


def list_all_therapists() -> list[dict]:
    """Return a summary of all therapists for the agent to present."""
    return [
        {
            "name": t["name"],
            "title": t["title"],
            "specializations": t["specializations"],
            "approaches": t["approaches"],
            "languages": t["languages"],
            "session_formats": t["session_formats"],
            "client_types": t["client_types"],
            "available_days": t["available_days"],
        }
        for t in THERAPISTS
    ]


def get_therapist_by_name(name: str) -> dict | None:
    """Look up a therapist by name (case-insensitive partial match)."""
    name_lower = name.lower()
    for t in THERAPISTS:
        if name_lower in t["name"].lower():
            return t
    return None


def get_available_slots(therapist_name: str, date: str) -> dict:
    """
    Given a therapist name and a date (YYYY-MM-DD), return available slots.
    """
    from datetime import datetime

    therapist = get_therapist_by_name(therapist_name)
    if not therapist:
        return {"available": False, "message": f"Therapist '{therapist_name}' not found."}

    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"available": False, "message": "Invalid date format. Use YYYY-MM-DD."}

    day_name = dt.strftime("%A")

    if day_name not in therapist["available_days"]:
        return {
            "therapist": therapist["name"],
            "date": date,
            "day": day_name,
            "available": False,
            "slots": [],
            "message": f"{therapist['name']} is not available on {day_name}s. They are available on: {', '.join(therapist['available_days'])}.",
        }

    slots = therapist["slots"].get(day_name, [])
    return {
        "therapist": therapist["name"],
        "date": date,
        "day": day_name,
        "available": len(slots) > 0,
        "slots": slots,
        "message": f"{therapist['name']} has {len(slots)} slot(s) on {day_name}, {date}.",
    }


def find_therapists_by_concern(concern: str) -> list[dict]:
    """Find therapists whose specializations match a patient's concern."""
    concern_lower = concern.lower()
    matches = []
    for t in THERAPISTS:
        for spec in t["specializations"]:
            if concern_lower in spec.lower() or spec.lower() in concern_lower:
                matches.append({
                    "name": t["name"],
                    "title": t["title"],
                    "specializations": t["specializations"],
                    "approaches": t["approaches"],
                    "session_formats": t["session_formats"],
                    "available_days": t["available_days"],
                })
                break
    return matches
