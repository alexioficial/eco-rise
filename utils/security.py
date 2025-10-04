from flask.globals import current_app
from utils.conexion import Session
from typing import Any
from jinja2 import Template
from flask import Flask
from flask.signals import before_render_template, template_rendered


def _render(app: Flask, template: Template, context: dict[str, Any]) -> str:
    app.update_template_context(context)
    before_render_template.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )
    rv = template.render(context)
    template_rendered.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )
    return rv


def render(
    template_name_or_list: str | Template | list[str | Template],
    **context: Any,
) -> str:
    """Render a template by name with the given context.

    :param template_name_or_list: The name of the template to render. If
        a list is given, the first name to exist will be rendered.
    :param context: The variables to make available in the template.
    """
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    template = app.jinja_env.get_or_select_template(template_name_or_list)
    context["session"] = Session.to_dict()
    return _render(app, template, context)
