import numpy
import os
import json

from PIL import Image, ImageOps

from modules.settings import Settings
from modules.db import DB
from modules.magick import MagickProcessor


class DesignProcessor:
    def __init__(self, design_filename, template_id, colorize=None, edits=None):
        self.settings = None
        self.design_path = None
        self.design_url = None
        self.db = None

        self.design_filename = design_filename
        self.template_id = template_id
        self.colorize = colorize
        self.edits = edits

        self.setup()

        self.result = None
        self.result_filename = self.design_filename.replace('.jpg', '.png')
        self.result_path = self.settings.path_for_image('download', self.result_filename)

    def setup(self):
        self.settings = Settings()
        self.db = DB()
        self.design_path = self.settings.path_for_image('design', self.design_filename)
        self.design_url = self.settings.url_for_image('design', self.design_filename)
        if self.edits:
            self.edits = json.loads(self.edits)

    def process(self, preview=False):
        template = TemplateImage(self.template_id, self.design_filename, color=self.colorize, db=self.db,
                                 is_preview=preview)
        if preview:
            self.result_path = self.settings.path_for_image('preview', self.result_filename)
        else:
            self.result_path = self.settings.path_for_image('download', self.result_filename)
        print('PROCESS: {}'.format(self.result_path))
        if template.template_type == 1:
            design = DesignImage(self.design_filename, db=self.db, edits=self.edits)
            design.resize_for_template(template)
            design.transform_for_template(template)
            result = self.combine_images(template, design)
            result.save(self.result_path)
        if template.template_type == 2:
            design = DesignImage(self.design_filename, edits=self.edits, db=self.db)
            design.resize_for_template(template)
            design.transform_for_template(template)
            design.save()
            design_path = design.path
            # Save template:
            if not template.is_found_in_db:
                template.save()
                template.colorize()
            template_color_path = template.path_color
            template_white_path = template.path_white
            displacement_map_path = template.displacement_map_path if not preview \
                else template.displacement_map_preview_path
            mp = MagickProcessor()
            displacement_ratio = int(max(template.img.size) * 0.0035)  # 7.5

            # Additional files paths:
            design_desaturated = self.settings.path_for_image('tmp', 'des-desaturated-{}'.format(self.result_filename))
            design_displaced = self.settings.path_for_image('tmp', 'des-displaced-{}'.format(self.result_filename))
            design_shaded = self.settings.path_for_image('tmp', 'des-shaded-{}'.format(self.result_filename))

            c_desaturate = mp.apply_desaturation(design_path, design_desaturated)
            c_displace = mp.apply_displacement(displacement_ratio, displacement_map_path, design_desaturated,
                                               design_displaced)
            c_shade = mp.apply_shading(design_displaced, template_white_path, design_shaded)
            c_comp = mp.compose_images(template_color_path, design_shaded, self.result_path)
            mp.run_cmd(c_desaturate)
            mp.run_cmd(c_displace)
            mp.run_cmd(c_shade)
            mp.run_cmd(c_comp)
            """
            convert -modulate 100,80,100 design_positioned.png design_desaturated.png
            composite map_displacement.png design_desaturated.png -displace 7.5 design_displaced.png
            convert design_displaced.png template_white.png -compose Multiply -composite design_shaded.png
            convert template_color.png design_shaded.png -composite output.png"""

    def response_preview_options(self):
        response_options = {
            'url': self.settings.url_for_image('preview', self.result_filename),
        }
        return response_options

    def response_download_options(self):
        response_options = {
            'filename': self.result_filename
        }
        return response_options

    @staticmethod
    def combine_images(template_object, design_object):
        template_image = template_object.img
        design_image = design_object.img
        if template_image.mode != design_image.mode:
            new_template_image = Image.new(design_image.mode, template_image.size)
            new_template_image.paste(template_image)
            template_image = new_template_image
        result = Image.new(design_image.mode, template_image.size)
        print('template mode: {}, design mode: {}, result mode: {}'.format(template_image.mode, design_image.mode,
                                                                           result.mode))
        print('template size: {}, design size: {}, result size: {}'.format(template_image.size, design_image.size,
                                                                           result.size))
        # Paste template image into result:
        if template_image.mode == 'RGB':
            # Without alpha
            result.paste(template_image, (0, 0))
        elif template_image.mode == 'RGBA':
            # With alpha
            result.paste(template_image, (0, 0), template_image)
        if design_image.mode == 'RGB':
            # Without alpha
            result.paste(design_image, (0, 0))
        elif design_image.mode == 'RGBA':
            # With alpha
            result.paste(design_image, (0, 0), design_image)
        return result


