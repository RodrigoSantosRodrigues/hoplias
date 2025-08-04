# Define initial positions
# position_chromosome_first_line_left = 592.06
# position_chromosome_first_line_top = 208.86
# position_chromosome_second_line_left = 592.06
# position_chromosome_second_line_top = 329.86
# position_chromosome_third_line_left = 592.06
# position_chromosome_third_line_top = 459.86
# position_chromosome_fourth_line_left = 592.06
# position_chromosome_fourth_line_top = 597.86

# position_label_fisrt_line_left = 600.94
# position_label_fisrt_line_top = 259.04
# position_label_second_line_left = 600.94
# position_label_second_line_top = 384.04
# position_label_third_line_left = 600.94
# position_label_third_line_top = 512.04
# position_label_fourth_line_left = 600.94
# position_label_fourth_line_top = 650.04

# position_size_fisrt_line_left = 600.64
# position_size_fisrt_line_top = 160.22
# position_size_second_line_left = 600.64
# position_size_second_line_top = 300.22
# position_size_third_line_left = 600.64
# position_size_third_line_top = 432.22
# position_size_fourth_line_left = 600.64
# position_size_fourth_line_top = 570.22


# position_chromosome_first_line_left, position_chromosome_first_line_top, position_label_fisrt_line_left, position_label_fisrt_line_top, position_size_fisrt_line_left, position_size_fisrt_line_top, index = append_chromosome_data(
#     first, position_chromosome_first_line_left, position_chromosome_first_line_top, position_label_fisrt_line_left, position_label_fisrt_line_top, position_size_fisrt_line_left, position_size_fisrt_line_top, index
# )
# position_chromosome_second_line_left, position_chromosome_second_line_top, position_label_second_line_left, position_label_second_line_top, position_size_second_line_left, position_size_second_line_top, index = append_chromosome_data(
#     second, position_chromosome_second_line_left, position_chromosome_second_line_top, position_label_second_line_left, position_label_second_line_top, position_size_second_line_left, position_size_second_line_top, index
# )
# position_chromosome_third_line_left, position_chromosome_third_line_top, position_label_third_line_left, position_label_third_line_top, position_size_third_line_left, position_size_third_line_top, index = append_chromosome_data(
#     third, position_chromosome_third_line_left, position_chromosome_third_line_top, position_label_third_line_left, position_label_third_line_top, position_size_third_line_left, position_size_third_line_top, index
# )
# position_chromosome_fourth_line_left, position_chromosome_fourth_line_top, position_label_fourth_line_left, position_label_fourth_line_top, position_size_fourth_line_left, position_size_fourth_line_top, index = append_chromosome_data(
#     fourth, position_chromosome_fourth_line_left, position_chromosome_fourth_line_top, position_label_fourth_line_left, position_label_fourth_line_top, position_size_fourth_line_left, position_size_fourth_line_top, index
# )


def save_result(classifier, skel, image, id_chromosome):
    import matplotlib.pyplot 	as plt 
    image_skel = classifier.create_overlay_image(image)
    image_geodesic = classifier.create_overlay_image_geodesic(image)
    image_simple = classifier.create_overlay_image_simple(image)
    image_final = classifier.create_overlay_image_final_paths(image)

    plt.figure(figsize=(30,30))
    plt.subplot(3, 3, 1)
    plt.imshow(classifier.binary, cmap='gray')
    plt.title('Img binary')
    plt.subplot(3, 3, 2)
    plt.imshow(classifier.binary, cmap='gray')
    plt.title('Img binary')
    plt.subplot(3, 3, 3)
    plt.imshow(skel, cmap='gray')
    plt.title('Img binary + skel')
    plt.subplot(3, 3, 4)
    plt.imshow(image_skel, cmap='gray')
    plt.title('Img skel + point + canny + convex')
    plt.subplot(3, 3, 5)
    plt.imshow(image_geodesic)
    plt.title('Result using distance geodesic')
    plt.subplot(3, 3, 6)
    plt.imshow(image_simple)
    plt.title('Result using distance simple')
    plt.subplot(3, 3, 8)
    plt.imshow(image_final)
    plt.title('Result final')
    plt.savefig(f'src/tmp/{id_chromosome}-plot-classifier.png')
    # plt.show()
