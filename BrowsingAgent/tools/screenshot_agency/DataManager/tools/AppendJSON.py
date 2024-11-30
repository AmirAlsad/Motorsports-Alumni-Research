import json
import os
from pydantic import BaseModel, Field, ValidationError
from agency_swarm.tools import BaseTool
from typing import List

# Define the name of the JSON file to which we will append data
JSON_FILE_PATH = "students_data.json"

class StudentData(BaseModel):
    """
    Model that represents the required structure for student data JSON input.
    Ensures the input JSON conforms to the specified format.
    """
    name: str = Field(..., description="The name of the student.")
    class_year: str = Field(..., description="The class year of the student.")
    degrees: List[str] = Field(..., description="List of degrees the student is pursuing or has completed.")
    major: str = Field(..., description="The major of the student.")

class AppendJSON(BaseTool):
    """
    This tool appends a correctly structured JSON data about a student
    to a larger JSON file in the same directory. If the input JSON is not
    in the correct format, it raises an error for the agent to correct it.

    The tool also accommodates for the input being passed as a string,
    converting it into JSON form if necessary.
    """
    student_data: str = Field(
        ..., description="JSON data representing the student's information. Must follow the correct format."
    )

    def run(self):
        """
        Validates the structure of the input JSON and appends it to the larger JSON file.
        If the structure is invalid, raises a ValidationError.
        Also parses the JSON string input if provided as a string.
        """
        try:
            # If the student_data is a string, attempt to parse it as JSON
            if isinstance(self.student_data, str):
                try:
                    self.student_data = json.loads(self.student_data)
                except json.JSONDecodeError as e:
                    return f"Error parsing input JSON string: {e}"

            # Validate the incoming student data with the defined model
            student = StudentData(**self.student_data)

            # Check if the JSON file exists; if not, create an empty one
            if not os.path.exists(JSON_FILE_PATH):
                with open(JSON_FILE_PATH, 'w') as f:
                    json.dump([], f)  # Create an empty list in the file

            # Load the existing data from the file
            with open(JSON_FILE_PATH, 'r') as f:
                data = json.load(f)

            # Ensure data is a list
            if not isinstance(data, list):
                raise ValueError(f"Expected the file to contain a list, but found {type(data)}")

            # Append the new student data to the list
            data.append(student.dict())

            # Save the updated data back to the JSON file
            with open(JSON_FILE_PATH, 'w') as f:
                json.dump(data, f, indent=4)

            return "Student data successfully appended."

        except ValidationError as e:
            # If the input doesn't conform to the required structure, raise an error
            return f"Invalid input format: {e}"

        except Exception as e:
            return f"An error occurred: {e}"


if __name__ == "__main__":
    # Test case: Correct format passed as string
    example_data_string = '{"name": "Jane Doe", "class_year": "2024", "degrees": ["BSc Computer Science"], "major": "Computer Science"}'

    tool = AppendJSON(student_data=example_data_string)
    print(tool.run())  # Should append successfully

    # Test case: Incorrect format passed as string
    incorrect_data_string = '{"name": "John Doe", "class_year": "2023", "degrees": "BSc Physics", "major": "Physics"}'

    tool = AppendJSON(student_data=incorrect_data_string)
    print(tool.run())  # Should raise validation error

    # New Test case: Correct format passed as a Python dictionary
    example_data_dict = {
        "name": "Alice Smith",
        "class_year": "2025",
        "degrees": ["BSc Mathematics", "MSc Data Science"],
        "major": "Data Science"
    }

    tool = AppendJSON(student_data=example_data_dict)
    print(tool.run())  # Should append successfully
