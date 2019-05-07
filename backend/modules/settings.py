import os


class Settings(object):
    def __init__(self):
        local = os.getenv('IMAGE_MOCK_LOCAL', False)
        self.local = local
        # local = True
        server_ip = '206.189.9.235'
        self.base_url = 'http://{}:5000/'.format(server_ip if not local else 'localhost')

        # Define application dir:
        self.dir_app = os.getcwd()

        # Define directory structure:
        self.dir_static = 'static'
        self.dir_templates = os.path.join(self.dir_static, 'templates')
        self.dir_designs = os.path.join(self.dir_static, 'designs')
        self.dir_previews = os.path.join(self.dir_static, 'previews')
        self.dir_downloads = os.path.join(self.dir_static, 'downloads')
        self.dir_tmp = os.path.join(self.dir_static, 'tmp')

        # Define paths:
        self.path_static = os.path.join(self.dir_app, self.dir_static)
        self.path_templates = os.path.join(self.dir_app, self.dir_templates)
        self.path_designs = os.path.join(self.dir_app, self.dir_designs)
        self.path_previews = os.path.join(self.dir_app, self.dir_previews)
        self.path_downloads = os.path.join(self.dir_app, self.dir_downloads)
        self.path_tmp = os.path.join(self.dir_app, self.dir_tmp)

        # Preview options:
        self.preview_size = (800, 800)

    # Relative path to full conversion:
    def path_relative_to_full(self, relative_path):
        return os.path.join(self.dir_app, relative_path)

    # Relative path to URL conversion:
    def path_relative_to_url(self, relative_path):
        return self.base_url + relative_path

    # Relative TEMPLATE dir:
    def relative_template_dir(self, template_id):
        return os.path.join('static', 'templates', template_id)

    # Relative path to TEMPLATE FILE:
    def relative_path_for_template(self, template_id):
        template_dir = self.relative_template_dir(template_id)
        return os.path.join(template_dir, 'template.png')

    def relative_path_for_processed_template(self, template_id, filename):
        rel_template_dir = self.relative_template_dir(template_id)
        rel_processed_dir = os.path.join(rel_template_dir, 'processed')
        full_processed_dir = self.path_relative_to_full(rel_processed_dir)
        if not os.path.isdir(rel_processed_dir):
            os.mkdir(full_processed_dir)
        return os.path.join(rel_processed_dir, filename)

    # Full path to template_file
    def path_to_template_file(self, template_id):
        relative_path = self.relative_path_for_template(template_id)
        path = os.path.join(self.dir_app, relative_path)
        return path

    def url_for_template(self, template_id):
        relative_path = self.relative_path_for_template(template_id)
        url = self.base_url + relative_path
        return url

    def relative_path_for_image(self, img_type, img_name):
        paths_by_type = {
            'template': self.dir_templates,
            'design': self.dir_designs,
            'preview': self.dir_previews,
            'download': self.dir_downloads,
            'tmp': self.dir_tmp
        }
        img_dir = paths_by_type.get(img_type)
        if img_dir and img_name:
            return os.path.join(img_dir, img_name)

    def path_for_image(self, img_type, img_name):
        relative_path = self.relative_path_for_image(img_type, img_name)
        if relative_path:
            return os.path.join(self.dir_app, relative_path)

    def url_for_image(self, img_type, img_name):
        relative_path = self.relative_path_for_image(img_type, img_name)
        if relative_path:
            return self.base_url + relative_path
