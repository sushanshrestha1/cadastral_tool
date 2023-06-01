from Tkinter import *
import tkFileDialog
import string
import os
import arcpy
import collections
root = Tk()
root.geometry("500x300")
root.title("Select Folder")

building = None
cadastral = None
save = None

def open_file1():
    global building
    filepath = tkFileDialog.askopenfilename(
        title="Select Building Shapefile",
        filetypes=(("Shapefile", "*.shp"),))
    path = os.path.abspath(filepath)
    loc.delete(0, END)
    loc.insert(0, path)
    building = path
    print(building)

def open_file2():
    global cadastral
    filepath = tkFileDialog.askopenfilename(
        title="Select Cadastral Shapefile",
        filetypes=(("Shapefile", "*.shp"),))
    path = os.path.abspath(filepath)
    loc1.delete(0, END)
    loc1.insert(0, path)
    cadastral = path
    print(cadastral)

def open_file3():
    global save
    filepath = tkFileDialog.askdirectory(initialdir="C:\\", title="Open folder: ")
    path = os.path.abspath(filepath)
    loc3.delete(0, END)
    loc3.insert(0, path)
    save = path
    print(save)

def open_file():
    global save
    filepath = tkFileDialog.askdirectory(initialdir="C:\\", title="Open folder: ")
    path = os.path.abspath(filepath)
    loc2.delete(0, END)
    loc2.insert(0, path)
    save = path
    print(save)

def ok():
    shp_in = loc2.get()
    field_name = "Area"

    flist = os.listdir(shp_in)
    shp_data = list('')
    for fname in flist:
        shp_fname = fname.split('.')
        if shp_fname[-1] == 'shp':
            if len(shp_fname) < 3:
                shp_data.append(fname)

    for i in range(len(shp_data)):
        arcpy.AddField_management(
            shp_in + "\\" + shp_data[i],
            field_name,
            "DOUBLE",
            "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", ""
        )
        arcpy.CalculateField_management(
            shp_in + "\\" + shp_data[i],
            field_name,
            "!shape.area!",
            "PYTHON_9.3",
            ""
        )

def cad():
    global save
    file = name.get()
    save_directory = save
    output_feature_class = os.path.join(save_directory, file + ".shp")
    print(output_feature_class)
    save = output_feature_class
    print(save)
    if arcpy.Exists(output_feature_class):
        arcpy.Delete_management(output_feature_class)

    arcpy.MakeFeatureLayer_management(building, 'building_layer')
    arcpy.MakeFeatureLayer_management(cadastral, 'cadastral_layer')

    input_features = ['building_layer', 'cadastral_layer']
    output_feature_class = save

    arcpy.Intersect_analysis(input_features, output_feature_class)

    print(save)
    cads = save
    fid = []
    
    plot = []
    cad_area = []
   
    bfid = []
    
    arcpy.MakeFeatureLayer_management(cads, 'highest_layer')

    
    
    with arcpy.da.SearchCursor('highest_layer', ["FID_Buildi", "PLOT_NO_1", "Area_1"]) as cursor:
        for row in cursor:
            fid.append(row[0])
            plot.append(row[1])
            cad_area.append(row[2])

    with arcpy.da.SearchCursor('building_layer',["FID"])as cursor:
        for row in cursor:
            bfid.append(row[0])   

    counter = collections.Counter(fid)
    max_repetitions = max(counter.values())

    print("Maximum number of repetitions:", max_repetitions)

    for k in range(max_repetitions):
        arcpy.AddField_management("building_layer", "plot" + str(k), "DOUBLE")
        arcpy.AddField_management("building_layer", "area" + str(k), "DOUBLE")

    plot_dict = {}
    area_dict = {}

    # Loop through the data and populate the dictionaries
    for i, p, c in zip(fid, plot, cad_area):
        if i not in plot_dict:
            plot_dict[i] = []
        plot_dict[i].append(p)
        
        if i not in area_dict:
            area_dict[i] = []
        area_dict[i].append(c)

    # Append 0 for missing values in plot_dict and area_dict
    for key in plot_dict:
        plot_dict[key].extend([0] * (max_repetitions - len(plot_dict[key])))

    for key in area_dict:
        area_dict[key].extend([0] * (max_repetitions - len(area_dict[key])))

    plot_lists = []  # List to store the grouped plot values
    plot_lists2 = []  # List to store the grouped area values

    for j in range(max_repetitions):
        plot_list = []
        for i in bfid:
            if i in plot_dict and j < len(plot_dict[i]):
                plot_list.append(plot_dict[i][j])
        if plot_list:
            plot_lists.append(plot_list)

    for m in range(max_repetitions):
        plot_list2 = []
        for l in bfid:
            if l in area_dict and m < len(area_dict[l]):
                plot_list2.append(area_dict[l][m])
        if plot_list2:
            plot_lists2.append(plot_list2)

    print("plot_lists:", plot_lists)
    print("plot_lists2:", plot_lists2)

    # Update the feature layer with the values from plot_lists and plot_lists2
    for j in range(max_repetitions):
        field_name = "plot" + str(j)
        field_name2 = "area" + str(j)
        with arcpy.da.UpdateCursor("building_layer", ["FID", field_name, field_name2]) as cursor:
            for row in cursor:
                fid = row[0]
                value = plot_lists[j][fid] if fid < len(plot_lists[j]) else 0
                value2 = plot_lists2[j][fid] if fid < len(plot_lists2[j]) else 0
                row[1] = value
                row[2] = value2
                cursor.updateRow(row)


    print("Data added to 'final_plot' and 'cad_area' fields.")


# Create a label and entry for folder selection
Label(root, text="Select  building").grid(row=0, column=0)
loc = Entry(root, width=40)
loc.grid(row=0, column=1)
Button(root, text="...", command=open_file1).grid(row=0, column=2)

Label(root, text="Select  cadastral").grid(row=1, column=0)
loc1 = Entry(root, width=40)
loc1.grid(row=1, column=1)
Button(root, text="...", command=open_file2).grid(row=1, column=2)

Label(root, text="Select the folder for area calculation").grid(row=2, column=0)
loc2 = Entry(root, width=40)
loc2.grid(row=2, column=1)
Button(root, text="...", command=open_file).grid(row=2, column=2)

# Create a label and entry for field name
# Label(root, text="Field name").grid(row=3, column=0)
# field = Entry(root, width=40)
# field.grid(row=3, column=1)

# Create buttons for actions
Button(root, text="OK", command=ok).grid(row=4, column=1)
Button(root, text="Quit", command=root.destroy).grid(row=8, column=1)

# generator
Label(root, text="Select where u want to store shp file").grid(row=5, column=0)
loc3 = Entry(root, width=40)
loc3.grid(row=5, column=1)
Button(root, text="...", command=open_file3).grid(row=5, column=2)

global name
Label(root, text="file name").grid(row=6, column=0)
name = Entry(root, width=40)
name.grid(row=6, column=1)

Button(root, text="Generate Output", command=cad).grid(row=7, column=1)

root.mainloop()

