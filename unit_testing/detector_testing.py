"""
Author: Nicholas Roosevelt Wong
Last updated: 23/10/19
Description: Python program that detects if an image has been forged.
"""

import cv2
import imutils
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist
from collections import Counter


def readImage(image_name):
    """
    Function to convert an image into a numpy array representation
    :param image_name: A string representing the name of the image
    :return: The image represented in a numpy.ndarray type
    """
    return cv2.imread(str(image_name))


def showImage(image):
    """
    Function to display the image to the user. Closes the image window when the user presses any key
    :param image: An image of type numpy.ndarray
    :return: None
    """
    image = imutils.resize(image, width=600)
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def featureExtraction(image):
    """
    Function to extract features from the image with the use of SIFT algorithm
    :param image: An image of type numpy.ndarray
    :return: A tuple representing (keypoints, descriptors)
    """
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sift = cv2.xfeatures2d.SIFT_create()
    kp, desc = sift.detectAndCompute(gray_img, None)
    return kp, desc


def featureMatching(keypoints, descriptors):
    """
    Function to match each keypoint in the image with its closest match
    :param keypoints: A 1-dimensional array representing all the keypoints extracted from the image
    :param descriptors: A 2-dimensional array of shape (n, 128), where n is the number of keypoints 
                        and 128 is the size of each descriptor for each keypoint
    :return: Returns a tuple (points1, points2), whereby the first element in points2 is the closest match to the first element in points1 and so on.
             Returns a tuple (None, None), if no matches was found.
    """
    norm = cv2.NORM_L2  # cv2.NORM_L2 is used since we are using the SIFT algorithm
    k = 10  # number of closest match we want to find for each descriptor

    # uses a brute force matcher(compare each descriptor of desc1, with each descriptor of desc2...)
    bf_matcher = cv2.BFMatcher(norm)
    matches = bf_matcher.knnMatch(descriptors, descriptors, k)  # finds 10 closest matches for each desc in desc1 with desc in desc2

    # apply ratio test to get good matches (2nn test)
    ratio = 0.5
    good_matches_1 = []
    good_matches_2 = []

    for match in matches:
        k = 1   # ignore the first element in the matches array (distance to itself is always 0)

        while match[k].distance < ratio * match[k + 1].distance:  # d_i/d_(i+1) < T (threshold)
            k += 1

        for i in range(1, k):
            # just to ensure points are spatially separated
            if pdist(np.array([keypoints[match[i].queryIdx].pt, keypoints[match[i].trainIdx].pt]), "euclidean") > 10:
                good_matches_1.append(keypoints[match[i].queryIdx])
                good_matches_2.append(keypoints[match[i].trainIdx])

    points_1 = [match.pt for match in good_matches_1]
    points_2 = [match.pt for match in good_matches_2]

    if len(points_1) > 0:
        points = np.hstack((points_1, points_2))  # column bind
        unique_points = np.unique(points, axis=0)  # remove any duplicated points
        return np.float32(unique_points[:, 0:2]), np.float32(unique_points[:, 2:4])

    else:
        return None, None


def hierarchicalClustering(points_1, points_2, metric, threshold):
    """
    Function to perform hierarchical agglomerative clustering on the two sets of points
    :param points_1: A 2d-array of shape (n, 2), where n is the number of points, and 2 is x and y coordinate
    :param points_2: A 2d-array of shape (n, 2), where n is the number of points, and 2 is x and y coordinate
    :param metric: The distance metric to use
    :param threshold: The threshold to apply when forming clusters
    :return: A triple (
                An array of length n. T[i] is the flat cluster number to which original observation i belongs.
                2d-array representing the first set of points,
                2d-array representing the second set of points)
    """
    points = np.vstack((points_1, points_2))     # vertically stack both sets of points (row bind)
    dist_matrix = pdist(points, metric='euclidean')  # obtain condensed distance matrix (needed in linkage function)
    Z = hierarchy.linkage(dist_matrix, metric)

    cluster = hierarchy.fcluster(Z, t=threshold, criterion='inconsistent', depth=4) # perform agglomerative hierarchical clustering
    cluster, points = filterOutliers(cluster, points)   # filter outliers

    n = int(np.shape(points)[0]/2)
    return cluster,  points[:n], points[n:]


def filterOutliers(cluster, points):
    """
    Function to filter the outliers in the image
    :param cluster: An array of length n. T[i] is the flat cluster number to which original observation i belongs.
    :param points: A 2d-array representing the candidate points in the image
    :return: A tuple (
                An 1d-array representing the cluster that each point correspond to,
                A 2d-array representing the candidate points after removing outliers)
    """
    cluster_count = Counter(cluster)
    to_remove = []  # find clusters that does not have more than 3 points (remove them)
    for key in cluster_count:
        if cluster_count[key] <= 3:
            to_remove.append(key)

    indices = np.array([])    # find indices of points that corresponds to the cluster that needs to be removed
    for i in range(len(to_remove)):
        indices = np.concatenate([indices, np.where(cluster == to_remove[i])], axis=None)

    indices = indices.astype(int)
    indices = sorted(indices, reverse=True)

    for i in range(len(indices)):   # remove points that belong to each unwanted cluster
        points = np.delete(points, indices[i], axis=0)

    for i in range(len(to_remove)):  # remove unwanted clusters
        cluster = cluster[cluster != to_remove[i]]

    return cluster, points


def plotImage(img, p1, p2, C):
    """
    Function to plot the region of forgery on the original image
    :param img: A numpy representation of the image (passed through readImage())
    :param p1: A 2d-array representing the first set of points
    :param p2: A 2d-array representing the second set of points
    :param C: A 1d-array representing the cluster that each point belongs to
    :return: None
    """
    plt.imshow(img)
    plt.axis('off')

    colors = C[:np.shape(p1)[0]]
    plt.scatter(p1[:, 0], p1[:, 1], c=colors, s=30)

    for item in zip(p1, p2):
        x1 = item[0][0]
        y1 = item[0][1]

        x2 = item[1][0]
        y2 = item[1][1]

        plt.plot([x1, x2], [y1, y2], 'c', linestyle=":")

    plt.clf()


def detect_copy_move(image):
    """
    Main function of the program, detects if an image has been forged with copy-move
    :param image: A numpy representation of the image (passed through readImage() function)
    :return: True if the image is forged with copy-move, False otherwise.
    """
    kp, desc = featureExtraction(image)
    p1, p2 = featureMatching(kp, desc)
    # showImage(image)x

    if p1 is None:
        # print("No tampering was found")
        return False

    clusters, p1, p2 = hierarchicalClustering(p1, p2, 'ward', 2.2)

    if len(clusters) == 0:
        # print("No tampering was found")
        return False

    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # plotImage(image, p1, p2, clusters)
    return True


