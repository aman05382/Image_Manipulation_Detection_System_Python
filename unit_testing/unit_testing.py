"""
Author: Khai Yuan Chee
Last updated: 23/10/19
Description: Python program to test the accuracy, TPR and FPR of the copy-move detection algorithm
"""

from detector_testing import detect_copy_move, readImage
from glob import glob

TP = 0  # True positive
FP = 0  # False positive
TN = 0  # True negative
FN = 0  # False negative

def test_images(paths, img_label):
    """
    Function to test the results of the copy-move forgery detection algorithm against the ground truth
    :param paths: List of path to image files
    :param img_label: label of images
    :return: None
    """
    assert img_label in ["original", "forged"], "img_label must be either 'original' or 'forged'"

    global TP
    global FP
    global TN
    global FN

    # Test each image in the paths
    for path in paths:
        img = readImage(path)
        result = detect_copy_move(img)

        if result and img_label == "forged":
            TP += 1

        elif result and img_label == "original":
            FP += 1

        elif not result and img_label == "original":
            TN += 1

        elif not result and img_label == "forged":
            FN += 1

            
            
def main():
    """
    Main Function
    """
    # Test original images
    original_path = './original/*'
    original_paths = glob(original_path)
    test_images(original_paths, "original")

    # Test forged images
    forged_path = './forged/*'
    forged_paths = glob(forged_path)
    test_images(forged_paths, "forged")

    # Number of test images
    n = len(original_paths) + len(forged_paths)

    # Accuracy
    acc = (TP + TN) / (TP + TN + FP + FN)

    # True positive rate
    TPR = TP / (TP + FN)

    # False positive rate
    FPR = FP / (FP + TN)


    # Write results into a text file
    filename = "test_results.txt"
    with open(filename, "w+") as file:
        file.write("Tested with " + str(n) + " images \n")
        file.write("Original images: " + str(len(original_paths)) + "\n")
        file.write("Forged imageas: " + str(len(forged_paths)) + "\n"
                   )
        file.write("Accuracy: " + str(acc) + "\n")
        file.write("True Positive Rate: " + str(TPR) + "\n")
        file.write("False Positive Rate: " + str(FPR) + "\n")


if __name__ == "__main__":
    main()
