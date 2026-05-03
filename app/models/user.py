from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    # -------- CORE (UNCHANGED) --------
    age: int
    location: str
    voting_location: Optional[str] = None
    is_registered: bool

    # -------- OPTIONAL (NEW) --------
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    preferred_language: Optional[str] = "en"

    # journey stage: "start", "registered", "voting"
    stage: Optional[str] = "start"

    # crowd preference: "low", "any"
    preference: Optional[str] = "low"

    # -------- HELPER METHODS (NEW) --------
    def is_eligible(self) -> bool:
        return self.age >= 18

    def needs_registration(self) -> bool:
        return not self.is_registered

    def get_status(self) -> str:
        if not self.is_eligible():
            return "Not Eligible"
        if self.needs_registration():
            return "Needs Registration"
        return "Ready to Vote"