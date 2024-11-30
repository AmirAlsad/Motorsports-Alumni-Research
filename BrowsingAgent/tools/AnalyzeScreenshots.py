from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import shutil

class AnalyzeScreenshots(BaseTool):
    """
    A tool that processes images using the ScreenshotAnalyzerAgent and communicates with the DataManagerAgent.
    """

    def run(self):
        """
        Processes images from the 'images' directory, one at a time, using the agency.
        """
        try:
            from agency_swarm import Agency
            from agency_swarm import get_openai_client
            from .screenshot_agency.ScreenshotAnalyzer.ScreenshotAnalyzerAgent import ScreenshotAnalyzerAgent
            from .screenshot_agency.DataManager import DataManager  # Ensure this is implemented
        except ImportError as e:
            print(f"Import error: {e}")
            return "Failed to import necessary modules."

        self.track_tool_usage()

        # Initialize agents for each image
        analyzer = ScreenshotAnalyzerAgent()
        data_manager = DataManager()

        # Create agency with communication flow for each image
        agency = Agency([
            analyzer,  # Entry point
            [analyzer, data_manager],
        ],
            temperature=0.5,
            max_prompt_tokens=25000
        )

        try:
            # Define directories
            images_folder = "screenshots"
            agent_image_dir = "image_dir"

            # Ensure directories exist
            os.makedirs(agent_image_dir, exist_ok=True)

            # Loop over images
            for image_name in os.listdir(images_folder):
                image_path = os.path.join(images_folder, image_name)
                if not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    continue

                # Clear agent's image directory
                for file in os.listdir(agent_image_dir):
                    file_path = os.path.join(agent_image_dir, file)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error removing file {file_path}: {e}")

                # Copy image to agent's directory
                try:
                    shutil.copy(image_path, agent_image_dir)
                except Exception as e:
                    print(f"Error copying file {image_path}: {e}")
                    continue

                # Run the agency for the current image
                try:
                    response = agency.get_completion(message=f"Reply with the '^screenshot^' command to get access to the screenshot.")
                    print(f"Processed image: {image_name}")
                    print("Response:", response)
                except Exception as e:
                    print(f"Error processing image {image_name}: {e}")

            return "All images have been processed."

        except Exception as e:
            print(f"An error occurred during processing: {e}")
            return "An error occurred during image processing."

    def track_tool_usage(self):
        """
        Keeps track of how many times the tool is called by maintaining a count in 'page_count.txt'.
        If the file does not exist, it initializes the count to 1.

        Returns:
            int: The updated count of how many times the tool has been used.
        """
        count_file = "page_count.txt"

        # Check if the count file exists
        if os.path.exists(count_file):
            # Read the current count
            with open(count_file, "r") as file:
                count = int(file.read().strip())
        else:
            # Initialize the count if file doesn't exist
            count = 0

        # Increment the count
        count += 1

        # Write the updated count back to the file
        with open(count_file, "w") as file:
            file.write(str(count))

        return
