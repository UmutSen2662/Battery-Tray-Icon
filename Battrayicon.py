import psutil, time, json, os, Logs, Plot, Razer, sys  # type: ignore
from PIL import Image, ImageDraw, ImageFont
import pystray as ps

FQ = 100
run = True
log = False
plot = False
path = sys._MEIPASS if hasattr(sys, "_MEIPASS") else "."


def main():
    battery_percent = psutil.sensors_battery().percent
    icon = ps.Icon(
        name="Battray",
        icon=create_tray_image(str(battery_percent)),
        menu=ps.Menu(ps.MenuItem("Plot", on_clicked), ps.MenuItem("Logs", on_clicked), ps.MenuItem("Exit", on_clicked)),
    )
    icon.run_detached()

    notified = False
    repetitions = FQ
    razer_battery = None
    razer_battery_state = "normal"
    global run, log, plot
    while run:
        repetitions += 1

        if plot:
            Plot.plot_graph()
            plot = False
        elif log:
            Logs.show_logs()
            log = False
        elif repetitions > FQ:
            battery_percent = update(icon, battery_percent, razer_battery_state)

        if repetitions > FQ:
            result = Razer.get_battery()
            if result:
                razer_battery, wireless = result
                icon.title = f"Mouse {razer_battery}%"

                if notified:
                    if razer_battery_state == "low" and not wireless:
                        icon.remove_notification()
                        razer_battery_state = "normal"
                    elif razer_battery_state == "high" and wireless:
                        icon.remove_notification()
                        razer_battery_state = "normal"

                    if razer_battery > 30 and razer_battery < 60:
                        notified = False
                        razer_battery_state = "normal"
                else:
                    notified = True
                    if razer_battery > 70 and not wireless:
                        icon.notify("Razer mouse battery is sufficiently charged", f"Charged to {razer_battery}%")
                        razer_battery_state = "high"
                    elif razer_battery < 25 and wireless:
                        icon.notify("Razer mouse battery is low plug in to charge", f"{razer_battery}% battery left")
                        razer_battery_state = "low"
                    else:
                        icon.remove_notification()
                        razer_battery_state = "normal"
                        notified = False
            else:
                icon.remove_notification()
                razer_battery_state = "normal"
            repetitions = 0

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


def create_tray_image(text, razer_battery_state="normal"):
    fill_color = (
        (255, 0, 0)
        if razer_battery_state == "low"
        else (0, 255, 0) if razer_battery_state == "high" else (255, 255, 255)
    )
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.text(
        (0, 0), text, font=ImageFont.truetype(os.path.join(path, "RobotoCondensed-Medium.ttf"), 64), fill=fill_color
    )
    return image


def update(icon, old_battery_percent, razer_battery_state):
    battery_percent = psutil.sensors_battery().percent
    icon.icon = create_tray_image(str(battery_percent), razer_battery_state)
    if battery_percent != old_battery_percent:
        log_data(battery_percent)
        return battery_percent
    return old_battery_percent


def log_data(percent):
    if os.path.exists("Log.json"):
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
        data = {"percent": [percent], "time": [int(time.time())]}

    with open("Log.json", "w") as file:
        json.dump(data, file)


if __name__ == "__main__":
    main()
