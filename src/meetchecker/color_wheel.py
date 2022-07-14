from itertools import cycle


class ColorWheel:
    DEFAULT = [
        "#fd0e35",  # tractor_red
        "#062a78",  # catalina_blue
        "#c71585",  # medium_violet_red
        "#00bfff",  # deep_sky_blue
        "#9400d3",  # dark_violet
        "#138808",  # india_green
        "#00a693",  # persian_green
        "#bb6528",  # ruddy_brown
        "#ff8c00",  # dark_orange
        "#4b0082",  # indigo_web
    ]

    def __init__(self, colorwheel_colors=None, exclude=None):
        self.colors = colorwheel_colors or self.DEFAULT
        if exclude:
            self.colors = list(set(self.colors).difference(exclude))
        self.iter = cycle(self.colors)

    @classmethod
    def from_checks(cls, checks, colorwheel_colors=None):
        colors_specifically_set = []
        for check in checks.values():
            if color := check.get("color"):
                colors_specifically_set.append(color)
        return cls(colorwheel_colors=colorwheel_colors, exclude=colors_specifically_set)

    def __next__(self):
        return next(self.iter)
