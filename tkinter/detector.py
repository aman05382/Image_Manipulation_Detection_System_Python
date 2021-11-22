import cv2
import imutils
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist
from collections import Counter


def readImage(image_name):
    """
    Function to read a given image name
    :param image_name: A string representing the name of the image
    :return: The image represented in a numpy.ndarray type
    """
    return cv2.imread(str(image_name))


def showImage(image):
    """
    Function to display the image to the user. Closes the image window when user presses any key
    :param image: An image of type numpy.ndarray
    :return: None
    """
    image = imutils.resize(image, width=600)
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def featureExtraction(image):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sift = cv2.xfeatures2d.SIFT_create()
    kp, desc = sift.detectAndCompute(gray_img, None)
    return kp, desc


def featureMatching(keypoints, descriptors):
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
    points = np.vstack((points_1, points_2))     # vertically stack both sets of points (row bind)
    dist_matrix = pdist(points, metric='euclidean')  # obtain condensed distance matrix (needed in linkage function)
    Z = hierarchy.linkage(dist_matrix, metric)

    cluster = hierarchy.fcluster(Z, t=threshold, criterion='inconsistent', depth=4) # perform agglomerative hierarchical clustering
    cluster, points = filterOutliers(cluster, points)   # filter outliers

    n = int(np.shape(points)[0]/2)
    return cluster,  points[:n], points[n:]


def filterOutliers(cluster, points):
    cluster_count = Counter(cluster)
    to_remove = []  # find clusters that does not have more than 3 points (remove them)
    for key in cluster_count:
        if cluster_count[key] <= 3:
            to_remove.append(key)

    indices = np.array([])   # find indices of points that corresponds to the cluster that needs to be removed

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
    plt.imshow(img)
    plt.axis('off')

    colors = C[:np.shape(p1)[0]]
    plt.scatter(p1[:, 0], p1[:, 1], c=colors, s=30)

    for coord1, coord2 in zip(p1, p2):
        x1 = coord1[0]
        y1 = coord1[1]

        x2 = coord2[0]
        y2 = coord2[1]

        plt.plot([x1, x2], [y1, y2], 'c', linestyle=":")

    plt.savefig("results.png", bbox_inches='tight', pad_inches=0)

    plt.clf()


def detect_copy_move(image):
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

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plotImage(image, p1, p2, clusters)
    return True


