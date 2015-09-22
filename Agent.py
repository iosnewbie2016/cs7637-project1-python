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
from enum import Enum
from RavensObject import RavensObject
from RelationshipDifference import RelationshipDifference
from ShapeRelationship import ShapeRelationship


class Agent:

    sizes = [
        "very small",
        "small",
        "medium",
        "large",
        "very large"
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

    def get_relationship_differences(current_figure, goal_figure):
        relationship_differences = []
        current_objects = {}
        goal_objects = {}

        # Create dictionary with RavensObject name as key and list of ShapeRelationship as value
        for raven_object in current_figure.attributes:
            current_objects[raven_object.name] = Agent.get_relationships(current_figure, raven_object)

        # Create dictionary with RavensObject name as key and list of ShapeRelationship as value
        for raven_object in goal_figure.attributes:
            goal_objects[raven_object.name] = Agent.get_relationships(goal_figure, raven_object)

        for key1 in current_objects:
            for key2 in goal_objects:
                if key1 == key2:
                    for current_relationship in current_objects[key1]:
                        found = False

                        for goal_relationship in goal_objects[key2]:
                            if current_relationship == goal_relationship:
                                found = True
                            if found is False:
                                relationship_differences.append(RelationshipDifference(
                                    current_relationship, goal_relationship
                                ))

        return relationship_differences

    def generate_figures(self, current_figure, goal_figure):
        relationship_differences = Agent.get_relationship_differences(current_figure, goal_figure)
        next_figures = {}

        # Generate a set of possible transformations that may rectify the relationship difference between the
        # current figure and the goal figure
        for difference in relationship_differences:
            new_objects = Agent.apply_all_transformations(difference.old_value.object1)

            for new_object in new_objects:
                new_figure = current_figure
                new_figure.objects[difference.old_value.object1.name] = new_object
                next_figures[new_figure.name] = new_figure

        return next_figures

    def test_figures(self, next_figures, goal_figure):
        figure_scores = {}

        for key in next_figures:
            figure_scores[key] = Agent.compare_figures(next_figures[key], goal_figure)

        highest_score = 0
        best_figure = RavensObject()

        for key in figure_scores:
            if figure_scores[key] > highest_score:
                highest_score = figure_scores[key]
                best_figure = next_figures[key]
            elif figure_scores[key] == highest_score:
                # Decide between the two figures based on the preferred order of transformations
                best_figure = Agent.utilize_preferences(next_figures[key], best_figure)

        return best_figure

    def compare_figures(figure, goal_figure):
        return 1

    def get_relationships(raven_figure, raven_object):
        relationships = []

        for key in raven_object.attributes:
            if key == "inside" or key == "above" or key == "left-of" or key == "overlaps":
                relationship_values = [x.strip() for x in raven_object.attributes[key].split(',')]
                for value in relationship_values:
                    relationships.append(ShapeRelationship(raven_object, raven_figure.objects[value], key))

        return relationships

    def apply_all_transformations(self, raven_object):
        # Expand object to all larger sizes
        # Contract object to all smaller sizes
        # Rotate object

        pass

    def utilize_preferences(self, figure1, figure2):
        return figure1

    def expand_object(self, raven_object):
        new_raven_object = raven_object

        # Get current size of shape
        size_value = raven_object.attributes.get("size")

        # Expand shape to next size if possible
        if size_value != "very large":
            size_value = self.sizes[self.sizes.index(size_value) + 1]

        # Assign new size to shape
        new_raven_object.attributes["size"] = size_value

        return new_raven_object

    def contract_object(self, raven_object):
        new_raven_object = raven_object

        # Get current size of shape
        size_value = raven_object.attributes.get("size")

        # Expand shape to next size if possible
        if size_value != "very small":
            size_value = self.sizes[self.sizes.index(size_value) - 1]

        # Assign new size to shape
        new_raven_object.attributes["size"] = size_value

        return new_raven_object

    def rotate_object(self, raven_object):
        pass
