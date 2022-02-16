import colorsys


class HlsColor:
    """
    Class for handling HLS colors. Component values are between 0 and 1
    """
    def __init__(self, hue: float, lightness: float, saturation: float):
        """
        Constructor

        Args:
            hue: hue value
            lightness: lightness
            saturation: saturation
        """
        self.hue = hue
        self.lightness = lightness
        self.saturation = saturation

    def to_rgb(self):
        """
        Translates color to RGB

        Returns:
            color in RGB
        """
        result = colorsys.hls_to_rgb(
            h=self.hue,
            l=self.lightness,
            s=self.saturation
        )

        return RgbColor(red=result[0] * 255, green=result[1] * 255, blue=result[2] * 255)


class RgbColor:
    """
    Class for handling RGB colors. Component values are between 0 and 255
    """

    def __init__(self, red: float, green: float, blue: float):
        """
        Constructor

        Args:
            red: red
            green: green
            blue: blue
        """
        self.red = red
        self.green = green
        self.blue = blue

    def to_css(self) -> str:
        """
        Returns value as CSS color
        Returns:
            value as CSS color
        """
        return f"rgb({round(self.red)}, {round(self.green)}, {round(self.blue)})"

    def to_hls(self) -> HlsColor:
        """
        Translates color to HLS color

        Returns:
            Color as HLS
        """
        result = colorsys.rgb_to_hls(
            r=self.red / 255,
            g=self.green / 255,
            b=self.blue / 255
        )

        return HlsColor(hue=result[0], lightness=result[1], saturation=result[2])
