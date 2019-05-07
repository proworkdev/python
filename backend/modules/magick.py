import os
from modules.settings import Settings


class MagickProcessor:
    def __init__(self):
        self.settings = Settings()

    def apply_desaturation(self, in_path, out_path=None):
        if not out_path:
            out_path = in_path
        cmd_string = 'convert -modulate 100,80,100 {} {}'.format(in_path, out_path)
        return cmd_string

    def apply_displacement(self, displacement_factor, displacement_map, in_path, out_path=None):
        if not out_path:
            out_path = in_path
        cmd_string = 'composite {} {} -displace {} {}'.format(
            displacement_map, in_path, displacement_factor, out_path
        )
        return cmd_string

    def apply_shading(self, displaced_design, white_template, out_path=None):
        if not out_path:
            out_path = displaced_design
        cmd_string = 'convert {} {} -compose Multiply -composite {}'.format(
            displaced_design, white_template, out_path
        )
        return cmd_string

    def compose_images(self, image_one, image_two, out_path):
        cmd_string = 'convert {} {} -composite {}'.format(
            image_one, image_two, out_path
        )
        return cmd_string

    def run_cmd(self, cmd_string):
        local = False
        if local:
            cmd_string = 'magick ' + cmd_string
        os.system(cmd_string)
