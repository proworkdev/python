import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_uploads import UploadSet, configure_uploads, IMAGES

from modules.image_processing import DesignProcessor, TemplateImage
from modules.settings import Settings
from modules.utilities import check_download_exists, filename_for_uploaded_file
from modules.db import DB

import threading

# Initiate settings:
settings = Settings()

# Initiate flask APP
app = Flask(__name__)

# Add CORS support:
CORS(app)

# Setup designs upload:
app.config['UPLOADED_DESIGNS_DEST'] = settings.path_designs
designs = UploadSet('designs', IMAGES)
configure_uploads(app, designs)


@app.route('/')
def starting():
    return 'nothing here'


@app.route('/design-upload', methods=['POST'])
def upload_design():
    """
    An endpoint where design upload is made and entrypoint for design processing.
    :return:
    json response
    """
    response = {'success': True}

    # Process non-POST requests:
    if request.method != 'POST':
        return 'wrong method, only post allowed.'

    # Process POST request
    #
    # Check uploaded design:
    uploaded_file = request.files.get('design')

    if not uploaded_file:
        response['success'] = False
        response['error'] = True
        response['error_description'] = 'No file was uploaded'
        return jsonify(response)

    # Save uploaded design with new filename:
    uploaded_filename = uploaded_file.filename
    design_filename = filename_for_uploaded_file(uploaded_filename)
    designs.save(request.files['design'], name=design_filename)

    design_url = settings.url_for_image('design', design_filename)
    options = {
        'design_filename': design_filename,
        'design_url': design_url
    }
    response['options'] = options

    return jsonify(response)


@app.route('/design-process', methods=['POST'])
def process_design():
    response = {'success': True}
    # Check design id in request:
    design_filename = request.form.get('design_id')

    # Check template info from request:
    template_id = request.form.get('template_id')
    colorize_color = request.form.get('colorize_color')
    colorize_color = '#FFF' if colorize_color == 'null' else colorize_color

    if not template_id:
        response['success'] = False
        response['error'] = True
        response['error_description'] = 'No template chosen'
        return jsonify(response)
    if not design_filename:
        response['success'] = False
        response['error'] = True
        response['error_description'] = 'No design specified'
        return jsonify(response)

    # Check design edits:
    edits = request.form.get('edits')

    data = design_filename, template_id, colorize_color
    [print('uploaded: {}'.format(x)) for x in data]

    design_processor = DesignProcessor(design_filename, template_id, colorize=colorize_color, edits=edits)
    design_processor.process(preview=True)

    response['success'] = True
    response['template_id'] = template_id
    response['uploaded_filename'] = design_filename
    response['preview'] = design_processor.response_preview_options()
    response['download'] = design_processor.response_download_options()

    # # Generate download in a background thread...
    download_processor = DesignProcessor(design_filename, template_id, colorize=colorize_color, edits=edits)
    dnl_thread = threading.Thread(target=download_processor.process)
    dnl_thread.start()

    return jsonify(response)


@app.route('/template-colored', methods=['POST'])
def get_colored_template():
    """
    Endpoint to get colored template for client preview
    :return:
    json response
    """
    response = {'success': False}
    # Check template info from request:
    template_id = request.form.get('template_id')
    colorize_color = request.form.get('colorize_color')
    colorize_color = '#FFF' if colorize_color == 'null' else colorize_color

    if not template_id:
        response['success'] = False
        response['error'] = True
        response['error_description'] = 'No template chosen'
        return jsonify(response)
    if not colorize_color:
        response['success'] = False
        response['error'] = True
        response['error_description'] = 'No color specified'
        return jsonify(response)
    design_filename = filename_for_uploaded_file('preview.png')
    template = TemplateImage(template_id, design_filename, color=colorize_color, db=None, is_preview=True)
    if not template.is_found_in_db:
        template.colorize()
        template.save()

    options = dict()
    print('URL: ', template.get_url())
    options['colored_url'] = template.get_url()

    response['success'] = True
    response['template_id'] = template_id
    response['options'] = options
    return jsonify(response)


@app.route('/check-dnl', methods=['POST'])
def check_download():
    """
    Endpoint to check if the download file is already available in static dir:
    :return:
    json response
    """
    exists = False
    url = None
    polling_timeout = 30    # seconds
    download_filename = request.form.get('download_filename')
    if not download_filename:
        return jsonify({'exists': exists})
    started = time.time()
    while not exists:
        exists, url = check_download_exists(download_filename)
        if started + polling_timeout <= time.time():
            break
        time.sleep(.5)  # 0.5 second refresh gap
    return jsonify({'exists': exists, 'url': url})


@app.route('/templates-available', methods=['GET'])
def avail_templates():
    """
    Endpoint returns available templates as a list of objects:
    {'title': template.title, 'identifier': template.identifier} in templates parameter.
    :return:
    """
    if request.method == 'GET':
        db = DB()
        template_list = db.get_available_templates_list()
        response = {
            'success': True,
            'templates': template_list
        }
        return jsonify(response)
    return 'oops'


@app.route('/template-cfg', methods=['POST'])
def cfg_template():
    """
    Endpoint returns configs for specified template ID, specifically options from DB.
    These are 'filename', 'url', 'bindings', 'colorizable', 'dispositionMap', 'color_mask'.
    :return:
    """
    if request.method == 'POST' and request.form.get('template_id'):
        template_id = request.form['template_id']
        db = DB()
        options = db.get_template_options(template_id)
        response = {
            'success': True,
            'template_id': template_id,
            'options': options
        }
        return jsonify(response)
    return 'oops'


if __name__ == '__main__':
    app.run(debug=True)
