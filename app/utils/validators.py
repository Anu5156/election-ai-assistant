def validate_age(age):
    return 18 <= age <= 120

def sanitize_input(text):
    blocked = ["ignore instructions", "hack", "bypass"]
    for word in blocked:
        if word in text.lower():
            return False
    return True