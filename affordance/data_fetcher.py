import vrpn
import threading
import time
from functools import partial
import config

class DataFetcher(threading.Thread):
    daemon = True

    def __init__(self, mongo, opti_track_mode=True):
        super(DataFetcher, self).__init__()
        self.opti_track_mode = opti_track_mode
        self.mongo = mongo
        self.trackables = list()
        self.trackers = []
        self.data_runner = None
        self.stop = True
        self.record_for_study = False
        self.study_data = []
        self.fat_var = []
        #self.mongo_tracking.remove({})

    def add_trackable(self, trackable):
        self.trackables.append(trackable)

    def middle_callback(self, trackable, index, userdata, data):
        if self.record_for_study:
            self.fat_var.append({"trials." + self.study_data[1] + ".optitrack_data": {"userdata": userdata, "data": data, "index": index, "trackable_name": trackable.machine_name}})
        if not self.stop:
            trackable.on_data_callback(userdata, data, index)

    def get_data_for_study(self, current_study_participant, q_index):
        self.record_for_study = True
        self.study_data = [current_study_participant, q_index]
        self.fat_var = []

    def done_with_study_data(self):
        self.record_for_study = False
        self.study_data = []
        return self.fat_var

    def unregister_trackers(self):
        for tracker in self.trackers:
            tracker[0].unregister_change_handler("position", tracker[1], "position")
        self.trackers = []
        if not self.data_runner is None:
            self.data_runner.join()
            self.data_runner = None
        print("All trackers stopped!")


    def register_trackers(self):
        if self.opti_track_mode:
            for trackable in self.trackables:
                for i, tracker in enumerate(trackable.trackables):
                    print(tracker, i)
                    tracker_var = vrpn.receiver.Tracker(tracker + "@" + config.OPTITRACK_IP)
                    handler = partial(self.middle_callback, trackable, i)
                    tracker_var.register_change_handler("position", handler, "position")
                    self.trackers.append([tracker_var, handler])

            self.data_runner = threading.Thread(target=self.data_fetcher_loop)
            self.data_runner.start()
        print("All trackers started!")

    def data_fetcher_loop(self):
        while len(self.trackers) > 0:
            if not self.stop:
                for tracker in self.trackers:
                    tracker[0].mainloop()
                time.sleep(0.005)
            else:
                time.sleep(0.1)




    # def run(self):
    #     if self.opti_track_mode:
    #         while True:
    #
    #     else:
    #         pickle_data = pickle.load( open( "massive_file.pkl", "rb" ) )
    #         for x in range(10):
    #             for data in pickle_data:
    #                 self.hand.on_data_callback('', data)
    #                 time.sleep(0.001)
