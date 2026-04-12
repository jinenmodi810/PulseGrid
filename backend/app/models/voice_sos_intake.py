"""Future voice SOS pipeline — structured intake only in this phase.

TODO(voice): Connect ElevenLabs conversational agent or cloud STT here.
Merge transcript → NLP extraction → fields below → build CreateIncidentRequest or ResponseEngineInput.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class VoiceSosIntakeStub(BaseModel):
    """Backend-ready payload once speech is converted to structured signals."""

    transcript: str = ""
    extracted_disaster_type: str = ""
    extracted_people_count: int | None = None
    extracted_severity_hint: str = ""
    urgency_medical: bool = False
    urgency_transport: bool = False
    urgency_shelter: bool = False
    preferred_language_detected: str = ""
    confidence_notes: str = Field(default="", description="Extraction caveats for ops review")


class VoiceSosIntakePreviewResponse(BaseModel):
    """Stub response for `POST /incidents/voice-intake/preview` until voice is wired."""

    status: str = "not_implemented"
    message: str = "Voice intake is not active. Use the form SOS or POST /incidents with intake_source=voice_stub after client-side STT."
    draft: VoiceSosIntakeStub = Field(default_factory=VoiceSosIntakeStub)
