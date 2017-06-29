from pprint import pprint
from shutil import rmtree as delete_directory
from pathlib import Path

from pyramid_jinja2 import (
    Jinja2TemplateRenderer,
    TemplateNotFound,
    DottedNameResolver,
    parse_loader_options_from_settings,
    parse_env_options_from_settings,
    create_environment_from_options,
    IJinja2Environment,
    ENV_CONFIG_PHASE,
)

from ninjadog.ninjadog import render
from ninjadog.constants import TEMPDIR

settings = {}


def asbool(value):
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return value.lower().startswith('t')


class PugTemplateRenderer(Jinja2TemplateRenderer):
    """
    Renders templates that have both pug and jinja2
    syntax.
    
    Conforms to `IRenderer <http://docs.pylonsproject.org/projects/pyramid/en/latest/api/interfaces.html#pyramid.interfaces.IRenderer>`_
    interface.
    """

    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError) as ex:
            raise ValueError('renderer was passed non-dictionary '
                             'as value: %s' % str(ex))
        template = self.template_loader()

        # cheap hack to be able to alter rendering based on config settings
        global settings
        # doctor pug static only option
        static_only = asbool(settings.get('pug.static_only'))
        reload = any(settings.get(val) for val in ('reload_all', 'reload_templates'))

        pprint(settings)

        if static_only and not reload:
            template_path = Path(TEMPDIR, Path(template.filename).name)
            if not template_path.exists():
                html = render(
                    template.render(system),
                    file=template.filename,
                    context=system,
                    with_jinja=True
                )
                template_path.write_text(html)
                return html

            return template_path.read_text()

        return render(
            template.render(system),
            file=template.filename,
            context=system,
            with_jinja=True
        )


class PugRendererFactory:
    """
    Renderer factory conforms to
    `IRendererFactory <http://docs.pylonsproject.org/projects/pyramid/en/latest/api/interfaces.html#pyramid.interfaces.IRendererFactory>`_
    interface.
    """
    environment = None

    def __call__(self, info):
        name, package = info.name, info.package

        def template_loader():
            # attempt to turn the name into a caller-relative asset spec
            if ':' not in name and package is not None:
                try:
                    name_with_package = '%s:%s' % (package.__name__, name)
                    return self.environment.get_template(name_with_package)
                except TemplateNotFound:
                    pass

            return self.environment.get_template(name)

        return PugTemplateRenderer(template_loader)


def add_pug_renderer(config, name, settings_prefix='pug.', package=None):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:
    .. code-block:: python
       config.add_jinja2_renderer('.html', settings_prefix='jinja2.')
    It will register a new renderer, loaded from settings at the specified
    ``settings_prefix`` prefix. This renderer will be active for files using
    the specified extension ``name``.
    """

    # set global settings dictionary
    global settings
    settings = config.get_settings()

    renderer_factory = PugRendererFactory()
    config.add_renderer(name, renderer_factory)

    package = package or config.package
    resolver = DottedNameResolver(package=package)

    def register():
        registry = config.registry
        settings = config.get_settings()

        loader_opts = parse_loader_options_from_settings(
            settings,
            settings_prefix,
            resolver.maybe_resolve,
            package,
        )
        env_opts = parse_env_options_from_settings(
            settings,
            settings_prefix,
            resolver.maybe_resolve,
            package,
        )
        env = create_environment_from_options(env_opts, loader_opts)
        renderer_factory.environment = env

        registry.registerUtility(env, IJinja2Environment, name=name)

    config.action(
        ('pug-renderer', name), register, order=ENV_CONFIG_PHASE)


def includeme(config):
    config.add_directive('add_pug_renderer', add_pug_renderer)
    config.add_pug_renderer('.pug')

    # start with fresh temporary directory
    delete_directory(TEMPDIR, ignore_errors=True)
    TEMPDIR.mkdir()