import pygame


class Calculator:
    SCREEN_WIDTH = 336
    SCREEN_HEIGHT = 476
    PRIMARY_COLOR = (255, 255, 255)
    SECONDARY_COLOR = (0, 0, 0)
    HIGHLIGHTED_COLOR = (40, 40, 40)
    SPACING = 16
    FONT = "Consolas"

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH,
                                               self.SCREEN_HEIGHT))
        pygame.display.set_caption("PyCalc")
        pygame.display.set_icon(pygame.image.load("icon.png").convert_alpha())
        self.display = Display()
        self.layout = [["C", "<-", "(", ")"],
                       ["7", "8", "9", "/"],
                       ["4", "5", "6", "x"],
                       ["1", "2", "3", "-"],
                       [".", "0", "=", "+"]]
        self.special_keys = ["*", "\b", "\r"]
        self.buttons = []
        self.create_buttons()

    def loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.buttons:
                        if button.is_hovered():
                            self.display.update(button.get_value())
                elif event.type == pygame.KEYDOWN:
                    for row in self.layout:
                        if event.unicode.upper() in row:
                            self.display.update(event.unicode.upper())
                    if event.unicode in self.special_keys:
                        self.display.update(event.unicode)
            self.screen.fill(self.SECONDARY_COLOR)
            self.screen.blit(self.display.get_image(), self.display.rect)
            for button in self.buttons:
                self.screen.blit(button.get_image(), button.rect)
            pygame.display.flip()

    def create_buttons(self):
        for row in range(len(self.layout)):
            for col in range(len(self.layout[0])):
                x = self.SPACING
                x += self.SPACING * col + Button.BASE_WIDTH * col
                y = self.SPACING * 2 + Display.HEIGHT
                y += self.SPACING * row + Button.BASE_HEIGHT * row
                self.buttons.append(Button(self.layout[row][col], x, y))


class Button:
    FONT_SIZE = 36
    BASE_WIDTH = 64
    BASE_HEIGHT = 64
    BORDER_WIDTH = 1

    def __init__(self, text, x, y, double_width=False):
        self.font = pygame.font.SysFont(Calculator.FONT, self.FONT_SIZE)
        self.text = text
        self.label = self.font.render(text, True, Calculator.PRIMARY_COLOR)
        self.rect = pygame.Rect(x, y, self.BASE_WIDTH, self.BASE_HEIGHT)
        if double_width:
            self.rect.width += self.rect.width + Calculator.SPACING

    def get_image(self):
        image = pygame.Surface(self.rect.size)
        if self.is_hovered():
            image.fill(Calculator.HIGHLIGHTED_COLOR)
        else:
            image.fill(Calculator.SECONDARY_COLOR)
        pygame.draw.rect(image, Calculator.PRIMARY_COLOR,
                         (0, 0, *self.rect.size), self.BORDER_WIDTH)

        label_half_width = self.label.get_width() / 2
        label_half_height = self.label.get_height() / 2
        image.blit(self.label, (self.rect.width / 2 - label_half_width,
                                self.rect.height / 2 - label_half_height))
        return image

    def is_hovered(self):
        return self.rect.collidepoint(*pygame.mouse.get_pos())

    def get_value(self):
        return self.text


class Display:
    FONT_SIZE = 32
    HEIGHT = 40
    LEFT_MARGIN = 5
    TOP_MARGIN = 5
    BORDER_WIDTH = 1

    def __init__(self):
        self.font = pygame.font.SysFont(Calculator.FONT, self.FONT_SIZE)
        self.text = ""
        self.rect = pygame.Rect(Calculator.SPACING, Calculator.SPACING,
                                Calculator.SCREEN_WIDTH - Calculator.SPACING * 2,
                                self.HEIGHT)

    def get_image(self):
        image = pygame.Surface(self.rect.size)
        image.fill(Calculator.SECONDARY_COLOR)
        pygame.draw.rect(image, Calculator.PRIMARY_COLOR,
                         (0, 0, *self.rect.size), self.BORDER_WIDTH)
        label = self.font.render(self.text, True, Calculator.PRIMARY_COLOR)
        image.blit(label, (self.LEFT_MARGIN, self.TOP_MARGIN))
        return image

    def update(self, value):
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
        digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        temp_text = self.text.replace("x", "*")
        self.text = ""
        i = 0
        while i < len(temp_text):
            if temp_text[i] in digits:
                if i + 1 < len(temp_text) and temp_text[i+1] == "(":
                    temp_text = temp_text[:(i + 1)] + "*" + temp_text[(i + 1):]
                    i += 2
            i += 1
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
        if "." in self.text:
            while self.text[-1] == "0" and self.text[-2] == "0":
                self.text = self.text[:-1]


if __name__ == "__main__":
    Calculator().loop()
