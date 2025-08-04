'''
plt.figure(figsize=(200,200))
plt.subplot(2,2,1)
plt.imshow(filtering.morphological_filtration())
plt.title('Image Filtred')
plt.subplot(2,2,2)
plt.imshow(morphologing.morphological_operations(), cmap='gray')
plt.title('Image Binary')
plt.subplot(2,2,3)
plt.imshow(image_build, cmap='gray')
plt.title('Image Classified')
plt.show()
'''