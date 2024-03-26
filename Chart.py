import matplotlib.pyplot as plt
import json
def show_chart():
    DAY = 86400
    font1 = {'family':'serif','color':'blue','size':20}
    font2 = {'family':'serif','color':'darkred','size':15}

    with open("Log.json") as file:
        data = json.load(file)
        while (data["times"][-1] - data["times"][0]) > (DAY * 3):
            data["times"].pop(0)
            data["percents"].pop(0)
        percents = data["percents"]
        times = data["times"]
        times = list(map(lambda x: x - times[0], times))
        times = list(map(lambda x: x // 60, times))

    with open("Log.json", "w") as file:
        json.dump(data, file)


    plt.figure(figsize=(10,6))
    plt.axis([times[0], times[-1], 0, 100])
    plt.title("Battery Tracker", fontdict = font1)
    plt.xlabel("Time (Minutes)", fontdict = font2)
    plt.ylabel("Percentage", fontdict = font2)
    plt.tight_layout()
    plt.grid()
    plt.subplots_adjust(left=0.07, bottom=0.09, right=0.98, top=0.94)
    plt.plot(times, percents, '-o', linewidth=2)
    plt.fill_between(times, percents, alpha=0.25)
    plt.show()
