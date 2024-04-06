from datetime import datetime
import PySimpleGUI as sg
import json

def show_logs():
   sg.theme("Dark Grey 13")
   sg.set_options(font=("None", 14))

   toprow = ["Time", "Percent"]
   rows = []
   with open("Log.json") as file:
      data = json.load(file)
      percents = data["percent"]
      times = data["time"]
      times = [ str(datetime.fromtimestamp(x)) for x in times ]
      times = [ (x[:10] + "  " + x[-9:-3]) for x in times ]
      
      for idx, time in enumerate(times):
         rows.append([time, percents[idx]])

   tbl1 = sg.Table(values=rows, headings=toprow,
      auto_size_columns=True,
      display_row_numbers=False,
      justification='center', key='-TABLE-',
      enable_events=True,
      expand_x=True,
      expand_y=True,
      enable_click_events=True)

   layout = [[sg.Text("Battery Charge Logs", expand_x=True, justification="cneter", font=("none", 18))],
            [tbl1],
            [sg.Button("Delete Selected"), sg.Push(), sg.Button("Save and Exit")]]
   window = sg.Window("Table Demo", layout, size=(400, 750), resizable=True)

   while True:
      event, values = window.read()
      if event == sg.WIN_CLOSED:
         break
      
      if values["-TABLE-"] != []:
         choice = values["-TABLE-"]
         if event == "Delete Selected":
            for idx in sorted(choice, reverse=True):
               rows.pop(idx)
               data["time"].pop(idx)
               data["percent"].pop(idx)
            tbl1.update(values=rows)
      
      if event == "Save and Exit":
         print("Saved")
         with open("Log.json", "w") as file:
            json.dump(data, file)
         break

   window.close()

if __name__ == "__main__":
    show_logs()
