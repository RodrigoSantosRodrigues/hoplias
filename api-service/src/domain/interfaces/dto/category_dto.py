import datetime

class CategoryData:
  def __init__(self, name, slug, description, team_id, user_id):
    self.name = name
    self.slug = slug
    self.description = description
    self.user_id = user_id,
    self.team_id = team_id
    self.active = True
    self.actived_at = None
    self.deactived_at = None
    self.deleted_at = None
    self.created_at = datetime.datetime.utcnow
    self.modified_at = datetime.datetime.utcnow
    self.created_by_user = None
    self.modified_by_user = None
    self.deleted_by_user = None

