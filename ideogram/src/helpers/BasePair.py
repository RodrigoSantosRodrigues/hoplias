# -*- coding: utf-8 -*-
'''
    author: Rodrigo Junior Santos
    Email:  rodrjuniorsantos@gmail.com

    Fonts reference: https://gist.github.com/kantale/e390cf7a47c4afdff9e4
           https://www.biostars.org/p/9922/
           http://pastebin.com/raw/6nBX6sdE
           https://www.ncbi.nlm.nih.gov/genome/542?fbclid=IwAR0rVGQST-xj-ndCRZDxy1epKkdgskbt47Co1-t6malN949LhQXtBsUSUY8
           https://cnvkit.readthedocs.io/en/stable/quickstart.html
           https://scfbm.biomedcentral.com/articles/10.1186/s13029-015-0042-6
           https://www.rug.nl/about-ug/latest-news/events/promoties/promoties-2018?hfId=2067&lang=nl
'''
import re
from matplotlib.collections import BrokenBarHCollection
from matplotlib import pyplot as plt
import mpld3
from ..utils.colors import colors

class BasePair:
    def __init__(self, html_content, logger=None):
        self.content = html_content
        self.logger = logger

    def detailplot(self):
        height = 0.2
        spacing = 0.3

        def ideograms(html_content):
            last_chromosome = None
            last_specie = None
            last_population = None
      
            lines = re.findall(r'<p>(.*?)</p>', html_content)
            x_ranges, color = [], []
            y_min = 0

            for line in lines:
                if self.logger:
                    self.logger.info(f"read line: {line}")
       
                values = re.split(r'\s+', line.strip())
                if values[0] == '#chrom':
                    continue

                if len(values) == 6:
                    chrom, start, stop, specie, population, stain = values
                elif len(values) == 5:
                    chrom, start, stop, type_col, stain = values
                    specie = type_col
                    population = ""
                else:
                    continue

                try:
                    start = float(start)
                    stop = float(stop)
                except ValueError:
                    if self.logger:
                        self.logger.error(f"Error in convert start/stop for int: {values}")
                    continue

                width = stop - start

                if chrom == last_chromosome or last_chromosome is None:
                    x_ranges.append((start, width))
                    color.append(colors[stain])
                    last_chromosome = chrom
                    last_specie = specie
                    last_population = population
                    continue

                y_min += height + spacing
                y_range = (y_min, height)
                yield x_ranges, y_range, color, last_chromosome, last_specie, last_population
                x_ranges, color = [], []
                x_ranges.append((start, width))
                color.append(colors[stain])
                last_chromosome = chrom
                last_specie = specie
                last_population = population
          
            y_min += height + spacing
            y_range = (y_min, height)
            yield x_ranges, y_range, color, last_chromosome, last_specie, last_population

        fig = plt.figure(figsize=(13, 5))
        ax = fig.add_subplot(111)
        d = {}
        yticks = []
        ytick_labels_list = []

        for x_ranges, y_range, color, chms, species, populations in ideograms(self.content):
            coll = BrokenBarHCollection(x_ranges, y_range, facecolors=color)
            ax.add_collection(coll)
            center = y_range[0] + y_range[1] / 2.
            yticks.append(center)
            label = '%s %s %s' % (chms, species, populations)
            ytick_labels_list.append(label)
            d[chms] = x_ranges
            values = []
            bp = []
            for inter in x_ranges:
                values.append(inter[0])
                bp.append(inter[1])
      
            if values and bp:
                values.append(bp[-1] + values[-1])

                for i in range(0, len(values) - 1):
                    xlabel = '%d bp' % (bp[i])
                    ax.annotate(xlabel, 
                                xy=(values[i + 1] / 2 + values[i] / 2, y_range[0] + y_range[1]),
                                xytext=(values[i + 1] / 2 + values[i] / 2, y_range[0] + y_range[1]),
                                fontsize=2)

        #ax.set_title('Chromosomes')
        ax.axis('tight')
        ax.set_yticks(yticks)
        ax.set_yticklabels(ytick_labels_list)
        ax.set_xticks([])

        plot_json = mpld3.fig_to_dict(fig)
        return plot_json
