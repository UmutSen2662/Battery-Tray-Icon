from PIL import Image, ImageDraw, ImageFont
import psutil, time, json, os, Logs, Plot, Razer
import pystray as ps

FQ = 600
run = True
log = False
plot = False

def main():
    battery_percent = psutil.sensors_battery().percent
    icon = ps.Icon(name="Battray",
                   icon=create_tray_image(str(battery_percent)), 
                   menu=ps.Menu(ps.MenuItem("Plot", on_clicked), 
                                ps.MenuItem("Logs", on_clicked), 
                                ps.MenuItem("Exit", on_clicked)))
    icon.run_detached()

    repetitions = FQ
    notified = False
    global run, log, plot
    while (run):
        repetitions += 1
        if (repetitions > FQ):
            razer_battery = Razer.get_battery()
            if razer_battery:
                icon.title = f"Mouse {razer_battery}%"
                if not notified:
                    if razer_battery < 25:
                        icon.notify("Razer mouse battery is low plug in to charge", f"{razer_battery}% battery left")
                        notified = True
                    elif razer_battery > 75:
                        icon.notify("Razer mouse battery is sufficiently charged", f"Charged to {razer_battery}%")
                        notified = True
                elif (razer_battery > 20 and razer_battery < 80):
                    notified = False
            repetitions = 0

        if plot:
            Plot.plot_graph()
            plot = False
        elif log:
            Logs.show_logs()
            log = False
        elif (repetitions % 50 == 0):
            battery_percent = update(icon, battery_percent)

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

def create_tray_image(text):
    image = Image.new('RGBA', (64, 64), (255, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.text((0,0), text, font=ImageFont.truetype("arial.ttf", 60), fill=(255, 255, 255))
    return image

def update(icon, old_battery_percent):
    battery_percent = psutil.sensors_battery().percent
    if (battery_percent != old_battery_percent):
        print(battery_percent)
        icon.icon = create_tray_image(str(battery_percent))
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

main()