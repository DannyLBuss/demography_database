from flask import jsonify, request, current_app, url_for
from . import api
from ..models import Population


@api.route('/query/population/<int:id>')
def get_population(id):
    population = Population.query.get_or_404(id)
    return jsonify(population.to_json())