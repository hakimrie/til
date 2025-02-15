from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
import io

def generate_gradient_background(width, height, colors):
    """Generates a vertical gradient background image."""
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)
    n_colors = len(colors)
    for y in range(height):
        blend_factor = float(y) / (height - 1) if height > 1 else 0
        if n_colors == 2:
            c1 = colors[0]
            c2 = colors[1]
            r = int(c1[0] + (c2[0] - c1[0]) * blend_factor)
            g = int(c1[1] + (c2[1] - c1[1]) * blend_factor)
            b = int(c1[2] + (c2[2] - c1[2]) * blend_factor)
            color = (r, g, b)
        elif n_colors > 2:
            step = height // (n_colors - 1) if n_colors > 1 else height
            color_index = min(int(blend_factor * (n_colors - 1)), n_colors - 2)
            segment_factor = (blend_factor * (n_colors - 1)) - color_index
            c1 = colors[color_index]
            c2 = colors[color_index+1]
            r = int(c1[0] + (c2[0] - c1[0]) * segment_factor)
            g = int(c1[1] + (c2[1] - c1[1]) * segment_factor)
            b = int(c2[2] + (c2[2] - c2[2]) * segment_factor) # Corrected typo here
            color = (r, g, b)
        else:
            color = colors[0] if colors else (255, 255, 255)
        draw.line([(0, y), (width, y)], fill=color)
    return gradient

def draw_top_rounded_rectangle(draw_obj, bounds, radius, fill):
    """Draws a rectangle with rounded corners on the top-left and top-right."""
    x1, y1, x2, y2 = bounds
    diameter = radius * 2
    # Top Corners:
    draw_obj.ellipse([(x1, y1), (x1 + diameter, y1 + diameter)], fill=fill)   # top-left
    draw_obj.ellipse([(x2 - diameter, y1), (x2, y1 + diameter)], fill=fill)   # top-right
    # Edges:
    draw_obj.rectangle([(x1 + radius, y1), (x2 - radius - 1, y1 + radius)], fill=fill) # top edge
    draw_obj.rectangle([(x1, y1 + radius), (x2, y2)], fill=fill) # main body of rectangle


def generate_code_slide_with_background(code, output_path="code_slide_bg_top_rounded.png"):
    """Generates a landscape code slide with top-rounded terminal bar."""
    # --- Background Settings ---
    background_width = 1920 #* 1.5
    background_height = 1080
    gradient_colors = [(255, 0, 255), (0, 0, 255)]

    background_image = generate_gradient_background(background_width, background_height, gradient_colors)

    # --- Terminal Settings (Top-Rounded Bar) ---
    terminal_background_color = "#282A36"
    terminal_bar_color = "#44475A"
    terminal_top_corner_radius = 20 # Radius for top rounded corners

    font_family = "JetBrainsMono-Regular.ttf"
    font_size = 60
    line_height = int(font_size * 1.3)

    padding_x = 100
    padding_y = 40

    terminal_bar_height = 80
    terminal_button_radius = 16
    terminal_button_spacing = 20
    terminal_button_y_offset = 20
    button_antialias_factor = 4
    bar_corner_antialias_factor = 4 # Anti-aliasing factor for top corners of bar


    # --- ImageFormatter Configuration ---
    formatter = ImageFormatter(
        style='dracula',
        font_name=font_family,
        font_size=font_size,
        background=terminal_background_color,
        line_number_bg=terminal_background_color,
        line_number_fg="#F8F8F2",
        line_numbers=False,
        image_pad=padding_x,
        line_pad=line_height - font_size
    )

    lexer = PythonLexer()
    highlighted_code_bytes = highlight(code, lexer, formatter)
    highlighted_code_image = Image.open(io.BytesIO(highlighted_code_bytes))
    code_width, code_height = highlighted_code_image.size

    # --- Calculate Terminal Image Size ---
    terminal_image_width = max(code_width + 2 * padding_x, 1200)
    terminal_image_height = terminal_bar_height + padding_y + code_height + padding_y

    # --- Create Terminal Image (RGBA for transparency) ---
    terminal_image = Image.new('RGBA', (terminal_image_width, terminal_image_height), (0, 0, 0, 0))
    d_terminal = ImageDraw.Draw(terminal_image)

    # --- Draw Terminal Background Rectangle (No rounding on background) ---
    terminal_bg_bounds = (0, terminal_bar_height, terminal_image_width, terminal_image_height)
    d_terminal.rectangle(terminal_bg_bounds, fill=terminal_background_color) # Just a regular rectangle for background


    # --- Create Terminal Bar Image for Buttons (Anti-aliased Top Rounded Corners) ---
    terminal_bar_image_buttons = Image.new('RGBA', (terminal_image_width * bar_corner_antialias_factor, terminal_bar_height * bar_corner_antialias_factor), (0,0,0,0)) # Larger bar for corner AA
    d_bar_buttons = ImageDraw.Draw(terminal_bar_image_buttons)
    terminal_bar_bounds_large = (0, 0, terminal_image_width * bar_corner_antialias_factor, terminal_bar_height * bar_corner_antialias_factor) # Large bounds for bar
    top_corner_radius_large = terminal_top_corner_radius * bar_corner_antialias_factor # Scaled radius for corners
    draw_top_rounded_rectangle(d_bar_buttons, terminal_bar_bounds_large, top_corner_radius_large, terminal_bar_color) # Top-rounded bar

    button_x_large = padding_x * bar_corner_antialias_factor // 2 # Scaled button positions
    button_radius_large = terminal_button_radius * bar_corner_antialias_factor
    button_spacing_large = terminal_button_spacing * bar_corner_antialias_factor
    terminal_button_y_offset_large = terminal_button_y_offset * bar_corner_antialias_factor

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
    print(f"Landscape code slide with top-rounded terminal bar saved to {output_path}")


# --- Example Usage ---
code_example = """@dataclass
class Item:

    name: str
    price: float
"""

generate_code_slide_with_background(code_example)