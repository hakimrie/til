from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
import io

def generate_code_slide(code, output_path="code_slide.png"):
    """
    Generates a higher resolution image slide with anti-aliased terminal buttons.
    """
    # --- Settings (Increased Base Resolution) ---
    background_color = "#282A36"
    terminal_bar_color = "#44475A"

    font_family = "JetBrainsMono-Regular.ttf"
    font_size = 60
    line_height = int(font_size * 1.3)

    padding_x = 100
    padding_y = 100

    terminal_bar_height = 80
    terminal_button_radius = 16
    terminal_button_spacing = 20
    terminal_button_y_offset = 20

    # --- Anti-aliasing Factor for Buttons ---
    button_antialias_factor = 4  # Draw buttons 4x larger, then downsample

    # --- ImageFormatter Configuration ---
    formatter = ImageFormatter(
        style='dracula',
        font_name=font_family,
        font_size=font_size,
        background=background_color,
        line_number_bg="#282A36",
        line_number_fg="#F8F8F2",
        line_numbers=False,
        image_pad=padding_x,
        line_pad=line_height - font_size
    )

    lexer = PythonLexer()
    highlighted_code_bytes = highlight(code, lexer, formatter)
    highlighted_code_image = Image.open(io.BytesIO(highlighted_code_bytes))
    code_width, code_height = highlighted_code_image.size

    # --- Calculate Final Image Size ---
    image_width = code_width
    image_height = terminal_bar_height + padding_y + code_height + padding_y

    # --- Create Main Image ---
    img = Image.new('RGB', (image_width, image_height), background_color)
    d = ImageDraw.Draw(img)

    # --- Create Terminal Bar Image (Separate for Button Anti-aliasing) ---
    terminal_bar_image = Image.new('RGB', (image_width * button_antialias_factor, terminal_bar_height * button_antialias_factor), terminal_bar_color) # Draw 4x larger
    d_bar = ImageDraw.Draw(terminal_bar_image)

    # --- Draw Terminal Bar Buttons (on the larger bar image) ---
    button_x_large = padding_x // 2 * button_antialias_factor # Scaled button position
    button_radius_large = terminal_button_radius * button_antialias_factor # Scaled radius
    button_spacing_large = terminal_button_spacing * button_antialias_factor # Scaled spacing
    terminal_button_y_offset_large = terminal_button_y_offset * button_antialias_factor # Scaled offset

    button_colors = ["#FF5F56", "#FFBD2E", "#27C93F"]
    for color in button_colors:
        d_bar.ellipse([(button_x_large - button_radius_large, terminal_button_y_offset_large),
                       (button_x_large + button_radius_large, terminal_button_y_offset_large + 2*button_radius_large)],
                      fill=color)
        button_x_large += 2 * button_radius_large + button_spacing_large

    # --- Resize Terminal Bar Image (Downsample for Anti-aliasing) ---
    terminal_bar_image = terminal_bar_image.resize((image_width, terminal_bar_height), Image.LANCZOS) # Use LANCZOS filter

    # --- Paste Terminal Bar Image onto Main Image ---
    img.paste(terminal_bar_image, (0, 0))


    # --- Paste Highlighted Code Image ---
    code_y_position = terminal_bar_height + padding_y
    img.paste(highlighted_code_image, (0, code_y_position))

    # --- Save Image ---
    img.save(output_path)
    print(f"High-resolution code slide with anti-aliased buttons saved to {output_path}")


# --- Example Usage ---
code_example = """from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    account_id: int
"""

generate_code_slide(code_example, output_path="code_slide_hires.png")