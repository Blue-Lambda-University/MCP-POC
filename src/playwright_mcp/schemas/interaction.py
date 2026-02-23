"""Input/output schemas for interaction tools (click, type, fill form)."""

from pydantic import BaseModel, Field


class ClickInput(BaseModel):
    """Input for clicking an element."""

    selector: str = Field(
        ...,
        description="CSS selector for the element to click (e.g. 'button.submit', '#login')",
    )


class ClickResult(BaseModel):
    """Result of a click action."""

    message: str = Field(..., description="Confirmation message")


class TypeInput(BaseModel):
    """Input for typing into an element."""

    selector: str = Field(
        ...,
        description="CSS selector for the input or textarea",
    )
    text: str = Field(..., description="Text to type into the element")


class TypeResult(BaseModel):
    """Result of a type/fill action."""

    message: str = Field(..., description="Confirmation message")


class FillFormInput(BaseModel):
    """Input for filling multiple form fields."""

    fields: dict[str, str] = Field(
        ...,
        description="Mapping of CSS selectors to values (e.g. {\"#email\": \"user@example.com\", \"#password\": \"secret\"})",
    )


class FillFormResult(BaseModel):
    """Result of a fill-form action."""

    message: str = Field(..., description="Confirmation message including number of fields filled")
