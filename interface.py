from PIL import Image, ImageDraw, ImageFont

WIDTH = 128
HEIGHT = 32

font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", HEIGHT//4)
font_m = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", HEIGHT//3)
font_l = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", HEIGHT//2)

def rect_page(draw):
    draw.rectangle((0, 0, WIDTH//2, HEIGHT //2), outline=255, fill=0)

def menu_page(draw, page_num=-1):
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=0)
    draw.rectangle((WIDTH//2-2*8-4, 0,  WIDTH//2+8+4, HEIGHT//4), outline=255, fill=0)
    text = "MENU"
    draw.text((WIDTH//2-2*8, 0), text, font=font_s, fill=255)

    draw.text((WIDTH-3*8, 0), "*^", font=font_l, fill=255)
    draw.text((WIDTH-3*8, HEIGHT//3*2), "#v", font=font_m, fill=255)

    if(page_num==0):
        text = "1. View Schedule"
        draw.text((0, HEIGHT//4), text, font=font_s, fill=255)
        
        text = "A. Set Pill A" 
        draw.text((0, HEIGHT//4*2), text, font=font_s, fill=255)

        text = "B. Set Pill B"
        draw.text((0, HEIGHT//4*3), text, font=font_s, fill=255)

    elif(page_num==1):
        text = "C. Set Pill C"
        draw.text((0, HEIGHT//4), text, font=font_s, fill=255)
        
        text = "D. Set Pill D" 
        draw.text((0, HEIGHT//4*2), text, font=font_s, fill=255)

        text = "0. Show Current Time"
        draw.text((0, HEIGHT//4*3), text, font=font_s, fill=255)

def med_schedule_page(draw, pillId=0, time="1200", amount=3, set=True):
    pillIds = ["A", "B", "C", "D"]
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=0)
    draw.rectangle((WIDTH//2-4*8-4, 0,  WIDTH//2+2*8, HEIGHT//4), outline=255, fill=0)

    draw.text((WIDTH-3*8, 0), "*^", font=font_l, fill=255)
    draw.text((WIDTH-3*8, HEIGHT//3*2), "#v", font=font_m, fill=255)

    text = "SCHEDULE"
    draw.text((WIDTH//2-4*8, 0), text, font=font_s, fill=255)

    if set:
        text = "Pill "+pillIds[pillId]
        draw.text((0, HEIGHT//4), text, font=font_s, fill=255)

        print(time)
        text = "Time: "+time[0]+time[1] + ":" + time[2] + time[3]
        draw.text((0, HEIGHT//4*2), text, font=font_s, fill=255)
        if(amount==0):
            amount = 3
        text= "Amount: "+str(amount) 
        draw.text((0, HEIGHT//4*3), text, font=font_s, fill=255)

    else:
        text = "Unset" 
        draw.text((0, HEIGHT//4), text, font=font_m, fill=255)
        text= "To set this pill, press "+str(pillIds[pillId]) 
        draw.text((0, HEIGHT//4*3), text, font=font_s, fill=255)



def alarm_setup_page(draw, id=0, time="1200", amount=0):
        pillIds = ["A", "B", "C", "D"]
        draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
        draw.line((0,HEIGHT//4, WIDTH, HEIGHT//4),fill=255)
        message_row1 = "Setting alarm for Pill " + pillIds[id]
        message_row2 = "Time: %c%c : %c%c"%(time[0],time[1],time[2],time[3])
        message_row3 = "Amount: %d"%(amount)
        draw.text((0, 0), message_row1, font=font_s, fill=255)
        draw.text((0, HEIGHT//4*2), message_row2, font=font_s, fill=255)
        draw.text((0, HEIGHT//4*3), message_row3, font=font_s, fill=255)

def recording_audio_page(draw, id=0):
    pillIds = ["A", "B", "C", "D"]
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
    text = "Recording for Pill" + pillIds[id] 
    draw.text((0, 0), text, font=font_l, fill=255)
    text= "Press # to complete" 
    draw.text((0, HEIGHT//4*3), text, font=font_s, fill=255)

def alarm_page(draw,id=0):
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
    text = "IT'S PILL TIME"
    draw.text((0,0), text, font=font_l, fill=255)





    
