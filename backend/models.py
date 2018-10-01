from geonature.utils.utilssqlalchemy import serializable
from geonature.utils.env import DB

@serializable
class TPrograms(DB.Model):
    __tablename__ = 't_programs'
    __table_args__ = {'schema': 'pr_cmr'}
    id_program = DB.Column(
        DB.Integer,
        primary_key=True,
    )
    program_name = DB.Column(DB.Unicode)
    program_desc = DB.Column(DB.Unicode)