import datetime
import route
from random import uniform


class Truck:
    # This is the standard class containing all the variables and state info regarding the truck and its load
    # Basically here we manage "local" resources

    def __init__(self, available, loading_space, energy, route_list=route.RouteList()):
        self.starting_point = route.Stop(38.13923025164979, 15.52299862370226, True,
                                         datetime.datetime.now(), 1, -1)
        self.available = available
        self.loading_space = loading_space
        self.loading_space_left = loading_space
        self.energy = energy
        if route_list is None:
            self.dummy_route(5)
        else:
            self.route_list = route_list
        self.actual_position = None
        self.path = None
        self.node_route = None
        self.last_time_info = None

    # Setters and getters
    def set_available(self, available):
        self.available = available

    def is_available(self):
        return self.available

    def set_loading_space(self, loading_space):
        self.loading_space = loading_space

    def get_loading_space(self):
        return self.loading_space

    def set_loading_space_left(self, loading_space_left):
        self.loading_space_left = loading_space_left

    def get_loading_space_left(self):
        return self.loading_space_left

    def set_energy(self, energy):
        self.energy = energy

    def get_energy(self):
        return self.energy

    def set_route_list(self, route_list):
        self.route_list = route_list

    def get_route_list(self):
        return self.route_list

    def set_actual_position(self, actual_position):
        self.actual_position = actual_position

    def get_actual_position(self):
        return self.actual_position

    def set_starting_point(self, starting_point):
        self.starting_point = starting_point

    def get_starting_point(self):
        return self.starting_point

    def set_path(self, path):
        self.path = path

    def get_path(self):
        return self.path

    def set_node_route(self, node_route):
        self.node_route = node_route

    def get_node_route(self):
        return self.node_route

    def set_last_time_info(self, last_time_info):
        self.last_time_info = last_time_info

    def get_last_time_info(self):
        return self.last_time_info

    # Methods for route optimization
    def append_to_stop_list_from_job(self, new_job):
        self.get_route_list().append_from_job(new_job)

    def append_to_stop_list(self, stop):
        self.route_list.append_stop_to_list(stop)

    def dummy_route(self, num):
        r = route.RouteList()
        r.append_stop_to_list(self.starting_point)
        for i in range(num):
            d = datetime.datetime.now()
            job = route.Job(route.Stop(uniform(38.12, 38.26), uniform(15.49, 15.65), True, d, 1, i),
                            route.Stop(uniform(38.12, 38.26), uniform(15.49, 15.65), False, d, 1, i))
            r.append_from_job(job)
        self.set_route_list(r)

    def print_status(self):
        self.update_status()
        available_string = "The truck is correctly running." if self.is_available() else \
            "The truck is currently unavailable."
        print(f"{available_string}\n"
              f"Time:\t{datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}\n"
              f"Battery left:\t{self.get_energy()}\n"
              f"Space left:\t{self.get_loading_space_left()}\n"
              f"Actual_position:\t{self.get_actual_position()}")

    def recalculate_route(self, new_job):
        pass

    def update_status(self):
        # Ideally this method would read this information directly from the sensors of the vehicle, but for testing
        # purposes we will read them from a file
        file = "truck_status"
        with open(file, "r") as f:
            lines = f.read().splitlines()
            time = datetime.datetime.strptime(lines[-5], "%Y-%m-%d %H:%M:%S.%f")
            if self.get_last_time_info():
                if self.get_last_time_info() > time:
                    return False
            self.set_last_time_info(time)
            self.set_energy(float(lines[-4]))
            self.set_loading_space_left(float(lines[-3]))
            actual_position = [float(lines[-2]), float(lines[-1])]
            self.set_actual_position(actual_position)
            return True
