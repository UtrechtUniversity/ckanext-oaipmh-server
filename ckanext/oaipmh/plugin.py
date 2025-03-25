import logging
from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import toolkit as tk
#from ckan.plugins import IRoutes, IConfigurer
from ckan.plugins import IConfigurer
from ckan.plugins import IBlueprint
import ckanext.oaipmh.blueprints as blueprints

log = logging.getLogger(__name__)


class OAIPMHPlugin(SingletonPlugin):
    '''OAI-PMH plugin, maps the controller and uses the template configuration
    stanza to have the template render in case there is no parameters to the
    interface.
    '''
#    implements(IRoutes, inherit=True)
    implements(IConfigurer)
    implements(IBlueprint)

    def update_config(self, config):
        """This IConfigurer implementation causes CKAN to look in the
        ```public``` and ```templates``` directories present in this
        package for any customisations.

        It also shows how to set the site title here (rather than in
        the main site .ini file), and causes CKAN to use the
        customised package form defined in ``package_form.py`` in this
        directory.
        """
        tk.add_template_directory(config, 'templates')

    #IBlueprint
    def get_blueprint(self):
        return [blueprints.oai]

    # def before_map(self, map):
    #     '''Map the controller to be used for OAI-PMH.
    #     '''
    #     controller = 'ckanext.oaipmh.controller:OAIPMHController'
    #     map.connect('oai', '/oai', controller=controller, action='index')
    #     return map
