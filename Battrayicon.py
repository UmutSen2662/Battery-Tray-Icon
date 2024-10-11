import psutil, time, json, os, Logs, Plot, Razer, sys
from PIL import Image, ImageDraw, ImageFont
import pystray as ps

FQ = 600
run = True
log = False
plot = False
path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else '.'

def main():
    battery_percent = psutil.sensors_battery().percent
    icon = ps.Icon(name="Battray",
                   icon=create_tray_image(str(battery_percent)), 
                   menu=ps.Menu(ps.MenuItem("Plot", on_clicked), 
                                ps.MenuItem("Logs", on_clicked), 
                                ps.MenuItem("Exit", on_clicked)))
    icon.run_detached()
    
    repetitions = FQ
    razer_battery = 50
    razer_battery_notification = "normal"
    global run, log, plot
    while (run):
        repetitions += 1
        if (repetitions > FQ):
            new_razer_battery = Razer.get_battery()
            if new_razer_battery:
                icon.title = f"Mouse {new_razer_battery}%"
                if new_razer_battery < 25:
                    if razer_battery - new_razer_battery > 0:
                        icon.notify("Razer mouse battery is low plug in to charge", f"{new_razer_battery}% battery left")
                        razer_battery_notification = "low"
                    elif razer_battery - new_razer_battery < 0:
                        icon.remove_notification()
                        razer_battery_notification = "normal"
                elif new_razer_battery > 70:
                    if new_razer_battery - razer_battery > 0:
                        icon.notify("Razer mouse battery is sufficiently charged", f"Charged to {new_razer_battery}%")
                        razer_battery_notification = "high"
                    elif new_razer_battery < 99:
                        icon.remove_notification()
                        razer_battery_notification = "normal"
                else:
                    icon.remove_notification()
                    razer_battery_notification = "normal"
                razer_battery = new_razer_battery
            repetitions = 0

        if plot:
            Plot.plot_graph()
            plot = False
        elif log:
            Logs.show_logs()
            log = False
        elif (repetitions % 50 == 0):
            battery_percent = update(icon, battery_percent, razer_battery_notification)

        time.sleep(0.1)
    return

def on_clicked(icon, item):
    global run, log, plot
    if str(item) == "Exit":
        icon.stop()
        run = False
    elif str(item) == "Plot":
        plot = True
    elif str(item) == "Logs":
        log = True

def create_tray_image(text, razer_battery_notification = "normal"):
    fill_color = (255, 0, 0) if razer_battery_notification == "low" else (0, 255, 0) if razer_battery_notification == "high" else (255, 255, 255)
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.text((0,0), text, font=ImageFont.truetype(os.path.join(path, "RobotoCondensed-Medium.ttf"), 64), fill=fill_color)
    return image

def update(icon, old_battery_percent, razer_battery_notification):
    battery_percent = psutil.sensors_battery().percent
    print(battery_percent)
    icon.icon = create_tray_image(str(battery_percent), razer_battery_notification)
    if (battery_percent != old_battery_percent):
        log_data(battery_percent)
        return battery_percent
    return old_battery_percent

def log_data(percent):
    if os.path.exists('Log.json'):
        DAY = 86400
        with open("Log.json") as file:
            data = json.load(file)
            if data["percent"][-1] != percent:
                data["percent"].append(percent)
                data["time"].append(int(time.time()))
            else:
                data["time"][-1] = int(time.time())

            while (data["time"][-1] - data["time"][0]) > (DAY * 7):
                data["time"] = data["time"][1:]
                data["percent"] = data["percent"][1:]
    else:
        data = {"percent" : [percent],
                "time" : [int(time.time())]}
    
    with open("Log.json", "w") as file:
        json.dump(data, file)

if __name__ == "__main__":
    main()