class TemplateImage:
    def __init__(self, template_id, design_filename, color=None, db=None, is_preview=False):
        self.settings = Settings()
        self.db = db if db else DB()

        self.template_id = template_id

        self.is_preview = is_preview

        self.dir_relative = self.settings.relative_template_dir(template_id)

        self.img = None
        self.img_white = None
        self.width = None
        self.height = None
        self.ratio = (1, 1)

        self.transform_plane = None
        self.paste_coordinates = None

        self.template_type = None

        self.img_colored = None
        self.colorizable = None
        self.colorize_color = color
        self.color_mask_filename = None
        self.color_mask_path = None

        self.displacement_map_path = None
        self.displacement_map_preview_path = None

        # Get template options:
        self.options = None
        self.get_options()

        self.design_filename = design_filename
        self.design_path = self.settings.path_for_image('design', design_filename)

        self.base_template_filename = self.options.get('filename')
        self.base_template_path = self.settings.path_to_template_file(template_id)

        self.filename_white = 'tpl_white_' + self.design_filename
        self.filename_color = 'tpl_colored_' + self.design_filename
        self.relative_white = self.settings.relative_path_for_processed_template(self.template_id, self.filename_white)
        self.relative_color = self.settings.relative_path_for_processed_template(self.template_id, self.filename_color)
        self.path_white = self.settings.path_relative_to_full(self.relative_white)
        self.path_color = self.settings.path_relative_to_full(self.relative_color)

        self.is_found_in_db = self.read_from_db()
        self.check_image_loaded()

        if self.is_preview:
            self.resize_for_preview()

    def read_from_db(self):
        colorized_template = self.db.get_colorized_template(self.template_id, self.colorize_color, self.is_preview)
        if not colorized_template:
            print('Colorized template was not found!')
            return False
        print('Colorized template was found!')
        self.is_preview = colorized_template.is_preview
        self.ratio = colorized_template.ratio
        self.filename_white = colorized_template.filename_white
        self.filename_color = colorized_template.filename_color
        self.relative_white = self.settings.relative_path_for_processed_template(self.template_id, self.filename_white)
        self.relative_color = self.settings.relative_path_for_processed_template(self.template_id, self.filename_color)
        self.path_white = self.settings.path_relative_to_full(self.relative_white)
        self.path_color = self.settings.path_relative_to_full(self.relative_color)
        return True

    def get_url(self):
        relative_path = self.settings.relative_path_for_processed_template(self.template_id, self.filename_color)
        return self.settings.path_relative_to_url(relative_path)

    def get_options(self):
        self.options = self.db.get_template_options(self.template_id)
        self.transform_plane, self.paste_coordinates = self.process_bindings()
        # Get colorizable options:
        self.colorizable = self.options.get('colorizable')
        if self.colorizable:
            # Set color mask filename:
            self.color_mask_filename = self.colorizable.get('color_mask')
            # Get color mask relative path:
            color_mask_path_relative = os.path.join(self.dir_relative, self.color_mask_filename)
            # Get and set color mask full path:
            self.color_mask_path = self.settings.path_relative_to_full(color_mask_path_relative)
            print('get_options: Template {} is colrizable. Mask: {}'.format(self.template_id, self.color_mask_filename))
        tpl_type = self.options.get('type')
        self.template_type = tpl_type if tpl_type else 1

        # Get disposition map:
        displacement_map_options = self.options.get('displacement_map')
        displacement_map_filename = displacement_map_options.get('d-map-filename') if displacement_map_options else None
        displacement_map_preview_filename = displacement_map_options.get(
            'd-map-preview-filename') if displacement_map_options else None

        if not displacement_map_filename or not displacement_map_preview_filename:
            return

        displacement_map_relative_path = os.path.join(self.dir_relative, displacement_map_filename)
        displacement_map_preview_relative_path = os.path.join(self.dir_relative, displacement_map_preview_filename)
        self.displacement_map_path = self.settings.path_relative_to_full(
            displacement_map_relative_path) if displacement_map_filename else None
        self.displacement_map_preview_path = self.settings.path_relative_to_full(
            displacement_map_preview_relative_path) if displacement_map_filename else None

    def process_bindings(self):
        # Get bindings for options:
        bindings = self.options.get('bindings')
        if not bindings:
            raise Exception('No bindings in options for {}'.format(self.template_id))

        # Make plane and paste coordinates from bindings:
        # plane = [A-A, B-A, C-A, D-A]
        a, b, c, d = bindings['a'], bindings['b'], bindings['c'], bindings['d']

        a, b, c, d = self.bindings_with_ratio(a, b, c, d)

        a0 = [0, 0]
        b0 = [b[0] - a[0], b[1] - a[1]]
        c0 = [c[0] - a[0], c[1] - a[1]]
        d0 = [d[0] - a[0], d[1] - a[1]]
        plane = [a0, b0, c0, d0]
        offset_x = 0
        offset_y = 0

        # Find offsets for x and y in case of negative point coordinate values:
        for point in plane:
            px = point[0]
            py = point[1]
            if px < offset_x:
                offset_x = px
            if py < offset_y:
                offset_y = py

        # Modify plane with offsets:
        offset_plane = []
        for point in plane:
            x = point[0] - offset_x
            y = point[1] - offset_y
            offset_plane.append([x, y])
        paste_coords = [a[0] + offset_x, a[1] + offset_y]

        self.transform_plane = offset_plane
        self.paste_coordinates = paste_coords

        return offset_plane, paste_coords

    def bindings_with_ratio(self, a, b, c, d):
        a1 = tuple(map(lambda x, y: int(x * y), self.ratio, a))
        b1 = tuple(map(lambda x, y: int(x * y), self.ratio, b))
        c1 = tuple(map(lambda x, y: int(x * y), self.ratio, c))
        d1 = tuple(map(lambda x, y: int(x * y), self.ratio, d))
        return a1, b1, c1, d1

    def read_original_template(self):
        """
        Reads the image from it's path and creates it's plane
        """
        img = Image.open(self.base_template_path).convert('RGBA')
        self.width, self.height = img.size
        self.img = img
        self.img_white = img

    def read_loaded_template(self):
        """
        Reads the image from it's path and creates it's plane
        """
        img = Image.open(self.path_color).convert('RGBA')
        self.width, self.height = img.size
        self.img = img
        self.img_white = Image.open(self.base_template_path).convert('RGBA')

    def resize_for_preview(self):
        """
        Resizes current template img to preview size
        """
        self.check_image_loaded()
        if self.is_found_in_db:
            self.process_bindings()
            return
        preview_size = self.settings.preview_size
        old_size = self.img.size
        self.img.thumbnail(preview_size, Image.ANTIALIAS)
        new_size = self.img.size
        new_ratio = tuple(map(lambda x, y: x / y, new_size, old_size))
        self.ratio = new_ratio
        print('template resized for preview with ratio: {}'.format(self.ratio))
        self.process_bindings()
        return new_ratio

    def check_image_loaded(self):
        if self.img and self.img_white:
            return
        if not self.img and not self.is_found_in_db:
            self.read_original_template()
        elif not self.img and self.is_found_in_db:
            self.read_loaded_template()
        else:
            raise Exception('check_image_loaded: unpredicted behavior')

    def colorize(self):
        """
        Applies colorization to template or loads colorized template from file if found in db.
        """
        if not self.colorizable or not self.color_mask_filename or not self.colorize_color:
            return
        mask = Image.open(self.color_mask_path).convert("RGBA")

        # Resize mask with new ratio:
        new_width = int(mask.width * self.ratio[0])
        new_height = int(mask.height * self.ratio[1])
        mask = mask.resize((new_width, new_height),
                           Image.ANTIALIAS)
        # Split gray
        r, g, b, alpha = mask.split()
        gray = ImageOps.grayscale(mask)
        # Colorize:
        colorized_mask = ImageOps.colorize(gray, (0, 0, 0, 0), self.colorize_color)
        colorized_mask.putalpha(alpha)
        img = Image.new('RGBA', self.img.size)
        img.paste(self.img)
        img.paste(colorized_mask, (0, 0), colorized_mask)
        if self.path_color.endswith('.jpg'):
            self.path_color = self.path_color.replace('.jpg', '.png')
            self.path_white = self.path_white.replace('.jpg', '.png')
        self.img_colored = img
        self.img = img
        self.img_colored.save(self.path_color)
        self.db.save_colorized_template(self.template_id, self.is_preview, self.ratio, self.colorize_color,
                                        self.filename_color, self.filename_white)
        return self.path_color, self.path_white

    def save(self, save_format='png'):
        self.img_white.save(self.path_white, save_format)
        self.img.save(self.path_color, save_format)
        return self.filename_color, self.path_color, self.get_url()


