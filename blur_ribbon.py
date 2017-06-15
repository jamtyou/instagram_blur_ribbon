import os, datetime, re, random, numpy, operator
from PIL import Image, ImageDraw

#create a list of all non-hidden files in input folder
def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

#find the group of n pixels (n=blur_w) along the edge of image im
#with the greatest colour variation between neighbours
def colour_scan(im,blur_w):
    #define variable values for top, bottom, left and right edges of image
    #variables are:
        #axis of direction(x=0 y=1)
        #pixel position on orthogonal axis
        #arbitrary indicator of edge (top=1, bottom=2, left=3, right=4)
    edge_variables = [(0,0,1),(0,im.size[1]-1,2),(1,0,3),(1,im.size[0]-1,4)]
    #loop through each edge
    for v in edge_variables:
        #record all pixel RGB values along edge
        #if x-axis
        if v[0] == 0:
            colour_list = [im.getpixel((p,v[1])) for p in range(0,im.size[0])]
        #if y-axis
        if v[0] == 1:
            colour_list = [im.getpixel((v[1],p)) for p in range(0,im.size[1])]
        #separate pixel colour tuples into R, G and B lists
        R_list = [px[0] for px in colour_list]
        G_list = [px[1] for px in colour_list]
        B_list = [px[2] for px in colour_list]
        #calculate colour "distance" between each neighbouring pixel
        dist_sq_list = [((R_list[n]-R_list[n+1])**2 + (G_list[n]-G_list[n+1])**2 + (B_list[n]-B_list[n+1])**2) for n in range(0,len(R_list)-1)]
        #for every pixel (px) along edge
        for px in range(0,im.size[v[0]]-blur_w):
            #sum total colour distances between neighbours in next n pixels (n=blur_w)
            blur_interest = sum(dist_sq_list[0+px:blur_w+px])
            #record sum of distances, first pixel position, and edge indicator
            interest_list.append((blur_interest,px,v[2]))

#create list of images in "input" directory
input_files = listdir_nohidden(os.getcwd()+'/input')

#for every image in file list
for i in input_files:

    #print state to terminal
    print("starting "+i)

    #open image and record image size
    old_im = Image.open('input/'+i)
    old_im = old_im.convert('RGB')
    old_size = old_im.size

    #define the width of the blur to be applied
    blur_width = int(min(old_size)/4)

    #declare interest_list as empty list
    interest_list = []

    #call function to find greatest colour variation
    colour_scan(old_im,blur_width)

    #return values of portion with greatest colour variation
    best_blur = max(interest_list, key=operator.itemgetter(0))
    #define edge with greatest colour variation
    best_edge = best_blur[2]
    #define starting pixel of best portion
    start_pixel = best_blur[1]

    #specify the size of the background image that will be used to form a border
    #around the original image
    #background will be 110% to 120% the size of the original max dimension
    random_size = int(((100+random.randrange(10,20))*max(old_size))/100)
    new_size = (random_size,random_size)

    #create background image (white)
    new_im = Image.new("RGB", new_size,(255,255,255))

    #declare border padding as a function of background image size
    border_pad = int(random_size/30)

    #specify the blur opacity.
    opac = 144

    #paste old image in a random position onto new image - making sure that the
    #edge that will have blur applied to it is not edge with largest "border"
    if old_size[0]>=old_size[1] and best_edge==1:
        x_paste = random.randrange(border_pad,random_size-old_size[0]-border_pad)
        y_paste = random.randrange(border_pad,(random_size/2)-(old_size[1]/2)-border_pad)
    elif old_size[0]>=old_size[1] and best_edge==2:
        x_paste = random.randrange(border_pad,random_size-old_size[0]-border_pad)
        y_paste = random.randrange((random_size/2)-(old_size[1]/2)+border_pad,random_size-old_size[1]-border_pad)
    elif old_size[0]<=old_size[1] and best_edge==3:
        x_paste = random.randrange(border_pad,(random_size/2)-(old_size[0]/2)-border_pad)
        y_paste = random.randrange(border_pad,random_size-old_size[1]-border_pad)
    elif old_size[0]<=old_size[1] and best_edge==4:
        x_paste = random.randrange((random_size/2)-(old_size[0]/2)+border_pad,random_size-old_size[0]-border_pad)
        y_paste = random.randrange(border_pad,random_size-old_size[1]-border_pad)
    else:
        y_paste = random.randrange(border_pad,random_size-old_size[1]-border_pad)
        x_paste = random.randrange(border_pad,random_size-old_size[0]-border_pad)

    #paste original image onto background
    new_im.paste(old_im,(x_paste,y_paste))
    #convert to RGBA to allow for blur to be applied with opacity
    new_im = new_im.convert('RGBA')

    #apply blur to portion of pixels with greatest colour variation
    if best_edge==1:
        blur_start = start_pixel+x_paste
        for j in range(0,blur_width):
            pixel = (blur_start+j,y_paste)
            pixel_colour = new_im.getpixel(pixel)
            pixel_colour = pixel_colour[:-1]+(opac,)
            draw = ImageDraw.Draw(new_im)
            draw.line((pixel[0],pixel[1]-1,pixel[0],0), fill=pixel_colour)
            del draw
    if best_edge==2:
        blur_start = start_pixel+x_paste
        for j in range(0,blur_width):
            pixel = (blur_start+j,y_paste+old_size[1]-1)
            pixel_colour = new_im.getpixel(pixel)
            pixel_colour = pixel_colour[:-1]+(opac,)
            draw = ImageDraw.Draw(new_im)
            draw.line((pixel[0],pixel[1]+1,pixel[0],new_im.size[1]), fill=pixel_colour)
            del draw
    if best_edge==3:
        blur_start = start_pixel+y_paste
        for j in range(0,blur_width):
            pixel = (x_paste,blur_start+j)
            pixel_colour = new_im.getpixel(pixel)
            pixel_colour = pixel_colour[:-1]+(opac,)
            draw = ImageDraw.Draw(new_im)
            draw.line((pixel[0]-1,pixel[1],0,pixel[1]), fill=pixel_colour)
            del draw
    if best_edge==4:
        blur_start = start_pixel+y_paste
        for j in range(0,blur_width):
            pixel = (x_paste+old_size[0]-1,blur_start+j)
            pixel_colour = new_im.getpixel(pixel)
            pixel_colour = pixel_colour[:-1]+(opac,)
            draw = ImageDraw.Draw(new_im)
            draw.line((pixel[0]+1,pixel[1],new_im.size[0],pixel[1]), fill=pixel_colour)
            del draw

    #paste image with mask onto blank "final" to preserve transparency and allow
    #saving as jpg
    final = Image.new("RGB", new_im.size, (255,255,255))
    final.paste(new_im,new_im)

    #resize final image for instagram
    final = final.resize((1080,1080), Image.ANTIALIAS)

    #get modified date of original photo - this allows the easy sorting of the
    #output files by age of the original
    mtime = os.path.getmtime(os.getcwd()+'/input/'+i)
    str_mtime = datetime.datetime.isoformat(datetime.datetime.fromtimestamp(mtime))
    str_mtime = re.sub("[^0-9.]", "-", str_mtime)

    #save the new image and prefix name with modified date
    final.save('output/'+str_mtime+'_'+i)

    #print state to terminal
    print(i+' converted')
