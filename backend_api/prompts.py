PROMPT = '''Here is example code and its docstring.
Example Code:
def get_note_history(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    # Check if the logged-in user has access to the note
    if request.user != note.owner and request.user not in note.shared_with.all():
        return JsonResponse(
            {"error": "You do not have permission to view this note"},
            status=status.HTTP_403_FORBIDDEN,
        )

    updates = note.updates.order_by("-timestamp").values("content", "timestamp")
    return JsonResponse(list(updates), safe=False)

Example docstring:
"""
Get note history, checks if requested user is the note owner or not generate a forbidden error else return history of note sorted by timestamp

Args:
    request : user request
    note_id (int:pk): note id to get fetch history for.

Returns:
    JSON: list of history for note
"""

Following the pattern of above example generate the docstring for following code below:

'''

SYS_PROMPT = """You are a helpful, respectful and honest Software Engineer expert in multiple programming language. Always generate docstring as helpfully as possible, while being safe. Your should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content."""
