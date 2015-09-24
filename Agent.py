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
#from PIL import Image
from enum import Enum


class Figure(Enum):
    A = 1
    B = 2
    C = 3
    D = 4
    E = 5
    F = 6
    G = 7
    H = 8
    I = 9


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

    relationships = [
        "inside",
        "above",
        "left-of",
        "overlaps"
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
        # Get size of matrix
        size = 0
        if problem.problemType == "2x2":
            size = 2
        elif problem.problemType == "3x3":
            size = 3

        # Get differences between last two figures in first row
        row_end = size
        figure1 = problem.figures[Figure(row_end - 1).name]
        figure2 = problem.figures[Figure(row_end).name]
        row_object_correspondences = self.get_object_correspondences(figure1, figure2)
        row_differences = self.get_object_differences(figure1, figure2, row_object_correspondences)

        # Get differences between last two figures in first column
        column_end = 1 + (size * (size - 1))
        figure1 = problem.figures[Figure(column_end - size).name]
        figure2 = problem.figures[Figure(column_end).name]
        column_object_correspondences = self.get_object_correspondences(figure1, figure2)
        column_differences = self.get_object_differences(figure1, figure2, column_object_correspondences)

        # The figure name as key and similarity score of differences as value
        answer_differences_similarity = {}
        for x in range(1, 7):
            score = 0

            last_element = size * size
            # Get differences between last two figures in last row
            figure1 = problem.figures[Figure(last_element - 1).name]
            figure2 = problem.figures[str(x)]
            answer_row_object_correspondences = self.get_object_correspondences(figure1, figure2)
            answer_row_differences = self.get_object_differences(figure1, figure2, answer_row_object_correspondences)

            # Get differences between last two figures in last column
            figure1 = problem.figures[Figure(last_element - size).name]
            figure2 = problem.figures[str(x)]
            answer_column_object_correspondences = self.get_object_correspondences(figure1, figure2)
            answer_column_differences = self.get_object_differences(figure1, figure2, answer_column_object_correspondences)

            # Compare differences between rows using the object correspondences for first two figures in row
            score += self.compare_differences(row_differences, answer_row_differences, column_object_correspondences)
            # Compare differences between rows using the object correspondences for the second two figures in row
            score += self.compare_differences(row_differences, answer_row_differences, answer_column_object_correspondences)
            # Compare differences between columns using the object correspondences for first two figures in column
            score += self.compare_differences(column_differences, answer_column_differences, row_object_correspondences)
            # Compare differences between columns using the object correspondences for second two figures in column
            score += self.compare_differences(column_differences, answer_column_differences, answer_row_object_correspondences)

            answer_differences_similarity[str(x)] = score

        # Choose answer with highest number of similarities
        answer = -1
        high_score = 0
        for figure_name, score in answer_differences_similarity.items():
            if score > high_score:
                answer = int(figure_name)
                high_score = score

        return answer

    # Returns dictionary with object name as key and list of attribute names as
    # value. The dictionary represents any differences between an object in
    # two figures, with the differing attribute noted in the list of attribute
    # names (value) for the object name (key).
    def get_object_differences(self, figure1, figure2, object_correspondences):
        object_differences = {}

        for object1_name, raven_object1 in figure1.objects.items():
            # Store names of differing attributes
            differences = []
            # Get corresponding object in second figure
            if object1_name in object_correspondences:
                object2_name = object_correspondences[object1_name]
                # Get list of differing attributes for the object in both figures
                for attribute1_name, attribute1 in raven_object1.attributes.items():
                    for attribute2_name, attribute2 in figure2.objects[object2_name].attributes.items():
                        if attribute1_name == attribute2_name:
                            # Inside is different if corresponding shape is not inside corresponding parent(s)
                            if attribute1_name == "inside":
                                object1_parents = [x.strip() for x in attribute1.split(',')]
                                object2_parents = [x.strip() for x in attribute2.split(',')]
                                if len(object1_parents) != len(object2_parents):
                                    differences.append(attribute1_name)
                                else:
                                    for object1_parent in object1_parents:
                                        if object1_parent in object_correspondences:
                                            if object_correspondences[object1_parent] not in object2_parents:
                                                differences.append(attribute1_name)
                            elif attribute1 != attribute2:
                                differences.append(attribute1_name)
                # Object was unchanged if there are no differences
                if not differences:
                    differences.append("unchanged")
            else:
                # Object was deleted in second figure
                differences.append("deleted")
            # Insert list in the dictionary if differences exist
            if differences:
                object_differences[object1_name] = differences

        # Check if any objects in second figure were added
        for object2_name in figure2.objects:
            differences = []
            if object2_name not in object_correspondences.values():
                differences.append("added")
                object_differences[object2_name] = differences

        return object_differences

    def compare_differences(self, set1, set2, object_correspondences):
        similarities = 0

        for object1_name, object1_differences in set1.items():
            if object1_name in object_correspondences:
                object2_name = object_correspondences[object1_name]
                for object1_difference in object1_differences:
                    if object2_name in set2:
                        for object2_difference in set2[object2_name]:
                            if object1_difference == object2_difference:
                                similarities += 1

        return similarities

    # Get objects in figure 1 and figure 2 that correspond with one another. In
    # other words match up the objects between the figures.
    def get_object_correspondences(self, figure1, figure2):
        # figure1.object.name as key and figure2.object.name as value
        object_correspondences = {}

        if len(figure1.objects) == 1 and len(figure2.objects) == 1:
            # There is a one to one correspondence of objects
            object_correspondences[list(figure1.objects.keys())[0]] = list(figure2.objects.keys())[0]
        # elif not self.has_repeated_shapes(figure1) and not self.has_repeated_shapes(figure2):
        #     for object1_name, raven_object1 in figure1.objects.items():
        #         for object2_name, raven_object2 in figure2.objects.items():
        #             if raven_object1.attributes["shape"] == raven_object2.attributes["shape"]:
        #                 object_correspondences[object1_name] = object2_name
        # Match up objects based on highest number of similarities
        else:
            # object1.name as key and dictionary of object2.name as key and similarity score as value
            object_similarity_scores = {}
            for object1_name, raven_object1 in figure1.objects.items():
                # object2.name as key and similarity score as value
                similarity_scores = {}
                for object2_name, raven_object2 in figure2.objects.items():
                    similarity_score = 0
                    for attribute1_name, attribute1 in raven_object1.attributes.items():
                        for attribute2_name, attribute2 in raven_object2.attributes.items():
                            if attribute1_name == attribute2_name and attribute1 == attribute2:
                                similarity_score += 1
                    similarity_scores[object2_name] = similarity_score
                object_similarity_scores[object1_name] = similarity_scores

            for object1_name in figure1.objects:
                for object2_name in figure2.objects:
                    # Check if object1 has the highest similarity score with object2
                    most_similar = True
                    for object_name, similarity_scores in object_similarity_scores.items():
                        if object_name != object1_name:
                            if (similarity_scores[object2_name] >
                                    object_similarity_scores[object1_name][object2_name]):
                                most_similar = False
                    if most_similar is True and object2_name not in object_correspondences.values():
                        object_correspondences[object1_name] = object2_name

        return object_correspondences

    # MEANS END ANALYSIS METHODS #

    # # Get the figure with the least number of differences
    # def test_figures(self, next_figures, goal_figure):
    #     figure_scores = {}
    #
    #     for figure_name, figure in next_figures.items():
    #         figure_scores[figure_name] = self.compare_figures(figure, goal_figure)
    #
    #     lowest_score = float("inf")
    #     best_figure = RavensObject()
    #     for figure_name, score in figure_scores.items():
    #         if score < lowest_score:
    #             lowest_score = score
    #             best_figure = next_figures[figure_name]
    #         elif score == lowest_score:
    #             # Decide between the two figures based on the preferred order of transformations
    #             best_figure = self.utilize_preferences(next_figures[figure_name], best_figure)
    #
    #     return best_figure
    #
    # # Return the number of differences between the shapes in two figures
    # def contrast_figures(self, figure1, figure2):
    #     differences = 0
    #
    #     for object1_name, raven_object1 in figure1.objects.items():
    #         for object2_name, raven_object2 in figure2.objects.items():
    #             if object1_name == object2_name:
    #                 # Calculate similarity of shape in both figures using attribute values
    #                 for attribute1_name, attribute1 in raven_object1.attributes.items():
    #                     for attribute2_name, attribute2 in raven_object2.attributes.items():
    #                         # Add difference if the shape between the figures is different
    #                         if attribute1_name == attribute2_name and attribute1 != attribute2:
    #                             differences += 1
    #
    #     return differences
    #
    # def generate_figures(self, current_figure, goal_figure):
    #     relationship_differences = self.get_relationship_differences(current_figure, goal_figure)
    #     next_figures = {}
    #
    #     # Generate a set of possible transformations that may rectify the relationship difference between the
    #     # current figure and the goal figure
    #     for difference in relationship_differences:
    #         new_objects = self.apply_all_transformations(difference.old_relationship.object1)
    #
    #         for new_object in new_objects:
    #             new_figure = current_figure
    #             new_figure.objects[difference.old_relationship.object1.name] = new_object
    #             next_figures[new_figure.name] = new_figure
    #
    #     return next_figures
    #
    # # Returns a set of figures
    # def generate_figures(self, current_figure, goal_figure):
    #     object_differences = self.get_object_differences(current_figure, goal_figure)
    #     next_figures = {}
    #
    #     # Generate a set of possible transformations that may rectify the object difference between the
    #     # current figure and the goal figure
    #     for object_name, difference_list in object_differences.items():
    #         new_object = self.apply_all_transformations(current_figure.objects[object_name])
    #         new_figure = current_figure
    #         new_figure.objects[object_name] = new_object
    #         next_figures[new_figure.name] = new_figure
    #
    #     return next_figures
    #
    # def get_relationship_differences(self, current_figure, goal_figure):
    #     relationship_differences = []
    #     current_objects = {}
    #     goal_objects = {}
    #
    #     # Create dictionary with RavensObject name as key and list of ShapeRelationship as value
    #     for object_name, raven_object in current_figure.objects.items():
    #         current_objects[object_name] = self.get_relationships(current_figure, raven_object)
    #
    #     # Create dictionary with RavensObject name as key and list of ShapeRelationship as value
    #     for object_name, raven_object in goal_figure.objects.items():
    #         goal_objects[object_name] = self.get_relationships(goal_figure, raven_object)
    #
    #     for object_name in current_objects:
    #         if object_name in goal_objects:
    #             for current_relationship in current_objects[object_name]:
    #                 for goal_relationship in goal_objects[object_name]:
    #                     # Add RelationshipDifference to list only if relationship between shapes has changed between
    #                     # the figures
    #                     if (current_relationship.object1.name == goal_relationship.object1.name and
    #                                 current_relationship.object2.name == goal_relationship.object2.name and
    #                                 current_relationship.value != goal_relationship.value):
    #                         relationship_differences.append(RelationshipDifference(
    #                             current_relationship, goal_relationship
    #                         ))
    #
    #     return relationship_differences
    #
    # def utilize_preferences(self, figure1, figure2):
    #     return figure1
    #
    # def get_relationships(self, raven_figure, raven_object):
    #     # List of ObjectRelationship objects
    #     object_relationships = []
    #
    #     for attribute_name, attribute in raven_object.attributes.items():
    #         if attribute_name in self.relationships:
    #             # An object can have the same relationship with multiple other objects
    #             relationship_values = [x.strip() for x in raven_object.attributes[attribute_name].split(',')]
    #             for value in relationship_values:
    #                 object_relationships.append(
    #                     ObjectRelationship(raven_object.name, raven_figure.objects[value], attribute_name
    #                 ))
    #
    #     return object_relationships
    #
    # def apply_all_transformations(self, raven_object):
    #     new_objects = []
    #
    #     # Append current shape state to list for 'unchanged' transformation
    #     new_objects.append(raven_object)
    #
    #     # Get all possible sizes of shape
    #     new_objects.extend(self.apply_size_transformations(raven_object))
    #
    #     # Get all possible angles shape
    #     if "angle" in raven_object.attributes:
    #         new_objects.extend(self.apply_rotate_transformations(raven_object))
    #
    #     # Fill shape
    #     if "fill" in raven_object.attributes:
    #         new_objects.extend(self.apply_object_fills(raven_object))
    #
    #     return new_objects
    #
    # def apply_size_transformations(self, raven_object):
    #     new_objects = []
    #
    #     # Keep expanding object to largest size
    #     new_object = raven_object
    #     while new_object.attributes["size"] != self.sizes[len(self.sizes) - 1]:
    #         new_object = self.expand_object(new_object)
    #         new_objects.append(new_object)
    #
    #     # Keep contracting object to smallest size
    #     new_object = raven_object
    #     while new_object.attributes["size"] != self.sizes[0]:
    #         new_object = self.contract_object(new_object)
    #         new_objects.append(new_object)
    #
    #     return new_objects
    #
    # def apply_rotate_transformations(self, raven_object):
    #     new_objects = []
    #
    #     # Keep rotating object counter clockwise to 360 degrees
    #     new_object = raven_object
    #     while new_object.attributes["angle"] < 360:
    #         new_object = self.rotate_object_counter_clockwise(raven_object)
    #         new_objects.append(new_object)
    #
    #     # Keep rotating object clockwise to 0 degrees
    #     new_object = raven_object
    #     while new_object.attributes["angle"] >= 0:
    #         new_object = self.rotate_object_clockwise(raven_object)
    #         new_objects.append(new_object)
    #
    #     return new_objects
    #
    # def apply_object_fills(self, raven_object):
    #     new_objects = []
    #
    #     # Apply all fills to object
    #     for fill in self.fills:
    #         new_object = raven_object
    #         if new_object.attributes["fill"] != fill:
    #             new_object.attributes["fill"] = fill
    #             new_objects.append(raven_object)
    #
    #     return new_objects
    #
    # def expand_object(self, raven_object):
    #     new_raven_object = raven_object
    #
    #     # Get current size of shape
    #     size_value = raven_object.attributes.get("size")
    #     # Expand shape to next size
    #     size_value = self.sizes[self.sizes.index(size_value) + 1]
    #     # Assign new size to shape
    #     new_raven_object.attributes["size"] = size_value
    #
    #     return new_raven_object
    #
    # def contract_object(self, raven_object):
    #     new_raven_object = raven_object
    #
    #     # Get current size of shape
    #     size_value = raven_object.attributes.get("size")
    #     # Contract shape to next size
    #     size_value = self.sizes[self.sizes.index(size_value) - 1]
    #     # Assign new size to shape
    #     new_raven_object.attributes["size"] = size_value
    #
    #     return new_raven_object
    #
    # def rotate_object_clockwise(self, raven_object):
    #     new_object = raven_object
    #
    #     # Get current angle of shape
    #     angle_value = raven_object.attributes.get("angle")
    #     # Decrease angle by 15 degrees
    #     angle_value -= 15
    #     # Assign new angle to shape
    #     new_object.attributes["angle"] = angle_value
    #
    #     return new_object
    #
    # def rotate_object_counter_clockwise(self, raven_object):
    #     new_object = raven_object
    #
    #     # Get current angle of shape
    #     angle_value = raven_object.attributes.get("angle")
    #     # Increase angle by 15 degrees
    #     angle_value += 15
    #     # Assign new angle to shape
    #     new_object.attributes["angle"] = angle_value
    #
    #     return new_object
