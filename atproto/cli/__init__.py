from pathlib import Path

import click

from atproto import __version__
from atproto.codegen.clients.generate_async_client import gen_client
from atproto.codegen.models.generator import generate_models
from atproto.codegen.namespaces.generator import generate_namespaces


class AliasedGroup(click.Group):
    """Ref: https://click.palletsprojects.com/en/8.1.x/advanced/"""

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f'Too many matches: {", ".join(sorted(matches))}')

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args


@click.group(cls=AliasedGroup)
@click.version_option(__version__)
@click.pass_context
def atproto_cli(ctx: click.Context):
    """CLI of AT Protocol SDK for Python"""
    ctx.ensure_object(dict)


@atproto_cli.group(cls=AliasedGroup)
@click.option('--lexicon-dir', type=click.Path(exists=True), default=None, help='Path to dir with .JSON lexicon files.')
@click.pass_context
def gen(ctx: click.Context, lexicon_dir):
    if lexicon_dir:
        lexicon_dir = Path(lexicon_dir)
    ctx.obj['lexicon_dir'] = lexicon_dir


@gen.command(name='all', help='Generated models, namespaces, and async clients with default configs.')
@click.pass_context
def gen_all(_: click.Context):
    click.echo('Generating all:')

    click.echo('- models...')
    _gen_models()
    click.echo('- namespaces...')
    _gen_namespaces()
    click.echo('- async clients...')
    _gen_async_version()

    click.echo('Done!')


def _gen_models(lexicon_dir=None, output_dir=None):
    generate_models(lexicon_dir, output_dir)


def _gen_namespaces(lexicon_dir=None, output_dir=None, async_filename=None, sync_filename=None):
    generate_namespaces(lexicon_dir, output_dir, async_filename, sync_filename)


def _gen_async_version():
    gen_client('client.py', 'async_client.py')


@gen.command(name='models')
@click.option('--output-dir', type=click.Path(exists=True), default=None)
@click.pass_context
def gen_models(ctx: click.Context, output_dir):
    click.echo('Generating models...')

    if output_dir:
        # FIXME(MarshalX)
        output_dir = Path(output_dir)
        click.secho(
            "It doesn't work with '--output-dir' option very well because of hardcoded imports! Replace by yourself",
            fg='red',
        )

    _gen_models(ctx.obj.get('lexicon_dir'), output_dir)

    click.echo('Done!')


@gen.command(name='namespaces')
@click.option('--output-dir', type=click.Path(exists=True), default=None)
@click.option('--async-filename', type=click.STRING, default=None, help='Should end with ".py".')
@click.option('--sync-filename', type=click.STRING, default=None, help='Should end with ".py".')
@click.pass_context
def gen_namespaces(ctx: click.Context, output_dir, async_filename, sync_filename):
    click.echo('Generating namespaces...')

    if output_dir:
        output_dir = Path(output_dir)

    _gen_namespaces(ctx.obj.get('lexicon_dir'), output_dir, async_filename, sync_filename)

    click.echo('Done!')


@gen.command(name='async')
@click.pass_context
def gen_async_version(_: click.Context):
    click.echo('Generating async clients...')
    _gen_async_version()
    click.echo('Done!')


if __name__ == '__main__':
    atproto_cli()
