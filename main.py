from selenium import webdriver
from PIL import Image, ImageOps
from io import BytesIO
import glob
import os
import numpy as np

def setup_web():
    driver.set_window_size(800, 600)
    html_file = os.getcwd() + "//html//" + [file for file in os.listdir('html') if file.endswith("html")][0]
    driver.get("file:///" + html_file)
    driver.execute_script('''var rules = document.styleSheets[0].cssRules;
                             for(var i=1; i < rules .length; i++){
                                     if(rules[i].style.lineHeight != '')
                                        rules[i].style.lineHeight = '2';
                                     if(rules[i].style.textIndent != '')
                                        rules[i].style.textIndent = '';
                             }
                             var hiddenElements = document.querySelectorAll('span');
                             var i = hiddenElements.length;
                             while(i--) {
                                 hiddenElements[i].style.display = '';
                             }
                        ''')
                        
def remove_img():
    files = glob.glob("img/*.png")
    for f in files:
        os.remove(f)

def img_file_name(a): return 'img/'+str(a).zfill(2) + '.png'

def get_crop_list():
    crop_list = []
    for question in questions:
        size = question.size
        location = question.location
        print(location)

        if(question.find_elements_by_tag_name("span")[0].get_attribute("style") != ''):
            crop_list[-1][1] += size['height']
            print('merge')
        else:
            top = location['y']
            bottom = top + size['height']
            crop_list.append([top, bottom])
        print(crop_list[-1])
    return crop_list

def crop_margin(img):
    ivt_image = ImageOps.invert(img.convert('RGB'))
    bbox = ivt_image.getbbox()
    cropped_image = img.crop(bbox)
    return cropped_image

def crop_save(crop_list):
    for index, box in enumerate(crop_list):
        im = img_base.crop((body_left, box[0], body_left + body_width, box[1]))
        im = crop_margin(im)
        count_black = np.count_nonzero(np.array(im) == 0)
        print(count_black)
        if count_black > 500:
            im.save(img_file_name(index))
        else:
            print('drop', index)

if __name__ == '__main__':
    driver = webdriver.PhantomJS(executable_path="phantomjs.exe")
    setup_web()
    remove_img()

    # get body boundary
    body = driver.find_elements_by_tag_name("body")[0]
    body_left = body.location['x']
    body_width = body.size['width']

    tag_list = ['p','ol']
    for tag in tag_list:
        questions = driver.find_elements_by_tag_name(tag) # find each question
        if questions != []:
            break

    png = driver.get_screenshot_as_png()  # saves screenshot of entire page
    img_base = Image.open(BytesIO(png))  # uses PIL library to open image in memory

    crop_list = get_crop_list() # get each question location
    print(len(crop_list))
    crop_save(crop_list) # crop from base image and save png

    driver.quit()
    print("\nFinish !!!")