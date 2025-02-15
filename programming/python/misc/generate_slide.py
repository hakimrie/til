from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
import io

def generate_gradient_background(width, height, colors):
    """
    Generates a vertical gradient background image.

    Args:
        width (int): Width of the image.
        height (int): Height of the image.
        colors (list of color tuples): List of RGB color tuples defining the gradient.
                                       e.g., [(R1, G1, B1), (R2, G2, B2)] for a 2-color gradient.

    Returns:
        PIL.Image.Image: Gradient background image.
    """
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)

    n_colors = len(colors)
    for y in range(height):
        blend_factor = float(y) / (height - 1) if height > 1 else 0
        if n_colors == 2: # Linear interpolation for 2 colors
            c1 = colors[0]
            c2 = colors[1]
            r = int(c1[0] + (c2[0] - c1[0]) * blend_factor)
            g = int(c1[1] + (c2[1] - c1[1]) * blend_factor)
            b = int(c1[2] + (c2[2] - c1[2]) * blend_factor)
            color = (r, g, b)
        elif n_colors > 2: # Simple step gradient for more than 2 colors (can be improved)
            step = height // (n_colors - 1) if n_colors > 1 else height
            color_index = min(int(blend_factor * (n_colors - 1)), n_colors - 2)
            segment_factor = (blend_factor * (n_colors - 1)) - color_index
            c1 = colors[color_index]
            c2 = colors[color_index+1]
            r = int(c1[0] + (c2[0] - c1[0]) * segment_factor)
            g = int(c1[1] + (c2[1] - c1[1]) * segment_factor)
            b = int(c1[2] + (c2[2] - c1[2]) * segment_factor)
            color = (r, g, b)

        else: # Fallback to first color if only one is provided
            color = colors[0] if colors else (255, 255, 255) # white default


        draw.line([(0, y), (width, y)], fill=color)
    return gradient

def generate_code_slide_with_background(code, output_path="code_slide_bg_landscape.png"):
    """Generates a landscape code slide with reduced vertical padding."""
    # --- Background Settings (Landscape & Wider) ---
    background_width = 1920 #* 1.5 # Wider background (1.5x HD width)
    background_height = 1080
    gradient_colors = [(255, 0, 255), (0, 0, 255)] # Magenta to Blue gradient

    background_image = generate_gradient_background(background_width, background_height, gradient_colors)

    # --- Terminal Settings (Adjusted Padding & Landscape Width) ---
    terminal_background_color = "#282A36"
    terminal_bar_color = "#44475A"

    font_family = "JetBrainsMono-Regular.ttf"
    font_size = 40
    line_height = int(font_size * 1.3)

    padding_x = 100 # Horizontal padding remains same
    padding_y = 40  # Reduced vertical padding - important change!

    terminal_bar_height = 80
    terminal_button_radius = 16
    terminal_button_spacing = 20
    terminal_button_y_offset = 20
    button_antialias_factor = 4

    # --- ImageFormatter Configuration ---
    formatter = ImageFormatter(
        style='dracula',
        font_name=font_family,
        font_size=font_size,
        background=terminal_background_color,
        line_number_bg=terminal_background_color,
        line_number_fg="#F8F8F2",
        line_numbers=False,
        image_pad=padding_y,
        line_pad=line_height - font_size
    )

    lexer = PythonLexer()
    highlighted_code_bytes = highlight(code, lexer, formatter)
    highlighted_code_image = Image.open(io.BytesIO(highlighted_code_bytes))
    code_width, code_height = highlighted_code_image.size

    # --- Calculate Terminal Image Size (Landscape width) ---
    terminal_image_width = max(code_width + 2 * padding_x, 1200) # Wider terminal, minimum width for landscape
    terminal_image_height = terminal_bar_height + padding_y + code_height + padding_y

    # --- Create Terminal Image (RGBA for transparency) ---
    terminal_image = Image.new('RGBA', (terminal_image_width, terminal_image_height), (0, 0, 0, 0))
    d_terminal = ImageDraw.Draw(terminal_image)

    # --- Draw Terminal Background Rectangle ---
    d_terminal.rectangle([(0, terminal_bar_height), (terminal_image_width, terminal_image_height)], fill=terminal_background_color)

    # --- Create Terminal Bar Image for Buttons (Anti-aliased) ---
    terminal_bar_image_buttons = Image.new('RGBA', (terminal_image_width * button_antialias_factor, terminal_bar_height * button_antialias_factor), (0,0,0,0))
    d_bar_buttons = ImageDraw.Draw(terminal_bar_image_buttons)
    d_bar_buttons.rectangle([(0, 0), (terminal_image_width * button_antialias_factor, terminal_bar_height * button_antialias_factor)], fill=terminal_bar_color)

    button_x_large = padding_x * button_antialias_factor // 2
    button_radius_large = terminal_button_radius * button_antialias_factor
    button_spacing_large = terminal_button_spacing * button_antialias_factor
    terminal_button_y_offset_large = terminal_button_y_offset * button_antialias_factor

    button_colors = ["#FF5F56", "#FFBD2E", "#27C93F"]
    for color in button_colors:
        d_bar_buttons.ellipse([(button_x_large - button_radius_large, terminal_button_y_offset_large),
                       (button_x_large + button_radius_large, terminal_button_y_offset_large + 2*button_radius_large)],
                      fill=color)
        button_x_large += 2 * button_radius_large + button_spacing_large

    terminal_bar_image_buttons_resized = terminal_bar_image_buttons.resize((terminal_image_width, terminal_bar_height), Image.LANCZOS)
    terminal_image.paste(terminal_bar_image_buttons_resized, (0, 0), mask=terminal_bar_image_buttons_resized)

    # --- Paste Highlighted Code Image onto Terminal Image ---
    code_y_position = terminal_bar_height + padding_y
    terminal_image.paste(highlighted_code_image, (padding_x, code_y_position))

    # --- Calculate Position to Center Terminal on Background ---
    terminal_x_position = (background_width - terminal_image_width) // 2
    terminal_y_position = (background_height - terminal_image_height) // 2

    # --- Composite Terminal Image onto Background ---
    background_image.paste(terminal_image, (terminal_x_position, terminal_y_position), mask=terminal_image)

    # --- Save Final Image ---
    background_image.save(output_path)
    print(f"Landscape code slide with background saved to {output_path}")


# --- Example Usage ---
code_example = """
agent = CodeAgent(
    tools=[go_back, close_popups, search_item_ctrl_f],
    model=model,
    additional_authorized_imports=["helium"],
    step_callbacks=[save_screenshot],
    max_steps=20,
    verbosity_level=2,
)
"""

generate_code_slide_with_background(code_example, output_path="code_slide_bg_landscape_2.png")