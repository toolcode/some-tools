from PIL import Image
import os

def reduce_imagesize(input_path,output_path,quality):
    with Image.open(input_path) as img:
        img.save(output_path, quality=quality)

def reduce_images_in_dir(input_dir,output_dir,quality):
    imagenames=os.listdir(input_dir)
    for imagename in imagenames:
        inputpath=os.path.join(input_dir, imagename)
        outputpath=os.path.join(output_dir, imagename)
        reduce_imagesize(input_path=inputpath,output_path=outputpath,quality=quality)
        
reduce_images_in_dir('./原图片','./压缩后',50)
     
  





