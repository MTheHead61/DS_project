import external_controller
import route
import truck
import routes_calculator
import plot_functions
import time
import datetime
from random import uniform
# import node
# import server

if __name__ == "__main__":

    truck = truck.Truck(True, 100, 100, None)

    routes_calculator = routes_calculator.RoutesCalculator(truck)

    plotter = plot_functions.Plotter(routes_calculator.get_graph())

    start_time = datetime.datetime.now()

    routes_calculator.ant_col_alg()

    end_time = datetime.datetime.now()
    print(f"Time for ant colony algorithm with {len(truck.get_path()['path'])} stops: {end_time-start_time} seconds")

    truck.print_status()

    '''server = server.Server('127.0.0.1', 12345)
    server.start()

    node = node.Node('127.0.0.1', 12345, truck, routes_calculator)
    node.start()'''

    '''# FOR TESTING THE ADDING OF A NEW JOB
    d = datetime.datetime.now()
    job_id = uniform(20, 1000)
    new_job = route.Job(route.Stop(uniform(38.12, 38.26), uniform(15.49, 15.65), True, d, 1, job_id),
                        route.Stop(uniform(38.12, 38.26), uniform(15.49, 15.65), False, d, 1, job_id))

    new_path = routes_calculator.shortest_deviation(truck.get_route_list(), new_job, truck.get_path())

    print(new_path["path"])
    print(new_path["distance"])'''

    '''# FOR TESTING THE PLOT OF THE ROUTES
    plotter.plot_routes(truck.get_node_route())
    input()'''

    '''FOR TESTING THE UPDATE OF THE STATUS
    time.sleep(5)
    external_controller.write_truck_status(50, 80, [38.20, 15.52])
    truck.update_status()
    truck.print_status()

    time.sleep(5)
    external_controller.write_truck_status(30, 70, [38.25, 15.63])
    truck.update_status()
    truck.print_status()'''
