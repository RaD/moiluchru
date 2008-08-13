import os, Image
from django.template import Library
from cargo import settings

register = Library()

THUMBNAILS = 'thumbnails'
SCALE_WIDTH = 'w'
SCALE_HEIGHT = 'h'
SCALE_BOTH = 'x'

def scale(max_x, pair):
    x, y = pair
    new_y = (float(max_x) / x) * y
    return (int(max_x), int(new_y))
    
# Thumbnail filter based on code from
# http://batiste.dosimple.ch/blog/2007-05-13-1/
def thumbnail(original_image_path, arg):  
    if not original_image_path:  
        return ''  
        
    if arg.find(','):
        size, upload_path = [a.strip() for a in  arg.split(',')]
    else:
        size = arg
        upload_path = ''

    if (size.lower().endswith('h')):
        mode = SCALE_HEIGHT
    elif (size.lower().endswith('w')):
        mode = SCALE_WIDTH
    else:
        mode = SCALE_BOTH
        
    # defining the size  
    size = size[:-1]
    max_size = int(size.strip())
    
    # defining the filename and the miniature filename  
    basename, format = original_image_path.rsplit('.', 1)  
    basename, name = basename.rsplit(os.path.sep, 1)  

    miniature = name + '_' + str(max_size) + mode + '.' + format
    thumbnail_path = os.path.join(basename, THUMBNAILS)
    if not os.path.exists(thumbnail_path):  
        os.mkdir(thumbnail_path)  
    
    miniature_filename = os.path.join(thumbnail_path, miniature)  
    miniature_url = '/'.join((settings.MEDIA_URL, upload_path, THUMBNAILS, miniature))  
    
    # if the image wasn't already resized, resize it  
    if not os.path.exists(miniature_filename) \
        or os.path.getmtime(original_image_path) > os.path.getmtime(miniature_filename):
        image = Image.open(original_image_path)  
        image_x, image_y = image.size  

        if mode == SCALE_BOTH:
            if image_x > image_y:
                mode = SCALE_WIDTH
            else:
                mode = SCALE_HEIGHT
            
        if mode == SCALE_HEIGHT:
            image_y, image_x = scale(max_size, (image_y, image_x))
        else:
            image_x, image_y = scale(max_size, (image_x, image_y))
            
        
        image = image.resize((image_x, image_y), Image.ANTIALIAS)
              
        image.save(miniature_filename, image.format)

    return miniature_url  

register.filter(thumbnail)