class DesignImage:
    def __init__(self, design_filename, edits=None, db=None):
        self.settings = Settings()
        self.db = db if db else DB()

        self.filename = design_filename
        self.path = self.settings.path_for_image('design', design_filename)
        self.edits = edits
        self.size_ratio = 1

        self.img = None
        self.width = None
        self.height = None

        self.transform_plane = None

        self.read_image()
        self.create_plane()

    def read_image(self):
        """
        Reads the image from it's path and creates it's plane

        """
        # Read the image from its path:
        img = Image.open(self.path).convert('RGBA')
        img = self.apply_edits(img)
        # Save width and height in a more accessible place (it's already stored in self.img.width/height):
        self.width, self.height = img.size
        # Save reading result into parameter:
        self.img = img

    def apply_edits(self, img):
        """
        Applies design edits sent from client: offsetX offsetY and scale
        :return:
        edited_image: Image
        """
        if not self.edits:
            return img
        offset_x, offset_y, scale = self.edits.get('offset_x'), self.edits.get('offset_y'), self.edits.get('scale')
        if offset_x == 0 and offset_y == 0 and scale == 1:
            return img
        new_img = Image.new('RGBA', img.size)
        # scale old image
        # crop old image with offset values (from top right)
        # paste old image into new one
        original_image_size = img.size
        paste_box = (0, 0)
        if scale != 1:
            print('Applied scale!')
            print('Old size: {}'.format(img.size))
            img = img.resize((int(img.width * scale), int(img.height * scale)))
            paste_x = int((original_image_size[0] - img.width) / 2)
            paste_y = int((original_image_size[1] - img.height) / 2)
            paste_box = (paste_x, paste_y)
            print('New size: {}'.format(img.size))
        if offset_x != 0 or offset_y != 0:
            max_offset_x = original_image_size[0] - original_image_size[0] / 100 * 10
            max_offset_y = original_image_size[1] - original_image_size[1] / 100 * 10
            if offset_x >= max_offset_x:
                offset_x = max_offset_x
            if offset_y >= max_offset_y:
                offset_y = max_offset_y
            print('Offsets applied!')
            cropped_area = (-offset_x, -offset_y, img.width, img.height)
            print('Cropped area: {}'.format(cropped_area))
            cropped = img.crop(cropped_area)
            # Calculate pastebox for new image:
            new_img.paste(cropped, paste_box)
        else:
            print("offsets x,y are 0, pastebox:", paste_box)
            new_img.paste(img, paste_box)
        return new_img

    def create_plane(self):
        """
        Creates a plane for the image read, describing 4 points coordinates

        """
        offset_x = 0
        offset_y = 0
        # Top left
        a1 = (0 - offset_x, 0 - offset_y)
        # Top right
        b1 = (self.width - offset_x, 0 - offset_y)
        # Bottom right
        c1 = (self.width - offset_x, self.height - offset_y)
        # Bottom left
        d1 = (0 - offset_x, self.height - offset_y)

        print("width: {} height: {} offset_x: {} offset_y: {} ratio {}".format(
            self.width, self.height, offset_x, offset_y, self.size_ratio
        ))

        # Save plane to object:
        self.transform_plane = [a1, b1, c1, d1]

    def save(self, ext='.png'):
        new_name = os.path.splitext(self.filename)[0] + ext
        self.filename = 'design_' + new_name
        self.path = self.settings.path_for_image('tmp', self.filename)
        # Convert alpha to white for jpg:
        if self.img.mode == 'RGBA' and ext != '.png':
            fill_color = (255, 255, 255)
            new_img = Image.new('RGB', self.img.size, fill_color)
            new_img.paste(self.img, self.img.split()[-1])  # omit transparency
            self.img = new_img
        self.img.save(self.path)

    def apply_antialiasing(self):
        aa_factor = 2
        old_width = self.img.width
        old_height = self.img.height
        # Upsize the image and downsize to apply antialiasing:
        self.img.thumbnail((old_width * aa_factor, old_height * aa_factor), Image.ANTIALIAS)
        self.img.thumbnail((old_width, old_height), Image.ANTIALIAS)

    def transform_for_template(self, template_object, disposition=False):
        # Get furthest x coord (for template result size):
        max_x = max([x[0] for x in template_object.transform_plane])
        # Get furthest y coord (for template result size):
        max_y = max([x[1] for x in template_object.transform_plane])
        old_width = self.img.width
        # Get transform ratios:
        ratios = self.find_ratios(template_object.transform_plane, self.transform_plane)
        # Transform the image with ratios and new size by max x,y values:
        self.img = self.img.transform((max_x, max_y), Image.PERSPECTIVE, ratios, Image.BICUBIC)
        self.size_ratio = old_width / self.img.width
        print("old width: {} new: {} ratio: {}".format(old_width, self.img.width, self.size_ratio))
        # If no disposition applied, a clean image of template size is created
        #   and design is pasted to template's paste coordinates:

        if not disposition:
            bg_sized = Image.new(template_object.img.mode, template_object.img.size)
            bg_sized.paste(self.img, template_object.paste_coordinates)
            self.img = bg_sized
        # If disposition applied, resize template to bg size and paste transformed template with offsets
        else:
            fill_color = (255, 255, 255)
            bg_sized = Image.new('RGB', template_object.img.size, fill_color)
            template_rgb = Image.new('RGB', self.img.size, fill_color)
            template_rgb.paste(self.img, self.img.split()[-1])
            bg_sized.paste(template_rgb, template_object.paste_coords)
            self.img = bg_sized

        # Apply anti-aliasing:
        self.apply_antialiasing()

    def resize_for_template(self, template_object):
        # Get furthest x coordinate (for template result size)
        max_x = max([x[0] for x in template_object.transform_plane])
        # Get furthest y coordinate (for template result size)
        max_y = max([y[1] for y in template_object.transform_plane])
        self.img.thumbnail((max_x, max_y), Image.ANTIALIAS)
        self.width, self.height = self.img.size
        # Update plane for new size:
        self.create_plane()

    @staticmethod
    def find_ratios(pa, pb):
        matrix = []
        for p1, p2 in zip(pa, pb):
            matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
            matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])

        A = numpy.matrix(matrix, dtype=numpy.float)
        B = numpy.array(pb).reshape(8)

        res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
        return numpy.array(res).reshape(8)
