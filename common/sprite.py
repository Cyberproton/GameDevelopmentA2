import json

import pygame
from pygame.surface import Surface


class Sprite:
    def __init__(self, surface: Surface, rect: (float, float, float, float), offset: (float, float) = (0, 0), step=-1):
        self.surface = surface
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2]
        self.h = rect[3]
        self.offset_x = offset[0]
        self.offset_y = offset[1]
        self.step = step


class SpriteSheet:
    def __init__(self, source_filename: str, metadata_filename: str):
        """Load the sheet."""
        try:
            self.sheet = pygame.image.load(source_filename).convert()
            with open(metadata_filename) as meta_file:
                self.metadata = json.load(meta_file)
            meta_file.close()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {source_filename}")
            raise SystemExit(e)

    def image_at(self, rectangle, colorkey=None) -> Surface:
        """Load a specific image from a specific rectangle."""
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def parse_sprites(self, sprite_name) -> list[Sprite]:
        t = self.get_metadata_or_value(["frames", sprite_name, "type"], "single")
        x = self.get_metadata(["frames", sprite_name, "x"])
        y = self.get_metadata(["frames", sprite_name, "y"])
        w = self.get_metadata(["frames", sprite_name, "w"])
        h = self.get_metadata(["frames", sprite_name, "h"])
        offset_x = self.get_metadata(["frames", sprite_name, "offset_x"])
        offset_y = self.get_metadata(["frames", sprite_name, "offset_y"])
        duplicate = self.get_metadata(["frames", sprite_name, "duplicate"])
        step = self.get_metadata(["frames", sprite_name, "step"])

        if t == "single":
            image = self.image_at((x, y, w, h), (255, 255, 255))
            return [Sprite(image, (x, y, w, h))]
        elif t == "auto":
            count = self.get_metadata(["frames", sprite_name, "count"])
            sprites = []
            for i in range(0, count):
                image = self.image_at((x, y, w, h), (255, 255, 255)).convert()
                sprites.append(Sprite(image, (x, y, w, h)))
                x += w
            return sprites
        elif t == "array":
            count = self.get_metadata(["frames", sprite_name, "count"])
            sprites = []
            for i in range(0, count):
                image = self.image_at((x[i], y[i], w[i], h[i]), (255, 255, 255))
                ox = offset_x[i] if offset_x and len(offset_x) > i else 0
                oy = offset_y[i] if offset_y and len(offset_y) > i else 0
                s = step[i] if step and len(step) > i else -1
                sprite = Sprite(image, (x[i], y[i], w[i], h[i]), (ox, oy), s)
                sprites.append(sprite)
                if duplicate and len(duplicate) > i:
                    for j in range(0, duplicate[i]):
                        sprites.append(sprite)
            return sprites
        else:
            return []

    def parse_sprites_horizontal(self, sprite_name) -> list[Sprite]:
        x = self.get_metadata(["frames", sprite_name, "x"])
        x_m = self.get_metadata_or_value(["frames", sprite_name, "x-m"], 0)
        y = self.get_metadata(["frames", sprite_name, "y"])
        w = self.get_metadata(["frames", sprite_name, "w"])
        h = self.get_metadata(["frames", sprite_name, "h"])
        count = self.get_metadata(["frames", sprite_name, "count"])
        print(count)
        sprites = []
        for i in range(0, count):
            image = self.image_at((x, y, w, h), (255, 255, 255))
            sprites.append(Sprite(image, (x, y, w, h)))
            x += w + x_m
        return sprites

    def get_metadata_or_else(self, path, default_path):
        value = self.get_metadata(path)
        if value is None:
            return value
        return self.get_metadata(default_path)

    def get_metadata_or_value(self, path, default_value):
        value = self.get_metadata(path)
        if value is None:
            return default_value
        return value

    def get_metadata(self, path):
        current = self.metadata
        for p in path:
            if p not in current:
                return None
            current = current[p]
        return current

    def images_at(self, rects, colorkey=None):
        """Load a bunch of images and return them as a list."""
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey=None):
        """Load a whole strip of images, and return them as a list."""
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

    def load_grid_images(self, num_rows, num_cols, x_margin=0, x_padding=0,
                         y_margin=0, y_padding=0):
        """Load a grid of images.
        x_margin is space between top of sheet and top of first row.
        x_padding is space between rows.
        Assumes symmetrical padding on left and right.
        Same reasoning for y.
        Calls self.images_at() to get list of images.
        """
        sheet_rect = self.sheet.get_rect()
        sheet_width, sheet_height = sheet_rect.size

        # To calculate the size of each sprite, subtract the two margins,
        #   and the padding between each row, then divide by num_cols.
        # Same reasoning for y.
        x_sprite_size = (sheet_width - 2 * x_margin
                         - (num_cols - 1) * x_padding) / num_cols
        y_sprite_size = (sheet_height - 2 * y_margin
                         - (num_rows - 1) * y_padding) / num_rows

        sprite_rects = []
        for row_num in range(num_rows):
            for col_num in range(num_cols):
                # Position of sprite rect is margin + one sprite size
                #   and one padding size for each row. Same for y.
                x = x_margin + col_num * (x_sprite_size + x_padding)
                y = y_margin + row_num * (y_sprite_size + y_padding)
                sprite_rect = (x, y, x_sprite_size, y_sprite_size)
                sprite_rects.append(sprite_rect)

        grid_images = self.images_at(sprite_rects)
        print(f"Loaded {len(grid_images)} grid images.")

        return grid_images


class PlayerSpriteSet:
    """Represents a set of chess pieces.
    Each piece is an object of the Piece class.
    """

    def __init__(self, chess_game):
        """Initialize attributes to represent the overall set of pieces."""

        self.chess_game = chess_game
        self.pieces = []
        self._load_pieces()

    def _load_pieces(self):
        """Builds the overall set:
        - Loads images from the sprite sheet.
        - Creates a Piece object, and sets appropriate attributes
          for that piece.
        - Adds each piece to the list self.pieces.
        """
        filename = 'images/chess_pieces.bmp'
        piece_ss = SpriteSheet(filename)

        # Create a black king.
        b_king_rect = (68, 70, 85, 85)
        b_king_image = piece_ss.image_at(b_king_rect)

        b_king = Sprite()
        b_king.surface = b_king_image
        b_king.name = 'king'
        b_king.color = 'black'
        self.pieces.append(b_king)
