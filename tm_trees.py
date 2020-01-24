"""
=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations
import os
import math
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None
        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        # You will change this in Task 5
        if len(self._subtrees) > 0:
            self._expanded = False
            self.data_size = 0
            for tree in self._subtrees:
                tree._parent_tree = self
                self.data_size += tree.data_size
        else:
            self._expanded = False
            self.data_size = data_size

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        """
        # Read the handout carefully to help get started identifying base cases,
        # then write the outline of a recursive step.
        #
        # Programming tip: use "tuple unpacking assignment" to easily extract
        # elements of a rectangle, as follows.
        x, y, width, height = rect
        self.rect = rect
        if self.data_size == 0:
            return
        elif width > height:
            total = self.data_size
            counter = 0
            for subtree in self._subtrees:
                percentage = subtree.data_size / total
                smaller_width = width * percentage
                if subtree != self._subtrees[-1]:
                    counter += smaller_width - int(smaller_width)
                    smaller_width = int(smaller_width)
                else:
                    if (smaller_width + counter) - \
                            (smaller_width + int(counter)) < 0.9999999:
                        smaller_width = math.ceil(smaller_width + counter)
                    else:
                        smaller_width += counter
                        smaller_width = int(smaller_width)
                rect = x, y, smaller_width, height
                subtree.update_rectangles(rect)
                x += smaller_width
        else:
            total = self.data_size
            counter = 0
            for subtree in self._subtrees:
                percentage = subtree.data_size / total
                smaller_height = height * percentage
                if subtree != self._subtrees[-1]:
                    counter += smaller_height - int(smaller_height)
                    smaller_height = int(smaller_height)
                else:
                    smaller_height += counter
                    smaller_height = int(smaller_height)
                rect = x, y, width, smaller_height
                subtree.update_rectangles(rect)
                y += smaller_height

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        if self.data_size == 0:
            return []
        elif not self._expanded:
            return [(self.rect, self._colour)]
        else:
            lst = []
            for subtree in self._subtrees:
                lst.extend(subtree.get_rectangles())
            return lst

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, return the
        tree represented by the rectangle that is closer to the origin.
        """
        required_x, required_y = pos
        if not self._expanded:
            return self
        else:
            a = None
            for subtree in self._subtrees:
                x, y, width, height = subtree.rect
                if x <= required_x <= x + width and \
                        y <= required_y <= y + height:
                    a = subtree.get_tree_at_position(pos)
            return a

    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        """
        if len(self._subtrees) == 0:
            return self.data_size
        else:
            total_size = 0
            for subtree in self._subtrees:
                total_size += subtree.update_data_sizes()
            self.data_size = total_size
            return total_size

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """
        if len(self._subtrees) == 0 and len(destination._subtrees) != 0:
            self._parent_tree._subtrees.remove(self)
            destination._subtrees.append(self)
            self._parent_tree = destination
        else:
            return

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        """
        if len(self._subtrees) == 0:
            if factor > 0:
                self.data_size = math.ceil(self.data_size * (1 + factor))
            else:
                if self.data_size > 1:
                    self.data_size = math.trunc(self.data_size * (1 + factor))
        else:
            return

    def expand(self) -> None:
        """Expand this tree so that it's subtrees are in the displayed tree.
        """
        if not len(self._subtrees) == 0:
            self._expanded = True

    def expand_all(self) -> None:
        """
        Expand this tree along with all of it's subtrees,
         and descendants.
        """
        if not len(self._subtrees) == 0:
            self._expanded = True
            for subtree in self._subtrees:
                subtree.expand_all()

    def collapse(self) -> None:
        """
        Collapse this tree so that it is no longer in the displayed tree
        """
        if self._parent_tree:
            self._parent_tree._expanded = False
        self._expanded = False
        for subtree in self._subtrees:
            subtree.collapse()

    def collapse_all(self) -> None:
        """
        Collapse all of this tree's subtrees and descendants so that they are no
        longer in the displayed tree.
        """
        root = self._get_tree_root()
        for subtree in root._subtrees:
            subtree.collapse()

    def _get_tree_root(self) -> TMTree:
        """
        Return the top-most root of this tree.
        """
        if not self._parent_tree:
            return self
        for subtree in self._parent_tree._subtrees:
            root = subtree._parent_tree._get_tree_root()
        return root

    # Methods for the string representation
    def get_path_string(self, final_node: bool = True) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this tree between each
        tree's name. If <final_node>, then add the suffix for the tree.
        """
        if self._parent_tree is None:
            path_str = self._name
            if final_node:
                path_str += self.get_suffix()
            return path_str
        else:
            path_str = (self._parent_tree.get_path_string(False) +
                        self.get_separator() + self._name)
            if final_node or len(self._subtrees) == 0:
                path_str += self.get_suffix()
            return path_str

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """
    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        # Remember that you should recursively go through the file system
        # and create new FileSystemTree objects for each file and folder
        # encountered.
        #
        # Also remember to make good use of the superclass constructor!
        if os.path.isdir(path):
            subtrees = []
            name = os.path.basename(path)
            for filename in os.listdir(path):
                sub_path = os.path.join(path, filename)
                subtree = FileSystemTree(sub_path)
                subtrees.append(subtree)
            TMTree.__init__(self, name, subtrees, os.path.getsize(path))
        else:
            name = os.path.basename(path)
            TMTree.__init__(self, name, [], os.path.getsize(path))

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (file)'
        else:
            return ' (folder)'


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
