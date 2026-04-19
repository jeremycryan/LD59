from image_manager import ImageManager
from primitives import *
import constants as c


class Island(GameObject):

    SLICES_X = 14
    SLICES_Y = 14

    def __init__(self, game):
        super().__init__(game)
        self.mask = ImageManager.load("images/water_mask.png")
        self.surf = ImageManager.load_copy("images/land_image.png")
        self.position = Pose((2000, 0))

        self.slices = []
        self.slice_positions = []
        self.generate_slices()

    def generate_slices(self):
        buffer = 0
        slice_surf = pygame.Surface((self.surf.get_width()//self.SLICES_X + buffer, self.surf.get_height()//self.SLICES_Y + buffer), pygame.SRCALPHA)
        for y in range(self.SLICES_Y):
            row = []
            position_row = []
            by = -y*slice_surf.get_height()
            for x in range(self.SLICES_X):
                bx = -x*slice_surf.get_width()
                slice_surf.fill((0, 0, 0, 0))
                slice_surf.blit(self.surf, (bx, by))
                row.append(slice_surf.copy())
                position_row.append((-bx + slice_surf.get_width()//2 - buffer//2, -by + slice_surf.get_height()//2 - buffer//2))
            self.slices.append(row)
            self.slice_positions.append(position_row)

    def draw_slices(self, surf, offset=(0, 0), scale=1):
        for y, row in enumerate(self.slices):
            for x, slice in enumerate(row):
                original_position = self.slice_positions[y][x]
                cx = original_position[0]*scale + offset[0]*scale - self.surf.get_width()*scale//2 + self.position.x*scale - slice.get_width()*scale//2
                cy = original_position[1]*scale + offset[1]*scale - self.surf.get_height()*scale//2 + self.position.y*scale - slice.get_height()*scale//2

                if (cx > c.WINDOW_WIDTH) or cy > c.WINDOW_HEIGHT:
                    continue
                if (cx < -slice.get_width()*scale or cy < -slice.get_height()*scale):
                    continue
                slice = scale_surface_by(slice, scale)
                surf.blit(slice, (cx, cy))


    def update(self, dt, events):
        pass

    def draw(self, surf, offset=(0, 0), scale = 1):

        self.draw_slices(surf, offset, scale)
        return
        surf_to_draw = scale_surface_by(self.mask, scale)

        x = self.position.x*scale + offset[0]*scale -surf_to_draw.get_width()//2
        y = self.position.y*scale + offset[1]*scale - surf_to_draw.get_height()//2

        surf.blit(surf_to_draw, (x, y))

    def water_at(self, position):
        x = position[0] - self.position.x + self.mask.get_width()//2
        y = position[1] - self.position.y + self.mask.get_height()//2
        pixel = self.mask.get_at((int(x), int(y)))
        if pixel.a > 64:
            return False
        return True

    def water_or_dock_at(self, position):
        x = position[0] - self.position.x + self.mask.get_width()//2
        y = position[1] - self.position.y + self.mask.get_height()//2
        pixel = self.mask.get_at((int(x), int(y)))
        if pixel.a > 192:
            return False
        return True

    def nearest_water_pixel(self, start_position, end_position, exclude_dock = False):
        divs = 4
        diff = end_position - start_position
        for i in range(divs):
            pos = start_position + diff * ((i+1)/divs)
            if (exclude_dock):
                if self.water_or_dock_at((int(pos.x), int(pos.y))):
                    return pos
            else:
                if self.water_at((int(pos.x), int(pos.y))):
                    return pos
        return end_position


    def nearest_non_water_pixel(self, position, direction_to_prioritize, exclude_dock = False):
        xdir = direction_to_prioritize[0]
        ydir = direction_to_prioritize[1]

        current_area = set()
        next_current_area = set()
        exhausted_area = set()


        x = int(position[0])
        y = int(position[1])

        current_area.add((x, y))

        while True:
            # Go once in desired direction
            if (xdir != 0 or ydir != 0):
                next_current_area = next_current_area.union(current_area)
                for pixel in current_area:
                    pixel_in_direction = (pixel[0] + xdir, pixel[1] + ydir)
                    if pixel_in_direction not in current_area:
                        next_current_area.add(pixel_in_direction)

            # expand twice
            current_area = current_area.union(next_current_area)

            for _ in range(1):
                for pixel in current_area:
                    for direction in (1, 0), (0, 1), (-1, 0), (0, -1):
                        pixel_in_direction = (pixel[0] + direction[0], pixel[1] + direction[1])
                        if pixel_in_direction not in current_area:
                            next_current_area.add(pixel_in_direction)
                current_area = current_area.union(next_current_area)

            for pixel in sorted(current_area, key= lambda x: direction_to_prioritize[0]*(x[0] - position[0]) + direction_to_prioritize[1]*(x[1] - position[1]) - abs(position[0] - x[0])/5 - abs(position[1] - x[1])/5, reverse=True):
                if pixel in exhausted_area:
                    continue
                if (exclude_dock):
                    if not self.water_or_dock_at(pixel):
                        return pixel
                else:
                    if not self.water_at(pixel):
                        return pixel
                exhausted_area.add(pixel)
