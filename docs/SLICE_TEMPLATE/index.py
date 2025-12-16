"""
Entry point for the slice.

This file must only expose functions declared in slice.schema.json.
"""

def exampleAction(input: dict) -> dict:
    """
    Implements exampleAction as defined in slice.schema.json
    """
    # Boundary validation should occur here

    example_field = input["exampleField"]

    # Delegate to internal logic
    result = f"Processed {example_field}"

    return {
        "result": result
    }
