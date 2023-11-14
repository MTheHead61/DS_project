import datetime


def write_truck_status(energy: float, loading_space_left: float, actual_position: list):
    with open("truck_status", "a") as f:
        f.writelines(str(datetime.datetime.now())+"\n")
        f.writelines(str(energy)+"\n")
        f.writelines(str(loading_space_left)+"\n")
        f.writelines(str(actual_position[0])+"\n")
        f.writelines(str(actual_position[1])+"\n")
