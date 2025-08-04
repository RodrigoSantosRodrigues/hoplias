# -*- coding: utf-8 -*-
'''
    author: Rodrigo Junior Santos
    Email:  rodrjuniorsantos@gmail.com
    
    Fonte: https://gist.github.com/kantale/e390cf7a47c4afdff9e4
           https://www.biostars.org/p/9922/
           http://pastebin.com/raw/6nBX6sdE
           https://www.ncbi.nlm.nih.gov/genome/542?fbclid=IwAR0rVGQST-xj-ndCRZDxy1epKkdgskbt47Co1-t6malN949LhQXtBsUSUY8
           https://cnvkit.readthedocs.io/en/stable/quickstart.html
'''
import re
#import matplotlib
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle
#from matplotlib.collections import PatchCollection, BrokenBarHCollection
from matplotlib import pyplot as plt
import mpld3
from ..utils.colors import colors

class Figure:
    def __init__(self, html_content, metadata={}, logger=None):
        self.content = html_content
        self.metadata = metadata
        self.logger = logger

    def karyoplot(self):
        karyo_dict = {}
  
        lines = re.findall(r'<p>(.*?)</p>', self.content)
        
        chroms = []
        for line in lines:
            values = re.split(r'\s+', line.strip())
            if len(values) == 5:
                chrom, start, stop, name, stain = values
                chroms.append(chrom)

        if chroms:
            chroms.pop(0)

        unique = list(dict.fromkeys(chroms))

        for chromosome in unique:
            karyo_dict[chromosome] = [
                [y[0], float(y[1]), float(y[2]), y[3], y[4]]
                for y in [re.split(r'\s+', line.strip()) for line in lines] 
                if y[0] == chromosome
            ]

        fig, ax = plt.subplots(figsize=(10, 5))

        DIM = 1.0

        def get_chromosome_length(chromosome):
            chromosome_start = float(min([x[1] for x in karyo_dict[chromosome]]))
            chromosome_end = float(max(x[2] for x in karyo_dict[chromosome]))
            chromosome_length = chromosome_end - chromosome_start
            return chromosome_length

        def plot_chromosome(chromosome, order):
            chromosome_length = get_chromosome_length(chromosome)
            chromosome_length_1 = get_chromosome_length(unique[0])

            x_start = order * DIM * 0.1 
            x_end = x_start + (DIM * 0.04)

            y_start = DIM * 0.8 * (chromosome_length / chromosome_length_1)
            y_end = DIM * 0.1

            center_x = x_start + (x_end - x_start) / 2.0
            radius = (x_end - x_start) / 2.0 * 0.96
            theta1 = 0
            theta2 = 180.0

            y_previous = y_start
            for piece in karyo_dict[chromosome]:
                current_height = piece[2] - piece[1]
                current_height_sc = ((y_end - y_start) / chromosome_length) * current_height
                
                y_next = y_previous + current_height_sc
                color = colors.get(piece[4], 'gray')

                r = Rectangle((x_start, y_previous), x_end - x_start, current_height_sc, color=color)
                ax.add_patch(r)

                if piece[3] == 'centromere':
                    square = Rectangle((x_start, y_previous), x_end - x_start, current_height_sc, facecolor='white', edgecolor='white')
                    ax.add_patch(square)
                 
                    half_width = (x_end - x_start)
                    height_tri = current_height_sc / 2

                    triangle_up = Polygon([
                        (center_x - half_width / 2, y_previous),
                        (center_x + half_width / 2, y_previous),
                        (center_x, y_previous + height_tri)
                    ], closed=True, facecolor='#c8c8c8', edgecolor='#c8c8c8')
                    ax.add_patch(triangle_up)

                    triangle_down = Polygon([
                        (center_x - half_width / 2, y_previous + current_height_sc),
                        (center_x + half_width / 2, y_previous + current_height_sc),
                        (center_x, y_previous + current_height_sc - height_tri)
                    ], closed=True, facecolor='#c8c8c8', edgecolor='#c8c8c8')
                    ax.add_patch(triangle_down)

                y_previous = y_next

            w1 = Wedge((center_x, y_start), radius, theta1, theta2, width=0.00001, facecolor='gray', edgecolor='white')
            w2 = Wedge((center_x, y_end), radius, theta2, theta1, width=0.00001, facecolor='gray', edgecolor='white')
            ax.add_patch(w1)
            ax.add_patch(w2)

            ax.plot([x_start, x_start], [y_start, y_end], ls='-', color='white')
            ax.plot([x_end, x_end], [y_start, y_end], ls='-', color='white')

            if chromosome in self.metadata:
                for md in self.metadata[chromosome]:
                    ax.plot([x_end + (DIM * 0.015)], [y_start + (y_end - y_start) * (md / chromosome_length)], '.', color='black')
        
            ax.text(center_x, y_end - (DIM * 0.07 * 2), chromosome, fontsize=3)

        for i, chromosome in enumerate(unique):
            plot_chromosome(chromosome, i + 1)

        ax.axis('off')
        plot_json = mpld3.fig_to_dict(fig)
        return plot_json
