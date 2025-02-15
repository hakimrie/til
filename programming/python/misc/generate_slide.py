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
            b = int(c2[2] + (c2[2] - c2[2]) * segment_factor)
            color = (r, g, b)
        else:
            color = colors[0] if colors else (255, 255, 255)
        draw.line([(0, y), (width, y)], fill=color)
    return gradient

def draw_corners_rounded_rectangle(draw_obj, bounds, radius, fill, round_top_left=True, round_top_right=True, round_bottom_left=True, round_bottom_right=True):
    """Draws a rectangle with specified rounded corners."""
    x1, y1, x2, y2 = bounds
    diameter = radius * 2

    if round_top_left:
        draw_obj.ellipse([(x1, y1), (x1 + diameter, y1 + diameter)], fill=fill) # top-left
    else:
        draw_obj.rectangle([(x1, y1), (x1 + radius, y1 + radius)], fill=fill) # Square top-left if not rounded

    if round_top_right:
        draw_obj.ellipse([(x2 - diameter, y1), (x2, y1 + diameter)], fill=fill) # top-right
    else:
        draw_obj.rectangle([(x2 - radius, y1), (x2, y1 + radius)], fill=fill) # Square top-right if not rounded

    if round_bottom_left:
        draw_obj.ellipse([(x1, y2 - diameter), (x1 + diameter, y2)], fill=fill) # bottom-left
    else:
        draw_obj.rectangle([(x1, y2 - radius), (x1 + radius, y2)], fill=fill) # Square bottom-left if not rounded

    if round_bottom_right:
        draw_obj.ellipse([(x2 - diameter, y2 - diameter), (x2, y2)], fill=fill) # bottom-right
    else:
        draw_obj.rectangle([(x2 - radius, y2 - radius), (x2, y2)], fill=fill) # Square bottom-right if not rounded


    # Edges (rectangles to connect corners):
    draw_obj.rectangle([(x1 + (radius if round_top_left else 0), y1), (x2 - (radius if round_top_right else 0) - 1, y1 + radius)], fill=fill) # top edge
    draw_obj.rectangle([(x1 + (radius if round_bottom_left else 0), y2 - radius - 1), (x2 - (radius if round_bottom_right else 0) - 1, y2)], fill=fill) # bottom edge
    draw_obj.rectangle([(x1, y1 + (radius if round_top_left else 0)), (x1 + radius, y2 - (radius if round_bottom_left else 0) - 1)], fill=fill) # left edge
    draw_obj.rectangle([(x2 - radius - 1, y1 + (radius if round_top_right else 0)), (x2, y2 - (radius if round_bottom_right else 0) - 1)], fill=fill) # right edge

    # Center rectangle:
    draw_obj.rectangle([(x1 + radius, y1 + radius), (x2 - radius - 1, y2 - radius - 1)], fill=fill) # center


def generate_terminal_image(code):
    """Generates just the terminal image with code, no background."""
    # --- Terminal Settings ---
    terminal_background_color = "#282A36"
    terminal_bar_color = "#44475A"
    terminal_corner_radius = 20
    terminal_top_corner_radius = 20

    font_family = "JetBrainsMono-Regular.ttf"
    font_size = 60
    line_height = int(font_size * 1.3)

    padding_x = 100
    padding_y = 40

    terminal_bar_height = 80
    terminal_button_radius = 16
    terminal_button_spacing = 20
    terminal_button_y_offset = 20
    corner_antialias_factor = 4

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

    # --- Draw Terminal Background with Rounded Corners (Anti-aliased) ---
    terminal_background_image = Image.new('RGBA', (terminal_image_width * corner_antialias_factor, (terminal_image_height - terminal_bar_height) * corner_antialias_factor), (0,0,0,0))
    d_terminal_bg = ImageDraw.Draw(terminal_background_image)
    terminal_bg_bounds_large = (0, 0, terminal_image_width * corner_antialias_factor, (terminal_image_height - terminal_bar_height) * corner_antialias_factor)
    corner_radius_large = terminal_corner_radius * corner_antialias_factor
    draw_corners_rounded_rectangle(d_terminal_bg, terminal_bg_bounds_large, corner_radius_large, terminal_background_color,
                                     round_top_left=False, round_top_right=False, round_bottom_left=True, round_bottom_right=True) # Bottom rounded only for background

    terminal_background_image_resized = terminal_background_image.resize((terminal_image_width, terminal_image_height - terminal_bar_height), Image.LANCZOS)
    terminal_image.paste(terminal_background_image_resized, (0, terminal_bar_height), mask=terminal_background_image_resized)


    # --- Create Terminal Bar Image for Buttons (Anti-aliased Top Rounded Corners) ---
    terminal_bar_image_buttons = Image.new('RGBA', (terminal_image_width * corner_antialias_factor, terminal_bar_height * corner_antialias_factor), (0,0,0,0))
    d_bar_buttons = ImageDraw.Draw(terminal_bar_image_buttons)
    terminal_bar_bounds_large = (0, 0, terminal_image_width * corner_antialias_factor, terminal_bar_height * corner_antialias_factor)
    top_corner_radius_large = terminal_top_corner_radius * corner_antialias_factor
    draw_corners_rounded_rectangle(d_bar_buttons, terminal_bar_bounds_large, top_corner_radius_large, terminal_bar_color,
                                     round_top_left=True, round_top_right=True, round_bottom_left=False, round_bottom_right=False) # Top rounded only for bar

    button_x_large = padding_x * corner_antialias_factor // 2
    button_radius_large = terminal_button_radius * corner_antialias_factor
    button_spacing_large = terminal_button_spacing * corner_antialias_factor
    terminal_button_y_offset_large = terminal_button_y_offset * corner_antialias_factor

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

    return terminal_image


def generate_code_slide(code, output_path="code_slide.png", with_background=False):
    """
    Generates a code slide, either with or without a background.

    Args:
        code (str): The Python code to display.
        output_path (str): Path to save the output image.
        with_background (bool, optional): Whether to include a gradient background.
                                         Defaults to True (with background).
    """
    terminal_image = generate_terminal_image(code)

    if with_background:
        background_width = 1920 #* 1.5
        background_height = 1080
        gradient_colors = [(255, 0, 255), (0, 0, 255)]
        background_image = generate_gradient_background(background_width, background_height, gradient_colors)

        terminal_x_position = (background_width - terminal_image.width) // 2
        terminal_y_position = (background_height - terminal_image.height) // 2
        background_image.paste(terminal_image, (terminal_x_position, terminal_y_position), mask=terminal_image)
        final_image = background_image
        output_message = f"Code slide with background saved to {output_path}"
    else:
        final_image = terminal_image
        output_message = f"Terminal code slide (no background) saved to {output_path}"

    final_image.save(output_path)
    print(output_message)


# --- Example Usage ---
code_example = """@dataclass
class Item:

    name: str
    price: float
"""

# Generate with background (default)
generate_code_slide(code_example, output_path="code_slide_with_bg.png", with_background=True)

# Generate without background (terminal only)
generate_code_slide(code_example, output_path="code_slide_terminal_only.png", with_background=False)