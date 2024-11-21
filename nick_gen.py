import random
import string
def load_club_names(file_path):
    with open(file_path, 'r') as file:
        clubs = file.read().splitlines()
    return clubs
def generate_codename(full_name):
    """Generates a code name in various formats.

    Args:
        full_name: The full name (e.g., "Brandon Hennen")

    Returns:
        A code name in one of the following formats:
            * Word Derived from Name + Number (e.g., "Brandon56")
            * Single-Word Code Name (e.g., "Eagle")
    """

    #initials = "".join(n[0] for n in full_name.split()).upper()

    # Choose a random format
    format_choice = random.choice([2, 3])


    if format_choice == 2:
        clubs = load_club_names("clubs.txt")
        nick = random.choice(clubs)
        return nick
    else:
        # Load a list of possible code words for variety
        with open('male-first-names.txt', 'r') as f:
            code_words = f.read().splitlines()
        return random.choice(code_words).capitalize()

#Example usage (assuming you have a 'code_words.txt' file)
full_name = "Brandon Hennen"
#codename = generate_codename(full_name)
#print(f"Code name for {full_name}: {codename}") 
