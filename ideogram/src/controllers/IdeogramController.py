from ..helpers.Ideo import Figure
from ..helpers.BasePair import BasePair
from ..db.IdeogramCrud import IdeogramRepository
from ..utils.utils import format_text_as_html


class IdeogramController:
  def __init__(self, db, data, logger):
    self.data = data
    self.logger= logger
    self.db = db
    self.ideogram_repository = IdeogramRepository(db)

  def create_plot_ideogram(self):
    citogenetic_html = format_text_as_html(self.data.get('text_file'))
    citogenomic_html = format_text_as_html(self.data.get('text_file'))

    ideo = Figure(citogenetic_html, {}, self.logger)
    pairs = BasePair(citogenomic_html, self.logger)

    response = {
      'karioplot': ideo.karyoplot(),
      'detail_plot': pairs.detailplot()
    }
    return response

  def background_plot_ideogram_process(self):
    property = self.ideogram_repository.get_by_id(self.data.get('ideogram_id'))

    citogenetic_html = format_text_as_html(property.get('text_gff'))
    citogenomic_html = format_text_as_html(property.get('text_gff'))

    ideo = Figure(citogenetic_html, {}, self.logger)
    pairs = BasePair(citogenomic_html, self.logger)

    karioplot = ideo.karyoplot()
    detail_plot = pairs.detailplot()

    self.ideogram_repository.update(
      property,
      { 
        'citogenetic_view': karioplot,
        'citogenomic_view': detail_plot
      }
    )
 