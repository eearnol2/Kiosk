import pygame
import pygame.gfxdraw
from Utils import config
from Input import input_handler
from Elements import window_elements
from Utils.logger import log
from Pages import info
from Utils.scale import get_image, scale

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

SCALE_FACTOR = 2


# Map background
class Background(window_elements.HierarchyObject):
    priority = 0  # Draw on bottom

    def __init__(self, window):
        global SCALE_FACTOR
        super().__init__(window)
        self.image = get_image("Resources/asu_poly_map.bmp", SCALE_FACTOR)
        self.imagerect = self.image.get_rect()
        self.width = self.imagerect.width
        self.height = self.imagerect.height
        self.x = self.width/2
        self.y = self.height/2

        self.x_max = self.width/2
        self.x_min = config.screen_x - self.width/2

        self.y_max = self.height/2
        self.y_min = config.screen_y - self.height/2

        self.off_x = 0
        self.off_y = 0

        self.cursor = input_handler.get_cursor()

    def update(self):
        super().update()
        self.cursor = input_handler.get_cursor()
        if self.cursor.is_valid:
            deadband = scale(100)
            min_speed = scale(5)  # Minimum movement speed if moving
            feathering = scale(150)  # Lower = faster

            # Distance from center
            x_off = scale(self.cursor.x_pos - config.screen_x / 2)
            y_off = scale(self.cursor.y_pos - config.screen_y / 2)

            # Check if x and y are outside the deadband (center) range
            if y_off > deadband:
                speed = min_speed + (y_off - deadband) / feathering
                self.y -= speed
            elif y_off < -deadband:
                speed = -min_speed + (y_off + deadband) / feathering
                self.y -= speed

            if x_off > deadband:
                speed = min_speed + (x_off - deadband) / feathering
                self.x -= speed
            elif x_off < -deadband:
                speed = - min_speed + (x_off + deadband) / feathering
                self.x -= speed

            # Make sure map doesn't go off the edge
            if self.x > self.x_max:
                self.x = self.x_max
            elif self.x < self.x_min:
                self.x = self.x_min

            if self.y > self.y_max:
                self.y = self.y_max
            elif self.y < self.y_min:
                self.y = self.y_min

            self.off_x = self.x - self.width/2
            self.off_y = self.y - self.height/2

        self.imagerect.center = (self.x, self.y)

    def draw(self):
        self.screen.blit(self.image, self.imagerect)
        super().draw()

    def get_offset(self):
        return self.off_x, self.off_y


# Box element to select buildings
class InteractionBox(window_elements.HierarchyObject):
    priority = 255  # Draw on top

    def __init__(self, background, x, y, width, height, target):
        global SCALE_FACTOR
        self.background = background
        super().__init__(background)
        self.base_x = scale(x, SCALE_FACTOR)
        self.base_y = scale(y, SCALE_FACTOR)
        self.box = pygame.Rect(self.base_x, self.base_y, scale(width, SCALE_FACTOR), scale(height, SCALE_FACTOR))
        self.is_selected = 0
        self.target = target

    def draw(self):
        super().draw()
        if self.is_selected:
            print(self.is_selected)
            pygame.gfxdraw.rectangle(self.screen, self.box, (255, 0, 0, self.is_selected))

    def update(self):
        # Move box with background so it's "stationary"
        self.box.x = self.base_x + self.background.off_x
        self.box.y = self.base_y + self.background.off_y

        cursor_x = self.background.cursor.x_pos
        cursor_y = self.background.cursor.y_pos

        # If box is selected
        if self.background.cursor.is_valid \
                and self.box.collidepoint(cursor_x, cursor_y):
            # Increase confidence user is actually "clicking" on the box
            self.is_selected += 3
            if self.is_selected > 255:
                log("Button pressed", 2)
                self.is_selected = 0
                self.parent.close()
                info.run(self.master, self.target)
        else:  # Decrease confidence user is "clicking" on the box
            if self.is_selected > 0:
                self.is_selected -= 10
                if self.is_selected < 0:
                    self.is_selected = 0


def run(master):
    log("Map window loading", 2)

    window = window_elements.HierarchyObject(master)
    log("Window set to map", 3)
    background = Background(window)

    #  X Y Width Height
    InteractionBox(background, 837, 837, 135, 119, "TechnologyCenter")
    InteractionBox(background, 1118, 688, 125, 62, "AravaipaAuditorium")
    InteractionBox(background, 1023, 874, 62, 40, "EngineeringStudio")
    InteractionBox(background, 1104, 23, 124, 67, "EagleResidenceHall")
    InteractionBox(background, 1087, 517, 150, 131, "AcademicCenter")
    InteractionBox(background, 967, 535, 109, 101, "AdministrationBuilding")
    InteractionBox(background, 1081, 855, 154, 129, "AgribusinessCenter")
    InteractionBox(background, 1417, 674, 100, 70, "ApliedArtsPavilion")
    InteractionBox(background, 1251, 346, 127, 149, "CenturyHall")
    InteractionBox(background, 1390, 414, 125, 84, "CitrusDiningPavilion")
    InteractionBox(background, 686, 735, 90, 119, "FacultiesManagementPoliceDepartment")
    InteractionBox(background, 970, 739, 146, 79, "PeraltaHall")
    InteractionBox(background, 969, 683, 87, 54, "PicachoHall")
    InteractionBox(background, 832, 362, 128, 126, "Quads")
    InteractionBox(background, 1390, 749, 116, 71, "SantaCatalinaHall")
    InteractionBox(background, 1109, 742, 140, 64, "SantanHall")
    InteractionBox(background, 1867, 4, 227, 154, "SimulatorBuilding")
    InteractionBox(background, 1266, 519, 148, 112, "StudentUnion")
    InteractionBox(background, 1413, 522, 114, 111, "SunDevilFitnessComplexPolytechnic")
    InteractionBox(background, 1259, 682, 111, 61, "SuttonHall")
    InteractionBox(background, 1259, 750, 113, 67, "WannerHall")
    InteractionBox(background, 1238, 849, 89, 95, "BellHall")
    InteractionBox(background, 1247, 942, 134, 43, "DeanHall")
    InteractionBox(background, 1317, 23, 128, 70, "FalconResidenceHall")
    InteractionBox(background, 1449, 18, 78, 166, "MustangResidenceHall")
    InteractionBox(background, 1529, 740, 116, 110, "PaloBlancoHall")
    InteractionBox(background, 1253, 94, 127, 76, "PhantomResidenceHall")
    InteractionBox(background, 1059, 97, 118, 64, "TalonResidenceHall")

    log("Loaded map window", 3)
