# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
from PIL import Image
from RavensObject import RavensObject
from RelationshipDifference import RelationshipDifference
from ShapeRelationship import ShapeRelationship


class Agent:

    sizes = [
        "very small",
        "small",
        "medium",
        "large",
        "very large",
        "huge"
    ]

    fills = [
        "no",
        "bottom-half",
        "top-half",
        "left-half",
        "right-half",
        "yes"
    ]

    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        pass

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an integer representing its
    # answer to the question: "1", "2", "3", "4", "5", or "6". These integers
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName() (as Strings).
    #
    # In addition to returning your answer at the end of the method, your Agent
    # may also call problem.checkAnswer(int givenAnswer). The parameter
    # passed to checkAnswer should be your Agent's current guess for the
    # problem; checkAnswer will return the correct answer to the problem. This
    # allows your Agent to check its answer. Note, however, that after your
    # agent has called checkAnswer, it will *not* be able to change its answer.
    # checkAnswer is used to allow your Agent to learn from its incorrect
    # answers; however, your Agent cannot change the answer to a question it
    # has already answered.
    #
    # If your Agent calls checkAnswer during execution of Solve, the answer it
    # returns will be ignored; otherwise, the answer returned at the end of
    # Solve will be taken as your Agent's answer to this problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self, problem):
        return 1

    def generate_figures(self, current_figure, goal_figure):
        relationship_differences = self.get_relationship_differences(current_figure, goal_figure)
        next_figures = {}

        # Generate a set of possible transformations that may rectify the relationship difference between the
        # current figure and the goal figure
        for difference in relationship_differences:
            new_objects = self.apply_all_transformations(difference.old_relationship.object1)

            for new_object in new_objects:
                new_figure = current_figure
                new_figure.objects[difference.old_relationship.object1.name] = new_object
                next_figures[new_figure.name] = new_figure

        return next_figures

    # Get the figure with the least number of differences
    def test_figures(self, next_figures, goal_figure):
        figure_scores = {}

        for figure_name, figure in next_figures.items():
            figure_scores[figure_name] = self.compare_figures(figure, goal_figure)

        lowest_score = float("inf")
        best_figure = RavensObject()
        for figure_name, score in figure_scores.items():
            if score < lowest_score:
                lowest_score = score
                best_figure = next_figures[figure_name]
            elif score == lowest_score:
                # Decide between the two figures based on the preferred order of transformations
                best_figure = self.utilize_preferences(next_figures[figure_name], best_figure)

        return best_figure

    def get_relationship_differences(self, current_figure, goal_figure):
        relationship_differences = []
        current_objects = {}
        goal_objects = {}

        # Create dictionary with RavensObject name as key and list of ShapeRelationship as value
        for object_name, raven_object in current_figure.objects.items():
            current_objects[object_name] = self.get_relationships(current_figure, raven_object)

        # Create dictionary with RavensObject name as key and list of ShapeRelationship as value
        for object_name, raven_object in goal_figure.objects.items():
            goal_objects[object_name] = self.get_relationships(goal_figure, raven_object)

        for object_name in current_objects:
            if object_name in goal_objects:
                for current_relationship in current_objects[object_name]:
                    for goal_relationship in goal_objects[object_name]:
                        # Add RelationshipDifference to list only if relationship between shapes has changed between
                        # the figures
                        if (current_relationship.object1.name == goal_relationship.object1.name and
                                current_relationship.object2.name == goal_relationship.object2.name and
                                current_relationship.value != goal_relationship.value):
                            relationship_differences.append(RelationshipDifference(
                                current_relationship, goal_relationship
                            ))

        return relationship_differences

    # Get the differences of shapes between figures by comparing the attributes of the shape for identical values
    def compare_figures(self, figure, goal_figure):
        score = 0

        for object_name, raven_object in figure.objects.items():
            for goal_object_name, goal_object in goal_figure.objects.items():
                if object_name == goal_object_name:
                    # Calculate similarity of shape in both figures using attribute values
                    for attribute_name, attribute in raven_object.attributes.items():
                        for goal_attribute_name, goal_attribute in goal_object.attributes.items():
                            # Increase score if the shape between the figures is different
                            if attribute_name == goal_attribute_name and attribute != goal_attribute:
                                score += 1

        return score

    def utilize_preferences(self, figure1, figure2):
        return figure1

    def get_relationships(self, raven_figure, raven_object):
        relationships = []

        for key in raven_object.attributes:
            if key == "inside" or key == "above" or key == "left-of" or key == "overlaps":
                relationship_values = [x.strip() for x in raven_object.attributes[key].split(',')]
                for value in relationship_values:
                    relationships.append(ShapeRelationship(raven_object, raven_figure.objects[value], key))

        return relationships

    def apply_all_transformations(self, raven_object):
        new_objects = []

        # Append current shape state to list for 'unchanged' transformation
        new_objects.append(raven_object)

        # Get all possible sizes of shape
        new_objects.extend(self.apply_size_transformations(raven_object))

        # Get all possible angles shape
        if "angle" in raven_object.attributes:
            new_objects.extend(self.apply_rotate_transformations(raven_object))

        # Fill shape
        if "fill" in raven_object.attributes:
            new_objects.extend(self.apply_object_fills(raven_object))

        return new_objects

    def apply_size_transformations(self, raven_object):
        new_objects = []

        # Keep expanding object to largest size
        new_object = raven_object
        while new_object.attributes["size"] != self.sizes[len(self.sizes) - 1]:
            new_object = self.expand_object(new_object)
            new_objects.append(new_object)

        # Keep contracting object to smallest size
        new_object = raven_object
        while new_object.attributes["size"] != self.sizes[0]:
            new_object = self.contract_object(new_object)
            new_objects.append(new_object)

        return new_objects

    def apply_rotate_transformations(self, raven_object):
        new_objects = []

        # Keep rotating object counter clockwise to 360 degrees
        new_object = raven_object
        while new_object.attributes["angle"] < 360:
            new_object = self.rotate_object_counter_clockwise(raven_object)
            new_objects.append(new_object)

        # Keep rotating object clockwise to 0 degrees
        new_object = raven_object
        while new_object.attributes["angle"] >= 0:
            new_object = self.rotate_object_clockwise(raven_object)
            new_objects.append(new_object)

        return new_objects

    def apply_object_fills(self, raven_object):
        new_objects = []

        # Apply all fills to object
        for fill in self.fills:
            new_object = raven_object
            if new_object.attributes["fill"] != fill:
                new_object.attributes["fill"] = fill
                new_objects.append(raven_object)

        return new_objects

    def expand_object(self, raven_object):
        new_raven_object = raven_object

        # Get current size of shape
        size_value = raven_object.attributes.get("size")
        # Expand shape to next size
        size_value = self.sizes[self.sizes.index(size_value) + 1]
        # Assign new size to shape
        new_raven_object.attributes["size"] = size_value

        return new_raven_object

    def contract_object(self, raven_object):
        new_raven_object = raven_object

        # Get current size of shape
        size_value = raven_object.attributes.get("size")
        # Contract shape to next size
        size_value = self.sizes[self.sizes.index(size_value) - 1]
        # Assign new size to shape
        new_raven_object.attributes["size"] = size_value

        return new_raven_object

    def rotate_object_clockwise(self, raven_object):
        new_object = raven_object

        # Get current angle of shape
        angle_value = raven_object.attributes.get("angle")
        # Decrease angle by 15 degrees
        angle_value -= 15
        # Assign new angle to shape
        new_object.attributes["angle"] = angle_value

        return new_object

    def rotate_object_counter_clockwise(self, raven_object):
        new_object = raven_object

        # Get current angle of shape
        angle_value = raven_object.attributes.get("angle")
        # Increase angle by 15 degrees
        angle_value += 15
        # Assign new angle to shape
        new_object.attributes["angle"] = angle_value

        return new_object
