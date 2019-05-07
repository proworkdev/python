import os

from modules.settings import Settings
from mongoengine import connect
from models import Template, ColorizedTemplate


class DB(object):
    def __init__(self):
        self.settings = Settings()
        mongo_host = 'mock_mongo' if not self.settings.local else 'localhost'
        mongo_port = 27017
        connect('image_mock', host=mongo_host, port=mongo_port)

    def get_template_options(self, template_id):
        """

        :param template_id: string
        :return: options: returns options object from DB for selected template
                            or None if template id not found
        """
        template = Template.objects(identifier=template_id)
        if not template:
            return None
        template = template[0]
        options = {
            'identifier': template_id,
            'type': template.type,
            'filename': template.filename,
            'url': self.settings.url_for_template(template_id),
            'bindings': template.bindings,
            'edit-zone': template.edit_zone,
            'colorizable': template.colorizable,
            'displacement_map': template.displacement_map
        }
        return options

    def get_available_templates_list(self):
        templates = Template.objects()
        result = []
        for t in templates:
            result.append({'title': t.title, 'identifier': t.identifier})
        return result

    def get_template_options_(self, template_id):
        """
        Returns options for template image by it's id
        :param bg_id(str): id if background searched

        """
        options = {}
        if template_id == 'laptop.png':
            options = {
                'type': 1,
                'filename': template_id,
                'url': self.settings.url_for_image('template', template_id),
                'bindings': {'a': [916, 260], 'b': [1550, 320], 'c': [1442, 848], 'd': [823, 702]},
                'edit-zone': [600, 460],
                'colorizable': False
            }
        elif template_id == 't-shirt.png':
            options = {
                'type': 2,
                'filename': template_id,
                'url': self.settings.url_for_image('template', template_id),
                'bindings': {'a': [656, 925], 'b': [1266, 1068], 'c': [1095, 1802], 'd': [484, 1660]},
                'edit-zone': [520, 800],
                'colorizable': {
                    'color_mask': 't-shirt-mask.png'
                },
                'displacement-map': 't-shirt-disp-map.jpg',
                'displacement-map-preview': 't-shirt-disp-map-preview.jpg'
            }
        return options

    def get_preview_options(self, filename):
        options = {
            'filename': filename,
            'preview_url': self.settings.url_for_image('preview', filename),
            'design_url': self.settings.url_for_image('template', filename)
        }
        return options

    @staticmethod
    def save_colorized_template(identifier, is_preview, ratio, color, path_color, path_white):
        colorized_template = ColorizedTemplate(
            identifier=identifier,
            is_preview=is_preview,
            ratio=ratio,
            color=color,
            filename_color=path_color,
            filename_white=path_white,
        )
        colorized_template.save()

    def get_colorized_template(self, template_id, color, is_preview):
        colorized_template = ColorizedTemplate.objects(identifier=template_id, color=color, is_preview=is_preview)
        if not colorized_template:
            return
        colorized_template = colorized_template[0]
        exists_color = os.path.isfile(
            self.settings.relative_path_for_processed_template(template_id, colorized_template.filename_color))
        exists_white = os.path.isfile(
            self.settings.relative_path_for_processed_template(template_id, colorized_template.filename_white))
        if not exists_color or not exists_white:
            colorized_template.delete()
            return
        return colorized_template


if __name__ == '__main__':
    db = DB()
    x = db.get_available_templates_list()
    # laptop_template = Template(
    #     identifier='tpl-laptop-0001',
    #     title='cool macbook',
    #     type=1,
    #     filename='laptop.png',
    #     bindings={'a': [916, 260],
    #               'b': [1550, 320],
    #               'c': [1442, 848],
    #               'd': [823, 702]
    #               },
    #     edit_zone=[600, 400],
    #     colorizable=None,
    #     displacement_map=None,
    # )
    # laptop_template.save()
    #
    # tee_template = Template(
    #     identifier='tpl-tee-0001',
    #     title='sxy tee',
    #     type=2,
    #     filename='t-shirt.png',
    #     bindings={
    #         'a': [656, 925],
    #         'b': [1266, 1068],
    #         'c': [1095, 1802],
    #         'd': [484, 1660]
    #     },
    #     edit_zone=[520, 800],
    #     colorizable={
    #         'color_mask': 't-shirt-mask.png'
    #     },
    #     displacement_map={
    #         'd-map-filename': 't-shirt-disp-map.jpg',
    #         'd-map-preview-filename': 't-shirt-disp-map-preview.jpg'
    #     }
    # )
    # tee_template.save()
