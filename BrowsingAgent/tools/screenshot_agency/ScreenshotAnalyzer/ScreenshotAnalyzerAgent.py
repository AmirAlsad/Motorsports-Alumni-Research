from agency_swarm import Agent
from typing_extensions import override
import os

class ScreenshotAnalyzerAgent(Agent):
    image_dir = "image_dir"

    def __init__(self):
        super().__init__(
            name="ScreenshotAnalyzerAgent",
            model="gpt-4o",
            description="Analyzes screenshots containing student information and communicates findings to the DataManagerAgent.",
            instructions="./instructions.md",
            temperature=0.2,
            max_prompt_tokens=25000,
        )

    @override
    def response_validator(self, message):
        if "^screenshot^" in message.lower():
            response_text = "Here is the requested screenshot:"
        else:
            return message

        content = self.create_response_content(response_text)
        raise ValueError(content)

    def create_response_content(self, response_text):
        try:
            # Get list of image files in directory
            image_files = [f for f in os.listdir(self.image_dir)
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

            if not image_files:
                raise FileNotFoundError(f"No image files found in {self.image_dir}")

            # Use the most recently modified image file
            latest_image = max(
                image_files,
                key=lambda x: os.path.getmtime(os.path.join(self.image_dir, x))
            )

            image_path = os.path.join(self.image_dir, latest_image)

            with open(image_path, "rb") as file:
                file_id = self.client.files.create(
                    file=file,
                    purpose="vision",
                ).id

            content = [
                {"type": "text", "text": response_text},
                {
                    "type": "image_file",
                    "image_file": {"file_id": file_id}
                }
            ]
            return content

        except FileNotFoundError as e:
            raise ValueError(f"Error accessing image: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
