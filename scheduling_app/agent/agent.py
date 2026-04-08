import os
import logging
import json
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# VideoSDK Agents v1.0.4
from videosdk.agents import (
    Agent,
    AgentSession,
    Pipeline,
    WorkerJob,
    JobContext,
    RoomOptions,
    EOUConfig,
    InterruptConfig,
    function_tool,
    # MCPServerHTTP # Commenting as agent mcp is not working
)

# Plugins
from videosdk.plugins.google import GoogleLLM
from videosdk.plugins.cartesia import CartesiaTTS
from videosdk.plugins.silero import SileroVAD
from videosdk.plugins.turn_detector import TurnDetector, pre_download_model
from videosdk.plugins.rnnoise import RNNoise
from videosdk.plugins.deepgram import DeepgramSTT

# Local modules
from instructions import get_tyho_instructions
from therapist_data import (
    list_all_therapists,
    get_therapist_by_name,
    get_available_slots,
    find_therapists_by_concern,
    SESSION_TYPES,
    SESSION_DURATION,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

pre_download_model()

logger = logging.getLogger("tyho_scheduling_agent")

# ─── Appointment store — persisted to appointments.json ──────────────────────
APPOINTMENTS_FILE = os.path.join(os.path.dirname(__file__), "appointments.json")


def _load_appointments() -> tuple[list[dict], int]:
    """Load appointments from JSON file."""
    if os.path.exists(APPOINTMENTS_FILE):
        with open(APPOINTMENTS_FILE, "r") as f:
            data = json.load(f)
            appts = data.get("appointments", [])
            counter = data.get("counter", 1000)
            return appts, counter
    return [], 1000


def _save_appointments(appts: list[dict], counter: int):
    """Save appointments to JSON file."""
    with open(APPOINTMENTS_FILE, "w") as f:
        json.dump({"appointments": appts, "counter": counter}, f, indent=2)


appointments, appointment_counter = _load_appointments()


class VoiceAgent(Agent):
    def __init__(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        logger.info("[INIT] TYHO VoiceAgent initializing | date=%s", current_date)

        super().__init__(
            instructions=get_tyho_instructions(
                current_date=current_date,
                agent_name="Anushka",
            ),
            # Commenting as agent mcp is not working
            # mcp_servers=[
            #     MCPServerHTTP(
            #         endpoint_url="https://mcp.zapier.com/api/v1/connect",
            #         request_headers={
            #             "Authorization": f"Bearer {os.getenv('ZAPIER_MCP_API_KEY')}"
            #         },
            #         session_timeout=60
            #     )
            # ]
        )
        logger.info("[INIT] TYHO VoiceAgent ready")

    async def on_enter(self) -> None:
        logger.info("[SESSION] Agent entered — greeting patient")
        await self.session.say(
            "Hello! I'm Anushka from Talk Your Heart Out. "
            "I'm here to help you schedule a therapy appointment. "
            "How can I assist you today?"
        )

    async def on_exit(self) -> None:
        logger.info("[SESSION] Agent exiting — farewell")
        await self.session.say(
            "Thank you for reaching out to Talk Your Heart Out. "
            "We look forward to supporting you on your journey. Take care!"
        )

    # ─── Tools ───────────────────────────────────────────────────────────────

    @function_tool
    async def get_therapists(self) -> list:
        """
        Returns a list of all therapists at Talk Your Heart Out,
        including their specializations, approaches, languages,
        session formats, and available days.
        Call this when a patient asks who is available or wants to know
        about the therapists.
        """
        logger.info("[TOOL] get_therapists called")
        result = list_all_therapists()
        logger.info("[TOOL] get_therapists returned %d therapist(s)", len(result))
        return result

    @function_tool
    async def find_therapist_for_concern(self, concern: str) -> list:
        """
        Finds therapists whose specializations match a patient's concern.

        Args:
            concern: The issue the patient wants help with, e.g. "anxiety",
                     "relationship issues", "depression", "child behaviour".

        Returns a list of matching therapists with their details.
        Call this when the patient describes what they are going through
        so you can recommend the best-fit therapist.
        """
        logger.info("[TOOL] find_therapist_for_concern | concern=%s", concern)
        result = find_therapists_by_concern(concern)
        logger.info("[TOOL] find_therapist_for_concern returned %d match(es)", len(result))
        return result

    @function_tool
    async def check_availability(self, therapist_name: str, date: str) -> dict:
        """
        Returns available time slots for a specific therapist on a given date.

        Args:
            therapist_name: The therapist's name, e.g. "Dr. Priya Menon".
            date:           The date to check, formatted as YYYY-MM-DD.

        Returns a dict with therapist name, date, day, available (bool),
        slots (list of "HH:MM" strings), and a message.
        Always call this before offering specific times to the patient.
        """
        logger.info("[TOOL] check_availability | therapist=%s date=%s", therapist_name, date)
        result = get_available_slots(therapist_name, date)
        logger.info(
            "[TOOL] check_availability | available=%s slots=%s",
            result.get("available"), result.get("slots")
        )
        return result

    @function_tool
    async def book_appointment(
        self,
        patient_name: str,
        patient_email: str,
        patient_phone: str,
        therapist_name: str,
        date: str,
        time_slot: str,
        session_format: str,
        session_type: str,
        appointment_reason: str,
    ) -> dict:
        """
        Finalizes and saves a therapy appointment booking.

        Args:
            patient_name:       Full name of the patient.
            patient_email:      Patient's email address for the calendar invite.
            patient_phone:      Patient's contact phone number.
            therapist_name:     Therapist's full name (must match a therapist from get_therapists).
            date:               Appointment date in YYYY-MM-DD format.
            time_slot:          Chosen time slot in HH:MM format, e.g. "18:00".
            session_format:     "Online" or "In-Person".
            session_type:       "Initial Consultation" or "Follow-Up Session".
            appointment_reason: A brief 1-2 sentence summary of the patient's reason
                                for booking (concerns or goals).

        Call this ONLY after the patient has confirmed all details.
        The appointment will be saved and the patient will receive a
        calendar invite from our team shortly.
        """
        global appointment_counter

        logger.info(
            "[TOOL] book_appointment | patient=%s therapist=%s date=%s time=%s format=%s type=%s",
            patient_name, therapist_name, date, time_slot, session_format, session_type
        )

        # Validate therapist exists
        therapist = get_therapist_by_name(therapist_name)
        if not therapist:
            return {"success": False, "message": f"Therapist '{therapist_name}' not found."}

        # Validate slot is available
        availability = get_available_slots(therapist_name, date)
        if not availability.get("available") or time_slot not in availability.get("slots", []):
            return {
                "success": False,
                "message": f"The {time_slot} slot on {date} is not available for {therapist_name}.",
            }

        # Validate session type
        if session_type not in SESSION_TYPES:
            return {
                "success": False,
                "message": f"Invalid session type. Choose from: {', '.join(SESSION_TYPES)}.",
            }

        # Create appointment record
        appointment_counter += 1
        appointment_id = f"TYHO-{appointment_counter}"

        appointment = {
            "appointment_id": appointment_id,
            "patient_name": patient_name,
            "patient_email": patient_email,
            "patient_phone": patient_phone,
            "therapist_name": therapist["name"],
            "therapist_title": therapist["title"],
            "date": date,
            "time_slot": time_slot,
            "session_format": session_format,
            "session_type": session_type,
            "session_duration": SESSION_DURATION.get(session_type, "50 minutes"),
            "appointment_reason": appointment_reason,
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
        }

        appointments.append(appointment)
        _save_appointments(appointments, appointment_counter)

        logger.info("[MILESTONE] Appointment booked & saved | id=%s", appointment_id)

        return {
            "success": True,
            "appointment_id": appointment_id,
            "message": (
                f"Appointment {appointment_id} confirmed! "
                f"{patient_name} with {therapist['name']} on {date} at {time_slot} ({session_format}). "
                f"Session type: {session_type}, Duration: {SESSION_DURATION.get(session_type, '50 minutes')}."
            ),
            "details": appointment,
        }

    @function_tool
    async def end_call(self):
        """
        End the current call and shutdown the session.
        Call this ONLY after the appointment has been successfully booked,
        the patient has been informed of the booking confirmation,
        and they have no more questions. Always say a warm goodbye before
        ending the call.
        """
        try:
            logger.info("[TOOL] end_call — hanging up")
            await self.hangup()
            logger.info("[TOOL] end_call — call ended successfully")
        except Exception as e:
            logger.error("[TOOL] end_call failed: %s", e)


async def entrypoint(ctx: JobContext):
    logger.info("[STARTUP] entrypoint called | room=%s", ctx.room_options.room_id)
    agent = VoiceAgent()

    pipeline = Pipeline(
        stt=DeepgramSTT(),
        llm=GoogleLLM(),
        tts=CartesiaTTS(
            voice_id="f786b574-daa5-4673-aa0c-cbe3e8534c02"  # Katie (Stable)
        ),
        vad=SileroVAD(),
        turn_detector=TurnDetector(),
        eou_config=EOUConfig(
            mode='ADAPTIVE',
            min_max_speech_wait_timeout=[0.2, 0.3],
        ),
        interrupt_config=InterruptConfig(
            mode="HYBRID",
            interrupt_min_duration=0.2,
            interrupt_min_words=2,
        )
    )

    session = AgentSession(agent=agent, pipeline=pipeline)
    room_id = ctx.room_options.room_id if ctx.room_options else "unknown"
    logger.info("[STARTUP] Pipeline built — waiting for participant | room=%s", room_id)

    await session.start(wait_for_participant=True, run_until_shutdown=True)
    logger.info("[SHUTDOWN] Session ended | room=%s", room_id)


def make_context() -> JobContext:
    room_options = RoomOptions(
        room_id=os.getenv("VIDEOSDK_ROOM_ID", "default-room"),
        name="TYHO-Therapy-Scheduler-Agent",
        playground=True
    )
    return JobContext(room_options=room_options)


if __name__ == "__main__":
    job = WorkerJob(entrypoint=entrypoint, jobctx=make_context)
    job.start()
