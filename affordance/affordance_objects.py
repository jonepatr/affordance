from .object_in_space import ObjectInSpace

# http://www.timotheegroleau.com/Flash/experiments/easing_function_generator.htm


class AffordanceObjects(ObjectInSpace):
    def __init__(self, df, uni, arduino, trackables, machine_name, human_name):
        ObjectInSpace.__init__(self, df, arduino)
        self.machine_name = machine_name
        self.human_name = human_name
        self.trackables = trackables
        self.arduino = arduino
        self.dependent_objects = dict()
        self.uni = uni
        self.state = ""
        self.uni.add_trackable(self, machine_name)
        
    def unity_answer(self):
        return [[
            self.machine_name,
            self.position[0],
            self.position[1],
            self.position[2],
            self.angle[0],
            self.angle[1],
            self.angle[2],
            self.angle[3]
        ]]







