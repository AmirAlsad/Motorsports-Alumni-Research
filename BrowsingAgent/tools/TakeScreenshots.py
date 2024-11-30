from agency_swarm.tools import BaseTool
import os
import time
import base64
import io
from PIL import Image
from .util.selenium import get_web_driver, set_web_driver
from .util import remove_highlight_and_labels, get_b64_screenshot

class TakeScreenshots(BaseTool):
    """
    A tool to automate capturing full-page screenshots of a webpage.
    The tool scrolls through the page vertically, captures screenshots,
    crops them according to specified parameters, and splits each into two images.
    Screenshots are saved in a specified output folder.
    """
    def run(self):
        """
        Automates the process of taking screenshots of a web page.
        Captures the page by scrolling through it, applies cropping and splitting
        to each screenshot, and saves them as PNG files.
        """
        output_folder = 'screenshots'

        # Get the existing WebDriver instance
        wd = get_web_driver()

        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        time.sleep(1)

        # Get total height of the page
        total_height = wd.execute_script("""
            return Math.max(
                document.documentElement.scrollHeight,
                document.body.scrollHeight
            );
        """)

        # Get viewport height
        viewport_height = wd.execute_script("return window.innerHeight;")

        # Initialize variables based on your measurements
        vertical_scroll_position = 475
        screenshot_count = 0
        max_screenshots = 5  # Ensure only 5 screenshots are taken

        remove_highlight_and_labels(wd)

        while screenshot_count < max_screenshots:
            # Scroll to the current vertical position
            wd.execute_script(f"window.scrollTo(0, {vertical_scroll_position});")
            actual_scroll_y = wd.execute_script("return window.pageYOffset;")
            print(f"Scrolled to y: {actual_scroll_y}")
            time.sleep(1)

            # Take the screenshot and crop it
            screenshot_b64 = get_b64_screenshot(wd)
            screenshot_data = base64.b64decode(screenshot_b64)

            # Open the image using PIL
            image = Image.open(io.BytesIO(screenshot_data))

            # Get dimensions of the image
            width, height = image.size

            # Define cropping parameters
            left_crop = int(width * 0.37)  # Crop 37% from the left side
            right_crop = width - int(width * 0.15)  # Crop 15% from the right side

            # Crop the image
            cropped_image = image.crop((left_crop, 0, right_crop, height))

            # Split the cropped image into two halves
            split_point = height // 2

            # Crop the top half of the image
            top_half = cropped_image.crop((0, 0, cropped_image.width, split_point))

            # Crop the bottom half of the image
            bottom_half = cropped_image.crop((0, split_point, cropped_image.width, height))

            # Save the top half image
            filename_top = f'screenshot_{screenshot_count + 1}_top_y{int(actual_scroll_y)}.png'
            filepath_top = os.path.join(output_folder, filename_top)
            top_half.save(filepath_top)

            # Save the bottom half image
            filename_bottom = f'screenshot_{screenshot_count + 1}_bottom_y{int(actual_scroll_y)}.png'
            filepath_bottom = os.path.join(output_folder, filename_bottom)
            bottom_half.save(filepath_bottom)

            screenshot_count += 1

            if screenshot_count == max_screenshots:
                # Jump to the bottom of the page; exit the loop
                wd.execute_script(f"window.scrollTo(0, {total_height});")
                actual_scroll_y = wd.execute_script("return window.pageYOffset;")
                print(f"Scrolled to bottom at y: {actual_scroll_y}")
                time.sleep(1)
                break

            # Adjust viewport height if needed
            if screenshot_count == 1:
                viewport_height += 50

            # Update vertical scroll position
            vertical_scroll_position += viewport_height

            # Check if next scroll would exceed total height
            if vertical_scroll_position >= total_height:
                # Scroll to the bottom without taking another screenshot
                wd.execute_script(f"window.scrollTo(0, {total_height});")
                actual_scroll_y = wd.execute_script("return window.pageYOffset;")
                print(f"Scrolled to bottom at y: {actual_scroll_y}")
                time.sleep(1)
                break

        print(f"Captured {screenshot_count} screenshots and saved in '{output_folder}' folder.")

        # Set the WebDriver back
        set_web_driver(wd)

        return f"Captured {screenshot_count} screenshots and saved in '{output_folder}' folder."

if __name__ == "__main__":
    tool = TakeScreenshots()
    print(tool.run())
