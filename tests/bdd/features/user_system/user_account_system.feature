Feature: User Account System Translation
  This feature tests the end-to-end translation of a realistic user account system specification, from natural language to Tau.

  Scenario: Translate a full user account system definition
    Given the natural language requirement is "We need a system to manage user accounts. A 'UserID' must be a string that follows the format 'U-' followed by exactly 8 digits. An 'Email' is a string that must be a valid email address. A 'Password' is a string. We need a function called 'is_strong_password' that checks if a password is at least 12 characters long and contains at least one uppercase letter, one lowercase letter, one digit, and one special character. This function should return a boolean."
    When the translator processes the natural language requirement
    Then the resulting Tau specification should be "typedef UserID as string where value matches r'^U-[0-9]{8}$';\ntypedef Email as string where value matches r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';\n\nfn is_strong_password(password: string) -> bool {\n    return len(password) >= 12 and\n           any(c.isupper() for c in password) and\n           any(c.islower() for c in password) and\n           any(c.isdigit() for c in password) and\n           any(not c.isalnum() for c in password);\n}"
