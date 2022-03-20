"""
Project : RGB-D Semantic Sampling
Authors : Marco Petri and Mirko Usuelli
--------------------------------------------------------------------------------
Degree : M.Sc. Computer Science and Engineering
Course : Image Analysis and Computer Vision
Professor : Vincenzo Caglioti
Advisors : Giacomo Boracchi, Luca Magri
University : Politecnico di Milano - A.Y. 2021/2022
"""
import cv2

from camera.Frame import Frame


class Matcher:
    """ Class implementing the tool 'Matcher' able to match relevant
    descriptors in an action, namely two images.
    """

    # Techniques available:
    FLANN = 'FLANN'
    DNN = 'DNN'

    def __init__(self,
                 num_features,
                 method,
                 search_algorithm=6,
                 filter_test=0.7):
        """ Constructor.

        :param num_features
            The number of features to be detected and matched afterwards.
        :type num_features: int

        :param method:
            The string name of the chosen matching-method.
        :type method: str

        :param search_algorithm:
            Search algorithm used by the matcher that must be recognizable also
            by the detecting method.
        :type search_algorithm: int

        :param filter_test:
            Value used to filter matching features through Lowe's Test.
        :type filter_test: float
        """
        self.num_features = num_features
        self.filter_test = filter_test

        # method choice
        if method == self.FLANN:
            # FLANN hyper-parameters by default
            if search_algorithm == 6:
                index_params = dict(algorithm=search_algorithm,
                                    table_number=6,
                                    key_size=12,
                                    multi_probe_level=1)
            else:
                index_params = dict(algorithm=search_algorithm,
                                    trees=5)
            search_params = dict(checks=self.num_features)
            self.core = cv2.FlannBasedMatcher(indexParams=index_params,
                                              searchParams=search_params)
        elif method == self.DNN:
            # TODO : link and develop Matching Deep Neural Network
            print('\033[91m' + 'DNN matcher to be done yet...' + '\033[0m')
        else:
            print('\033[91m' + 'Method not found' + '\033[0m')

    @staticmethod
    def _filter(matches,
                filter_test):
        """ Private static method useful to filter the images matching in a
        built-in way within the class.

        :param matches:
            Matched features.
        :type matches: list

        :param filter_test:
            Value used to filter matching features through Lowe's Test.
        :type: int

        :return:
            Good matches which passed the Lowe's test.
        :rtype: list
        """
        # empty list which will be enriched of inliers
        good = []
        try:
            for m, n in matches:
                # Lowe's test
                if m.distance < filter_test * n.distance:
                    good.append(m)
            return good
        except ValueError:
            print('\033[91m' + 'Filter matching error' + '\033[0m')
            pass

    def match(self,
              img_1: Frame,
              img_2: Frame):
        """ Merge the behaviour of all possible core techniques in one function
        in purpose of matching descriptors of the two images.

        :param img_1:
            First image.
        :type img_1: Frame

        :param img_2:
            Second image.
        :type img_2: Frame

        :return:
            Good matches which passed the Lowe's test.
        :rtype: list
        """
        matches = self.core.knnMatch(img_1.descriptors, img_2.descriptors, k=2)
        matches = [x for x in matches if len(x) == 2]
        return self._filter(matches, self.filter_test)

    @staticmethod
    def draw_matches(img_1: Frame,
                     img_2: Frame,
                     matches,
                     limit=-1):
        """ Private static method to be used to draw the final result of the
        matching procedure.

        :param img_1:
            First image.
        :type img_1: Frame

        :param img_2:
            Second image.
        :type img_2: Frame

        :param matches:
            Matched features.
        :type matches: list

        :param limit:
            Integer number which limits how many matching links to be drawn.
        :type limit: int

        :return:
            The two images merged into one image with matching links drawn.
        :rtype: image
        """
        # pre-conditions
        assert img_1.get_size() == img_2.get_size()

        # hyper-parameters before drawing
        draw_params = dict(matchColor=-1,  # draw matches in green color
                           singlePointColor=None,
                           matchesMask=None,  # draw only inliers
                           flags=2)

        # proper drawing method
        final_img = cv2.drawMatches(img_1.get_cv2_images(ret="rgb"),
                                    img_1.key_points,
                                    img_2.get_cv2_images(ret="rgb"),
                                    img_2.key_points,
                                    matches[:limit],
                                    None, **draw_params)

        width, height = img_1.get_size()
        return cv2.resize(final_img, (width * 2, height))
