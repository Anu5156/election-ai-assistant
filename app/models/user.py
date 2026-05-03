from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    """
    Data model representing a voter profile in the CivicGuide AI system.
    Strictly follows Pydantic validation for schema integrity.
    """
    
    # -------- CORE FIELDS --------
    age: int = Field(..., ge=0, le=120, description="Age of the voter")
    location: str = Field(..., description="Current city or area of the voter")
    voting_location: Optional[str] = Field(None, description="Registered voting area if different from current location")
    is_registered: bool = Field(..., description="Voter registration status")

    # -------- GEOSPATIAL FIELDS --------
    latitude: Optional[float] = Field(None, description="GPS Latitude coordinate")
    longitude: Optional[float] = Field(None, description="GPS Longitude coordinate")

    # -------- PREFERENCES --------
    preferred_language: Optional[str] = Field("en", description="ISO language code for translations")
    stage: Optional[str] = Field("start", description="Current stage in the voting journey")
    preference: Optional[str] = Field("low", description="User preference for crowd density (low, any)")

    # -------- BUSINESS LOGIC --------
    def is_eligible(self) -> bool:
        """Checks if the user meets the minimum voting age (18)."""
        return self.age >= 18

    def needs_registration(self) -> bool:
        """Checks if the user still needs to register with the ECI."""
        return not self.is_registered

    def get_status(self) -> str:
        """Returns a human-readable status string based on eligibility and registration."""
        if not self.is_eligible():
            return "Not Eligible"
        if self.needs_registration():
            return "Needs Registration"
        return "Ready to Vote"