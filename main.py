import pygame


class Calculator:
    """ A calculator application """
    BACKGROUND_COLOR = (36, 34, 52)
    SPACING = 16  # Distance between buttons
    FONT = "Arial"
    SCREEN_WIDTH = 64 * 4 + SPACING * 5
    SCREEN_HEIGHT = 64 * 5 + SPACING * 7 + 40  # 40 is height of display
    LAYOUT = [["C", "<-", "(", ")"],
               ["7", "8", "9", "/"],
               ["4", "5", "6", "x"],
               ["1", "2", "3", "-"],
               [".", "0", "=", "+"]]
    SPECIAL_KEYS = ["*", "\b", "\r"]

    def __init__(self):
        """ Create application """
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH,
                                               self.SCREEN_HEIGHT))
        pygame.display.set_caption("PyCalc")
        pygame.display.set_icon(pygame.image.load("icon.png").convert_alpha())
        self.display = Display()
        self.buttons = []
        self.create_buttons()
        self.loop()

    def loop(self):
        """ Event and draw loop """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.buttons:
                        if button.is_hovered():
                            self.display.update(button.get_value())
                elif event.type == pygame.KEYDOWN:
                    for row in self.LAYOUT:
                        if event.unicode.upper() in row:
                            self.display.update(event.unicode.upper())
                    if event.unicode in self.SPECIAL_KEYS:
                        self.display.update(event.unicode)
            self.screen.fill(self.BACKGROUND_COLOR)
            self.screen.blit(self.display.get_image(), self.display.rect)
            for button in self.buttons:
                self.screen.blit(button.get_image(), button.rect)
            pygame.display.flip()

    def create_buttons(self):
        """ Create buttons from LAYOUT """
        y = self.SPACING * 2 + Display.HEIGHT
        for row in self.LAYOUT:
            x = self.SPACING
            for char in row:
                self.buttons.append(Button(char, x, y))
                x += self.SPACING + Button.BASE_WIDTH
            y += self.SPACING + Button.BASE_HEIGHT


class Button:
    """ A pressable button that changes color when hovered """
    FONT_SIZE = 32
    BASE_WIDTH = 64
    BASE_HEIGHT = 64
    BORDER_WIDTH = 1
    BACKGROUND_COLOR = (51, 57, 65)
    BORDER_COLOR = (89, 193, 53)
    HIGHLIGHTED_COLOR = (74, 84, 98)
    FONT_COLOR = (255, 255, 255)


    def __init__(self, text, x, y, double_width=False):
        """ Create a button that contains text at given position """
        self.font = pygame.font.SysFont(Calculator.FONT, self.FONT_SIZE)
        self.text = text
        self.label = self.font.render(text, True, self.FONT_COLOR)
        self.rect = pygame.Rect(x, y, self.BASE_WIDTH, self.BASE_HEIGHT)
        if double_width:
            self.rect.width += self.rect.width + Calculator.SPACING

    def get_image(self):
        """ Get current image """
        image = pygame.Surface(self.rect.size)
        if self.is_hovered():
            image.fill(self.HIGHLIGHTED_COLOR)
        else:
            image.fill(self.BACKGROUND_COLOR)
        pygame.draw.rect(image, self.BORDER_COLOR,
                         (0, 0, *self.rect.size), self.BORDER_WIDTH)

        label_half_width = int(self.label.get_width() / 2)
        label_half_height = int(self.label.get_height() / 2)
        x = int(self.rect.width / 2 - label_half_width)
        y = int(self.rect.height / 2 - label_half_height)
        image.blit(self.label, (x, y))
        return image

    def is_hovered(self):
        """ Returns true if the mouse is colliding with the rect """
        return self.rect.collidepoint(*pygame.mouse.get_pos())

    def get_value(self):
        """ Get the text of the button """
        return self.text


class Display:
    """ Displays entered/calculated values and evaluates them when enter or button is pressed """
    FONT_SIZE = 32
    HEIGHT = 40
    LEFT_MARGIN = 5
    TOP_MARGIN = 2
    BORDER_WIDTH = 1
    BACKGROUND_COLOR = (51, 57, 65)
    FONT_COLOR = (255, 255, 255)
    BORDER_COLOR = (89, 193, 53)
    DIGITS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    def __init__(self):
        """ Create a display """
        self.font = pygame.font.SysFont(Calculator.FONT, self.FONT_SIZE)
        self.text = ""
        self.rect = pygame.Rect(Calculator.SPACING, Calculator.SPACING,
                                Calculator.SCREEN_WIDTH - Calculator.SPACING * 2,
                                self.HEIGHT)

    def get_image(self):
        """ Get the current image """
        image = pygame.Surface(self.rect.size)
        image.fill(self.BACKGROUND_COLOR)
        pygame.draw.rect(image, self.BORDER_COLOR,
                         (0, 0, *self.rect.size), self.BORDER_WIDTH)
        label = self.font.render(self.text, True, self.FONT_COLOR)
        image.blit(label, (self.LEFT_MARGIN, self.TOP_MARGIN))
        return image

    def update(self, value):
        """ Update content of display """
        if self.text == "Syntax Error" or self.text == "Division by Zero":
            self.text = ""
        if value == "C":
            self.text = ""
        elif value == "<-" or value == "\b":
            self.text = self.text[:-1]
        elif value == "=" or value == "\r":
            if len(self.text) > 0:
                self.parse_text()
        else:
            self.text += value
            if self.font.size(self.text)[0] > self.rect.width - self.LEFT_MARGIN:
                self.text = self.text[:-1]

    def parse_text(self):
        """ Attempt to calculate the contents of the display """
        
        temp_text = self.text.replace("x", "*")
        self.text = ""
        i = 0
        # Handle multiplication through brackts. For example: 6(2) instead of 6*(2)
        while i < len(temp_text):
            if temp_text[i] in self.DIGITS:
                if i + 1 < len(temp_text) and temp_text[i+1] == "(":
                    temp_text = temp_text[:(i + 1)] + "*" + temp_text[(i + 1):]
                    i += 2
            i += 1
        # Attempt to evaluate
        try:
            temp_text = "%.20f" % eval(temp_text)
            for char in temp_text:
                self.update(char)
            self.remove_trailing_zeros()
        except SyntaxError:
            self.text = "Syntax Error"
        except ZeroDivisionError:
            self.text = "Division by Zero"

    def remove_trailing_zeros(self):
        """ Remove the trailing zeros of floats after calculation """
        if "." in self.text:
            while self.text[-1] == "0" and self.text[-2] == "0":
                self.text = self.text[:-1]


if __name__ == "__main__":
    Calculator()
