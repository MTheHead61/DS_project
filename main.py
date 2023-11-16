import external_controller
import route
import truck
import routes_calculator
import plot_functions
import time
import datetime
from random import uniform
import json

if __name__ == "__main__":
    # INITIALIZATION
    truck = truck.Truck(True, 100, 100, None)

    routes_calculator = routes_calculator.RoutesCalculator(truck)

    plotter = plot_functions.Plotter(routes_calculator.get_graph())

    '''# TESTING THE JSON ENCODER AND DECODER
    d = datetime.datetime.now()
    job_id = uniform(20, 1000)
    job = route.Job(route.Stop(uniform(38.12, 38.26), uniform(15.49, 15.65), True, d, 1, job_id),
                    route.Stop(uniform(38.12, 38.26), uniform(15.49, 15.65), False, d, 1, job_id))

    print(type(job))
    w_1 = job.get_withdrawal()
    d_1 = job.get_delivery()
    print(w_1.get_latitude(), w_1.get_longitude())
    print(d_1.get_latitude(), d_1.get_longitude())

    job_json = json.dumps(job, cls=route.JobEncoder)

    print(type(job_json))
    print(job_json)

    job_2 = json.loads(job_json, cls=route.JobDecoder)

    print(type(job_2))
    w_2 = job.get_withdrawal()
    d_2 = job.get_delivery()
    print(w_2.get_latitude(), w_2.get_longitude())
    print(d_2.get_latitude(), d_2.get_longitude())'''

    # TESTING THE ANT COLONY ALGORITHM
    start_time = datetime.datetime.now()

    routes_calculator.ant_col_alg()

    end_time = datetime.datetime.now()
    print(f"Time for ant colony algorithm with {len(truck.get_path()['path'])} stops: {end_time-start_time} seconds")

    truck.print_status()

    '''# TESTING THE ADDING OF A NEW JOB
    d = datetime.datetime.now()
    job_id = uniform(20, 1000)
    new_job = route.Job(route.Stop(uniform(38.12, 38.26), uniform(15.49, 15.65), True, d, 1, job_id),
                        route.Stop(uniform(38.12, 38.26), uniform(15.49, 15.65), False, d, 1, job_id))

    new_path = routes_calculator.shortest_deviation(truck.get_route_list(), new_job, truck.get_path())

    print(new_path["path"])
    print(new_path["distance"])'''

    '''# TESTING THE PLOT OF THE ROUTES
    plotter.plot_routes(truck.get_node_route())
    input()'''

    '''TESTING THE UPDATE OF THE STATUS
    time.sleep(5)
    external_controller.write_truck_status(50, 80, [38.20, 15.52])
    truck.print_status()

    time.sleep(5)
    external_controller.write_truck_status(30, 70, [38.25, 15.63])
    truck.print_status()'''
