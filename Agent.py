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
# from PIL import Image
from enum import Enum
from collections import OrderedDict
from operator import itemgetter

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

    transformations = [
        "unchanged",
        "reflected",
        "deleted",
        "added",
        "rotated",
        "expanded",
        "contracted"
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

        # Get the set of differences for each answer inserted in the matrix
        for x in range(1, 7):
            # The number of similarities between the sets of differences
            similarity_score = 0

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

            similarity_score += self.compare_differences(
                row_differences,
                answer_row_differences,
                self.merge_two_dicts(
                    column_object_correspondences,
                    answer_column_object_correspondences)
            )

            similarity_score += self.compare_differences(
                column_differences,
                answer_column_differences,
                self.merge_two_dicts(
                    row_object_correspondences,
                    answer_row_object_correspondences)
            )

            answer_differences_similarity[str(x)] = similarity_score

        # Choose answer with highest number of similarities
        answer = -1
        high_score = 0
        for figure_name, similarity_score in answer_differences_similarity.items():
            if similarity_score > high_score:
                answer = int(figure_name)
                high_score = similarity_score

        return answer

    # Returns dictionary with object name as key and list of attribute names as
    # value. The dictionary represents any differences between an object in
    # two figures, with the differing attribute noted in the list of attribute
    # names (value) for the object name (key).
    def get_object_differences(self, figure1, figure2, object_correspondences):
        # The object name as key and list of attribute names as value
        object_differences = {}

        for object1_name, raven_object1 in figure1.objects.items():
            # Attribute as name and tuple with attribute value from object 1 as first value
            # and attribute value from object 2 as second value
            differences = {}
            # Get corresponding object in second figure
            if object1_name in object_correspondences:
                object2_name = object_correspondences[object1_name]
                # Get list of differing attributes for the object in both figures
                for attribute1_name, attribute1 in raven_object1.attributes.items():
                    raven_object2 = figure2.objects[object2_name]
                    for attribute2_name, attribute2 in raven_object2.attributes.items():
                        if attribute1_name == attribute2_name:
                            # Inside is different if corresponding shape is not inside corresponding parent(s)
                            if attribute1_name == "inside":
                                # Get list of objects in the relationship
                                object1_parents = [x.strip() for x in attribute1.split(',')]
                                object2_parents = [x.strip() for x in attribute2.split(',')]
                                if len(object1_parents) != len(object2_parents):
                                    differences[attribute1_name] = (attribute1, attribute2)
                                else:
                                    for object1_parent in object1_parents:
                                        if object1_parent in object_correspondences:
                                            if object_correspondences[object1_parent] not in object2_parents:
                                                differences[attribute1_name] = (attribute1, attribute2)
                            elif attribute1 != attribute2:
                                differences[attribute1_name] = (attribute1, attribute2)

                            # Check for reflection transformation only if shape hasn't changed
                            if (raven_object1.attributes["shape"] == raven_object2.attributes["shape"] and
                                    attribute1_name == "angle"):
                                # Check if reflected across x or y-axis
                                if (int(attribute1) - int(attribute2) == 90 or
                                        int(attribute1) - int(attribute2) == -90):
                                    differences["reflected"] = ()
                # Object was unchanged if there are no differences
                if not differences:
                    differences["unchanged"] = ()
            else:
                # Object was deleted in second figure
                differences["deleted"] = ()
            # Insert list in the dictionary if differences exist
            if differences:
                object_differences[object1_name] = differences

        # Check if any objects in second figure were added
        for object2_name in figure2.objects:
            differences = {}
            if object2_name not in object_correspondences.values():
                differences["added"] = ()
                object_differences[object2_name] = differences

        return object_differences

    # Returns the number of similarities between two sets of differences as
    # an integer.
    def compare_differences(self, set1, set2, object_correspondences):
        similarities = 0

        for object1_name, object1_differences in set1.items():
            if object1_name in object_correspondences:
                object2_name = object_correspondences[object1_name]
                for object1_difference, values1 in object1_differences.items():
                    if object2_name in set2:
                        for object2_difference, values2 in set2[object2_name].items():
                            if object1_difference == object2_difference:
                                # Don't compare old and new values of difference if transformation
                                if object1_difference in self.transformations:
                                    similarities += 1
                                else:
                                    if values1[0] == values2[0] and values1[1] == values2[1]:
                                        similarities += 1

        # Check for differences that are not in both sets
        for object2_name in set2:
            if object2_name not in object_correspondences.values():
                similarities -= 1

        return similarities

    # Get objects in figure 1 and figure 2 that correspond with one another. In
    # other words match up the objects between the figures. Returns a dictionary
    # of an object name from the first figure  as key and its corresponding object
    # name in the second figure as value.
    def get_object_correspondences(self, figure1, figure2):
        # figure1.object.name as key and figure2.object.name as value
        object_correspondences = {}

        # Check if there is a one to one correspondence of objects
        if len(figure1.objects) == 1 and len(figure2.objects) == 1:
            object_correspondences[list(figure1.objects.keys())[0]] = list(figure2.objects.keys())[0]
        # Match up objects based on highest number of similarities
        else:
            # First figure object name as key and dictionary of second figure object name as key and
            # similarity score as value
            object_similarity_scores = {}
            # Get the number of similarities between an object in the first figure and each object
            # in the second figure
            for object1_name, raven_object1 in figure1.objects.items():
                # object2.name as key and similarity score as value
                similarity_scores = {}
                for object2_name, raven_object2 in figure2.objects.items():
                    similarity_score = 0
                    # Check if objects share the same attributes
                    if set(raven_object1.attributes.keys()) == set(raven_object2.attributes.keys()):
                        similarity_score += 1

                    # Check if attribute values are equal
                    for attribute1_name, attribute1 in raven_object1.attributes.items():
                        for attribute2_name, attribute2 in raven_object2.attributes.items():
                            if attribute1_name == attribute2_name and attribute1 == attribute2:
                                similarity_score += 1
                    similarity_scores[object2_name] = similarity_score
                object_similarity_scores[object1_name] = similarity_scores

            # Match up objects between the two figures based on the number of similarities
            for object1_name in figure1.objects:
                # Do not find corresponding object in second figure if already found
                if object1_name not in object_correspondences:
                    # Sort dictionary of second figure object names by highest similarity score
                    object2_similarities_sorted = OrderedDict(sorted(
                        object_similarity_scores[object1_name].items(),
                        key=itemgetter(1),
                        reverse=True
                    ))
                    # For each object name in second figure
                    for object2_name, similarity_score in object2_similarities_sorted.items():
                        # Get the other object from first figure with the highest similarity score for
                        # the object from the second figure
                        highest_similarity_score = similarity_score
                        most_similar_object1 = object1_name
                        for other_object1_name in figure1.objects:
                            if object1_name != other_object1_name:
                                other_similarity_score = object_similarity_scores[other_object1_name][object2_name]
                                if other_similarity_score >= highest_similarity_score:
                                    highest_similarity_score = other_similarity_score
                                    most_similar_object1 = other_object1_name

                        # Check if object1 has highest similarity with object from second figure
                        # compared to all other objects in the first figure
                        if similarity_score > highest_similarity_score:
                            object_correspondences[object1_name] = object2_name
                            break
                        else:
                            object_correspondences[most_similar_object1] = object2_name

        return object_correspondences

    def merge_two_dicts(self, x, y):
        z = x.copy()
        z.update(y)
        return z
