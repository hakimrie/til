from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
import io

def generate_code_slide(code, output_path="code_slide.png"):
    """
    Generates a higher resolution image slide with Python code and improved terminal buttons.
    """
    # --- Settings (Increased Resolution) ---
    background_color = "#282A36"
    terminal_bar_color = "#44475A"

    font_family = "JetBrainsMono-Regular.ttf"
    font_size = 60  # Doubled font size for higher resolution
    line_height = int(font_size * 1.3) # Adjusted line height

    padding_x = 100 # Increased padding
    padding_y = 100 # Increased padding

    terminal_bar_height = 80 # Increased terminal bar height
    terminal_button_radius = 16 # Doubled button radius
    terminal_button_spacing = 20 # Increased spacing
    terminal_button_y_offset = 20 # Adjusted offset

    # --- ImageFormatter Configuration (Keep Style, Adjust Padding) ---
    formatter = ImageFormatter(
        style='dracula',
        font_name=font_family,
        font_size=font_size,
        background=background_color,
        line_number_bg="#282A36",
        line_number_fg="#F8F8F2",
        line_numbers=False,
        image_pad=padding_x, # Use the increased padding
        line_pad=line_height - font_size # Adjust line padding based on new line_height
    )

    lexer = PythonLexer()
    highlighted_code_bytes = highlight(code, lexer, formatter)
    highlighted_code_image = Image.open(io.BytesIO(highlighted_code_bytes))
    code_width, code_height = highlighted_code_image.size

    # --- Calculate Final Image Size ---
    image_width = code_width
    image_height = terminal_bar_height + padding_y + code_height + padding_y

    # --- Create Image ---
    img = Image.new('RGB', (image_width, image_height), background_color)
    d = ImageDraw.Draw(img)

    # --- Draw Terminal Bar (Higher Resolution Buttons) ---
    d.rectangle([(0, 0), (image_width, terminal_bar_height)], fill=terminal_bar_color)
    button_x = padding_x // 2 # Adjust button x position for increased padding
    button_colors = ["#FF5F56", "#FFBD2E", "#27C93F"]
    for color in button_colors:
        d.ellipse([(button_x - terminal_button_radius, terminal_button_y_offset),
                   (button_x + terminal_button_radius, terminal_button_y_offset + 2*terminal_button_radius)],
                  fill=color)
        button_x += 2 * terminal_button_radius + terminal_button_spacing

    # --- Paste Highlighted Code Image ---
    code_y_position = terminal_bar_height + padding_y
    img.paste(highlighted_code_image, (0, code_y_position))

    # --- Save Image ---
    img.save(output_path)
    print(f"High-resolution code slide saved to {output_path}")


# --- Example Usage ---
code_example = """from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    account_id: int
"""

generate_code_slide(code_example, output_path="code_slide_high_res.png")