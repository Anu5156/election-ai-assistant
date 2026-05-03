def validate_age(age: int) -> bool:
    """
    Validates if the user's age is within the legal and biological range.
    Args:
        age: The age to validate.
    Returns:
        True if age is between 18 and 120, False otherwise.
    """
    return 18 <= age <= 120

def sanitize_input(text: str) -> bool:
    """
    Sanitizes user input to prevent prompt injection, XSS, and other malicious attacks.
    Args:
        text: The input string to sanitize.
    Returns:
        True if the input is safe, False if it contains suspicious patterns.
    """
    if not text:
        return True
        
    # 🔒 Length Limit (Security Policy)
    if len(text) > 500:
        return False

    # 🚫 Injection & Evasion Patterns
    blocked = [
        "ignore", "hack", "bypass", "system prompt", 
        "forget", "sudo", "exec(", "eval(", "prompt injection",
        "<script", "onerror=", "onload="
    ]
    
    # 🕵️ Check for malicious patterns
    text_lower = text.lower()
    for word in blocked:
        if word in text_lower:
            return False
            
    # 🧩 HTML Tag Filtering (Basic XSS Prevention)
    if "<" in text and ">" in text:
        return False
        
    return True