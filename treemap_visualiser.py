"""
=== Module Description ===
This module contains the main program code for the treemap visualisation.
It is responsible for initializing an instance of TMTree (using a
concrete subclass, of course), rendering it to the user using pygame,
and detecting user events like mouse clicks and key presses and responding
to them.
"""
from typing import Optional, Tuple
import pygame
from tm_trees import TMTree, FileSystemTree

# Screen dimensions and coordinates
ORIGIN = (0, 0)
# You may adjust these values as you'd like, depending on your screen resolution
WIDTH = 1080  # 1024, 800
HEIGHT = 720  # 768, 600
FONT_HEIGHT = 30  # The height of the text display.
TREEMAP_HEIGHT = HEIGHT - FONT_HEIGHT  # The height of the treemap display.

# Font to use for the treemap program.
FONT_FAMILY = 'Consolas'


def run_visualisation(tree: TMTree) -> None:
    """Display an interactive graphical display of the given tree's treemap.
    """

    # Setup pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Render the initial display of the static treemap.
    render_display(screen, tree, None, None)
    tree.update_rectangles((0, 0, WIDTH, HEIGHT - FONT_HEIGHT))

    # Start an event loop to respond to events.
    event_loop(screen, tree)


def render_display(screen: pygame.Surface, tree: Optional[TMTree],
                   selected_node: Optional[TMTree],
                   hover_node: Optional[TMTree]) -> None:
    """Render a treemap and text display to the given screen.

    Use the constants TREEMAP_HEIGHT and FONT_HEIGHT to divide the
    screen vertically into the treemap and text comments.
    """
    # First, clear the screen
    pygame.draw.rect(screen, pygame.color.THECOLORS['black'],
                     (0, 0, WIDTH, HEIGHT))

    subscreen = screen.subsurface((0, 0, WIDTH, TREEMAP_HEIGHT))

    for rect, colour in tree.get_rectangles():
        # Note that the arguments are in the opposite order
        pygame.draw.rect(subscreen, colour, rect)

    # add the hover rectangle
    if selected_node is not None:
        pygame.draw.rect(subscreen, (255, 255, 255), selected_node.rect, 5)
    if hover_node is not None:
        pygame.draw.rect(subscreen, (255, 255, 255), hover_node.rect, 2)

    _render_text(screen, _get_display_text(selected_node))

    # This must be called *after* all other pygame functions have run.
    pygame.display.flip()


def _render_text(screen: pygame.Surface, text: str) -> None:
    """Render text at the bottom of the display.
    """
    # The font we want to use
    font = pygame.font.SysFont(FONT_FAMILY, FONT_HEIGHT - 8)
    text_surface = font.render(text, 1, pygame.color.THECOLORS['white'])

    # Where to render the text_surface
    text_pos = (0, HEIGHT - FONT_HEIGHT + 4)
    screen.blit(text_surface, text_pos)


def event_loop(screen: pygame.Surface, tree: TMTree) -> None:
    """Respond to events (mouse clicks, key presses) and update the display.

    Note that the event loop is an *infinite loop*: it continually waits for
    the next event, determines the event's type, and then updates the state
    of the visualisation or the tree itself, updating the display if necessary.
    This loop ends only when the user closes the window.
    """
    selected_node = None

    while True:
        # Wait for an event
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            return

        # get the hover position and the corresponding node
        hover_node = tree.get_tree_at_position(pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONUP:
            selected_node = \
                _handle_click(event.button, event.pos, tree, selected_node)

        elif event.type == pygame.KEYUP and selected_node is not None:
            if event.key == pygame.K_UP:
                selected_node.change_size(0.01)
                tree.update_data_sizes()
                tree.update_rectangles((0, 0, WIDTH, HEIGHT - FONT_HEIGHT))

            elif event.key == pygame.K_DOWN:
                selected_node.change_size(-0.01)
                tree.update_data_sizes()
                tree.update_rectangles((0, 0, WIDTH, HEIGHT - FONT_HEIGHT))

            elif event.key == pygame.K_m:
                selected_node.move(hover_node)
                tree.update_data_sizes()
                tree.update_rectangles((0, 0, WIDTH, HEIGHT - FONT_HEIGHT))

            elif event.key == pygame.K_e:
                selected_node.expand()

            elif event.key == pygame.K_a:
                selected_node.expand_all()

            elif event.key == pygame.K_c:
                selected_node.collapse()

            elif event.key == pygame.K_x:
                selected_node.collapse_all()

        # Update display
        render_display(screen, tree, selected_node, hover_node)


def _handle_click(button: int, pos: Tuple[int, int], tree: TMTree,
                  old_selected_leaf: Optional[TMTree]) -> Optional[TMTree]:
    """Return the new selection after handling the mouse event.

    We need to use old_selected_leaf to handle the case when the selected
    leaf is left-clicked again.
    """
    # left mouse click
    if button == 1:
        selected_leaf = tree.get_tree_at_position(pos)
        if selected_leaf is None:
            return old_selected_leaf
        elif selected_leaf is old_selected_leaf:
            return None
        else:
            return selected_leaf
    # right click or any other click does nothing
    else:
        return old_selected_leaf


def _get_display_text(leaf: Optional[TMTree]) -> str:
    """Return the display text of this leaf.
    """
    if leaf is None:
        return ''
    else:
        return leaf.get_path_string() + '  ({})'.format(leaf.data_size)


def run_treemap_file_system(path: str) -> None:
    """Run a treemap visualisation for the given path's file structure.

    Precondition: <path> is a valid path to a file or folder.
    """
    file_tree = FileSystemTree(path)
    run_visualisation(file_tree)


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'pygame', 'tm_trees', 'papers'
        ],
        'generated-members': 'pygame.*'
    })

    run_treemap_file_system('C:\\Users\\Shayan\\Desktop')
