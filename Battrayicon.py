from PIL import Image, ImageDraw, ImageFont
import psutil, time, json, os, Logs, Chart
import pystray as ps
run = True
log = False
chart = False

def main():
    battery_percent = psutil.sensors_battery().percent
    icon = ps.Icon('Battray', icon=create_tray_image(str(battery_percent)), 
                    menu=ps.Menu(ps.MenuItem("Logs", on_clicked), ps.MenuItem("Chart", on_clicked), ps.MenuItem("Exit", on_clicked)))
    icon.run_detached()
    global run
    global log
    global chart
    while (run):
        if log:
            Logs.show_logs()
            log = False
        elif chart:
            Chart.show_chart()
            chart = False
        battery_percent = update(icon, battery_percent)
        #print(battery_percent)
        time.sleep(2)
    return

def create_tray_image(text):
    image = Image.new('RGBA', (64, 64), (255, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.text((0,0), text, font=ImageFont.truetype("arial.ttf", 60), fill=(255, 255, 255))
    return image

def on_clicked(icon, item):
    global run
    global log
    global chart
    if str(item) == "Exit":
        icon.stop()
        run = False
        #print("exit")
    elif str(item) == "Chart":
        battery_percent = psutil.sensors_battery().percent
        log_data(battery_percent)
        chart = True
        #print("chart")
    elif str(item) == "Logs":
        log = True
        #print("logs")

def update(icon, old_battery_percent):
    battery_percent = psutil.sensors_battery().percent
    icon.icon = create_tray_image(str(battery_percent))
    if (battery_percent != old_battery_percent):
        log_data(battery_percent)
    return battery_percent

def log_data(percent):
    if os.path.exists('Log.json'):
        with open("Log.json") as file:
            data = json.load(file)
            data["percents"].append(percent)
            data["times"].append(int(time.time()))
    else:
        data = {"percents" : [percent],
                "times" : [int(time.time())]}
        
    with open("Log.json", "w") as file:
        json.dump(data, file)

main()