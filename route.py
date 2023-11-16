import datetime
import json


class RouteList:
    def __init__(self, stop_list=None):
        if stop_list is None:
            stop_list = []
        self.stop_list = stop_list

    def set_stop_list(self, stop_list):
        self.stop_list = stop_list

    def get_stop_list(self):
        return self.stop_list

    def get_stop_list_as_dict(self):
        i = 0
        d = {}
        for el in self.stop_list:
            d[i] = el
            i += 1
        return d

    def append_from_job(self, job):
        w, d = job.explode()
        self.stop_list.append(w)
        self.stop_list.append(d)

    def append_stop_to_list(self, stop):
        self.stop_list.append(stop)

    def delete_by_id(self, job_id, withdrawal=0):
        # I am using a value based flag to understand what stop must be deleted:
        # 0 = just the withdrawal
        # 1 = just the delivery
        # 2 = both
        for i in range(len(self.get_stop_list())):
            if self.get_stop_list()[i].get_delivery_id() == job_id:
                if withdrawal == 0:
                    if self.get_stop_list()[i].is_withdrawal():
                        del self.get_stop_list()[i]
                        break
                elif withdrawal == 1:
                    if not self.get_stop_list()[i].is_withdrawal():
                        del self.get_stop_list()[i]
                        break
                elif withdrawal == 2:
                    if self.get_stop_list()[i].is_withdrawal():
                        del self.get_stop_list()[i]
                        self.delete_by_id(job_id, 1)
                        break
                    if not self.get_stop_list()[i].is_withdrawal():
                        del self.get_stop_list()[i]
                        self.delete_by_id(job_id, 0)
                        break


class Stop:
    def __init__(self, longitude, latitude, withdrawal, time_of_request, priority, delivery_id):
        self.latitude = latitude
        self.longitude = longitude
        self.withdrawal = withdrawal
        self.time_of_request = time_of_request
        self.priority = priority
        self.delivery_id = delivery_id

    def set_latitude(self, latitude):
        self.latitude = latitude

    def get_latitude(self):
        return self.latitude

    def set_longitude(self, longitude):
        self.longitude = longitude

    def get_longitude(self):
        return self.longitude

    def set_withdrawal(self, withdrawal):
        self.withdrawal = withdrawal

    def is_withdrawal(self):
        return self.withdrawal

    def set_time_of_request(self, time_of_request):
        self.time_of_request = time_of_request

    def get_time_of_request(self):
        return self.time_of_request

    def set_priority(self, priority):
        self.priority = priority

    def get_priority(self):
        return self.priority

    def set_delivery_id(self, delivery_id):
        self.delivery_id = delivery_id

    def get_delivery_id(self):
        return self.delivery_id


class Job:
    def __init__(self, withdrawal, delivery):
        self.withdrawal = withdrawal
        self.delivery = delivery

    def set_withdrawal(self, withdrawal):
        self.withdrawal = withdrawal

    def get_withdrawal(self):
        return self.withdrawal

    def set_delivery(self, delivery):
        self.delivery = delivery

    def get_delivery(self):
        return self.delivery

    def explode(self):
        return self.get_withdrawal(), self.get_delivery()


class JobEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Job):
            stop_encoder = StopEncoder()
            return {
                "withdrawal": stop_encoder.encode(o.get_withdrawal()),
                "delivery": stop_encoder.encode(o.get_delivery())
            }
        else:
            return super().default(o)


class JobDecoder(json.JSONDecoder):
    def __init__(self, object_hook=None, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, o):
        stop_decoder = StopDecoder()
        decoded_job = Job(stop_decoder.decode(o.get("withdrawal")),
                          stop_decoder.decode(o.get("delivery")))
        return decoded_job


class StopEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Stop):
            return {
                "latitude": o.get_latitude(),
                "longitude": o.get_longitude(),
                "withdrawal": o.is_withdrawal(),
                "time_of_request": str(o.get_time_of_request()),
                "priority": o.get_priority(),
                "delivery_id": o.get_delivery_id()
            }
        else:
            return super().default(o)


class StopDecoder(json.JSONDecoder):
    def __init__(self, object_hook=None, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, o):
        decoded_stop = Stop(o.get("latitude"),
                            o.get("longitude"),
                            o.get("withdrawal"),
                            datetime.datetime.strptime(o.get("time_of_request"), "%Y-%m-%d %H:%M:%S.%f"),
                            o.get("priority"),
                            o.get("delivery_id"))
        return decoded_stop
